# Data and code availability (verified public snapshot: 2026-11-05)

The source repository is available at
https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility .
It includes the R9 manuscript and supplementary LaTeX, vector figures, source-qualification and mathematical verification software, 29 frozen input SHA256 pins, the original CTRPv2 and GDSC2 independent scorer scripts, and an execution-receipt summary verified from the original author server.

The 2026-11-05 author-server run reproduced CTRPv2 700/700 and GDSC2 420/420 historical numeric metric fields, including byte-identical fold-level historical TSVs. The scorer source files themselves are byte-identical to the audited originals. See `reproduction/original_scorers/README.md` and `evidence/P2_R9_PUBLIC_RESCORE_RECEIPT.json`.

Original third-party experimental observations and frozen model-prediction matrices are not redistributed in this public repository. Their original providers, licensing, access conditions, and historical model/split bindings are specified in the source/evidence documents. The original K562 producer call trace cannot yet be authenticated, and the GDSC1 prediction mount was unavailable in the 2026-11-05 replay. This distinction is part of the public evidence status.

The repository has no immutable archive DOI or author-selected open-source license at this time; do not attribute a DOI, unrestricted reuse permission, or full-data reproducibility to the public snapshot. An Editor/Reviewer should use the exact verified commit for any assessed software snapshot.
