# Supplementary Code S1: released code and author-server rescoring

Public files include the complete R9 English main and S1-S16 supplementary source, references, vector-figure PDF assets, exact-algebra verifiers, input-bound G0/G2 checker, constructed tests, SHA256 frozen-asset pins, and a GitHub Actions CI job.

**New on 2026-11-05:** the original independent CTRPv2 and GDSC1/GDSC2 scorer source files were added byte-identically, together with `run_gdsc2_only.py`, original-source checks, a pinned historical environment and a redacted public run receipt. On the author server, the frozen CTRPv2 and GDSC2 predictions were rescored against historical results: 700/700 and 420/420 matching numeric fields respectively, with byte-identical historical fold-metric TSVs. GDSC2 preserved zero persistent reversal pairs.

The public repository does not distribute complete row-aligned frozen predictions or upstream third-party experimental data. Reproducing these empirical checks on another machine therefore requires approved access to those inputs. GDSC1 is not rescored because its mounted predictions were absent; K562 original producer lineage remains uncertified. Author-server hashes and provenance are recorded, but file integrity alone is not full producer certification.

Use the repository URL above, or an exact immutable commit SHA, in the formal data/code statement. No public release DOI or redistribution license has been assigned.
