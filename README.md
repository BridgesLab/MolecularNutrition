# Molecular Nutrition

This repository contains notes used for teaching nutrition to graduate and undergraduate students at the University of Michigan.  For more information about Dave Bridges and the reasearch of his group see the [Bridges Lab Website](https://bridgeslab.sph.umich.edu).  Find more information about the [Nutritional Sciences Department at the University of Michigan School of Public Health](https://sph.umich.edu/ns/).

## Organization

* Files are written as tex files in the `tex folder`.
* Automated processing of these files generates `html files` that can be viewed at [Molecular Nutrition Notes](https://bridgeslab.github.io/MolecularNutrition/).
* Files are also automatically processed into `tex-processed` for compilation into a combined book.
* Scripts for processign these files can be found in `scripts` and via github workflows found in `.github/workflows`.

## Creating Your Own Version

You can fork this repository and publish your own website with your own content. GitHub will automatically build and deploy it using the same workflow.

### 1. Fork the repository

Click **Fork** at the top right of this page. All the build workflows come with it.

### 2. Enable GitHub Pages on your fork

In your fork, go to **Settings → Pages** and set:
- **Source**: GitHub Actions

The site will be published at `https://<your-username>.github.io/MolecularNutrition/` after your first push to `main`.

### 3. Edit or add chapters

All content lives in `tex/*.tex`. Each file is one chapter and compiles to both a PDF and an HTML page. When you push changes to `main`, the website and PDFs rebuild automatically.

Every `.tex` file must include this block near the top (after `\usepackage` declarations) for the HTML build to work:

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

### 4. Add or remove chapters from the book and website

Edit `nutr630-notes.tex` to add or remove `\chapter` and `\subfile` entries. The website index page is auto-generated from this file on every build, so it will always stay in sync.

### 5. Build locally

To build HTML pages locally, set up the conda environment and run pandoc manually:

```bash
conda env create -f environment.yml
conda activate molecuar-nutrition
pandoc tex/<chapter>.tex \
  --from=latex+raw_tex --to=html5 \
  --filter=scripts/tufte_filter.py \
  --template=html/tufte_template.html \
  --citeproc --bibliography=tex/library.bib \
  -V htmlversion --standalone \
  -o output/<chapter>.html
```

To build the combined PDF book locally, first run the preprocessor then compile:

```bash
bash scripts/process-tex-files.sh
latexmk -pdf -interaction=nonstopmode nutr630-notes.tex
```

## Contributing and Using These Notes

For information on how to contribute to these notes see [CONTRIBUTING.md].  If you find an issue or an error please report it on the [issue tracker](https://github.com/BridgesLab/MolecularNutrition/issues.)

### License

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

This repository and its contents are licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). Attribution: Dave Bridges.
