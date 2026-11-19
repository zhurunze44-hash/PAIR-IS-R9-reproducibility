#!/usr/bin/env bash
set -euo pipefail

src="$(cd -- "$(dirname -- "$0")" && pwd)"
root="$(cd -- "$src/.." && pwd)"
out="${1:-$root/output/manuscript-build}"
mkdir -p -- "$out"
out="$(cd -- "$out" && pwd)"
case "$out/" in
    "$src/"*) echo 'Choose an output directory outside manuscript/' >&2; exit 2 ;;
esac

python3 -m zipfile -e "$src/kbs-source.zip" "$out"
cd -- "$out"

# Frozen .bbl files are included in the submitted source bundle.
for entry in PAIR_KBS_Main PAIR_KBS_Supplement; do
    pdflatex -interaction=nonstopmode -halt-on-error "$entry.tex" >/dev/null
    pdflatex -interaction=nonstopmode -halt-on-error "$entry.tex" >/dev/null
done

cp -- PAIR_KBS_Main.pdf kbs.pdf
cp -- PAIR_KBS_Supplement.pdf kbs-supplement.pdf
python3 - <<'PY'
from pypdf import PdfWriter
w = PdfWriter()
w.append("kbs.pdf")
w.append("kbs-supplement.pdf")
with open("kbs-full.pdf", "wb") as f:
    w.write(f)
PY
echo "Built KBS documents in $out"
