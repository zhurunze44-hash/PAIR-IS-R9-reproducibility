#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
out="${1:-$root/output/constructed}"
mkdir -p "$out"
# The inherited exact test writes next to its own script; isolate it in output.
cp "$root/verification/independent_contract_checks.py" "$out/"
python3 "$out/independent_contract_checks.py"
python3 "$root/verification/test_G0_G2_synthetic.py"
python3 - "$out/constructed_theory_receipt.json" <<'PYX'
import json,sys
j=json.load(open(sys.argv[1]))
assert j.get('status')=='PASS_CONSTRUCTED_ONLY'
assert j.get('no_native_experimental_data') is True
print('PASS_CONSTRUCTED_ONLY: no native-performance or biological claim')
PYX
