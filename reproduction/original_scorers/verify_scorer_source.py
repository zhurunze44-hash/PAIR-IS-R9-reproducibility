#!/usr/bin/env python3
"""Check exact historical scorer source bytes; does not execute real-data scoring."""
from pathlib import Path
import ast,hashlib,json,sys
root=Path(__file__).resolve().parent
expected={
"independent_scorer.py":"c42ff2c49a1d74952d28a42a031410bfcac587d46ddf3f01db2a58e1934aa83a",
"gdsc_independent_scorer.py":"fd218e164737f4f06d2c6e2f30412e749e4a8cc07b85a8bf39d40bcd1c8d3133"}
rows=[]
for name,sha in expected.items():
    path=root/name
    if not path.is_file():
        rows.append({"file":name,"status":"HOLD_MISSING"});continue
    blob=path.read_bytes()
    actual=hashlib.sha256(blob).hexdigest()
    try:ast.parse(blob.decode("utf-8"),filename=name);syntax=True
    except (UnicodeError,SyntaxError):syntax=False
    rows.append({"file":name,"sha256":actual,"status":"PASS_ORIGINAL_SOURCE_BYTES" if actual==sha and syntax else "FAIL_SOURCE_IDENTITY_OR_SYNTAX"})
status="PASS_SOURCE_BYTES_ONLY" if all(r["status"]=="PASS_ORIGINAL_SOURCE_BYTES" for r in rows) else "HOLD_OR_FAIL"
print(json.dumps({"status":status,"files":rows,"original_scoring_replay":"NOT_PERFORMED"},indent=2))
sys.exit(0 if status.startswith("PASS") else 3)
