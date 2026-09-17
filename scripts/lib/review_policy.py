"""Pure validation and review routing; no Git, filesystem or model calls."""
from fnmatch import fnmatchcase

SOURCE_PATTERNS = ['*.py', '*.sh', '*.js', '*.jsx', '*.ts', '*.tsx', '*.rs',
                   '*.go', '*.c', '*.h', '*.cpp', '*.hpp', '*.java', '*.rb', '*.swift']
LARGE_DEFAULTS = dict(enabled=False, source_line_threshold=300,
                      changed_line_threshold=500, changed_file_threshold=5,
                      cross_module_trigger=True, isolation='separate_context', model='')
STRUCTURE_DEFAULTS = dict(source_file_line_threshold=300, implementation_file_line_threshold=300,
                          changed_line_threshold=500, source_globs=SOURCE_PATTERNS,
                          implementation_globs=SOURCE_PATTERNS, exclude_globs=[], modules={})


def table(value, name):
    if not isinstance(value, dict):
        raise ValueError(f'{name} must be a table')
    return value


def validate_route(value, choices, name):
    table(value, name)
    if value.get('isolation') not in choices:
        raise ValueError(f'{name}.isolation must be one of {sorted(choices)}')
    if not isinstance(value.get('model'), str):
        raise ValueError(f'{name}.model must be a string')
    if any(ord(char) < 32 or ord(char) == 127 for char in value['model']):
        raise ValueError(f'{name}.model must not contain control characters')


def positive_int(value, name):
    if type(value) is not int or value < 1:
        raise ValueError(f'{name} must be a positive integer')


def patterns(value, name):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
        raise ValueError(f'{name} must be an array of nonempty glob strings')


def validate_settings(raw):
    table(raw, 'settings')
    if set(raw) - {'review', 'implementation', 'source_structure'}:
        raise ValueError('unknown settings section')
    review = dict(isolation='same_context', model='')
    review.update(table(raw.get('review', {}), 'review'))
    if set(review) - {'isolation', 'model', 'large_change'}:
        raise ValueError('unknown review setting')
    validate_route(review, {'same_context', 'separate_context', 'ask'}, 'review')
    implementation = dict(isolation='host', model='')
    implementation.update(table(raw.get('implementation', {}), 'implementation'))
    if set(implementation) - {'isolation', 'model'}:
        raise ValueError('unknown implementation setting')
    validate_route(implementation, {'host', 'separate_context', 'ask'}, 'implementation')
    large = dict(LARGE_DEFAULTS)
    large.update(table(review.get('large_change', {}), 'review.large_change'))
    if set(large) - (set(LARGE_DEFAULTS) | {'token_budget'}):
        raise ValueError('unknown large_change setting')
    validate_route(large, {'same_context', 'separate_context', 'ask'}, 'review.large_change')
    for key in ['enabled', 'cross_module_trigger']:
        if type(large[key]) is not bool:
            raise ValueError(f'{key} must be boolean')
    for key in ['source_line_threshold', 'changed_line_threshold', 'changed_file_threshold', 'token_budget']:
        if key in large:
            positive_int(large[key], key)
    structure = dict(STRUCTURE_DEFAULTS)
    structure.update(table(raw.get('source_structure', {}), 'source_structure'))
    if set(structure) - set(STRUCTURE_DEFAULTS):
        raise ValueError('unknown source_structure setting')
    for key in ['source_file_line_threshold', 'implementation_file_line_threshold', 'changed_line_threshold']:
        positive_int(structure[key], key)
    for key in ['source_globs', 'implementation_globs', 'exclude_globs']:
        patterns(structure[key], key)
    for name, globs in table(structure['modules'], 'modules').items():
        patterns(globs, f'modules.{name}')
    return dict(review=review, implementation=implementation, large_change=large,
                source_structure=structure, structure_configured='source_structure' in raw)


def matches(path, globs):
    return any(fnmatchcase(path, pattern) for pattern in globs)


def select_review(settings, metrics):
    normal, large = settings['review'], settings['large_change']
    result = dict(isolation=normal['isolation'], model=normal['model'], reasons=[], status='normal')
    if not large['enabled']:
        return result
    for field, threshold in [('max_implementation_lines', 'source_line_threshold'),
                             ('changed_lines', 'changed_line_threshold'),
                             ('changed_files', 'changed_file_threshold')]:
        if metrics[field] is not None and metrics[field] > large[threshold]:
            result['reasons'].append(field)
    if large['cross_module_trigger'] and metrics['module_count'] is not None and metrics['module_count'] > 1:
        result['reasons'].append('cross_module')
    if result['reasons']:
        result.update(isolation=large['isolation'], model=large['model'], status='large_change')
        if 'token_budget' in large:
            result['token_budget'] = large['token_budget']
    elif metrics['unknown']:
        result.update(isolation='ask', status='unknown', reasons=metrics['unknown'])
    return result
