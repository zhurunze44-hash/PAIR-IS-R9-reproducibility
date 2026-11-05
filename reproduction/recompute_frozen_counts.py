#!/usr/bin/env python3
"""Read-only saved-count diagnostics; these are NOT independent biological replays."""
import argparse,csv,gzip,json,sys
from pathlib import Path
from verify_native_inputs import resolved_path
def tsv_data_rows(path,opener=open):
    with opener(path,"rt",encoding="utf-8",newline="") as f:return max(0,sum(1 for _ in csv.reader(f,delimiter="\t"))-1)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("pins","locations","audit","out"):p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--k562-status-column",default="status");a=p.parse_args()
    pins=json.loads(a.pins.read_text());loc=json.loads(a.locations.read_text());audit=json.loads(a.audit.read_text())
    if audit.get("status")!="PASS_ALL_PINNED_INPUT_BYTES_ONLY":raise SystemExit("HOLD: native SHA gate has not passed")
    out=a.out.resolve()
    if out.exists():raise SystemExit("HOLD: output directory exists")
    if any(out.is_relative_to(Path(x).resolve()) for x in loc["roots"].values()):raise SystemExit("HOLD: write into source root forbidden")
    out.mkdir(parents=True,mode=0o700)
    paths={x["name"]:resolved_path(loc["roots"],loc["locations"][x["id"]]) for x in pins["artifacts"]}
    checks={}
    for name,n,opener in (("ENCODE_V4F03_COMPOSITE_BASIS.tsv.gz",56395,gzip.open),("QUERY_PANEL_Q4.tsv",100000,open),("NTC_97.tsv",97,open)):
        try:
            rows=tsv_data_rows(paths[name],opener)
            checks[name]={"status":"PASS_COUNT" if rows==n else "FAIL_COUNT","rows":rows,"expected":n}
        except Exception as exc:checks[name]={"status":"HOLD_READ_ERROR","error_type":type(exc).__name__}
    try:
        import pyarrow.parquet as pq
        pf=pq.ParquetFile(paths["QUERY_RESULTS.parquet"]);col=a.k562_status_column
        if col not in pf.schema.names:raise ValueError("Status column not found: "+col)
        counts={}
        for batch in pf.iter_batches(columns=[col],batch_size=2048):
            for val in batch.column(0).to_pylist():
                key=str(val);counts[key]=counts.get(key,0)+1
        good=(pf.metadata.num_rows==3125 and counts.get("COMPARATIVE_ASSERTABLE")==349 and counts.get("NOT_IDENTIFIABLE")==2776 and sum(counts.values())==3125)
        checks["QUERY_RESULTS.parquet"]={"status":"PASS_SAVED_TERMINAL_COUNTS_ONLY" if good else "FAIL_TERMINAL_COUNTS","counts":counts}
    except Exception as exc:checks["QUERY_RESULTS.parquet"]={"status":"HOLD_PARQUET_CHECK","reason":str(exc)[:300]}
    source=paths.get("is_train_split00.npy")
    if source:
        n=len(list(source.parent.glob("is_train_split*.npy")))
        checks["ENCODE_masks"]={"status":"PASS_FILE_COUNT_ONLY" if n==20 else "HOLD_FILE_COUNT","found":n,"expected":20}
    ok=all(v["status"].startswith("PASS") for v in checks.values())
    verdict={"status":"PASS_SAVED_COUNT_DIAGNOSTICS_ONLY" if ok else "HOLD_SAVED_COUNT_DIAGNOSTICS","checks":checks,
             "source_producer_certified":False,"score_recomputed":False,"measured_biological_effects_verified":False}
    (out/"FROZEN_COUNT_CHECK.json").write_text(json.dumps(verdict,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(verdict,indent=2,ensure_ascii=False));return 0 if ok else 3
if __name__=="__main__":sys.exit(main())
