#!/usr/bin/env python3
r"""Tufte-style macros filter for Panflute.

Need to add this to the top of all tex files

% Conditionally redefine Tufte-style macros for HTML output
\ifdefined\htmlversion
  \def\newthought#1{@@newthought:#1@@}
  \def\marginnote#1{@@marginnote:#1@@}
  \def\sidenote#1{@@sidenote:#1@@}
  \def\alttext#1{@@alttext:#1@@}
\fi
\providecommand{\alttext}[1]{}

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
import html as html_module
import panflute as pf
import re


# ---------------------------------------------------------------------------
# Helpers for LaTeX figure environment conversion
# ---------------------------------------------------------------------------

def extract_braced_content(text, cmd):
    r"""Return content of \cmd{...} in text, handling nested braces.

    cmd should include the leading backslash, e.g. '\\caption'.
    Returns None if cmd is not found.
    """
    marker = cmd + '{'
    start = text.find(marker)
    if start == -1:
        return None
    pos = start + len(marker)
    depth = 1
    while pos < len(text) and depth > 0:
        if text[pos] == '{':
            depth += 1
        elif text[pos] == '}':
            depth -= 1
        if depth > 0:
            pos += 1
    return text[start + len(marker):pos] if depth == 0 else None


def caption_latex_to_html(text):
    """Convert LaTeX caption text to basic HTML suitable for <figcaption>."""
    if not text:
        return ''
    # Citations → [key]
    text = re.sub(r'\\cite[tp]?\*?\{([^}]+)\}', r'[\1]', text)
    # Inline math $...$ → \(...\) for MathJax
    text = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', text)
    # sub/sup
    text = re.sub(r'\\textsubscript\{([^}]*)\}', r'<sub>\1</sub>', text)
    text = re.sub(r'\\textsuperscript\{([^}]*)\}', r'<sup>\1</sup>', text)
    # emphasis
    text = re.sub(r'\\emph\{([^}]*)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\textbf\{([^}]*)\}', r'<strong>\1</strong>', text)
    # strip remaining \cmd{arg} → arg
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    # strip standalone \cmd
    text = re.sub(r'\\[a-zA-Z]+\*?\s*', '', text)
    # strip stray braces and backslashes
    text = re.sub(r'[{}\\]', '', text)
    # normalise whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ---------------------------------------------------------------------------
# Para-level @@token:content@@ substitutions
# ---------------------------------------------------------------------------

def extract_text_from_elem(elem):
    """Extract text from an element, preserving non-text elements."""
    if isinstance(elem, pf.Str):
        return elem.text, None
    elif isinstance(elem, pf.Space):
        return ' ', None
    elif isinstance(elem, pf.SoftBreak):
        return '\n', None
    else:
        # For non-text elements (like citations, images), return placeholder and store the element
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

    # If no tufte macros or alttext tokens, return unchanged
    if '@@' not in full_text:
        return None

    # Extract @@alttext:...@@ tokens: store pending alt text and remove from text.
    # \alttext{} is typically on the line immediately before \includegraphics{},
    # so both end up in the same paragraph and the image is in preserved_elems.
    alttext_pattern = r'@@alttext:(.*?)@@'
    for m in re.finditer(alttext_pattern, full_text):
        doc._pending_alt = m.group(1).strip()
    full_text = re.sub(alttext_pattern, '', full_text)

    # If nothing remains after stripping alttext, suppress the paragraph entirely
    if not full_text.strip() and not re.search(r'__ELEM_\d+__', full_text):
        return []

    pattern = r'@@(newthought|marginnote|sidenote):(.*?)@@'

    # Process the text and build new elements
    new_elems = []
    pos = 0

    for m in re.finditer(pattern, full_text):
        start, end = m.span()
        macro_type, macro_content = m.groups()

        # Handle text before the macro
        before_text = full_text[pos:start]
        new_elems.extend(process_text_with_preserved_elems(before_text, preserved_elems, doc))

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

    # Handle remaining text after last macro.
    # Strip orphaned @@ tokens that arise when sidenote content spans multiple
    # paragraphs or block elements (e.g. sidenotes containing \begin{enumerate}).
    after_text = full_text[pos:]
    # Remove incomplete opening tokens (@@type:... with no closing @@)
    after_text = re.sub(
        r'@@(?:newthought|marginnote|sidenote|alttext):[^@]*$', '', after_text, flags=re.DOTALL
    )
    # Remove orphaned lone @@ at start (leftover closing token from a split block)
    after_text = re.sub(r'^@@', '', after_text)
    after_text = after_text.strip()
    new_elems.extend(process_text_with_preserved_elems(after_text, preserved_elems, doc))

    # Suppress the paragraph entirely if nothing substantive remains
    if not new_elems:
        return []

    return pf.Para(*new_elems)

def process_text_with_preserved_elems(text, preserved_elems, doc=None):
    """Process text string and restore preserved elements.

    If doc has a _pending_alt attribute, applies it to the first Image encountered.
    """
    elems = []

    # Split by preserved element placeholders
    parts = re.split(r'(__ELEM_\d+__)', text)

    for part in parts:
        if part in preserved_elems:
            elem = preserved_elems[part]
            # Apply pending alt text to the first Image that has none (SC 1.1.1)
            if (doc is not None
                    and isinstance(elem, pf.Image)
                    and not elem.content):
                pending = getattr(doc, '_pending_alt', None)
                if pending:
                    elem.content = [pf.Str(pending)]
                    doc._pending_alt = None
            elems.append(elem)
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


# ---------------------------------------------------------------------------
# Image alt text (standalone <img> not inside a figure environment)
# ---------------------------------------------------------------------------

def apply_alt_to_image(elem, doc):
    """Apply pending alt text to an Image element (SC 1.1.1).

    Handles the case where \\alttext{} and \\includegraphics{} are in separate
    paragraphs (e.g. a blank line between them, or different figure structure).
    """
    if not isinstance(elem, pf.Image):
        return None
    if doc.format not in ['html', 'html5']:
        return None
    pending = getattr(doc, '_pending_alt', None)
    if pending and not elem.content:
        elem.content = [pf.Str(pending)]
        doc._pending_alt = None
        return elem
    return None


# ---------------------------------------------------------------------------
# Table accessibility
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# RawBlock handler: marginfigure / figure → <figure>
# ---------------------------------------------------------------------------

def handle_raw_block(elem, doc):
    r"""Convert \begin{marginfigure} and \begin{figure} environments to HTML."""
    if not isinstance(elem, pf.RawBlock):
        return None
    if doc.format not in ['html', 'html5']:
        return None
    if elem.format != 'latex':
        return None

    text = elem.text.strip()

    env_re = re.compile(
        r'\\begin\{(marginfigure|figure\*?)\}(.*?)\\end\{(?:marginfigure|figure\*?)\}',
        re.DOTALL
    )
    m = env_re.match(text)
    if not m:
        return None

    env_type = m.group(1)
    content = m.group(2)

    # Image path
    img_m = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', content)
    if not img_m:
        return None
    img_src = img_m.group(1)

    # Label → id attribute
    label_m = re.search(r'\\label\{([^}]+)\}', content)
    label = label_m.group(1) if label_m else ''

    # Alt text: prefer \alttext{} inside the environment, then pending alt
    alt_m = re.search(r'\\alttext\{([^}]+)\}', content)
    if alt_m:
        alt = alt_m.group(1).strip()
        doc._pending_alt = None
    else:
        alt = getattr(doc, '_pending_alt', '') or ''
        if alt:
            doc._pending_alt = None

    # Caption with nested-brace-aware extraction
    caption_latex = extract_braced_content(content, '\\caption')
    caption_html = caption_latex_to_html(caption_latex) if caption_latex else ''

    # Build HTML
    css_class = 'marginfigure' if env_type == 'marginfigure' else 'figure'
    id_attr = f' id="{html_module.escape(label)}"' if label else ''
    alt_escaped = html_module.escape(alt) if alt else ''
    img_tag = f'<img src="{html_module.escape(img_src)}" alt="{alt_escaped}">'
    cap_tag = f'<figcaption>{caption_html}</figcaption>' if caption_html else ''
    figure_html = f'<figure class="{css_class}"{id_attr}>{img_tag}{cap_tag}</figure>'

    return pf.RawBlock('html', figure_html)


# ---------------------------------------------------------------------------
# RawInline handler: \ref{} and \eqref{} cross-references → anchor links
# ---------------------------------------------------------------------------

def handle_raw_inline(elem, doc):
    r"""Convert \ref{label} RawInline elements to HTML anchor links."""
    if not isinstance(elem, pf.RawInline):
        return None
    if doc.format not in ['html', 'html5']:
        return None
    if elem.format != 'latex':
        return None

    m = re.match(r'\\e?ref\{([^}]+)\}', elem.text.strip())
    if m:
        label = m.group(1)
        return pf.Link(pf.Str('↑'), url=f'#{label}', title=f'See {label}')

    return None


# ---------------------------------------------------------------------------
# Main action dispatcher
# ---------------------------------------------------------------------------

def action(elem, doc):
    if isinstance(elem, pf.Para):
        return replace_macros_in_para(elem, doc)
    if isinstance(elem, pf.Image):
        return apply_alt_to_image(elem, doc)
    if isinstance(elem, pf.Table):
        return add_table_scope(elem, doc)
    if isinstance(elem, pf.RawBlock):
        return handle_raw_block(elem, doc)
    if isinstance(elem, pf.RawInline):
        return handle_raw_inline(elem, doc)
    return None

def main(doc=None):
    pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()
