#!/usr/bin/env python3
"""Independent GDSC2/GDSC1 primary LDO scorer from frozen fold prediction TSVs."""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr
from sklearn.metrics import r2_score

SCORER_VERSION = "P2_FINAL_CLOSURE_GDSC_INDEPENDENT_SCORER_V1"
PRIMARY = [
    "ElasticNet",
    "GradientBoosting",
    "MultiOmicsNeuralNetwork",
    "MultiOmicsRandomForest",
    "RandomForest",
    "SimpleNeuralNetwork",
]
REPRO_ATOL = 1e-8
REPRO_RTOL = 1e-6


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def close(a, b):
    if np.isnan(a) and np.isnan(b):
        return True
    if not (np.isfinite(a) and np.isfinite(b)):
        return False
    return abs(a - b) <= REPRO_ATOL or abs(a - b) <= REPRO_RTOL * max(1.0, abs(b))


def dreval_r2(y, p):
    m = ~(np.isnan(y) | np.isnan(p))
    if m.sum() < 2:
        return float("nan")
    return float(r2_score(y[m], p[m]))


def dreval_pearson(y, p):
    if len(y) < 2:
        return float("nan")
    if np.all(np.isclose(p, p[0], atol=1e-6)):
        return 0.0
    if np.all(np.isclose(y, y[0], atol=1e-6)):
        return float("nan")
    return float(pearsonr(p, y)[0])


def within_group_center(values, codes):
    out = values.astype(float, copy=True)
    for code in np.unique(codes):
        mask = codes == code
        out[mask] -= np.mean(out[mask])
    return out


def load_fold(pred_root: Path, model: str, fold: int) -> pd.DataFrame:
    path = pred_root / model / f"fold_{fold}.tsv"
    df = pd.read_csv(path, sep="\t", dtype={"cell_line_id": str, "drug_id": str, "row_id": str})
    return df


def common_rows(pred_root: Path, fold: int) -> pd.Index:
    sets = []
    for m in PRIMARY + ["NaiveMeanEffectsPredictor"]:
        df = load_fold(pred_root, m, fold)
        sets.append(set(df["row_id"].astype(str)))
    inter = set.intersection(*sets)
    return pd.Index(sorted(inter))


def score_model_on_support(df: pd.DataFrame, naive: pd.DataFrame, rows: pd.Index):
    sub = df[df.row_id.astype(str).isin(rows)].copy()
    nv = naive[naive.row_id.astype(str).isin(rows)].copy()
    # align by row_id (stable sort)
    sub = sub.sort_values("row_id")
    nv = nv.sort_values("row_id")
    if list(sub.row_id) != list(nv.row_id):
        # left-join multiplicity semantics not expected for GDSC sealed TSVs; require exact row match
        merged = sub.merge(nv[["row_id", "y_pred"]], on="row_id", how="inner", suffixes=("", "_b"))
        if len(merged) != len(rows):
            raise RuntimeError(f"support mismatch {len(merged)} vs {len(rows)}")
        y = merged.y_true.to_numpy(float)
        p = merged.y_pred.to_numpy(float)
        b = merged.y_pred_b.to_numpy(float)
        drug = merged.drug_id.astype(str).to_numpy()
    else:
        y = sub.y_true.to_numpy(float)
        p = sub.y_pred.to_numpy(float)
        b = nv.y_pred.to_numpy(float)
        drug = sub.drug_id.astype(str).to_numpy()
    y_n, p_n = y - b, p - b
    _, inv = np.unique(drug, return_inverse=True)
    y_q, p_q = within_group_center(y_n, inv), within_group_center(p_n, inv)
    return {
        "n_eval": int(len(y)),
        "normalized_R2_FULL": dreval_r2(y_n, p_n),
        "normalized_R2_PAIR_Q": dreval_r2(y_q, p_q),
        "normalized_Pearson_FULL": dreval_pearson(y_n, p_n),
        "normalized_Pearson_PAIR_Q": dreval_pearson(y_q, p_q),
    }


def rank_order(scores):
    items = [(m, s) for m, s in scores.items() if np.isfinite(s)]
    return [m for m, _ in sorted(items, key=lambda t: (-t[1], t[0]))]


def pairwise_reversal(order_a, order_b):
    pos_a = {m: i for i, m in enumerate(order_a)}
    pos_b = {m: i for i, m in enumerate(order_b)}
    models = [m for m in order_a if m in pos_b]
    pairs = list(combinations(models, 2))
    if not pairs:
        return float("nan")
    rev = 0
    for i, j in pairs:
        da, db = pos_a[i] - pos_a[j], pos_b[i] - pos_b[j]
        if da == 0 or db == 0:
            continue
        if (da > 0) != (db > 0):
            rev += 1
    return rev / len(pairs)


