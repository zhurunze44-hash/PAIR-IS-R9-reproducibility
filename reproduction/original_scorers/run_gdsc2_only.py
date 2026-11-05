#!/usr/bin/env python3
"""Run the archived GDSC scorer on GDSC2 only without modifying the original scorer."""
import argparse
import json
from pathlib import Path
from gdsc_independent_scorer import run_resource

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pred-root",type=Path,required=True)
    p.add_argument("--published-scores",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    if not a.pred_root.is_dir() or not a.published_scores.is_file():
        p.error("The original prediction root and published-score TSV must exist")
    if a.out_dir.exists():
        p.error("Output directory must be new; frozen results may never be overwritten")
    a.out_dir.mkdir(parents=True)
    result=run_resource("GDSC2",a.pred_root,a.published_scores,a.out_dir)
    status="PASS_GDSC2_SCORER_RESULT_ONLY" if result.get("all_match") and result.get("persistent_pairs_nR2")==0 else "FAIL_OR_HOLD_GDSC2"
    report={"status":status,"source_function":"gdsc_independent_scorer.run_resource",
            "source_sha256":"fd218e164737f4f06d2c6e2f30412e749e4a8cc07b85a8bf39d40bcd1c8d3133",
            "GDSC1":"NOT_EXECUTED","K562_PRODUCER":"NOT_CERTIFIED","summary":result}
    (a.out_dir/"GDSC2_ONLY_WRAPPER_VERDICT.json").write_text(json.dumps(report,indent=2)+"\n")
    print(status)
    return 0 if status.startswith("PASS") else 3
if __name__=="__main__":
    raise SystemExit(main())
