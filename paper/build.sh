#!/usr/bin/env bash
# build.sh — regenerates numbers/tables/figures from the result files, compiles the paper and packs the arXiv source.
set -e
cd "$(dirname "$0")"
python build_assets.py
pdflatex -interaction=nonstopmode main.tex > /dev/null
bibtex main > /dev/null
pdflatex -interaction=nonstopmode main.tex > /dev/null
pdflatex -interaction=nonstopmode main.tex > /dev/null
! grep -E "^!|undefined" main.log || { echo "LaTeX errors or undefined references"; exit 1; }
rm -rf arxiv && mkdir -p arxiv/generated arxiv/figures
cp main.tex main.bbl arxiv/ && cp generated/*.tex arxiv/generated/ && cp figures/*.pdf arxiv/figures/
(cd arxiv && tar -czf ../arxiv_source.tar.gz .)
echo "main.pdf and arxiv_source.tar.gz ready"
