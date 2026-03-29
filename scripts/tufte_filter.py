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

def extract_text_from_elem(elem):
    """Extract text from an element, preserving non-text elements."""
    if isinstance(elem, pf.Str):
        return elem.text, None
    elif isinstance(elem, pf.Space):
        return ' ', None
    elif isinstance(elem, pf.SoftBreak):
        return '\n', None
    else:
        # For non-text elements (like citations), return placeholder and store the element
        return f"__ELEM_{id(elem)}__", elem

def replace_macros_in_para(elem, doc):
    if doc.format not in ['html', 'html5']:
        return None

    # Extract text and preserve non-text elements
    text_parts = []
    preserved_elems = {}
    
    for item in elem.content:
        text, preserved_elem = extract_text_from_elem(item)
        text_parts.append(text)
        if preserved_elem is not None:
            preserved_elems[f"__ELEM_{id(item)}__"] = preserved_elem

    full_text = ''.join(text_parts)

    # If no tufte macros, return unchanged
    if '@@' not in full_text:
        return None

    pattern = r'@@(newthought|marginnote|sidenote):(.*?)@@'

    # Process the text and build new elements
    new_elems = []
    pos = 0
    
    for m in re.finditer(pattern, full_text):
        start, end = m.span()
        macro_type, macro_content = m.groups()

        # Handle text before the macro
        before_text = full_text[pos:start]
        new_elems.extend(process_text_with_preserved_elems(before_text, preserved_elems))

        # Add the macro
        if macro_type in ['marginnote', 'sidenote']:
            wrapper = pf.Span(
                # aria-hidden: icon is visual only; screen readers read the
                # note content directly from the DOM (SC 4.1.2)
                pf.Span(pf.Str('‡'), classes=['margin-icon'],
                        attributes={'aria-hidden': 'true'}),
                # role="note" marks the content semantically; tabindex="0"
                # makes it keyboard-reachable so :focus-within shows the
                # visual tooltip (SC 2.1.1)
                pf.Span(pf.Str(macro_content), classes=[macro_type],
                        attributes={'role': 'note', 'tabindex': '0'}),
                classes=[f"{macro_type}-wrapper"]
            )
            new_elems.append(wrapper)
        else:
            new_elems.append(pf.Span(pf.Str(macro_content), classes=[macro_type]))

        pos = end

    # Handle remaining text after last macro
    after_text = full_text[pos:]
    new_elems.extend(process_text_with_preserved_elems(after_text, preserved_elems))

    return pf.Para(*new_elems)

def process_text_with_preserved_elems(text, preserved_elems):
    """Process text string and restore preserved elements."""
    elems = []
    
    # Split by preserved element placeholders
    parts = re.split(r'(__ELEM_\d+__)', text)
    
    for part in parts:
        if part in preserved_elems:
            # Restore preserved element
            elems.append(preserved_elems[part])
        elif part:
            # Process regular text, preserving spaces
            tokens = split_text_with_spaces(part)
            for token in tokens:
                if token.isspace():
                    elems.append(pf.Space())
                else:
                    elems.append(pf.Str(token))
    
    return elems

def split_text_with_spaces(text):
    """Split text by spaces but keep spaces as separate tokens."""
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

def add_table_scope(elem, doc):
    """Add scope='col' to header cells for screen reader table navigation (SC 1.3.1)."""
    if not isinstance(elem, pf.Table):
        return None
    if doc.format not in ['html', 'html5']:
        return None
    for row in elem.head.content:
        for cell in row.content:
            if 'scope' not in cell.attributes:
                cell.attributes['scope'] = 'col'
    return elem


def action(elem, doc):
    if isinstance(elem, pf.Para):
        return replace_macros_in_para(elem, doc)
    if isinstance(elem, pf.Table):
        return add_table_scope(elem, doc)
    return None

def main(doc=None):
    pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()