#!/usr/bin/env python3
r"""Tufte-style macros filter for Panflute.

Need to add this to the top of all tex files

% Conditionally redefine Tufte-style macros for HTML output
\ifdefined\htmlversion
  \def\newthought#1{@@newthought:#1@@}
  \def\marginnote#1{@@marginnote:#1@@}
  \def\sidenote#1{@@sidenote:#1@@}
\else
  \newcommand{\newthought}[1]{\textsc{#1}}
  \newcommand{\marginnote}[1]{\marginpar{#1}}
  \newcommand{\sidenote}[1]{\footnote{#1}}
\fi

Local usage:
    pandoc test.tex \
        --from=latex+raw_tex \
        --to=html5 \
        --filter=../scripts/tufte_filter.py \
        --template=../html/tufte_template.html \
        --mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js \
        --citeproc \
        --bibliography=library.bib \
        -V htmlversion \
        --standalone \
        -o test.html
"""
import panflute as pf
import re

def split_text_with_spaces(text):
    # Split text by spaces but keep spaces as separate tokens
    tokens = []
    pos = 0
    for m in re.finditer(r'\s+', text):
        if m.start() > pos:
            tokens.append(text[pos:m.start()])
        tokens.append(text[m.start():m.end()])
        pos = m.end()
    if pos < len(text):
        tokens.append(text[pos:])
    return tokens

def replace_macros_in_para(elem, doc):
    if doc.format not in ['html', 'html5']:
        return None

    # Reassemble full paragraph text
    text_parts = []
    for item in elem.content:
        if isinstance(item, pf.Str):
            text_parts.append(item.text)
        elif isinstance(item, pf.Space):
            text_parts.append(' ')
        elif isinstance(item, pf.SoftBreak):
            text_parts.append('\n')
        else:
            text_parts.append(pf.stringify(item))
    full_text = ''.join(text_parts)

    if '@@' not in full_text:
        return None

    pattern = r'@@(newthought|marginnote|sidenote):(.*?)@@'

    new_elems = []
    pos = 0
    for m in re.finditer(pattern, full_text):
        start, end = m.span()
        macro_type, macro_content = m.groups()

        before_text = full_text[pos:start]
        tokens = split_text_with_spaces(before_text)
        for t in tokens:
            if t.isspace():
                new_elems.append(pf.Space())
            else:
                new_elems.append(pf.Str(t))

        if macro_type in ['marginnote', 'sidenote']:
            wrapper = pf.Span(
                pf.Span(pf.Str('‡'), classes=['margin-icon']),
                pf.Span(pf.Str(macro_content), classes=[macro_type]),
                classes=[f"{macro_type}-wrapper"]
            )
            new_elems.append(wrapper)
        else:
            new_elems.append(pf.Span(pf.Str(macro_content), classes=[macro_type]))

        pos = end

    after_text = full_text[pos:]
    tokens = split_text_with_spaces(after_text)
    for t in tokens:
        if t.isspace():
            new_elems.append(pf.Space())
        else:
            new_elems.append(pf.Str(t))

    return pf.Para(*new_elems)

def action(elem, doc):
    if isinstance(elem, pf.Para):
        return replace_macros_in_para(elem, doc)
    return None

def main(doc=None):
    pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()
