# Paper2 R9: frozen-input checks and reproduction boundaries

This directory provides executable checks for **actual frozen Paper2 files**, not only synthetic algebra tests.

## Validation levels

1. Constructed mathematics: `bash scripts/run_constructed_checks.sh` runs synthetic and exact-algebra tests. It is NOT an original experiment replay.
2. Frozen byte identities: `verify_native_inputs.py` checks the 29 immutable SHA256 pins in `evidence/native_input_pins.json` against real original file locations **supplied privately by the authors**. The output is `PER_ARTIFACT.csv` and `VERDICT.json`.
3. Saved-count diagnostics: `recompute_frozen_counts.py` checks the saved K562 3,125 terminals (349/2,776), ENCODE 56,395 basis rows and 20 mask files, and Replogle 100,000 Q4 designs / 97 guide records. This is not a source-generation or scoring replay.
4. Original producer and model-scoring replay: requires authenticated producer TRAIN/call trace, source ledger, frozen predictions, exact historical scoring invocation and environment. **Still not certified by levels 1–3.**

Run from repository root on the author machine (do not commit the locations file):

```bash
python reproduction/verify_native_inputs.py --pins evidence/native_input_pins.json \
  --locations /private/author_locations.PRIVATE.json --out /scratch/new_sha_audit
python reproduction/recompute_frozen_counts.py --pins evidence/native_input_pins.json \
  --locations /private/author_locations.PRIVATE.json \
  --audit /scratch/new_sha_audit/VERDICT.json --out /scratch/new_counts
```

The byte-identity check uses the Python standard library. For Parquet counts, install `pyarrow` into a separate environment without altering the historic production environment. Missing schemas must remain HOLD, never be guessed or inferred from summary tables.

**No original measurements or private author-server paths are committed.**  A passing SHA check establishes file identity, not scientific reproduction, upstream redistribution rights, or method novelty. See `RELEASE_STATUS.json` for the current public scope.
