"""Git measurements and Python syntax counts; responsibility remains a review judgment."""
import ast
import subprocess

from review_policy import matches


def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, check=True)
    return result.stdout


def blob(root, ref, path):
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=root, capture_output=True)
    if result.returncode:
        return None
    return result.stdout


def syntax_counts(content, path):
    if not path.endswith('.py') or content is None:
        return dict(classes=None, functions=None, imports=None)
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError):
        return dict(classes=None, functions=None, imports=None)
    nodes = list(ast.walk(tree))
    imports = []
    for node in nodes:
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append('.' * node.level + (node.module or ''))
    return dict(classes=sum(isinstance(node, ast.ClassDef) for node in nodes),
                functions=sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in nodes),
                imports=sorted(set(imports)))


def line_count(content):
    if content is None:
        return 0
    if b'\0' in content:
        return None
    try:
        return len(content.decode('utf-8').splitlines())
    except UnicodeDecodeError:
        return None


def measure(root, base, head, settings):
    base = git(root, 'rev-parse', '--verify', f'{base}^{{commit}}').decode().strip()
    head = git(root, 'rev-parse', '--verify', f'{head}^{{commit}}').decode().strip()
    structure = settings['source_structure']
    unknown, files, modules = [], [], set()
    if git(root, 'status', '--porcelain', '--untracked-files=normal'):
        unknown.append('working tree contains changes not represented by the committed diff')
    stats = git(root, 'diff', '--no-renames', '--numstat', '-z', base, head, '--')
    changed_lines, max_lines = 0, 0
    for entry in stats.split(b'\0'):
        if not entry:
            continue
        added, deleted, raw_path = entry.split(b'\t', 2)
        path = raw_path.decode('utf-8', errors='surrogateescape')
        if matches(path, structure['exclude_globs']):
            continue
        delta = None if added == b'-' else int(added) + int(deleted)
        if delta is None:
            unknown.append(f'binary diff: {path}')
        else:
            changed_lines += delta
        item = dict(path=path, changed_lines=delta)
        is_source = matches(path, structure['source_globs'])
        is_implementation = matches(path, structure['implementation_globs'])
        if is_source or is_implementation:
            before, after = blob(root, base, path), blob(root, head, path)
            lengths = [line_count(before), line_count(after)]
            if None in lengths:
                unknown.append(f'unreadable source: {path}')
            maximum = max(value for value in lengths if value is not None) if any(x is not None for x in lengths) else 0
            if is_implementation:
                max_lines = max(max_lines, maximum)
            item.update(base_lines=lengths[0], head_lines=lengths[1], **syntax_counts(after, path))
            item['responsibilities'] = 'review required'
            item['cycles'] = 'not assessed; imports are static observations, not a resolved dependency graph'
            if settings['structure_configured']:
                exceeded = []
                if is_source and maximum > structure['source_file_line_threshold']:
                    exceeded.append('source_file_line_threshold')
                if is_implementation and maximum > structure['implementation_file_line_threshold']:
                    exceeded.append('implementation_file_line_threshold')
                item['structure_exceeded'] = exceeded
            owners = {name for name, globs in structure['modules'].items() if matches(path, globs)}
            modules.update(owners)
            if len(owners) != 1 and settings['large_change']['cross_module_trigger']:
                unknown.append(f'module ownership missing or ambiguous: {path}')
        files.append(item)
    metrics = dict(base_sha=base, head_sha=head, changed_lines=changed_lines, changed_files=len(files),
                   max_implementation_lines=max_lines, module_count=len(modules), unknown=unknown,
                   files=files, excluded_globs=structure['exclude_globs'])
    metrics['structure_change_exceeded'] = (settings['structure_configured'] and
                                            changed_lines > structure['changed_line_threshold'])
    return metrics
