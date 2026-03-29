#!/usr/bin/env python3
"""Generate output/index.html from the chapter list in nutr630-notes.tex.

Usage:
    python scripts/generate_index.py                        # writes to output/index.html
    python scripts/generate_index.py path/to/output.html   # writes to custom path
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def parse_book_structure(tex_path: Path) -> list[tuple[str, list[tuple[str, str]]]]:
    """Return [(part_title, [(chapter_title, html_filename), ...]), ...]."""
    parts = []
    current_part = None
    current_chapters: list[tuple[str, str]] = []
    pending_chapter = None

    with open(tex_path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('%'):
                continue

            part_match = re.match(r'\\part\{(.+?)\}', stripped)
            if part_match:
                if current_part is not None:
                    parts.append((current_part, current_chapters))
                current_part = part_match.group(1)
                current_chapters = []
                pending_chapter = None
                continue

            chapter_match = re.match(r'\\chapter\{(.+?)\}', stripped)
            if chapter_match:
                pending_chapter = chapter_match.group(1)
                continue

            subfile_match = re.match(r'\\subfile\{tex-processed/(.+?)-book\}', stripped)
            if subfile_match and pending_chapter is not None:
                filename = subfile_match.group(1) + '.html'
                current_chapters.append((pending_chapter, filename))
                pending_chapter = None

    if current_part is not None:
        parts.append((current_part, current_chapters))

    return parts


def render_html(parts: list[tuple[str, list[tuple[str, str]]]]) -> str:
    sections_html = []
    for part_title, chapters in parts:
        if not chapters:
            continue
        items = '\n'.join(
            f'    <li><a href="{fname}">{title}</a></li>'
            for title, fname in chapters
        )
        sections_html.append(f'  <h2>{part_title}</h2>\n  <ul>\n{items}\n  </ul>')

    sections = '\n\n'.join(sections_html)

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="google-site-verification" content="QctZ7qyz-itg4QVvR-ZmZjWuTyH3ApL4i8szOfiLaCs" />
  <title>Molecular Nutrition Notes</title>
  <link rel="stylesheet" href="tufte.css">
  <style>
    body {{ max-width: 900px; margin: 2rem auto; padding: 2rem; font-family: serif; }}
    h1, h2, h3 {{ font-weight: normal; }}
    ul {{ list-style-type: none; padding-left: 1em; }}
    li::before {{ content: "→ "; color: #999; }}
    footer {{ margin-top: 4rem; font-size: 0.9em; color: #555; border-top: 1px solid #ccc; padding-top: 1rem; }}
  </style>
</head>
<body>
  <h1>Molecular Nutrition</h1>
  <p><strong>Authors:</strong> Dave Bridges, Ph.D. and Olivia Anderson, MPH, R.D., Ph.D.</p>
  <p><a href="https://sph.umich.edu/ns/" style="color:inherit;text-decoration:none;">Department of Nutritional Sciences, University of Michigan School of Public Health</a></p>

{sections}

  <footer>
    <p>Licensed under the <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License (CC BY 4.0)</a>.</p>
    <p>Last updated: <span id="date"></span></p>
    <p>This site is open source; suggestions and improvements can be made via <a href="https://github.com/BridgesLab/MolecularNutrition/">GitHub</a>.</p>
  </footer>

  <script>
    document.getElementById("date").textContent = new Date().toISOString().split('T')[0];
  </script>
</body>
</html>
"""


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "output" / "index.html"
    tex_path = REPO_ROOT / "nutr630-notes.tex"

    parts = parse_book_structure(tex_path)
    if not parts:
        print("ERROR: No parts/chapters found — check nutr630-notes.tex path", file=sys.stderr)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_html(parts))
    print(f"Generated {out_path} ({sum(len(c) for _, c in parts)} chapters across {len(parts)} parts)")


if __name__ == "__main__":
    main()
