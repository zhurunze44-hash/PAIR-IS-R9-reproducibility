# Data and code availability

This repository provides the current KBS manuscript, its LaTeX and figure
sources, public verification scripts, and the original CTRPv2 and GDSC
scoring programs. See the [scorer guide](reproduction/original_scorers/README.md)
for the pinned historical implementation.

Public evaluation inputs come from [DrEval, Zenodo record 23916090](https://zenodo.org/records/23916090),
AMLB and TabArena. Supplementary Sections S17–S23 identify the exact benchmark
snapshots. Sections S6, S15, S22 and S25 describe the molecular data sources
and available replays.

The research archive accompanying the manuscript is distributed separately.
It contains the frozen analysis inputs, offline replay programs and verification
records. Its version and checksums appear in the
[source README](manuscript/README_SOURCE.txt).

The original scorer replay requires the frozen prediction matrices and other
inputs identified in the [native data requirements](NATIVE_DATA_REQUIREMENTS.md)
and [input pins](evidence/native_input_pins.json). The
[historical replay receipt](evidence/P2_R9_PUBLIC_RESCORE_RECEIPT.json) records
700 matching CTRPv2 fields and 420 matching GDSC2 fields. Third-party data
remain subject to their original provider terms. See the [rights notice](RIGHTS_NOTICE.md).
