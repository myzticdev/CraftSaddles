"""Extract a matching changelog entry and require completed manual release checks."""
from pathlib import Path
import re
import sys

import hashlib

from build import TARGETS, parse, require, release_files

ROOT = Path(__file__).resolve().parents[1]


def release_notes(tag):
    require(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', tag), 'Expected vMAJOR.MINOR.PATCH')
    changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    entry = re.search(r'^## \[' + re.escape(tag[1:]) + r'\][^\n]*\n(.*?)(?=^## |\Z)',
                      changelog, re.MULTILINE | re.DOTALL)
    require(entry and entry[1].strip(), 'No changelog entry for this tag')
    record = parse((ROOT / 'tests/manual-results.json').read_bytes())
    required = ['1.13', '1.13.2', '1.14', '1.16.1', '1.16.5', '1.17.1', '1.18.1',
                '1.18.2', '1.19.3', '1.19.4', '1.20.1', '1.20.2', '1.20.4', '1.20.5',
                '1.20.6', '1.21', '1.21.1', '1.21.2', '1.21.4', '1.21.5']
    require([r['minecraft'] for r in record] == required, 'Incomplete manual test matrix')
    releases = release_files()
    for row in record:
        version = tuple(int(part) for part in row['minecraft'].split('.'))
        expected_zip = None
        for name, _, _ in TARGETS:
            endpoints = name.split('-')
            low = tuple(int(part) for part in endpoints[0].split('.'))
            high = tuple(int(part) for part in endpoints[-1].split('.'))
            if low <= version <= high:
                expected_zip = f'CraftSaddles-{name}.zip'
        require(row['zip'] == expected_zip, f"Wrong test artifact: {row['minecraft']}")
        require(row['status'] == 'passed' and row['date'] and row['notes'],
                f"Manual check pending or failed: {row['minecraft']}")
        require(all(row['checks'].get(check) is True for check in
                    ('enabled', 'creative_output', 'survival_consumption', 'wrong_pattern', 'batch_consumption')),
                f"Incomplete gameplay results: {row['minecraft']}")
        require(row['artifact_sha256'] == hashlib.sha256(releases[row['zip']]).hexdigest(),
                f"Tested artifact differs from this build: {row['minecraft']}")
    require(re.search(r'^## \[' + re.escape(tag[1:]) + r'\] - \d{4}-\d{2}-\d{2}$',
                      changelog, re.MULTILINE), 'Release changelog entry must be dated')
    return entry[1].strip()


if __name__ == '__main__':
    try:
        print(release_notes(sys.argv[1] if len(sys.argv) == 2 else ''))
    except (ValueError, OSError, KeyError, TypeError) as error:
        sys.exit(str(error))
