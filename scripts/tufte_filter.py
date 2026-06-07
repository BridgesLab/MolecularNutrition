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

    # Parse the (possibly nested) macro token stream into a tree and render it.
    # A stack-based parse handles \newthought{...\sidenote{...}} nesting and
    # note content that contains newlines, and silently drops orphaned markers
    # (e.g. a marginnote whose content pandoc split across paragraphs), so no
    # raw @@ tokens leak into the output.
    tree = parse_macro_tree(full_text)
    new_elems = render_macro_nodes(tree, preserved_elems, doc)

    # Suppress the paragraph entirely if nothing substantive remains
    if not new_elems:
        return []

    return pf.Para(*new_elems)


# A macro marker is either an opening "@@type:" or a bare closing "@@".
_MACRO_MARK = re.compile(r'@@(newthought|marginnote|sidenote):|@@')


def parse_macro_tree(text):
    """Parse the @@-token stream into a nested tree.

    Returns a list of nodes, each ('text', str) or (macro_type, [child nodes]).
    A stack pairs each opening "@@type:" with the next bare "@@", which makes
    nesting work. Stray closing markers are ignored; unclosed openers are
    flushed with whatever content they collected so output never contains
    literal @@ tokens.
    """
    root = []
    stack = [root]          # node lists, innermost last
    types = []              # macro type for each open frame
    pos = 0
    for m in _MACRO_MARK.finditer(text):
        seg = text[pos:m.start()]
        if seg:
            stack[-1].append(('text', seg))
        pos = m.end()
        if m.group(1):                      # opening @@type:
            frame = []
            stack.append(frame)
            types.append(m.group(1))
        elif types:                         # closing @@ for an open frame
            frame = stack.pop()
            stack[-1].append((types.pop(), frame))
        # else: stray closing marker with no open frame → drop it
    tail = text[pos:]
    if tail:
        stack[-1].append(('text', tail))
    # Flush any unclosed openers (note content split across paragraphs)
    while types:
        frame = stack.pop()
        stack[-1].append((types.pop(), frame))
    return root


def render_macro_nodes(nodes, preserved_elems, doc):
    """Render a macro tree (from parse_macro_tree) into a list of inlines."""
    out = []
    for kind, payload in nodes:
        if kind == 'text':
            out.extend(restore_inline(payload, preserved_elems, doc))
        elif kind == 'newthought':
            out.append(pf.Span(
                *render_macro_nodes(payload, preserved_elems, doc),
                classes=['newthought']))
        else:  # sidenote / marginnote
            children = render_macro_nodes(payload, preserved_elems, doc)
            out.extend(build_note(kind, children, doc))
    return out


def build_note(macro_type, children, doc):
    """Build a checkbox-hack disclosure note around already-rendered children.

    label + checkbox + span are all *phrasing* content, so unlike <details>
    the marker stays inside the host <p> and does not break the line. On
    desktop CSS floats the note into the margin (always shown); on mobile it is
    a tap-to-expand disclosure. The checkbox is hidden but keyboard-focusable.
    """
    nid = getattr(doc, '_note_id', 0) + 1
    doc._note_id = nid
    if macro_type == 'sidenote':
        snum = getattr(doc, '_sn_num', 0) + 1
        doc._sn_num = snum
        tid = f'sn-{nid}'
        open_html = (
            f'<label class="note-toggle sn-toggle" for="{tid}" '
            f'aria-label="note {snum}"><sup class="sn-num">{snum}</sup></label>'
            f'<input type="checkbox" id="{tid}" class="note-toggle-input">'
            f'<span class="sidenote" role="note">'
            f'<span class="sn-num-prefix" aria-hidden="true">{snum}. </span>'
        )
    else:
        tid = f'mn-{nid}'
        open_html = (
            f'<label class="note-toggle mn-toggle" for="{tid}" '
            f'aria-label="margin note"><sup class="mn-mark" aria-hidden="true">'
            f'&#9656;</sup></label>'
            f'<input type="checkbox" id="{tid}" class="note-toggle-input">'
            f'<span class="marginnote" role="note">'
        )
    return [pf.RawInline(open_html, 'html'), *children, pf.RawInline('</span>', 'html')]

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

