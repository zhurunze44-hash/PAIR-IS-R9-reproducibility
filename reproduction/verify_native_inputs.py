#!/usr/bin/env python3
"""Read-only hash check of historical Paper2 inputs; NOT a model or producer replay."""
import argparse,csv,datetime as dt,hashlib,json,re,sys
from pathlib import Path
SCHEMA="PAIR_R9_PINNED_ASSETS_V1"
HEX64=re.compile(r"^[0-9a-f]{64}$")
def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def resolved_path(roots,loc):
    key=loc["root"]
    if key not in roots:raise ValueError("Unknown source root")
    root=Path(roots[key]).expanduser().resolve()
    rel=Path(loc["relative_path"])
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:raise ValueError("Unsafe relative path")
    path=(root/rel).resolve()
    if not path.is_relative_to(root):raise ValueError("Path escapes source root")
    return path
def verify(pins,locations,out):
    if pins.get("schema_version")!=SCHEMA or locations.get("schema_version")!=SCHEMA:raise ValueError("Manifest schema mismatch")
    artifacts=pins.get("artifacts");roots=locations.get("roots");locs=locations.get("locations")
    if not isinstance(artifacts,list) or not artifacts or not isinstance(roots,dict) or not isinstance(locs,dict):raise ValueError("Missing artifact/location records")
    out=Path(out).expanduser().resolve()
    if out.exists():raise ValueError("Output must be a new directory")
    for src in roots.values():
        if out.is_relative_to(Path(src).expanduser().resolve()):raise ValueError("Output may not be under a frozen source root")
    out.mkdir(parents=True,mode=0o700)
    rows=[]
    for obj in artifacts:
        ident=str(obj.get("id",""));expect=obj.get("sha256","");size=obj.get("size_bytes")
        row={"id":ident,"claims":",".join(obj.get("claims",[])),"name":obj.get("name",""),
             "expected_sha256":expect,"observed_sha256":"","expected_size":size,"observed_size":None,"status":"HOLD_UNCHECKED"}
        try:
            if not isinstance(expect,str) or not HEX64.fullmatch(expect):raise ValueError("Invalid SHA256")
            if not isinstance(size,int) or size<0:raise ValueError("Invalid size")
            path=resolved_path(roots,locs[ident])
            if not path.is_file():row["status"]="HOLD_MISSING"
            else:
                row["observed_size"]=path.stat().st_size
                if row["observed_size"]!=size:row["status"]="FAIL_SIZE_MISMATCH"
                else:
                    row["observed_sha256"]=sha256_file(path)
                    row["status"]="PASS_INPUT_BYTES" if row["observed_sha256"]==expect else "FAIL_SHA256_MISMATCH"
        except (OSError,ValueError,KeyError,TypeError) as exc:
            row["status"]="HOLD_LOCATION_OR_IO_"+type(exc).__name__
        rows.append(row)
    path=out/"PER_ARTIFACT.csv"
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    claims=sorted({c for r in rows for c in r["claims"].split(",") if c})
    per={c:("PASS_PINNED_INPUT_BYTES_ONLY" if all(r["status"]=="PASS_INPUT_BYTES" for r in rows if c in r["claims"].split(",")) else "HOLD_SOME_INPUTS_MISSING_OR_CHANGED") for c in claims}
    state="PASS_ALL_PINNED_INPUT_BYTES_ONLY" if all(r["status"]=="PASS_INPUT_BYTES" for r in rows) else "HOLD_MISSING_OR_CHANGED_INPUTS"
    report={"schema_version":SCHEMA,"generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"status":state,
            "checked_artifacts":len(rows),"passed_artifacts":sum(r["status"]=="PASS_INPUT_BYTES" for r in rows),
            "claims":per,"scientific_replay_status":"NOT_EXECUTED","original_producer_authentication":"NOT_ESTABLISHED_BY_HASH_CHECK",
            "redistribution_license":"NOT_ESTABLISHED","no_source_files_modified":True,"receipt_sha256":sha256_file(path)}
    (out/"VERDICT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pins",type=Path,required=True);p.add_argument("--locations",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    try:report=verify(json.loads(a.pins.read_text()),json.loads(a.locations.read_text()),a.out)
    except Exception as exc:print("HOLD:",str(exc),file=sys.stderr);return 2
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report["status"]=="PASS_ALL_PINNED_INPUT_BYTES_ONLY" else 3
if __name__=="__main__":raise SystemExit(main())
