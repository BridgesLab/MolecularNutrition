#!/usr/bin/env python3
"""Build the Molecular Nutrition HTML website.

Reads the part/chapter structure from nutr630-notes.tex, converts each
tex/<stem>.tex chapter to HTML with pandoc + tufte_filter.py + the U-M
themed template, injects a shared navigation fragment (current chapter
marked), and generates a themed index.html that links the compiled book.

Usage:
    python scripts/build_html.py [output_dir]      # default: output/
"""

import html as html_module
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TEX_DIR = REPO_ROOT / "tex"
HTML_DIR = REPO_ROOT / "html"
SCRIPTS_DIR = REPO_ROOT / "scripts"
MASTER_TEX = REPO_ROOT / "nutr630-notes.tex"
BOOK_PDF = "Principles of Nutrition Science.pdf"
# Public base URL of the GitHub Pages site (trailing slash required) — used
# for the sitemap so search engines get absolute, canonical URLs.
SITE_BASE = "https://bridgeslab.github.io/MolecularNutrition/"

AUTHORS = ("Dave Bridges, Ph.D. &amp; Olivia Anderson, MPH, R.D., Ph.D.")


def parse_book_structure(tex_path):
    """Return [(part_title, [(chapter_title, stem), ...]), ...]."""
    parts = []
    current_part = None
    current_chapters = []
    pending_chapter = None
    with open(tex_path) as f:
        for line in f:
            s = line.strip()
            if s.startswith('%'):
                continue
            pm = re.match(r'\\part\{(.+?)\}', s)
            if pm:
                if current_part is not None:
                    parts.append((current_part, current_chapters))
                current_part, current_chapters, pending_chapter = pm.group(1), [], None
                continue
            cm = re.match(r'\\chapter\{(.+?)\}', s)
            if cm:
                pending_chapter = cm.group(1)
                continue
            sm = re.match(r'\\subfile\{tex-processed/(.+?)-book\}', s)
            if sm and pending_chapter is not None:
                current_chapters.append((pending_chapter, sm.group(1)))
                pending_chapter = None
    if current_part is not None:
        parts.append((current_part, current_chapters))
    # Drop parts with no chapters (e.g. backmatter "Abbreviations…")
    return [(t, c) for t, c in parts if c]


# Short labels for the top-level nav menus (full part titles are long).
PART_LABELS = {
    "Regulation of Metabolism and Overview of Digestion": "General",
    "Carbohydrates": "Carbohydrates",
    "Lipids": "Lipids",
    "Proteins and Nitrogenous Compounds": "Proteins",
}


def build_nav(parts, current_stem):
    """Build the site navigation fragment, marking the current chapter."""
    menus = []
    for part_title, chapters in parts:
        label = PART_LABELS.get(part_title, part_title)
        items = []
        for title, stem in chapters:
            current = ' aria-current="page"' if stem == current_stem else ''
            items.append(
                f'            <li><a href="{stem}.html"{current}>{title}</a></li>')
        items_html = "\n".join(items)
        menus.append(
            '        <li><details>\n'
            f'          <summary>{label}</summary>\n'
            '          <ul class="nav-dropdown">\n'
            f'{items_html}\n'
            '          </ul>\n'
            '        </details></li>')
    menus_html = "\n".join(menus)
    return (
        '  <nav class="site-nav" aria-label="Chapters">\n'
        '    <div class="nav-inner">\n'
        '      <a class="brand" href="index.html">Molecular Nutrition</a>\n'
        '      <details class="nav-collapse">\n'
        '      <summary class="nav-burger" aria-label="Toggle chapter menu">'
        '<span class="burger-icon" aria-hidden="true">☰</span> Chapters</summary>\n'
        '      <ul class="nav-menu">\n'
        f'{menus_html}\n'
        '      </ul>\n'
        '      </details>\n'
        '    </div>\n'
        '  </nav>')


def commit_date_iso(stem):
    """Return YYYY-MM-DD of the last git commit touching tex/<stem>.tex, or
    '' if unavailable (untracked file, or shallow history — see fetch-depth)."""
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", f"tex/{stem}.tex"],
        cwd=REPO_ROOT, capture_output=True, text=True)
    return proc.stdout.strip()


def last_updated(stem):
    """Human-readable last-updated date, e.g. "June 7, 2026" (or '')."""
    iso = commit_date_iso(stem)
    try:
        from datetime import date
        d = date.fromisoformat(iso)
        return f"{d.strftime('%B')} {d.day}, {d.year}"
    except (ValueError, ImportError):
        return iso


def render_sitemap(parts, out_dir):
    """Write sitemap.xml listing the home page + every chapter, with the
    git commit date as <lastmod>. Submit this URL in Search Console."""
    from datetime import date
    urls = []  # (loc, lastmod_iso)
    chapter_dates = []
    for _, chapters in parts:
        for _, stem in chapters:
            iso = commit_date_iso(stem)
            if iso:
                chapter_dates.append(iso)
            urls.append((f"{SITE_BASE}{stem}.html", iso))
    # Home page: use the most recent chapter date as its lastmod.
    home_lastmod = max(chapter_dates) if chapter_dates else date.today().isoformat()
    urls.insert(0, (SITE_BASE, home_lastmod))

    entries = []
    for loc, lastmod in urls:
        lm = f"\n    <lastmod>{lastmod}</lastmod>" if lastmod else ""
        entries.append(f"  <url>\n    <loc>{loc}</loc>{lm}\n  </url>")
    body = "\n".join(entries)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n")
    (out_dir / "sitemap.xml").write_text(xml)


