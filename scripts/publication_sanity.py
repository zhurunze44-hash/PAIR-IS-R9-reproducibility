#!/usr/bin/env python3
"""Check that the code capsule has real files without claiming native replay."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parent.parent
required=[
 'manuscript/PAIR_IS_R9_Main.tex','manuscript/PAIR_IS_R9_Supplement.tex',
 'manuscript/references.bib','manuscript/figures/figure_01.pdf',
 'verification/independent_contract_checks.py',
 'verification/G0_G2_native_fair_baseline.py',
 'verification/test_G0_G2_synthetic.py',
 'evidence/evidence_index_historical.csv','evidence/RELEASE_COVERAGE.csv',
 'evidence/upstream_data_sources.csv','scripts/release_gate.py'
]
missing=[v for v in required if not (root/v).is_file()]
if missing:raise SystemExit('HOLD MISSING '+str(missing))
s=(root/'manuscript/PAIR_IS_R9_Main.tex').read_text(encoding='utf-8')
if 'must be confirmed by the authors before submission' in s:
 raise SystemExit('HOLD original draft availability statement present')
if 'REPLACE_WITH_ACTUAL_OWNER' in (root/'CITATION.cff').read_text():
 raise SystemExit('HOLD invented GitHub URL')
status=json.loads((root/'RELEASE_STATUS.json').read_text())
assert status['may_claim_full_public_reproduction'] is False
print('PASS software capsule present; NOT full native data reproduction')
