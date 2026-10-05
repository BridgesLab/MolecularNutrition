#!/usr/bin/env python3
"""Parse an exam draft markdown file into JSON for build_exam.js.

Draft format (see SKILL.md):
  ## Part I ... ## Part II   (MC section)
  **N.** [tags] stem          (one line; an optional second line starting with "(" is joined to the stem)
  - A. ✅ option              (✅ marks correct; more than one allowed for "Select all")
  ### Short Answer K (P pts)  (SA section; parts "**a. (2 points)** prompt"; lines starting ">" are key-only)

Usage: parse_draft.py draft.md out.json [--order 5,15,3,...] [--title "..."] [--footer "..."]
"""
import json, re, sys, argparse

ap = argparse.ArgumentParser()
ap.add_argument("draft"); ap.add_argument("out")
ap.add_argument("--order", help="comma-separated draft numbers in exam order")
ap.add_argument("--title", default="Midterm Exam"); ap.add_argument("--footer", default="NUTR 630 Exam")
a = ap.parse_args()

s = open(a.draft).read()
p1 = s[s.index("## Part I"):s.index("## Part II")]
mc = {}
for blk in re.split(r"\n(?=\*\*\d+\.\*\*)", p1)[1:]:
    lines = [l for l in blk.strip().split("\n") if l.strip()]
    m = re.match(r"\*\*(\d+)\.\*\*\s*(?:\[[^\]]*\]\s*)?(.*)", lines[0])
    n, stem = int(m.group(1)), m.group(2)
    opts = []
    for l in lines[1:]:
        mo = re.match(r"- ([A-D])\. (✅ )?(.*)", l)
        if mo:
            opts.append({"L": mo.group(1), "t": mo.group(3), "c": bool(mo.group(2))})
        elif l.startswith("(") and not opts:
            stem += " " + l
    assert len(opts) == 4, f"Q{n} has {len(opts)} options"
    assert any(o["c"] for o in opts), f"Q{n} has no correct answer marked"
    mc[n] = {"stem": stem, "opts": opts}

order = [int(x) for x in a.order.split(",")] if a.order else sorted(mc)
assert sorted(order) == sorted(mc), "order must list every MC question exactly once"
MC = [dict(mc[o], old=o) for o in order]

p2 = s[s.index("## Part II"):]
SA = []
for sec in re.split(r"\n(?=### )", p2)[1:]:
    lines = sec.split("\n")
    pts = int(re.search(r"\((\d+) (?:pts|points)\)", lines[0]).group(1))
    items = []
    for l in lines[1:]:
        if not l.strip() or l.startswith(">") or l.startswith("⚠️"):
            continue
        mp = re.match(r"\*\*([a-z])\. \((\d+) (?:pts?|points?)\)\*\*\s*(.*)", l)
        if mp:
            t = re.sub(r"\s*\[[^\]]*\]\s*$", "", mp.group(3))  # strip trailing [tags]
            items.append({"type": "part", "L": mp.group(1), "pts": int(mp.group(2)), "t": t})
        elif l.startswith("- "):
            items.append({"type": "bullet", "t": l[2:]})
        else:
            items.append({"type": "para", "t": l})
    part_sum = sum(i["pts"] for i in items if i["type"] == "part")
    assert part_sum == pts, f"{lines[0]}: parts sum to {part_sum}, header says {pts}"
    SA.append({"pts": pts, "items": items})

json.dump({"title": a.title, "footer": a.footer, "MC": MC, "SA": SA}, open(a.out, "w"), indent=1, ensure_ascii=False)
mc_pts, sa_pts = 2 * len(MC), sum(x["pts"] for x in SA)
print(f"{len(MC)} MC ({mc_pts} pts) + {len(SA)} SA ({sa_pts} pts) = {mc_pts + sa_pts} pts")
for i, q in enumerate(MC, 1):
    print(f"  exam #{i:2d} <- draft #{q['old']:2d}  correct: {','.join(o['L'] for o in q['opts'] if o['c'])}")
