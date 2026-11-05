#!/usr/bin/env bash
# Rebuild from sources, keeping all figure and numerical inputs unchanged.
set -euo pipefail
cd "$(dirname "$0")"
for BASE in PAIR_IS_R9_Main PAIR_IS_R9_Supplement; do
  pdflatex -interaction=nonstopmode -halt-on-error "$BASE.tex"
  bibtex8 "$BASE"
  pdflatex -interaction=nonstopmode -halt-on-error "$BASE.tex"
  pdflatex -interaction=nonstopmode -halt-on-error "$BASE.tex"
done
