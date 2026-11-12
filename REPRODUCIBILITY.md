# Reproducing the KBS companion materials

## Public software checks

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

These commands run the existing exact-algebra and synthetic checks, native-input
verifier tests, scorer-source checksums and current KBS file correspondence.
The original verification and scoring implementations are unchanged.

## Manuscript build

```bash
bash manuscript/build.sh
```

The main document and supplement build in `output/manuscript-build/` using the
included BBL files. Install a complete TeX Live distribution with
`texlive-latex-extra`, `texlive-fonts-recommended` and `texlive-science`.
The archived PDFs are the original Gemini KBS files; rebuilding in another TeX
environment can change font rendering, line breaks and PDF metadata.

## Original data replay

The 29 frozen SHA256/size identities remain in `evidence/native_input_pins.json`;
their historical claim mapping remains in `evidence/CLAIM_TO_ARTIFACT_MAP.tsv`.
Follow [reproduction/README.md](reproduction/README.md) for original-byte checks
and saved-count diagnostics, and the
[original scorer guide](reproduction/original_scorers/README.md) for CTRPv2/GDSC
commands on a host with the corresponding original input matrices.

The recorded author-server replay and its resource-specific availability scope
are preserved in `evidence/P2_R9_PUBLIC_RESCORE_RECEIPT.json`. Historical version
names in receipts and source pins identify those original artifacts.
The KBS alignment does not change their scientific interpretation.
