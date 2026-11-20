#!/usr/bin/env python3
"""Check the current manuscript files, source archive and public entry points."""

import hashlib
import json
from pathlib import Path
import re
import zipfile

root = Path(__file__).resolve().parents[1]
record = json.loads((root / 'evidence/KBS_FILE_ALIGNMENT.json').read_text())
release = json.loads((root / 'RELEASE_STATUS.json').read_text())

assert record['scientific_results_changed'] is False
for field in ('title', 'main_pages', 'supplement_pages', 'complete_pages'):
    assert record[field] == release[field], field
assert record['complete_pages'] == record['main_pages'] + record['supplement_pages']

files = record['files']
for path, digest in files.items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, path

source = record['source_zip']
assert source == release['current_source']
source_files = set(files) - {*record['pdfs'], source}
excluded = set(record['source_zip_excluded_frozen_files'])
assert excluded <= source_files, sorted(excluded - source_files)
expected_members = {path.removeprefix('manuscript/') for path in source_files - excluded}
with zipfile.ZipFile(root / source) as archive:
    assert archive.testzip() is None
    members = archive.namelist()
    actual_members = set(members)
    assert len(members) == len(actual_members), 'Duplicate source ZIP member names'
    assert actual_members == expected_members, {
        'missing': sorted(expected_members - actual_members),
        'extra': sorted(actual_members - expected_members),
    }
    for member in members:
        assert archive.read(member) == (root / 'manuscript' / member).read_bytes(), member

title = record['title']
main = (root / 'manuscript/PAIR_KBS_Main.tex').read_text()
supplement = (root / 'manuscript/PAIR_KBS_Supplement.tex').read_text()
assert '\\journal{Knowledge-Based Systems}' in main
assert f'\\providecommand{{\\PaperTitle}}{{{title}}}' in main
assert title in supplement
assert f'title: {json.dumps(title)}' in (root / 'CITATION.cff').read_text()

docs = ['README.md', 'DATA_AND_CODE_AVAILABILITY.md', 'REPRODUCIBILITY.md',
        'SUBMISSION_SOFTWARE_COVERAGE.md', 'submission/README.md']
for name in docs:
    doc = root / name
    for target in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
        if re.match(r'^[a-z]+://', target) or target.startswith('#'):
            continue
        assert (doc.parent / target.split('#', 1)[0]).exists(), (name, target)

print(f'PASS KBS alignment: {len(files)} files, {len(expected_members)} source members and public links')
