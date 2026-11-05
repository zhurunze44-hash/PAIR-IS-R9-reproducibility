# Original producer and evaluation evidence required for native reproduction

| Experiment/group | Required original source files | State in supplied R9 ZIP |
|---|---|---|
| K562 fold-0 (3,125 requests / 349 values) | Historical TRAIN mask, source ledger `RR`/`RE`, bound numerical arrays/row IDs, producer call trace, frozen result labels, original completion `F` | MISSING original lineage; conditioned replay reported |
| K562/HEK/ENCODE legal-space screens | Exact processed tables, frozen split masks, source maps, original operators, counted outputs and executable replay scripts | MISSING in R9 ZIP |
| Replogle design-only 100,000 queries | Original metadata and native source identity roster, fixed query builder, seed and 100k query program/replay receipts | MISSING in R9 ZIP |
| CTRPv2 7 models, 10 folds | Original truth/prediction matrices, per-fold common support, source IDs, scorer and versioned environment | MISSING in R9 ZIP |
| GDSC1/GDSC2 confirmatory | Frozen predictions, fold assignments, scorer, heldout metadata, predeclared stopping thresholds | MISSING in R9 ZIP |
| Figure reproducibility | Script and exact numeric inputs for each vector plot, registered hashes | MISSING generators, PDF figures available |

**No requirement to upload huge third-party raw data to GitHub.** Link to original
accessions and publish small legally redistributable processed/native inputs
with checksums and scripts, or give a justified restriction. Source authentication
requires genuine original files, not a manifest reassembled from the paper.

Start with `Author_Server_Native_Export/inventory_and_stage.py` from the delivery
bundle on the original author server; it is read-only
on frozen assets and writes evidence to an independent new output directory.
