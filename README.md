# PAIR: Verifiable quantitative knowledge and model comparison

Companion repository for **PAIR: Verifiable quantitative knowledge and model
comparison from incomplete experimental references**, prepared for
**Knowledge-Based Systems (KBS)**.

The current paper is the Gemini KBS manuscript: **26-page main article and
46-page supplementary information**. The PDFs, matching compact LaTeX sources
and submission documents are included without changing their scientific text.
Repository alignment date: **12 November 2026**.

## The PAIR framework

Quantitative knowledge systems reuse comparisons computed from experimental
references. An incomplete reference can support a comparison among measured
cells while leaving the individual adjusted cells unresolved. PAIR connects
knowledge compilation and model comparison through this shared reference geometry.

- **PAIR-KG** retains complete linear comparisons, binding their coefficients,
  registered completion, source maps and locally verifiable witness.
- **PAIR-Eval** uses the dual quotient response space to separate resolved
  prediction error from training-unresolved offsets and characterize model
  preferences under reference completion.

The paper develops cancellation and aggregation properties, source-refinement
monotonicity, universal completion conditions and explicit computational costs,
with molecular and pharmacogenomic evaluations.

## Paper and submission materials

| Material | File |
|---|---|
| KBS main manuscript | [PDF](manuscript/PAIR_KBS_Main.pdf) · [LaTeX](manuscript/PAIR_KBS_Main.tex) |
| KBS supplementary information S1-S16 | [PDF](manuscript/PAIR_KBS_Supplement.pdf) · [LaTeX](manuscript/PAIR_KBS_Supplement.tex) |
| Cover letter, highlights, title page and metadata | [submission/](submission/README.md) |
| Main editable source bundle | [Manuscript_Source.zip](submission/Manuscript_Source.zip) |
| Supplement editable source bundle | [Supplementary_Source.zip](submission/Supplementary_Source.zip) |
| File version correspondence and SHA256 | [KBS_FILE_ALIGNMENT.json](evidence/KBS_FILE_ALIGNMENT.json) |

The repository retains its historical URL so existing links and scorer citations
continue to resolve. The active manuscript directory now contains the KBS files;
the earlier IS manuscript remains in Git history.

## Run the companion checks

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-verified.txt
python3 scripts/publication_sanity.py
bash scripts/run_constructed_checks.sh
PYTHONPATH=reproduction python3 -m unittest discover -s reproduction -p 'test_*.py' -v
python3 reproduction/original_scorers/verify_scorer_source.py
python3 scripts/verify_kbs_alignment.py
```

With a complete TeX Live installation, rebuild the paper and supplement using:

```bash
bash manuscript/build.sh
```

The build writes to `output/manuscript-build/`; the archived manuscript PDFs
remain unchanged. Included BBL files support the current bibliography.
See [GitHub Actions](https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility/actions)
and [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for verification details.

## Data and scoring resources

The repository includes the original independent CTRPv2/GDSC scoring programs,
29 frozen input SHA256 identities and the historical author-server rescore
receipt. The receipt records matching 700 CTRPv2 and 420 GDSC2 metric fields.
Original scoring sources and historical evidence files are retained unchanged.

Access to large frozen prediction matrices and historical experiment inputs
follows the original data and code availability statement and provider terms.
The public checks verify the supplied software; resource-specific empirical
reproduction uses the corresponding original inputs. Details are in
[DATA_AND_CODE_AVAILABILITY.md](DATA_AND_CODE_AVAILABILITY.md),
[NATIVE_DATA_REQUIREMENTS.md](NATIVE_DATA_REQUIREMENTS.md) and
[the original scorer guide](reproduction/original_scorers/README.md).

Please cite the exact Git commit used. Software and data rights remain as
documented in [RIGHTS_NOTICE.md](RIGHTS_NOTICE.md).
