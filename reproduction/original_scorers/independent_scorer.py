#!/usr/bin/env python3
"""Independent DrEval-style scorer for frozen predictions.

Does NOT import historical Stage1 modules. Contract reconstructed from
read-only inspection of frozen semantics (v1.4.1 cartesian NME merge,
LDO within-drug centering for PAIR_Q). Fail-closed on naive miss.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq
from scipy.stats import pearsonr, kendalltau
from sklearn.metrics import r2_score

SCORER_VERSION = "P2_FINAL_CLOSURE_INDEPENDENT_SCORER_V1_20261013"
REPRO_ATOL = 1e-8
REPRO_RTOL = 1e-6
LDO_PRIMARY = [
    "DIPK",
    "ElasticNet",
    "GradientBoosting",
    "MultiOmicsNeuralNetwork",
    "MultiOmicsRandomForest",
    "RandomForest",
    "SimpleNeuralNetwork",
]
HIST_PERSISTENT = [
    ("normalized_R2", "ElasticNet", "RandomForest", "published_A_gt_B__pair_A_lt_B"),
    ("normalized_R2", "MultiOmicsNeuralNetwork", "MultiOmicsRandomForest", "published_A_gt_B__pair_A_lt_B"),
    ("normalized_R2", "MultiOmicsNeuralNetwork", "RandomForest", "published_A_gt_B__pair_A_lt_B"),
    ("normalized_Pearson", "MultiOmicsNeuralNetwork", "RandomForest", "published_A_gt_B__pair_A_lt_B"),
    ("normalized_Pearson", "RandomForest", "SimpleNeuralNetwork", "published_A_lt_B__pair_A_gt_B"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def close(a: float, b: float) -> bool:
    if np.isnan(a) and np.isnan(b):
        return True
    if not (np.isfinite(a) and np.isfinite(b)):
        return False
    return abs(a - b) <= REPRO_ATOL or abs(a - b) <= REPRO_RTOL * max(1.0, abs(b))


def dreval_pearson(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 2:
        return float("nan")
    if np.all(np.isclose(y_pred, y_pred[0], atol=1e-6)):
        return 0.0
    if np.all(np.isclose(y_true, y_true[0], atol=1e-6)):
        return float("nan")
    return float(pearsonr(y_pred, y_true)[0])


def dreval_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    if mask.sum() < 2:
        return float("nan")
    return float(r2_score(y_true[mask], y_pred[mask]))


def within_group_center(values: np.ndarray, codes: np.ndarray) -> np.ndarray:
    out = values.astype(float, copy=True)
    for code in np.unique(codes):
        mask = codes == code
        out[mask] = out[mask] - np.mean(out[mask])
    return out


def v14_normalize_merge(sub: pd.DataFrame, naive_fold: pd.DataFrame) -> pd.DataFrame:
    left = sub[["drug_name", "cell_line_name", "y_true", "y_pred", "pubchem_id"]].copy()
    right = naive_fold[["drug_name", "cell_line_name", "y_pred"]].rename(columns={"y_pred": "b"})
    return left.merge(right, on=["drug_name", "cell_line_name"], how="left")


def load_ldo_panel(parquet_path: Path, models: list[str]) -> pd.DataFrame:
    """Stream row-groups; keep LDO rows for NME + primary models only."""
    want = set(models) | {"NaiveMeanEffectsPredictor"}
    pf = pq.ParquetFile(parquet_path)
    chunks = []
    for i in range(pf.num_row_groups):
        t = pf.read_row_group(i)
        # filter LDO
        mask = pc.equal(t.column("test_mode"), "LDO")
        t = t.filter(mask)
        if t.num_rows == 0:
            continue
        alg = t.column("algorithm")
        keep = None
        for m in want:
            msk = pc.equal(alg, m)
            keep = msk if keep is None else pc.or_(keep, msk)
        t = t.filter(keep)
        if t.num_rows:
            chunks.append(t.to_pandas())
    if not chunks:
        raise RuntimeError("no LDO panel rows loaded")
    df = pd.concat(chunks, ignore_index=True)
    for c in ("pubchem_id", "cell_line_name", "drug_name", "algorithm"):
        df[c] = df[c].astype(str)
    return df


def score_fold(sub: pd.DataFrame, naive_fold: pd.DataFrame, mode: str = "LDO"):
    merged = v14_normalize_merge(sub, naive_fold)
    if merged["b"].isna().any():
        raise RuntimeError("naive miss after cartesian merge — fail closed")
    y = merged.y_true.to_numpy(float)
    p = merged.y_pred.to_numpy(float)
    b = merged.b.to_numpy(float)
    y_n, p_n = y - b, p - b
    _, inv_m = np.unique(merged.pubchem_id.astype(str), return_inverse=True)
    y_qn, p_qn = within_group_center(y_n, inv_m), within_group_center(p_n, inv_m)
    return {
        "normalized_R2_FULL": dreval_r2(y_n, p_n),
        "normalized_R2_PAIR_Q": dreval_r2(y_qn, p_qn),
        "normalized_Pearson_FULL": dreval_pearson(y_n, p_n),
        "normalized_Pearson_PAIR_Q": dreval_pearson(y_qn, p_qn),
        "n_rows_model": int(len(sub)),
        "n_rows_after_cartesian": int(len(merged)),
        "n_dup_expand": int(len(merged) - len(sub)),
    }


def rank_order(scores: dict[str, float]) -> list[str]:
    items = [(m, s) for m, s in scores.items() if np.isfinite(s)]
    return [m for m, _ in sorted(items, key=lambda t: (-t[1], t[0]))]


def pairwise_reversal(order_a: list[str], order_b: list[str]) -> float:
    pos_a = {m: i for i, m in enumerate(order_a)}
    pos_b = {m: i for i, m in enumerate(order_b)}
    models = [m for m in order_a if m in pos_b]
    pairs = list(combinations(models, 2))
    if not pairs:
        return float("nan")
    rev = 0
    for i, j in pairs:
        da = pos_a[i] - pos_a[j]
        db = pos_b[i] - pos_b[j]
        if da == 0 or db == 0:
            continue
        if (da > 0) != (db > 0):
            rev += 1
    return rev / len(pairs)


def orientation_full_vs_q(full_a: float, full_b: float, q_a: float, q_b: float) -> str:
    # higher score better
    if not all(map(np.isfinite, [full_a, full_b, q_a, q_b])):
        return "NONFINITE"
    pub = "A_gt_B" if full_a > full_b else ("A_lt_B" if full_a < full_b else "TIE")
    pr = "A_gt_B" if q_a > q_b else ("A_lt_B" if q_a < q_b else "TIE")
    return f"published_{pub}__pair_{pr}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--published-scores", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--preflight-only", action="store_true")
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    parquet = Path(args.parquet)
    bind = {
        "scorer_version": SCORER_VERSION,
        "parquet": str(parquet),
        "parquet_sha256": sha256_file(parquet),
        "parquet_bytes": parquet.stat().st_size,
        "models": LDO_PRIMARY,
    }
    (out / "G2_FROZEN_INPUT_BINDINGS.json").write_text(json.dumps(bind, indent=2) + "\n")

    print("[load] LDO panel…", flush=True)
    tvp = load_ldo_panel(parquet, LDO_PRIMARY)
    print(f"[load] rows={len(tvp)} algs={sorted(tvp.algorithm.unique())}", flush=True)

    pub = pd.read_csv(args.published_scores, sep="\t")
    pub_ldo = pub[(pub["mode"] == "LDO") & (pub["metric"].isin(["normalized_R2", "normalized_Pearson"]))]

    # Preflight fold0 ElasticNet nR2 FULL
    fold0 = 0
    naive0 = tvp[(tvp.algorithm == "NaiveMeanEffectsPredictor") & (tvp.CV_split == fold0)]
    en0 = tvp[(tvp.algorithm == "ElasticNet") & (tvp.CV_split == fold0)]
    sc0 = score_fold(en0, naive0)
    exp = pub_ldo[(pub_ldo.fold == fold0) & (pub_ldo.model == "ElasticNet") & (pub_ldo.metric == "normalized_R2")]
    if exp.empty:
        raise RuntimeError("missing published ElasticNet fold0 nR2")
    exp_v = float(exp.published_score.iloc[0])
    pre = {
        "fold": fold0,
        "model": "ElasticNet",
        "independent_nR2_FULL": sc0["normalized_R2_FULL"],
        "published_nR2": exp_v,
        "match": close(sc0["normalized_R2_FULL"], exp_v),
        "n_rows_model": sc0["n_rows_model"],
        "n_rows_after_cartesian": sc0["n_rows_after_cartesian"],
    }
    (out / "G2_PREFLIGHT_FOLD0.json").write_text(json.dumps(pre, indent=2) + "\n")
    print("[preflight]", pre, flush=True)
    if not pre["match"]:
        (out / "G2_FINAL.json").write_text(
            json.dumps({"terminal": "FAIL__INDEPENDENT_SCORE_MISMATCH", "preflight": pre}, indent=2) + "\n"
        )
        raise SystemExit(2)
    if args.preflight_only:
        return

    rows = []
    for fold in range(10):
        naive = tvp[(tvp.algorithm == "NaiveMeanEffectsPredictor") & (tvp.CV_split == fold)]
        if naive.empty:
            raise RuntimeError(f"missing NME fold{fold}")
        for model in LDO_PRIMARY:
            sub = tvp[(tvp.algorithm == model) & (tvp.CV_split == fold)]
            if sub.empty:
                raise RuntimeError(f"missing {model} fold{fold}")
            sc = score_fold(sub, naive)
            for metric_base, full_key, q_key in [
                ("normalized_R2", "normalized_R2_FULL", "normalized_R2_PAIR_Q"),
                ("normalized_Pearson", "normalized_Pearson_FULL", "normalized_Pearson_PAIR_Q"),
            ]:
                exp_rows = pub_ldo[(pub_ldo.fold == fold) & (pub_ldo.model == model) & (pub_ldo.metric == metric_base)]
                pub_v = float(exp_rows.published_score.iloc[0]) if len(exp_rows) else float("nan")
                rows.append(
                    {
                        "fold": fold,
                        "model": model,
                        "metric": metric_base,
                        "independent_FULL": sc[full_key],
                        "independent_PAIR_Q": sc[q_key],
                        "published_FULL": pub_v,
                        "FULL_match_published": close(sc[full_key], pub_v) if np.isfinite(pub_v) else False,
                        "n_rows_model": sc["n_rows_model"],
                        "n_rows_after_cartesian": sc["n_rows_after_cartesian"],
                    }
                )
        print(f"[fold] {fold} done", flush=True)

    fold_df = pd.DataFrame(rows)
    fold_df.to_csv(out / "G2_FOLD_METRICS.tsv", sep="\t", index=False)
    n_match = int(fold_df["FULL_match_published"].sum())
    n_tot = int(len(fold_df))
    print(f"[match] FULL vs published {n_match}/{n_tot}", flush=True)

    # persistent pairs FULL vs PAIR_Q
    pair_rows = []
    for metric, mi, mj, expected_orient in HIST_PERSISTENT:
        dirs = []
        for fold in range(10):
            fa = fold_df[(fold_df.fold == fold) & (fold_df.model == mi) & (fold_df.metric == metric)].iloc[0]
            fb = fold_df[(fold_df.fold == fold) & (fold_df.model == mj) & (fold_df.metric == metric)].iloc[0]
            orient = orientation_full_vs_q(
                fa.independent_FULL, fb.independent_FULL, fa.independent_PAIR_Q, fb.independent_PAIR_Q
            )
            dirs.append(orient)
        # persistence: same direction as expected, and is a true reversal (FULL vs Q disagree)
        same = sum(1 for o in dirs if o == expected_orient)
        pair_rows.append(
            {
                "metric": metric,
                "model_i": mi,
                "model_j": mj,
                "expected_orientation": expected_orient,
                "n_folds_same_as_expected": same,
                "persistent_ge_7": same >= 7,
                "fold_orientations": "|".join(dirs),
            }
        )
    pairs_df = pd.DataFrame(pair_rows)
    pairs_df.to_csv(out / "G2_STRICT_PAIRS.tsv", sep="\t", index=False)

    # median tau / reversal FULL vs Q ranks
    taus_r2, revs_r2, taus_pe, revs_pe = [], [], [], []
    top_full_r2, top_q_r2 = [], []
    for fold in range(10):
        for metric, taus, revs, tops in [
            ("normalized_R2", taus_r2, revs_r2, top_full_r2),
            ("normalized_Pearson", taus_pe, revs_pe, None),
        ]:
            sub = fold_df[(fold_df.fold == fold) & (fold_df.metric == metric)]
            full_scores = {r.model: r.independent_FULL for _, r in sub.iterrows()}
            q_scores = {r.model: r.independent_PAIR_Q for _, r in sub.iterrows()}
            of, oq = rank_order(full_scores), rank_order(q_scores)
            # kendall on rank vectors aligned by model list
            models = LDO_PRIMARY
            rf = [of.index(m) for m in models]
            rq = [oq.index(m) for m in models]
            tau = float(kendalltau(rf, rq).correlation)
            rev = pairwise_reversal(of, oq)
            taus.append(tau)
            revs.append(rev)
            if metric == "normalized_R2":
                top_full_r2.append(of[0])
                top_q_r2.append(oq[0])

    summary = {
        "scorer_version": SCORER_VERSION,
        "FULL_vs_published_matches": f"{n_match}/{n_tot}",
        "all_FULL_match_published": n_match == n_tot,
        "median_kendall_tau_nR2_FULL_vs_Q": float(np.nanmedian(taus_r2)),
        "median_reversal_nR2_FULL_vs_Q": float(np.nanmedian(revs_r2)),
        "median_kendall_tau_nPearson_FULL_vs_Q": float(np.nanmedian(taus_pe)),
        "median_reversal_nPearson_FULL_vs_Q": float(np.nanmedian(revs_pe)),
        "expected_median_tau": [0.0, 0.285714],
        "expected_median_reversal": [0.50, 0.357143],
        "persistent_pairs_ge7": int(pairs_df.persistent_ge_7.sum()),
        "persistent_pair_detail": pairs_df.to_dict(orient="records"),
        "top_model_FULL_nR2_by_fold": top_full_r2,
        "top_model_PAIR_Q_nR2_by_fold": top_q_r2,
        "top_model_by_fold_mode_FULL_nR2": (
            pd.Series(top_full_r2).mode().iloc[0] if top_full_r2 else None
        ),
        "top_model_by_fold_mode_PAIR_Q_nR2": (
            pd.Series(top_q_r2).mode().iloc[0] if top_q_r2 else None
        ),
    }
    # True mean-score tops (across folds) — not mode of per-fold tops
    sub_r2 = fold_df[fold_df.metric == "normalized_R2"]
    mean_full_nR2 = sub_r2.groupby("model")["independent_FULL"].mean()
    mean_pair_nR2 = sub_r2.groupby("model")["independent_PAIR_Q"].mean()
    top_by_mean_full = str(mean_full_nR2.idxmax()) if len(mean_full_nR2) else None
    top_by_mean_pair = str(mean_pair_nR2.idxmax()) if len(mean_pair_nR2) else None
    top_changed_mean = [top_by_mean_full, top_by_mean_pair]
    summary["top_model_by_mean_score_FULL_nR2"] = top_by_mean_full
    summary["top_model_by_mean_score_PAIR_Q_nR2"] = top_by_mean_pair
    summary["mean_nR2_FULL_by_model"] = {k: float(v) for k, v in mean_full_nR2.items()}
    summary["mean_nR2_PAIR_Q_by_model"] = {k: float(v) for k, v in mean_pair_nR2.items()}
    summary["top_model_changed_mean_score"] = top_changed_mean
    summary["top_model_changed_mean_score_proxy"] = top_changed_mean  # alias to true mean-score list
    # Decision
    five_ok = int(pairs_df.persistent_ge_7.sum()) == 5 and all(pairs_df.persistent_ge_7)
    med_ok = (
        abs(summary["median_kendall_tau_nR2_FULL_vs_Q"] - 0.0) < 0.05
        and abs(summary["median_reversal_nR2_FULL_vs_Q"] - 0.50) < 0.05
    )
    if n_match != n_tot:
        terminal = "FAIL__INDEPENDENT_SCORE_MISMATCH"
    elif five_ok:
        terminal = "PASS__PREDICTION_BYTES_INDEPENDENTLY_REPRODUCE_FROZEN_RESULTS"
    else:
        terminal = "FAIL__INDEPENDENT_SCORE_MISMATCH"
    summary["terminal"] = terminal
    summary["median_ok_loose"] = med_ok
    (out / "G2_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "G2_FINAL.json").write_text(json.dumps({"terminal": terminal, "summary": summary}, indent=2) + "\n")
    print(json.dumps({"terminal": terminal, "matches": f"{n_match}/{n_tot}", "persistent": int(pairs_df.persistent_ge_7.sum())}, indent=2))


if __name__ == "__main__":
    main()
