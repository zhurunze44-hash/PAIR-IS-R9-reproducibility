# PAIR

**PAIR: A Framework for Verifiable Quantitative Knowledge Representation and
Model Comparison under Incomplete Evidence**

Companion repository for the PAIR full-length article submitted to **Knowledge-Based Systems on 19 November 2026**. The manuscript and supplement PDFs below are byte-identical to the files submitted in Editorial Manager; the 96-page reading copy is a repository-only merge.

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
| [kbs-source.zip](manuscript/kbs-source.zip) | Combined 44-file LaTeX source with frozen bibliography, editable tables, 12 vector figures and figure-generation code |

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

See the [reproduction guide](REPRODUCIBILITY.md),
[submitted-file checksums](evidence/KBS_FILE_ALIGNMENT.json), and
[full evidence archive verification receipt](evidence/KBS_20261119_REPLAY_VERIFICATION.json).

**Complete frozen evidence archive:** [`KBS_Reproduction.zip` (217,964,454 bytes)](https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility/releases/download/kbs-2026-11-19-reproduction/KBS_Reproduction.zip) is publicly available as a [versioned GitHub Release attachment](https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility/releases/tag/kbs-2026-11-19-reproduction), separate from the Git tree. SHA-256: `1881b092ef78bd6ef8b05883f0cf6857309f5e12fead826b1418aaee44719535`. Its [26-stage offline verification receipt](evidence/KBS_20261119_REPLAY_VERIFICATION.json), [source README](manuscript/README_SOURCE.txt), and [scientific release manifest](evidence/KBS_20261119_SCIENTIFIC_RELEASE_MANIFEST.json) are also available. Archived validation receipts do not by themselves establish that a new independent host has successfully rerun the study. Reuse or redistribution of third-party material remains subject to the original licenses and permissions.

## Data and scoring code

The [original scoring programs](reproduction/original_scorers/) cover CTRPv2
and GDSC. The paper also uses public DrEval, AMLB and TabArena inputs and
separately archived analysis inputs. See
[data and code availability](DATA_AND_CODE_AVAILABILITY.md) for sources and
replay coverage, and the [rights notice](RIGHTS_NOTICE.md) for terms.
