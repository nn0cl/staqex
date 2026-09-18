#!/usr/bin/env python3
"""Emit committed change evidence and requested review routing; Python 3.11+."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent/'lib'))
from change_metrics import measure
from review_policy import select_review, validate_settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--base', required=True, help='explicit comparison commit/ref')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--settings', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    path = args.settings or root/'docs/collaboration/runtime-routing.toml'
    if args.settings and not path.is_file():
        raise ValueError(f'explicit settings file not found: {path}')
    settings = validate_settings(tomllib.loads(path.read_text()) if path.is_file() else {})
    metrics = measure(root, args.base, args.head, settings)
    print(json.dumps(dict(schema_version=1, settings_path=str(path), metrics=metrics,
                          review=select_review(settings, metrics)), indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'review measurement failed: {error}', file=sys.stderr)
        raise SystemExit(1)
