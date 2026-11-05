# Reproducing Paper2 IS R9

A fresh clone can compile the manuscript (with TeX dependencies), run exact-algebra and synthetic checks, and audit real frozen asset bytes when those assets are available under the author's authorized access. The available source snapshot currently does not constitute an independent re-execution of every original experiment.

## Public test (available without research data)

```bash
git clone https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility.git
cd PAIR-IS-R9-reproducibility
python -m pip install -r requirements-verified.txt
bash scripts/run_constructed_checks.sh
PYTHONPATH=reproduction python -m unittest discover -s reproduction -p 'test_*.py' -v
```

The results correspond to `PASS_CONSTRUCTED_ONLY`. GitHub Actions repeats the public tests on each push.

## Original frozen-input verification

The public manifest `evidence/native_input_pins.json` fixes 29 SHA256 / byte-size identities from the 2026-11-05 author-server evidence ledger. `evidence/CLAIM_TO_ARTIFACT_MAP.tsv` maps K1-K7 to these pins. The private locations manifest is intentionally absent from GitHub.

Run `python reproduction/verify_native_inputs.py --help`. The author-server execution package supplies private paths and an orchestrator. Passing this check establishes original file **byte identity**, not producer identity or numerical re-execution.

After a passing byte check, `python reproduction/recompute_frozen_counts.py --help` can perform saved-result count diagnostics. It requires `pyarrow` for Parquet. Do not equate 100,000 Replogle query designs with 100,000 measured biological effects.

## Full original-data reproduction gate

For source-certified original producer claims, a third party needs the actual original TRAIN membership, original producer call trace and aligned RR/RE source ledger, and an unmodified producer executable. The current evidence lacks independent certification of that producer lineage. For CTRPv2/GDSC scorer replay, byte-pinned frozen predictions, target/split bindings, original scoring code and its exact invocation are required. The author-server package stages these assets for bounded review.

No original observations or unapproved redistribution-sensitive files are committed here. See `NATIVE_DATA_REQUIREMENTS.md`, `RIGHTS_NOTICE.md` and `RELEASE_STATUS.json`.

## Repo roles

- `manuscript/`: R9 paper and figures
- `verification/`: checked theoretical and synthetic methods
- `reproduction/`: original file identity verifier and saved-count diagnostics
- `evidence/`: claim-to-asset map and immutable SHA256 pins
- `.github/workflows/checks.yml`: public automated tests

This repository is not a substitute for original published datasets or their access requirements.
