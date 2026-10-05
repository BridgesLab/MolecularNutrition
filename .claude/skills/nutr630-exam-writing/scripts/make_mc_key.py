#!/usr/bin/env python3
"""Make a Gradescope MC key from the FINAL student .docx (including the instructor's hand edits).

Copies the exam .docx and adds a small red "→" in the left margin of each correct option,
without changing line wrapping or pagination:
  - the option paragraph's hanging indent grows 400 -> 800 (first line starts further left),
  - a tab stop at 600 keeps the option letter aligned with the other options,
  - the arrow uses Calibri (a fallback font for fancier arrows changes line height and shifts pages).
Short-answer boxes are left blank.

Usage: make_mc_key.py exam.docx exam.json key.docx
  exam.json = output of parse_draft.py, in exam order (supplies the correct letters and the text used to verify them).
Verify afterwards with render_check.sh: same page count, and identical text per page once the arrows are removed.
"""
import json, re, sys, zipfile, shutil, os, tempfile

src, jpath, out = sys.argv[1:4]
MC = json.load(open(jpath))["MC"]
correct = {i + 1: [o for o in q["opts"] if o["c"]] for i, q in enumerate(MC)}
norm = lambda s: re.sub(r"[\s*]", "", s)
text = lambda p: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))

tmp = tempfile.mkdtemp()
with zipfile.ZipFile(src) as z:
    z.extractall(tmp)
docp = os.path.join(tmp, "word", "document.xml")
x = open(docp, encoding="utf-8").read()

ARROW = ('<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:b/>'
         '<w:color w:val="C00000"/><w:sz w:val="22"/></w:rPr><w:t>→</w:t></w:r>'
         '<w:r><w:rPr><w:sz w:val="22"/></w:rPr><w:tab/></w:r>')
out_parts, pos, q, hits = [], 0, None, []
for m in re.finditer(r"<w:p[ >].*?</w:p>", x, flags=re.S):
    p, t = m.group(0), text(m.group(0))
    mq = re.match(r"\s*(\d+)\.", t)
    if mq and 'w:left="440"' in p:          # MC stem paragraph (indent set by build_exam.js)
        q = int(mq.group(1))
    mo = re.match(r"\s*([A-D])\.", t)
    newp = p
    if q and q in correct and mo and 'w:hanging="400"' in p:
        for o in correct[q]:
            if o["L"] == mo.group(1):
                assert norm(o["t"])[:25] == norm(t[2:])[:25], f"Q{q}{o['L']} text mismatch: {t[:60]!r}"
                newp = newp.replace('<w:tab w:val="left" w:pos="1000"/>',
                                    '<w:tab w:val="left" w:pos="600"/><w:tab w:val="left" w:pos="1000"/>', 1)
                newp = newp.replace('w:hanging="400"', 'w:hanging="800"', 1)
                i = newp.index("</w:pPr>") + len("</w:pPr>")
                newp = newp[:i] + ARROW + newp[i:]
                hits.append(f"{q}{o['L']}")
    out_parts += [x[pos:m.start()], newp]; pos = m.end()
out_parts.append(x[pos:])
open(docp, "w", encoding="utf-8").write("".join(out_parts))

expected = sum(len(v) for v in correct.values())
assert len(hits) == expected, f"placed {len(hits)} arrows, expected {expected}"
if os.path.exists(out): os.remove(out)
shutil.make_archive(out[:-5] if out.endswith(".docx") else out, "zip", tmp)
os.replace((out[:-5] if out.endswith(".docx") else out) + ".zip", out)
print(f"{len(hits)} arrows placed: {' '.join(hits)}")