def run_resource(resource: str, pred_root: Path, published_path: Path, out_dir: Path):
    pub = pd.read_csv(published_path, sep="\t")
    rows = []
    bindings = []
    for fold in range(10):
        rows_idx = common_rows(pred_root, fold)
        naive = load_fold(pred_root, "NaiveMeanEffectsPredictor", fold)
        bindings.append({"fold": fold, "n_common": int(len(rows_idx))})
        for model in PRIMARY:
            path = pred_root / model / f"fold_{fold}.tsv"
            df = load_fold(pred_root, model, fold)
            sc = score_model_on_support(df, naive, rows_idx)
            exp = pub[(pub.fold == fold) & (pub.model == model)]
            pub_nr2 = float(exp.normalized_R2.iloc[0]) if len(exp) else float("nan")
            pub_npe = float(exp.normalized_Pearson.iloc[0]) if len(exp) else float("nan")
            # published n_eval
            pub_n = int(exp.n_eval.iloc[0]) if len(exp) and "n_eval" in exp.columns else None
            rows.append(
                {
                    "resource": resource,
                    "fold": fold,
                    "model": model,
                    "n_eval": sc["n_eval"],
                    "published_n_eval": pub_n,
                    "independent_nR2_FULL": sc["normalized_R2_FULL"],
                    "published_nR2": pub_nr2,
                    "nR2_match": close(sc["normalized_R2_FULL"], pub_nr2),
                    "independent_nPearson_FULL": sc["normalized_Pearson_FULL"],
                    "published_nPearson": pub_npe,
                    "nPearson_match": close(sc["normalized_Pearson_FULL"], pub_npe),
                    "independent_nR2_PAIR_Q": sc["normalized_R2_PAIR_Q"],
                    "independent_nPearson_PAIR_Q": sc["normalized_Pearson_PAIR_Q"],
                    "pred_sha256": sha256_file(path),
                }
            )
        print(f"[{resource}] fold {fold} n_common={len(rows_idx)}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / f"G2_{resource}_FOLD_METRICS.tsv", sep="\t", index=False)

    # medians of FULL vs Q reversal / tau; persistent pairs
    taus_r2, revs_r2, taus_pe, revs_pe = [], [], [], []
    # all model pairs persistence for nR2
    pair_persist = []
    for mi, mj in combinations(PRIMARY, 2):
        same_r2 = 0
        orients = []
        for fold in range(10):
            a = df[(df.fold == fold) & (df.model == mi)].iloc[0]
            b = df[(df.fold == fold) & (df.model == mj)].iloc[0]
            full_dir = np.sign(a.independent_nR2_FULL - b.independent_nR2_FULL)
            q_dir = np.sign(a.independent_nR2_PAIR_Q - b.independent_nR2_PAIR_Q)
            rev = full_dir != 0 and q_dir != 0 and full_dir != q_dir
            orients.append(int(rev) * int(np.sign(q_dir - full_dir) or 1))
            # count same-orientation reversals: FULL A>B and Q A<B (or opposite), same across folds
            if rev:
                # orientation code
                code = "FULL_A_gt_Q_A_lt" if (a.independent_nR2_FULL > b.independent_nR2_FULL and a.independent_nR2_PAIR_Q < b.independent_nR2_PAIR_Q) else (
                    "FULL_A_lt_Q_A_gt" if (a.independent_nR2_FULL < b.independent_nR2_FULL and a.independent_nR2_PAIR_Q > b.independent_nR2_PAIR_Q) else "OTHER"
                )
                orients[-1] = code
        # persistence: same reversal orientation >=7
        from collections import Counter
        c = Counter([o for o in orients if isinstance(o, str) and o in ("FULL_A_gt_Q_A_lt", "FULL_A_lt_Q_A_gt")])
        best = c.most_common(1)[0] if c else (None, 0)
        pair_persist.append({"model_i": mi, "model_j": mj, "best_orient": best[0], "n": best[1], "persistent": best[1] >= 7})

    for fold in range(10):
        sub = df[df.fold == fold]
        for metric, full_col, q_col, taus, revs in [
            ("nR2", "independent_nR2_FULL", "independent_nR2_PAIR_Q", taus_r2, revs_r2),
            ("nPearson", "independent_nPearson_FULL", "independent_nPearson_PAIR_Q", taus_pe, revs_pe),
        ]:
            full_scores = {r.model: getattr(r, full_col) for _, r in sub.iterrows()}
            q_scores = {r.model: getattr(r, q_col) for _, r in sub.iterrows()}
            of, oq = rank_order(full_scores), rank_order(q_scores)
            rf = [of.index(m) for m in PRIMARY]
            rq = [oq.index(m) for m in PRIMARY]
            taus.append(float(kendalltau(rf, rq).correlation))
            revs.append(pairwise_reversal(of, oq))

    n_match = int(df.nR2_match.sum() + df.nPearson_match.sum())
    n_tot = int(2 * len(df))
    n_persist = int(sum(1 for p in pair_persist if p["persistent"]))
    summary = {
        "resource": resource,
        "scorer_version": SCORER_VERSION,
        "FULL_vs_published_matches": f"{int(df.nR2_match.sum())}/{len(df)} nR2; {int(df.nPearson_match.sum())}/{len(df)} nPearson",
        "all_match": bool(df.nR2_match.all() and df.nPearson_match.all()),
        "median_tau_nR2": float(np.nanmedian(taus_r2)),
        "median_reversal_nR2": float(np.nanmedian(revs_r2)),
        "median_tau_nPearson": float(np.nanmedian(taus_pe)),
        "median_reversal_nPearson": float(np.nanmedian(revs_pe)),
        "persistent_pairs_nR2": n_persist,
        "pair_persist_detail": pair_persist,
        "bindings": bindings,
        "pred_root": str(pred_root),
    }
    expected = {
        "GDSC2": {"rev_r2": 0.30, "rev_pe": 0.30, "persist": 0},
        "GDSC1": {"rev_r2": 0.37, "rev_pe": 0.33, "persist": 0},
    }[resource]
    ok_persist = n_persist == 0
    ok_rev = abs(summary["median_reversal_nR2"] - expected["rev_r2"]) < 0.05
    summary["expected"] = expected
    summary["ok_persist_zero"] = ok_persist
    summary["ok_rev_near_expected"] = ok_rev
    if not summary["all_match"]:
        terminal = "FAIL__INDEPENDENT_SCORE_MISMATCH"
    elif ok_persist:
        terminal = "PASS__GDSC_PRIMARY_INDEPENDENT_REPLAY"
    else:
        terminal = "FAIL__INDEPENDENT_SCORE_MISMATCH"
    summary["terminal"] = terminal
    (out_dir / f"G2_{resource}_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage2-root", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    root = Path(args.stage2_root)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for res in ("GDSC2", "GDSC1"):
        results[res] = run_resource(
            res,
            root / f"results/{res}/predictions",
            root / f"results/{res}/published_scores.tsv",
            out,
        )
    both_pass = all(r["terminal"].startswith("PASS") for r in results.values())
    final = {
        "terminal": "PASS__PREDICTION_BYTES_INDEPENDENTLY_REPRODUCE_FROZEN_RESULTS" if both_pass else "FAIL__INDEPENDENT_SCORE_MISMATCH",
        "GDSC2": results["GDSC2"],
        "GDSC1": results["GDSC1"],
        "note": "Negatives (0 persistent) preserved; not rescued.",
    }
    # merge with CTRPv2 if present
    ctrp = out / "G2_FINAL.json"
    if ctrp.exists():
        prev = json.loads(ctrp.read_text())
        if prev.get("terminal", "").startswith("PASS") and both_pass:
            final["terminal"] = "PASS__PREDICTION_BYTES_INDEPENDENTLY_REPRODUCE_FROZEN_RESULTS"
            final["CTRPv2_terminal"] = prev["terminal"]
        elif prev.get("terminal", "").startswith("PASS") and not both_pass:
            final["terminal"] = "FAIL__INDEPENDENT_SCORE_MISMATCH"
            final["CTRPv2_terminal"] = prev["terminal"]
    (out / "G2_GDSC_FINAL.json").write_text(json.dumps(final, indent=2) + "\n")
    print(json.dumps({"terminal": final["terminal"], "GDSC2_persist": results["GDSC2"]["persistent_pairs_nR2"], "GDSC1_persist": results["GDSC1"]["persistent_pairs_nR2"], "GDSC2_match": results["GDSC2"]["all_match"], "GDSC1_match": results["GDSC1"]["all_match"]}, indent=2))


if __name__ == "__main__":
    main()
