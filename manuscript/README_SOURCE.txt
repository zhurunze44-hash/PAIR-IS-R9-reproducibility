PAIR: A Framework for Verifiable Quantitative Knowledge Representation and
Model Comparison under Incomplete Evidence
Knowledge-Based Systems / 19 November 2026

Main manuscript: PAIR_KBS_Main.tex
Supplementary information: PAIR_KBS_Supplement.tex

Build both PDFs and the merged reading copy with bash REBUILD.sh. The build
uses TeX Live, latexmk, and Python 3 with pypdf. Either LaTeX entry point also
builds on its own with latexmk -pdf. The bibliography sources and generated
bibliographies are included.

The 12 vector PDF figures are ready to include in LaTeX. To regenerate them,
run python3 figure_sources/draw_figures.py with Matplotlib, NumPy, and the
Liberation Serif font installed. The plotted aggregates are in
figure_sources/plot_data.json.

Reproduction archive

Paper2_KBS_Final_Writing_20261117.zip contains the frozen numerical evidence.
Run RUN_PUBLIC_EVIDENCE.sh from the extracted archive with a new output
directory to run the offline replays. The evidence release is
PAIR-KBS-20261117-final-writing-v4. Its archive SHA-256 is
5143e6416979e4cd0ae13634da06dad753d0e48869285f9da6230916276bc431.
The SHA-256 of SCIENTIFIC_RELEASE_MANIFEST.json inside it is
82b911175729dc2af31da57a404a86088aa0aed54528367e543fa4a7e74fe2f2.

The reproduction archive contains its own writing snapshot. Use the LaTeX
files in this source bundle for the current manuscript. The historical public
CTRPv2 and GDSC scoring snapshot is commit
496d1a3f3ea80009033891811ffa11ed9f7cf334 in the PAIR companion repository.

The author source bundle also includes the 64 source-to-paper mappings in
author_check. The patch and receipts there document the preceding editorial
revision.
