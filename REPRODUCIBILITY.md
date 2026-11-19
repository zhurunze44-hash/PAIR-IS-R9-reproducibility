# Reproducing the KBS companion materials

## Public verification

```bash
git clone https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility.git
cd PAIR-IS-R9-reproducibility
python3 -m pip install -r requirements-verified.txt
python3 scripts/publication_sanity.py
bash scripts/run_constructed_checks.sh
PYTHONPATH=reproduction python3 -m unittest discover -s reproduction -p 'test_*.py' -v
python3 reproduction/original_scorers/verify_scorer_source.py
python3 scripts/verify_kbs_alignment.py
```

The commands check the exact-algebra and synthetic fixtures, native-input
verifier, scorer-source checksums and the current manuscript package. The
[environment note](ENVIRONMENT.md) describes the public test environment.

## Manuscript and figures

With TeX Live, `latexmk` and Python 3 with `pypdf` installed, run:

```bash
bash manuscript/build.sh
```

The build extracts the [source bundle](manuscript/kbs-source.zip) and writes
`kbs.pdf`, `kbs-supplement.pdf` and `kbs-full.pdf` to
`output/manuscript-build/`. The checked-in PDFs are the reference copies.

Run `python3 manuscript/figure_sources/draw_figures.py` to render the vector
figures from the supplied plotting data. The script uses Matplotlib, NumPy and
Liberation Serif. The papers build directly with the supplied vector PDFs.

## Empirical replay

The [data and code availability statement](DATA_AND_CODE_AVAILABILITY.md)
identifies the available inputs. The [source README](manuscript/README_SOURCE.txt)
identifies the separately distributed evidence archive. Run its offline replay
from an extracted copy after installing its stated Python dependencies.

For original CTRPv2 and GDSC replay, consult the
[scorer guide](reproduction/original_scorers/README.md) and
[original input identities](evidence/native_input_pins.json). The historical
[replay receipt](evidence/P2_R9_PUBLIC_RESCORE_RECEIPT.json) records the
author-server results.
