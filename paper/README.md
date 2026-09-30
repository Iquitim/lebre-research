# paper/

Preprint: *LEBRE: Online Forecasting with Evidence-Gated Structural Changes at a Cost of a Few Hundred Operations per Step* (English, arXiv format).

| File | Content |
|---|---|
| `main.tex`, `refs.bib` | Source of the paper |
| `build_assets.py` | Generates every number (`generated/numbers.tex`), table (`generated/tab_*.tex`) and data figure (`figures/*.pdf`) from the result files of the research record; no number is typed by hand |
| `build.sh` | Regenerates the assets, compiles `main.pdf` and packs `arxiv_source.tar.gz` (tex + bbl + generated + figures, as arXiv expects) |
| `main.pdf` | Compiled paper |
| `arxiv_metadata.txt` | Title, abstract (ASCII, length-checked against the 1,920-character limit), comments and suggested categories for the arXiv form |

Requirements: the Python environment of the research record and a LaTeX distribution with `pdflatex` and `bibtex`.
