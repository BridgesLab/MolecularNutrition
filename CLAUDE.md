# CLAUDE.md — MolecularNutrition

Teaching notes for NUTR630: Principles of Nutritional Science at the University of Michigan (Drs. Dave Bridges and Olivia Anderson). Licensed CC BY 4.0.

This repository compiles to three outputs:
- Individual PDF files per chapter (via LaTeX, `tufte-handout` class)
- A combined PDF book (`nutr630-notes.pdf`, `tufte-book` class)
- A GitHub Pages website (raw HTML via pandoc)

## Repository Structure

```
tex/                    # Source .tex chapter files (one per lecture) + library.bib + figures/
tex-processed/          # Auto-generated — do not edit directly (recreated by process-tex-files.sh)
html/                   # Website template, index page, and CSS
scripts/                # Build scripts and pandoc filter
nutr630-notes.tex       # Master book file (tufte-book class)
.github/workflows/      # CI pipelines for HTML site and PDF book
environment.yml         # Conda environment for local HTML builds
tstex_modules/          # Dead artifact from ts-tex toolchain — not used
```

## Key Files

| File/Path | Purpose |
|---|---|
| `nutr630-notes.tex` | Master book file; includes all chapters via `\subfile{}` |
| `tex/*.tex` | Individual chapter source files (one per lecture topic) |
| `tex/library.bib` | Shared BibTeX bibliography used by all chapters and the book |
| `tex/figures/` | All figures shared across chapters |
| `tex-processed/` | Auto-generated — do not edit directly; recreated by `process-tex-files.sh` |
| `scripts/process-tex-files.sh` | Preprocesses chapters for book assembly (strips preamble, rewrites figure paths) |
| `scripts/tufte_filter.py` | Pandoc/panflute filter; required for correct HTML output of Tufte macros |
| `html/tufte_template.html` | Pandoc HTML template for the website |
| `html/index.html` | Website landing page |
| `html/tufte.css` / `html/custom.css` | Stylesheet for the website |
| `environment.yml` | Conda environment (pandoc + panflute) for local HTML builds |
| `.github/workflows/build.yml` | CI: builds and deploys the HTML website to GitHub Pages |
| `.github/workflows/compile-book.yml` | CI: assembles and compiles the combined PDF book |

## How PDFs Are Compiled

Individual chapter PDFs use the `tufte-handout` class and can be compiled standalone with `latexmk`:

```bash
latexmk -pdf -f -file-line-error -interaction=nonstopmode -latexoption="-shell-escape" tex/<chapter>.tex
bibtex <chapter>
latexmk -pdf -f -interaction=nonstopmode tex/<chapter>.tex
```

The CI uses `xu-cheng/latex-action@v4` with TeX Live 2025.

## How the Combined Book Is Assembled

1. Run `scripts/process-tex-files.sh` — this awk script strips the preamble from each `tex/*.tex` chapter, wraps it as a `subfiles`-compatible document, rewrites `\includegraphics{figures/...}` paths to `tex-processed/figures/...`, and writes output to `tex-processed/<name>-book.tex`. It also copies `tex/figures/` into `tex-processed/figures/`.

2. Compile `nutr630-notes.tex`, which pulls in chapters via `\subfile{tex-processed/<name>-book}`:

```bash
latexmk -pdf -f -interaction=nonstopmode nutr630-notes.tex
bibtex nutr630-notes
makeindex nutr630-notes.idx
makeindex nutr630-notes.nlo -s nomencl.ist -o nutr630-notes.nls
latexmk -pdf -f -interaction=nonstopmode nutr630-notes.tex   # rerun to resolve refs
```

3. The CI workflow (`compile-book.yml`) handles this automatically on push to `main` when any `tex/*.tex` or `library.bib` changes.

**Do not edit files in `tex-processed/` directly** — they are overwritten on every build.

## How the Website Is Built

Raw HTML — no Jekyll, no Quarto. Each `tex/*.tex` is converted independently by **pandoc**:

```bash
pandoc tex/<file>.tex \
  --from=latex+raw_tex \
  --to=html5 \
  --filter=scripts/tufte_filter.py \
  --template=html/tufte_template.html \
  --mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js \
  --citeproc \
  --bibliography=tex/library.bib \
  -V htmlversion \
  --standalone \
  -o output/<file>.html
```

The `-V htmlversion` flag activates conditional macro definitions inside each `.tex` file (see Tufte Macro Bridge below). The conda environment (`environment.yml`) provides pandoc and panflute. CSS lives in `html/tufte.css` and `html/custom.css`. The CI workflow (`build.yml`) deploys to GitHub Pages on push to `main`.

## Tufte Macro Bridge

Each `.tex` file must include this block near the top to work with both PDF and HTML output:

```latex
\ifdefined\htmlversion
  \def\newthought#1{@@newthought:#1@@}
  \def\marginnote#1{@@marginnote:#1@@}
  \def\sidenote#1{@@sidenote:#1@@}
\else
  \newcommand{\newthought}[1]{\textsc{#1}}
  \newcommand{\marginnote}[1]{\marginpar{#1}}
  \newcommand{\sidenote}[1]{\footnote{#1}}
\fi
```

`tufte_filter.py` (a panflute pandoc filter) converts the `@@...@@` tokens into styled HTML `<span>` elements. Without this filter, the HTML output will be broken.

## Automation Goals

- Automate the annual update/compilation pipeline
- Fix build errors
- Keep website and PDFs in sync

## Known Issues / Gotchas

- **`tex-processed/` is auto-generated** — never edit it directly.
- **No workflow trigger on `scripts/`** — changes to `tufte_filter.py` or `process-tex-files.sh` will not auto-trigger a rebuild; use `workflow_dispatch` manually.
- **`test.tex`** is a scaffolding file in `tex/`; it will be converted to an HTML page by the build but is not included in the book.
- **`tstex_modules/`** is a dead artifact from a ts-tex toolchain and is not used.
- **Individual chapter PDFs** in `tex/` are committed as binary files — they are also regenerated by CI.
