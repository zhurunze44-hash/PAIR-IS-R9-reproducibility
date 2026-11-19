PAIR: A Framework for Verifiable Quantitative Knowledge Representation and
Model Comparison under Incomplete Evidence
Knowledge-Based Systems (Full Length Article), submitted 19 November 2026.

Official submission files (byte-identical)
------------------------------------------
manuscript/kbs.pdf             36 pages; SHA-256 ae4777c17ef3d9ea8622f98fee0e516096c6943aab2328538e26f685ca808395
manuscript/kbs-supplement.pdf  60 pages; SHA-256 984882e4020e3ab01b9399b1f68326ecac92b2edd8cf26c93d818f13db955cd6

Repository-only convenience files
---------------------------------
manuscript/kbs-full.pdf        96-page combination of submitted PDFs
manuscript/kbs-source.zip      Combined 44-file LaTeX, bibliography, figures,
                               tables and figure-generation source archive.
LaTeX entry points: PAIR_KBS_Main.tex and PAIR_KBS_Supplement.tex.

To rebuild from the repository checkout:
  python3 -m pip install pypdf
  bash manuscript/build.sh

The submitted source includes frozen .bbl files and can be compiled with two
passes of pdflatex per LaTeX entry point. A configured TeX Live installation
is required. The 12 vector figures and the Matplotlib drawing script/data are
included in the combined source archive.

Reproduction archive (public GitHub Release asset)
-------------------------------------------------
KBS_Reproduction.zip is available at:
https://github.com/zhurunze44-hash/PAIR-IS-R9-reproducibility/releases/download/kbs-2026-11-19-reproduction/KBS_Reproduction.zip
It is a 217,964,454-byte ZIP with frozen numerical inputs, scripts and evidence
records. Its SHA-256 is:
  1881b092ef78bd6ef8b05883f0cf6857309f5e12fead826b1418aaee44719535

Its historical 26-stage PASS receipt and scientific file manifest are publicly
available under evidence/KBS_20261119_REPLAY_VERIFICATION.json and
evidence/KBS_20261119_SCIENTIFIC_RELEASE_MANIFEST.json.

The receipt documents tests run on the archived evidence, but does NOT establish
that independent remote reproduction has been run on a new host. Original biological and benchmark
source files remain subject to their providers' rights and terms.
