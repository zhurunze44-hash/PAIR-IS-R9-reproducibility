#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p revision_audit
latexmk -pdf -interaction=nonstopmode -halt-on-error PAIR_KBS_Main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error PAIR_KBS_Supplement.tex
python3 editorial/merge_pdfs.py
