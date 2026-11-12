#!/usr/bin/env python3
"""Check GitHub correspondence with the unchanged Gemini KBS materials."""
from pathlib import Path
import hashlib,json,re,zipfile

root=Path(__file__).resolve().parents[1]
record=json.loads((root/'evidence/KBS_FILE_ALIGNMENT.json').read_text())
assert record['scientific_text_changed'] is False
assert record['scientific_results_changed'] is False
assert (record['main_pages'],record['supplement_pages'])==(26,46)
for entry in record['files']:
    p=root/entry['repository_path']
    assert p.is_file(),entry['repository_path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],entry['repository_path']
capsule=record['generated_software_capsule']
assert hashlib.sha256((root/capsule['path']).read_bytes()).hexdigest()==capsule['sha256']
for name in ['Manuscript_Source.zip','Supplementary_Source.zip']:
    with zipfile.ZipFile(root/'submission'/name) as z:
        assert z.testzip() is None
        for entry in z.namelist():
            assert z.read(entry)==(root/'manuscript'/entry).read_bytes(),(name,entry)
main=(root/'manuscript/PAIR_KBS_Main.tex').read_text()
assert '\\journal{Knowledge-Based Systems}' in main
assert record['title'] in main
assert not list((root/'manuscript').glob('*IS_R9*'))
metadata=(root/'submission/Metadata.txt').read_text()
assert 'TARGET JOURNAL: Knowledge-Based Systems' in metadata
assert record['title'] in metadata
for p in [root/'README.md',root/'REPRODUCIBILITY.md',root/'submission/README.md']:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if re.match(r'^[a-z]+://',link) or link.startswith('#'):continue
        assert (p.parent/link.split('#',1)[0]).exists(),(p.name,link)
print(f'PASS_GEMINI_KBS_ALIGNMENT: {len(record["files"])} original file identities, source ZIPs and KBS entry points agree')
