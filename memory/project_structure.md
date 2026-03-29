---
name: Project Structure and Build System
description: Overview of MolecularNutrition repo layout, build pipeline, and automation workflows
type: project
---

# MolecularNutrition Project Structure

Teaching notes for NUTR630 at University of Michigan (Drs. Dave Bridges and Olivia Anderson). Licensed CC BY 4.0.

## Directory Layout
- `tex/` — 22 source `.tex` chapter files + `library.bib` + `figures/` subfolder
- `tex-processed/` — generated `-book.tex` variants (preprocessed for subfile inclusion in the combined book)
- `html/` — HTML template (`tufte_template.html`), `index.html`, `tufte.css`, `custom.css`
- `scripts/` — `process-tex-files.sh` (awk preprocessor) + `tufte_filter.py` (panflute pandoc filter)
- `nutr630-notes.tex` — master book file (tufte-book class, uses `\subfile{}` for each chapter)
- `.github/workflows/` — two CI workflows: `build.yml` (HTML/GitHub Pages) and `compile-book.yml` (PDF book)
- `environment.yml` — conda env: python 3.11 + pandoc + panflute
- `tstex_modules/` — leftover ts-tex TypeScript stub, not actively used

## Build Pipeline

### HTML website (build.yml → GitHub Pages)
1. Triggered on push to `main` when `tex/*.tex`, `tex/*.bib`, or `tex/figures/**` change
2. Conda env set up with pandoc + panflute
3. Each `tex/*.tex` converted via pandoc → HTML5, using `tufte_filter.py` and `tufte_template.html`
4. PDFs, figures, CSS, and custom `index.html` copied to `output/`
5. Deployed to GitHub Pages via `actions/deploy-pages`

### Combined PDF book (compile-book.yml)
1. Triggered on push to `main` when `tex/*.tex` or `tex/library.bib` change
2. `scripts/process-tex-files.sh` strips preamble, wraps each chapter as a `subfiles` document, rewrites figure paths
3. `latexmk` compiles `nutr630-notes.tex` (tufte-book) via `xu-cheng/latex-action@v4`
4. BibTeX + makeindex run, then recompile to resolve refs
5. `nutr630-notes.pdf` and `nutr630-notes.log` uploaded as artifacts

### Tufte macro bridge
Individual `.tex` files use conditional macros (`\ifdefined\htmlversion`) so `\sidenote`, `\marginnote`, `\newthought` render as proper HTML spans (via panflute filter) or as LaTeX footnotes/marginpar.

## Potential Issues / Automation Gaps
- `tstex_modules/_api.ts` is a dead artifact — can be deleted
- Individual chapter PDFs in `tex/` are committed directly (binary artifacts in git)
- `compile-book.yml` runs bibtex/makeindex in a plain `run:` step after the latex-action step — the working directory may not match where latex-action left files; could cause reference resolution issues
- `test.tex` / `test-book.tex` are scaffolding files; if included accidentally in the book they could cause issues
- No workflow triggers on changes to `scripts/` — modifying the filter or preprocessor won't auto-rebuild
- No linting or spell-check automation
