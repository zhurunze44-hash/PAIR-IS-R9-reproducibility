# Data and code availability

This repository provides the current KBS manuscript, its LaTeX and figure
sources, public verification scripts, and the original CTRPv2 and GDSC
scoring programs. See the [scorer guide](reproduction/original_scorers/README.md)
for the pinned historical implementation.

Public evaluation inputs come from [DrEval, Zenodo record 23916090](https://zenodo.org/records/23916090),
AMLB and TabArena. Supplementary Sections S17–S23 identify the exact benchmark
snapshots. Sections S6, S15, S22 and S25 describe the molecular data sources
and available replays.

The complete frozen research archive ([`KBS_Reproduction.zip`](https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility/releases/download/kbs-2026-11-19-reproduction/KBS_Reproduction.zip), 217,964,454 bytes) is now publicly downloadable as a [GitHub Release asset](https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility/releases/tag/kbs-2026-11-19-reproduction); it is not committed to the Git source tree. It contains frozen analysis inputs, offline replay programs and verification records. Its archive SHA-256 is `1881b092ef78bd6ef8b05883f0cf6857309f5e12fead826b1418aaee44719535`. The archived 26-stage PASS receipt and scientific file SHA-256 manifest have been published under [`evidence/KBS_20261119_REPLAY_VERIFICATION.json`](evidence/KBS_20261119_REPLAY_VERIFICATION.json) and [`evidence/KBS_20261119_SCIENTIFIC_RELEASE_MANIFEST.json`](evidence/KBS_20261119_SCIENTIFIC_RELEASE_MANIFEST.json). These receipts do not constitute a complete public reproduction archive.

The original scorer replay requires the frozen prediction matrices and other
inputs identified in the [native data requirements](NATIVE_DATA_REQUIREMENTS.md)
and [input pins](evidence/native_input_pins.json). The
[historical replay receipt](evidence/P2_R9_PUBLIC_RESCORE_RECEIPT.json) records
700 matching CTRPv2 fields and 420 matching GDSC2 fields. Third-party data
remain subject to their original provider terms. See the [rights notice](RIGHTS_NOTICE.md).
