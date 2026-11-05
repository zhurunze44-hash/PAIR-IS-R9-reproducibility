# PAIR: reference- and source-qualified molecular comparisons

This repository is the software and manuscript-source companion to
*PAIR: Compiling reference- and source-qualified comparisons from incomplete
molecular screens* (Information Sciences submission candidate, R9).

## Contents

- `manuscript/`: complete editable English article, supplement (S1-S16), bibliography and vector figures.
- `verification/`: exact algebraic checks, native-input-bound comparator and synthetic tests.
- `scripts/`: executed-test runner, release gate and private-repository publication helper.
- `schemas/`: schema for authenticated original historical producer/query arrays.
- `evidence/`: structured paper-to-evidence index, source citation table and constructed test receipt.
- `NATIVE_DATA_REQUIREMENTS.md`: artifact-level description of original experiment inputs required for full reproduction.
- `SUBMISSION_SOFTWARE_COVERAGE.md`: exact release contents, without overstated reproducibility.

## Quick local verification

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-verified.txt
bash scripts/run_constructed_checks.sh
```

The expected result is `PASS_CONSTRUCTED_ONLY`, not a real-data or model-training replay.

## Rebuild manuscript

```bash
cd manuscript
bash build.sh
```

The original figure-generation scripts and all frozen plot inputs are not contained
in the R9 manuscript archive; the submitted figure PDFs are supplied unchanged.

## Original data and experiments

See `evidence/upstream_data_sources.csv` for citations to source publications, and
`NATIVE_DATA_REQUIREMENTS.md` for required frozen inputs. The author-server
export tool is distributed separately with the editor package and never
alters research source data. Third-party raw observations cannot be assumed
redistributable. This software snapshot does not independently rerun all
K562, ENCODE, Replogle, CTRPv2 or GDSC findings.

## Versioning and distribution

The archive is suitable for creation of a private GitHub repository. A public
release must use an actual URL and immutable tag, a rights-reviewed license
and an audited native-asset manifest. No DOI is assigned by this local package.
