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
bash "$out/REBUILD.sh"
cp -- "$out/PAIR_KBS_Main.pdf" "$out/kbs.pdf"
cp -- "$out/PAIR_KBS_Supplement.pdf" "$out/kbs-supplement.pdf"
cp -- "$out/PAIR_KBS_Complete.pdf" "$out/kbs-full.pdf"
echo "Built KBS documents in $out"
