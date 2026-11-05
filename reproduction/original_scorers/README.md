# Original independent scorers (2026-11-05 evidence replay)

These are the **exact byte-identical source files** returned by the Paper2 author-server reproduction audit. Their local Git blob SHA and SHA256 match the author-server originals. Neither scorer imports the historical Stage1 scoring package.

| Source | SHA256 | Native author-server replay |
|---|---|---|
| `independent_scorer.py` | `c42ff2c49a1d74952d28a42a031410bfcac587d46ddf3f01db2a58e1934aa83a` | CTRPv2 700/700 metric fields; historical fold TSV byte-identical |
| `gdsc_independent_scorer.py` | `fd218e164737f4f06d2c6e2f30412e749e4a8cc07b85a8bf39d40bcd1c8d3133` | GDSC2 420/420 metric fields; historical fold TSV byte-identical; 0 persistent pairs |

Run `python verify_scorer_source.py` to check source SHA256 without needing model data.

## Environment used for 2026-11-05 historical scoring replay

Python 3.13.5 (Anaconda); NumPy 2.1.3, pandas 2.2.3, PyArrow 23.0.1, SciPy 1.15.3, scikit-learn 1.8.0. See `requirements-author-replay.txt`. This is distinct from the exact-algebra public CI environment.

## CTRPv2: command on an authorized original-data host

```bash
python independent_scorer.py \
  --parquet /secure/data/true_vs_pred_predictions_LPO_LCO_LDO.parquet \
  --published-scores /secure/data/fold_scores_published.tsv \
  --out-dir /scratch/ctrp_replay
```

Requires the exact frozen Parquet (SHA256 `db0c046e0b1c2a4f96e363640935deb8ce4e9146fb0a5281da26fe5b24ae7f73`) and its historical published-score TSV. Output `G2_FOLD_METRICS.tsv` must have SHA256 `f0b7dd1dd2a17cb0a6910329e395a43f48bb8263e3bde154cd530be693125a17`. The model-pair reversal table `G2_STRICT_PAIRS.tsv` must have SHA256 `c8578922f08201fb9e676d8c7fe565c09aeca0cec22c45766796f2a5170adc34`. The summary JSON contains additional derived fields relative to the historical summary; do not demand byte-identity for all JSON files.

## GDSC2: command on an authorized original-data host

The original GDSC scorer CLI runs both GDSC2 and GDSC1. GDSC1 input is currently not mounted. To reproduce **only GDSC2** using the unchanged original scorer functions:

```bash
python run_gdsc2_only.py \
  --pred-root /secure/data/GDSC2/predictions \
  --published-scores /secure/data/GDSC2/published_scores.tsv \
  --out-dir /scratch/gdsc2_replay
```

The 2026-11-05 author-server run found 140 source prediction files and regenerated `G2_GDSC2_FOLD_METRICS.tsv` (SHA256 `f77fcb24a43a4864a3554148485921a0b676848e0e29e9c04a3733f2820ab292`). Prespecified persistent pairs remained **zero**. This is a confirmed negative result, not a PAIR-specific predictive improvement.

## Availability and scientific scope

Original prediction matrices, historical source row ledgers and sensitive author-server logs are **not** in the public repository. This source code and its checksum receipt therefore do not by themselves make K562 or GDSC1 reproducible. Third-party data rights must be cleared before distributing frozen inputs; no software redistribution license has been granted. Details: [public rescore receipt](../../evidence/P2_R9_PUBLIC_RESCORE_RECEIPT.json).

The full original K562 fold-0 historical producer TRAIN/call-trace remains unauthenticated. Source identity, valid observation contracts and algorithmic gains must be evaluated separately from scorer TSV agreement.
