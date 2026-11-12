#!/usr/bin/env bash
set -euo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$src/.." && pwd)"
out="${1:-$root/output/manuscript-build}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"
case "$out/" in "$src/"*) echo 'Choose an output directory outside manuscript/' >&2; exit 2;; esac
command -v pdflatex >/dev/null || { echo 'Install TeX Live with pdflatex' >&2; exit 2; }
cp "$src"/*.tex "$src"/*.bbl "$src"/*.bib "$src"/*.bst "$src"/*.cls "$out/"
mkdir -p "$out/figures"
cp "$src"/figures/*.pdf "$out/figures/"
cd "$out"
for name in PAIR_KBS_Main PAIR_KBS_Supplement; do
  for round in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error -file-line-error "${name}.tex" > "${name}_pass${round}.txt" 2>&1 || {
      tail -n 35 "${name}_pass${round}.txt" >&2; exit 1;
    }
  done
done
echo "Built KBS documents in $out; original PDFs are unchanged."