def restore_inline(text, preserved_elems, doc=None):
    r"""Restore preserved inline elements inside macro content.

    Unlike process_text_with_preserved_elems, this is used for the *content*
    of \newthought/\sidenote/\marginnote, which is returned as a new element
    and therefore not re-walked by the main filter pass. So raw-LaTeX inlines
    that the filter would normally rewrite later (\ref, \url) are converted
    here, and output-less ones (\index, \nomenclature, \label) are dropped.
    Math, citations, emphasis, links, etc. are kept as their parsed elements.
    """
    out = []
    for part in re.split(r'(__ELEM_\d+__)', text):
        if part in preserved_elems:
            el = preserved_elems[part]
            if isinstance(el, pf.RawInline) and el.format == 'latex':
                t = el.text.strip()
                ref = re.match(r'\\e?ref\{([^}]+)\}', t)
                url = re.match(r'\\url\{([^}]+)\}', t)
                href = re.match(r'\\href\{([^}]+)\}\{([^}]*)\}', t)
                if ref:
                    out.append(pf.Link(pf.Str('↑'), url=f'#{ref.group(1)}',
                                       title=f'See {ref.group(1)}'))
                elif url:
                    out.append(pf.Link(pf.Str(url.group(1)), url=url.group(1)))
                elif href:
                    out.append(pf.Link(pf.Str(href.group(2)), url=href.group(1)))
                # \index, \nomenclature, \label, … produce no HTML → drop
                continue
            out.append(el)
        elif part:
            for token in split_text_with_spaces(part):
                out.append(pf.Space() if token.isspace() else pf.Str(token))
    return out

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
# margintable → margin-floated <table>
# ---------------------------------------------------------------------------

def latex_tabular_to_html(tabular_body):
    r"""Convert a simple LaTeX tabular body to HTML <thead>/<tbody> rows.

    Handles the simple tables used in these notes (no \multicolumn/\multirow).
    A row whose first cell contains \textbf is treated as the header row.
    """
    # Drop rules; split into rows on \\, cells on unescaped &.
    body = re.sub(r'\\hline|\\toprule|\\midrule|\\bottomrule', '', tabular_body)
    rows = [r.strip() for r in re.split(r'\\\\', body) if r.strip()]
    head_html, body_html = '', ''
    for i, row in enumerate(rows):
        cells = [caption_latex_to_html(c) for c in re.split(r'(?<!\\)&', row)]
        is_header = (i == 0 and '\\textbf' in row)
        if is_header:
            head_html = ('<tr>'
                         + ''.join(f'<th scope="col">{c}</th>' for c in cells)
                         + '</tr>')
        else:
            body_html += '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'
    thead = f'<thead>{head_html}</thead>' if head_html else ''
    return f'{thead}<tbody>{body_html}</tbody>'


def handle_margintable(text):
    r"""Convert \begin{margintable}...\end{margintable} to a margin <figure>."""
    m = re.match(r'\\begin\{margintable\}(.*?)\\end\{margintable\}', text, re.DOTALL)
    if not m:
        return None
    content = m.group(1)

    label_m = re.search(r'\\label\{([^}]+)\}', content)
    id_attr = f' id="{html_module.escape(label_m.group(1))}"' if label_m else ''

    caption_latex = extract_braced_content(content, '\\caption')
    caption_html = caption_latex_to_html(caption_latex) if caption_latex else ''

    tab_m = re.search(r'\\begin\{tabular\}(?:\{[^}]*\})?(.*?)\\end\{tabular\}',
                      content, re.DOTALL)
    if not tab_m:
        return None
    rows_html = latex_tabular_to_html(tab_m.group(1))

    cap = f'<figcaption>{caption_html}</figcaption>' if caption_html else ''
    return pf.RawBlock(
        f'<figure class="margintable"{id_attr}><table>{rows_html}</table>{cap}</figure>',
        'html'
    )


# ---------------------------------------------------------------------------
# RawBlock handler: marginfigure / figure → <figure>
# ---------------------------------------------------------------------------

def handle_raw_block(elem, doc):
    r"""Convert \begin{marginfigure}, \begin{figure}, \begin{margintable}."""
    if not isinstance(elem, pf.RawBlock):
        return None
    if doc.format not in ['html', 'html5']:
        return None
    if elem.format != 'latex':
        return None

    text = elem.text.strip()

    if text.startswith('\\begin{margintable}'):
        result = handle_margintable(text)
        if result is not None:
            return result

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

    return pf.RawBlock(figure_html, 'html')


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
