#!/usr/bin/env python3
"""Paper2 R8 bounded, read-only G0/G1/G2 auditor.

This tool NEVER discovers or certifies a historical producer on its own. It only
checks byte identities supplied by an independently authenticated original
manifest, and recomputes algebra on fully supplied per-query arrays. All output
is written under --out, not under the source root. It cannot prove B3 gains.

Input schema: native_manifest_TEMPLATE.json; query data are numeric .npz
containing XR, XE, F, YR, YE, a, RR, RE and ref_ids, eval_ids. No pickle.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from pathlib import Path
import numpy as np

REQUIRED_SOURCE = ("historical_train_mask", "historical_source_ledger", "historical_producer_call_trace")
REQ_ARRAYS = ("XR", "XE", "F", "YR", "YE", "a", "RR", "RE", "ref_ids", "eval_ids", "source_ids")


def hash_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 19), b""):
            h.update(b)
    return h.hexdigest()


def in_root(root: Path, rel: str) -> Path:
    if not rel or Path(rel).is_absolute():
        raise ValueError("Relative source file path required; never write to source root")
    p = (root / rel).resolve(strict=False)
    if not p.is_relative_to(root):
        raise ValueError("Path escapes declared source root")
    return p


def checked_file(root: Path, obj: dict, name: str) -> Path:
    if not isinstance(obj, dict):
        raise ValueError(f"{name}: missing file evidence descriptor")
    p = in_root(root, obj.get("path", ""))
    sha = obj.get("sha256", "")
    if not (len(sha) == 64 and all(c in "0123456789abcdef" for c in sha)):
        raise ValueError(f"{name}: sha256 must be full lowercase digest")
    if not p.is_file():
        raise ValueError(f"{name}: missing at declared path")
    if hash_file(p) != sha:
        raise ValueError(f"{name}: hash mismatch")
    return p


def normalize(arr, nd, name):
    z = np.asarray(arr)
    if z.ndim != nd or z.dtype.kind not in "biuf":
        raise ValueError(f"{name} numeric ndim {nd} required")
    z = np.asarray(z, dtype=np.float64)
    if not np.isfinite(z).all():
        raise ValueError(f"{name} non-finite values")
    return z


def compute_one(path: Path, q: dict, tolerances: dict) -> dict:
    with np.load(path, allow_pickle=False) as npz:
        missing = [k for k in REQ_ARRAYS if k not in npz]
        if missing:
            raise ValueError(f"{q['query_id']}: array keys missing {missing}")
        XR = normalize(npz["XR"], 2, "XR")
        XE = normalize(npz["XE"], 2, "XE")
        F = normalize(npz["F"], 2, "F")
        YR = normalize(npz["YR"], 1, "YR")
        YE = normalize(npz["YE"], 1, "YE")
        a = normalize(npz["a"], 1, "a")
        RR = normalize(npz["RR"], 2, "RR")
        RE = normalize(npz["RE"], 2, "RE")
        ids_r = [str(z) for z in npz["ref_ids"].tolist()]
        ids_e = [str(z) for z in npz["eval_ids"].tolist()]
        ids_s = [str(z) for z in npz["source_ids"].tolist()]
    nr, p = XR.shape
    ne, p2 = XE.shape
    if nr < 1 or ne < 1 or p != p2 or p < 1:
        raise ValueError("Invalid nonempty reference/evaluation designs")
    if F.shape != (p, nr) or YR.shape != (nr,) or YE.shape != (ne,) or a.shape != (ne,):
        raise ValueError("Array dimensional mismatch to declared query")
    if RR.shape[0] != nr or RE.shape[0] != ne or RR.shape[1] != RE.shape[1]:
        raise ValueError("Source ledger row/column mismatch")
    if len(ids_r) != nr or len(ids_e) != ne or len(set(ids_r)) != nr or len(set(ids_e)) != ne or len(ids_s)!=RR.shape[1] or len(set(ids_s)) !=len(ids_s):
        raise ValueError("Identity order / duplicate identity invalid")
    if any(not x for x in ids_r + ids_e):
        raise ValueError("Empty row identity")
    if q.get("reference_row_ids") != ids_r or q.get("request_row_ids") != ids_e or q.get("ordered_source_ids") != ids_s:
        raise ValueError("Ordered row identities disagree with manifest")
    abs_tol = float(tolerances["absolute"])
    relative_tol = float(tolerances["relative"])
    # A fixed linear completion must act as generalized inverse on the reference design.
    ginv = float(np.linalg.norm(XR @ F @ XR-XR, ord=np.inf))
    if ginv > abs_tol + relative_tol * max(float(np.linalg.norm(XR, np.inf)), 1.0):
        raise ValueError("F is not a verified generalized-inverse completion at tolerance")
    w = a @ XE
    # Structural B1 via row-space LS, separately using the numerical nullspace.
    coef, *_ = np.linalg.lstsq(XR.T, w, rcond=None)
    residual = float(np.linalg.norm(XR.T @ coef-w, ord=np.inf))
    colscale = max(float(np.linalg.norm(w, ord=np.inf)), 1.)
    classical_legal = residual <= abs_tol + relative_tol*colscale
    u, sing, vh = np.linalg.svd(XR, full_matrices=True)
    s_tol = abs_tol + relative_tol*(sing[0] if sing.size else 1.)
    rank = int((sing>s_tol).sum())
    null = vh[rank:].T
    null_residual = float(np.linalg.norm(w @ null, ord=np.inf)) if null.size else 0.0
    pair_legal = null_residual <= abs_tol + relative_tol*colscale
    if classical_legal != pair_legal:
        raise ValueError("B1 structural discrepancy: numerical threshold/rank ambiguity")
    h = w @ F
    classical_z = float(a @ YE - h @ YR)
    pair_z = float(a @ (YE-XE @ (F @ YR)))
    source = a @ RE - h @ RR
    source_norm = float(np.max(np.abs(source))) if source.size else 0.0
    source_ok = source_norm <= abs_tol + relative_tol * max(float(np.max(np.abs(a @ RE))) if source.size else 0., 1.)
    readout_delta = abs(classical_z-pair_z)
    if readout_delta > abs_tol + relative_tol*max(abs(classical_z),abs(pair_z),1.):
        raise ValueError("Algebraic readout paths inconsistent")
    proposed_status = "QUALIFIED" if (classical_legal and source_ok) else ("REJECT_REFERENCE" if not classical_legal else "REJECT_SOURCE")
    # Saved original labels are compared only when the authenticated historical label map is provided.
    recorded = q.get("historical_status")
    if recorded is None:
        raise ValueError("Original historical status is missing; cannot reproduce saved terminals")
    status_mapping = q.get("original_status_to_standard",{})
    if str(recorded) not in status_mapping:
        raise ValueError("No authenticated mapping for original producer status vocabulary")
    normalized_recorded = status_mapping[str(recorded)]
    if normalized_recorded not in ("QUALIFIED","REJECT_REFERENCE","REJECT_SOURCE"):
        raise ValueError("Invalid historical status mapping")
    status_match = normalized_recorded == proposed_status
    if not status_match:
        raise ValueError("Original producer terminal differs from independent classical calculation")
    recorded_val = q.get("historical_value")
    if recorded_val is not None and not np.isfinite(float(recorded_val)):
        raise ValueError("Nonfinite stored original producer value")
    val_delta = "UNASSESSED" if recorded_val is None else abs(float(recorded_val)-classical_z)
    if (classical_legal and source_ok) and recorded_val is None:
        raise ValueError("Accepted query missing saved original producer numerical value")
    if recorded_val is not None and abs(float(recorded_val)-classical_z) > abs_tol+relative_tol*max(abs(classical_z),1.):
        raise ValueError("Original producer stored numerical value disagrees with native algebra")
    if recorded_val is not None and not (classical_legal and source_ok):
        raise ValueError("Historical value attached to unqualified synthetic/processed query")
    return {
        "query_id": q["query_id"], "query_type": q.get("query_type", "UNKNOWN"),
        "n_reference": nr, "n_request": ne, "a_XE_inf": float(np.linalg.norm(w, ord=np.inf)),
        "rank_XR": rank, "rowspace_residual": residual, "nullspace_residual": null_residual,
        "classic_structural_legal": classical_legal, "pair_structural_legal": pair_legal,
        "source_residual_inf": source_norm, "qualified": classical_legal and source_ok,
        "computed_status": proposed_status, "historical_status_match": status_match,
        "value_classical": classical_z, "value_alternative_association": pair_z,
        "pair_classic_delta": readout_delta,
        "historical_value_abs_error": val_delta,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root=args.source_root.resolve(strict=False)
    out=args.out.resolve(strict=False)
    if not root.is_dir():
        print("HOLD: source root missing",file=sys.stderr);sys.exit(2)
    if out.is_relative_to(root):
        print("REFUSE: output may not be nested within source root",file=sys.stderr);sys.exit(2)
    if out.exists():
        print("REFUSE: output must be new and never overwrite previous evidence",file=sys.stderr);sys.exit(2)
    out.mkdir(parents=True,exist_ok=False)
    try:
        man=json.loads(args.manifest.read_text(encoding="utf-8"))
        if man.get("manifest_version") != "PAIR_NATIVE_G0_V1":
            raise ValueError("Manifest version mismatch")
        if man.get("data_class") != "HISTORICAL_NATIVE_ORIGINAL":
            raise ValueError("No historical original producer data attested")
        inventory_sha=man.get("original_query_inventory_sha256", "")
        if not man.get("producer_id") or not (isinstance(inventory_sha,str) and len(inventory_sha)==64 and all(c in "0123456789abcdef" for c in inventory_sha)):
            raise ValueError("Missing immutable producer identity or full query inventory SHA256 fingerprint")
        evid=man.get("original_source_evidence",{})
        for kind in REQUIRED_SOURCE:
            checked_file(root, evid.get(kind), kind)
        tols=man.get("numeric_tolerances",{})
        for name in ("absolute", "relative"):
            if name not in tols or not (0<float(tols[name])<=1e-4):
                raise ValueError("Numeric tolerances missing, nonpositive or implausibly large")
        queries=man.get("queries",[])
        if not isinstance(queries,list) or not queries:
            raise ValueError("No bound original queries supplied")
        count = man.get("historical_query_count_expected")
        if not isinstance(count,int) or count <= 0 or count !=len(queries):
            raise ValueError("Historical query count not complete or not prebound")
        seen=set()
        rows=[]
        for i,q in enumerate(queries):
            qid=q.get("query_id", "")
            if not qid or qid in seen:
                raise ValueError("Missing/duplicate query ID")
            seen.add(qid)
            p=checked_file(root,q.get("bound_arrays"),f"query[{i}] bound arrays")
            rows.append(compute_one(p,q,tols))
        with (out/"G1_G2_per_query.csv").open("w",newline="",encoding="utf-8") as f:
            dw=csv.DictWriter(f,fieldnames=list(rows[0]));dw.writeheader();dw.writerows(rows)
        qualified=sum(int(r["qualified"]) for r in rows)
        # Relying on an author-supplied manifest cannot authenticate its own link to the original producer.
        status="PASS_CHECKED_MANIFEST_BYTES_AND_CLASSICAL_ALGEBRA_ONLY__NATIVE_AUTHORITY_EXTERNAL"
        output={"status":status,"queries":len(rows),"qualified":qualified,
                "method_specific_increment":"NOT_DEMONSTRATED_BY_ALGEBRA",
                "B3_end_to_end_benchmark":"NOT_RUN",
                "native_authority_note":"Manifest and original producer genealogy require independent human/source-system attestation. Script cannot authenticate its own inputs.",
                "input_manifest_sha256":hash_file(args.manifest),"results_sha256":hash_file(out/"G1_G2_per_query.csv")}
        (out/"VERDICT.json").write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding="utf-8")
        print(json.dumps(output,ensure_ascii=False))
    except Exception as e:
        output={"status":"HOLD_NATIVE_INPUTS_OR_NUMERICAL_DISCREPANCY","reason":str(e),
                "B3_end_to_end_benchmark":"NOT_RUN","no_historical_replay_certified":True}
        (out/"VERDICT.json").write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding="utf-8")
        print(json.dumps(output,ensure_ascii=False),file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":main()
