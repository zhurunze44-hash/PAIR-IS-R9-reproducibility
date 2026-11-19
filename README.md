# PAIR

**PAIR: A Framework for Verifiable Quantitative Knowledge Representation and
Model Comparison under Incomplete Evidence**

Companion repository for the 19 November 2026 Knowledge-Based Systems manuscript.

PAIR binds a quantitative comparison to its target, observation measure,
scoring rule, aggregation and admissible completion domain. PAIR-KG compiles
reference- and source-qualified contrasts with local verification witnesses.
PAIR-Eval checks model comparisons and identifies repairs or decision bounds
under the declared contract.

## Manuscript

| File | Contents |
|---|---|
| [kbs.pdf](manuscript/kbs.pdf) | Main article, 36 pages |
| [kbs-supplement.pdf](manuscript/kbs-supplement.pdf) | Supplementary Sections S1–S25, 60 pages |
| [kbs-full.pdf](manuscript/kbs-full.pdf) | Main article and supplement, 96 pages |
| [kbs-source.zip](manuscript/kbs-source.zip) | Compilable LaTeX, bibliography, editable tables, vector figures and figure code |

The [source files](manuscript/) are also available individually. The
[12 November snapshot](https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility/tree/ae3697aeb23ee42621b314a8a1b8b9c812f74ee9)
contains the earlier paper and its submission materials.

## Build and verify

Install TeX Live with `latexmk` and install `pypdf` for the combined PDF.

```bash
python3 -m pip install pypdf
bash manuscript/build.sh
```

Run the public verification checks:

```bash
python3 -m pip install -r requirements-verified.txt
python3 scripts/publication_sanity.py
bash scripts/run_constructed_checks.sh
PYTHONPATH=reproduction python3 -m unittest discover -s reproduction -p 'test_*.py' -v
python3 reproduction/original_scorers/verify_scorer_source.py
python3 scripts/verify_kbs_alignment.py
```

See the [reproduction guide](REPRODUCIBILITY.md) and
[manuscript file checksums](evidence/KBS_FILE_ALIGNMENT.json).

## Data and scoring code

The [original scoring programs](reproduction/original_scorers/) cover CTRPv2
and GDSC. The paper also uses public DrEval, AMLB and TabArena inputs and
separately archived analysis inputs. See
[data and code availability](DATA_AND_CODE_AVAILABILITY.md) for sources and
replay coverage, and the [rights notice](RIGHTS_NOTICE.md) for terms.
