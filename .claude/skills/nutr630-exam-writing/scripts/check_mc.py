#!/usr/bin/env python3
"""Check MC items in an exam draft for answer-length cues and letter balance.

Usage: check_mc.py draft.md

Reports, for questions whose longest option is >= 30 characters:
  - the rank of the correct answer by length (1 = longest)
  - questions where the correct answer is the longest by a wide margin (> 20% longer than the next option)
Targets: correct answer is longest in roughly 25% of such questions (never ~0% and never >40%),
and no correct answer stands out by length. Letters A-D should each be correct ~25% of the time.
Exits non-zero if the pattern is exploitable.
"""
import re, sys
from collections import Counter

s = open(sys.argv[1]).read()
s = s[s.index("## Part I"):s.index("## Part II")]
ranks, letters, standouts, n_text = Counter(), Counter(), [], 0
for blk in re.split(r"\n(?=\*\*\d+\.\*\*)", s)[1:]:
    q = int(re.match(r"\*\*(\d+)", blk).group(1))
    opts = [(m.group(1), bool(m.group(2)), len(m.group(3).replace("*", "")))
            for m in re.finditer(r"^- ([A-D])\. (✅ )?(.*)$", blk, re.M)]
    for L, c, _ in opts:
        if c:
            letters[L] += 1
    lens = sorted((o[2] for o in opts), reverse=True)
    if lens[0] < 30:
        continue
    n_text += 1
    for L, c, ln in opts:
        if c:
            r = lens.index(ln) + 1
            ranks[r] += 1
            others = [o[2] for o in opts if o[0] != L]
            if ln > 1.2 * max(others):
                standouts.append(f"Q{q}{L} ({ln} vs {max(others)} chars)")

print(f"Sentence-length questions: {n_text}")
print("Correct-answer length rank (1=longest):", dict(sorted(ranks.items())))
print("Correct letters:", dict(sorted(letters.items())))
frac = ranks[1] / n_text if n_text else 0
problems = []
if frac > 0.4: problems.append(f"correct answer is longest in {frac:.0%} of questions (target ~25%)")
if n_text >= 8 and frac < 0.1: problems.append(f"correct answer is almost never longest ({frac:.0%}); that is its own cue")
if standouts: problems.append("correct answer much longer than every distractor: " + ", ".join(standouts))
if letters and max(letters.values()) - min(letters.get(x, 0) for x in "ABCD") > 3:
    problems.append("correct letters are unbalanced")
print("\n".join("PROBLEM: " + p for p in problems) or "OK: no length or letter cues detected")
sys.exit(1 if problems else 0)