def build_chapter(stem, parts, out_dir):
    """Run pandoc for one chapter and inject the nav. Returns (ok, message)."""
    src = TEX_DIR / f"{stem}.tex"
    if not src.exists():
        return False, f"missing source {src}"
    out = out_dir / f"{stem}.html"
    cmd = [
        "pandoc", str(src),
        "--from=latex+raw_tex", "--to=html5",
        f"--filter={SCRIPTS_DIR / 'tufte_filter.py'}",
        f"--template={HTML_DIR / 'tufte_template.html'}",
        "--mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
        "--citeproc", f"--bibliography={TEX_DIR / 'library.bib'}",
        "-V", "htmlversion", "-V", f"chapterstem={stem}",
        "--standalone", "-o", str(out),
    ]
    updated = last_updated(stem)
    if updated:
        cmd[-2:-2] = ["-V", f"updated={updated}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, proc.stderr.strip().splitlines()[-1] if proc.stderr else "pandoc failed"
    # Inject navigation
    page = out.read_text()
    page = page.replace("<!--SITE_NAV-->", build_nav(parts, stem))
    out.write_text(page)
    # Surface content issues
    warns = []
    leaked = len(re.findall(r'__ELEM_\d+__', page))
    if leaked:
        warns.append(f"{leaked} unrestored __ELEM__ placeholder(s)")
    stray = len(re.findall(r'@@', page))
    if stray:
        warns.append(f"{stray} stray @@ token(s)")
    raw_latex = re.findall(r'\\begin\{(\w+)\}', page)
    if raw_latex:
        warns.append(f"raw LaTeX env(s) left: {sorted(set(raw_latex))}")
    return True, "; ".join(warns)


def render_index(parts, out_dir):
    """Generate the themed home page with the compiled-book download."""
    sections = []
    for part_title, chapters in parts:
        items = "\n".join(
            f'        <li><a href="{stem}.html">{title}</a></li>'
            for title, stem in chapters)
        sections.append(
            f'      <h2>{part_title}</h2>\n'
            f'      <ul class="chapter-list">\n{items}\n      </ul>')
    sections_html = "\n\n".join(sections)
    book_href = html_module.escape(BOOK_PDF).replace(" ", "%20")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="google-site-verification" content="QctZ7qyz-itg4QVvR-ZmZjWuTyH3ApL4i8szOfiLaCs" />
  <title>Molecular Nutrition — NUTR630 Notes</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="um.css">
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <nav class="site-nav" aria-label="Chapters">
    <div class="nav-inner">
      <a class="brand" href="index.html">Molecular Nutrition</a>
    </div>
  </nav>
  <main id="main-content">
    <article class="home">
      <h1>Principles of Nutrition Science</h1>
      <p class="home-authors">{AUTHORS}<br>
        <a href="https://sph.umich.edu/ns/">Department of Nutritional Sciences, University of Michigan School of Public Health</a></p>
      <p>Lecture notes for <strong>NUTR630: Principles of Nutritional Science</strong>. Each chapter is one lecture; read online below or download the complete typeset book.</p>

      <aside class="book-callout">
        <div>
          <h2>The complete book</h2>
          <p>All chapters in one typeset volume, <em>Principles of Nutrition Science</em>.</p>
        </div>
        <a class="pdf-button" href="{book_href}">⬇ Download the full book (PDF)</a>
      </aside>

{sections_html}

      <footer class="home-footer">
        <p>Licensed under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
        Open source — suggestions welcome via <a href="https://github.com/BridgesLab/MolecularNutrition/">GitHub</a>.</p>
      </footer>
    </article>
  </main>
</body>
</html>
"""
    (out_dir / "index.html").write_text(page)


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    parts = parse_book_structure(MASTER_TEX)
    if not parts:
        print("ERROR: no parts/chapters parsed from", MASTER_TEX, file=sys.stderr)
        sys.exit(1)

    all_ok = True
    print(f"Building {sum(len(c) for _, c in parts)} chapters → {out_dir}")
    for _, chapters in parts:
        for title, stem in chapters:
            ok, msg = build_chapter(stem, parts, out_dir)
            status = "ok " if ok else "FAIL"
            flag = f"  ⚠ {msg}" if (msg and ok) else (f"  ✗ {msg}" if not ok else "")
            print(f"  [{status}] {stem}{flag}")
            all_ok = all_ok and ok

    render_index(parts, out_dir)
    print("Generated index.html")
    render_sitemap(parts, out_dir)
    print("Generated sitemap.xml")
    sys.exit(0 if all_ok else 2)


if __name__ == "__main__":
    main()
