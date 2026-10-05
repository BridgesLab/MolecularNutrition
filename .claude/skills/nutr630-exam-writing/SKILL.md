---
name: nutr630-exam-writing
description: Write NUTR630 exams, quizzes, and make-up versions from course learning objectives, notes, video transcripts, and readings. Produces a coverage blueprint, a reviewable markdown draft with rubrics, a Gradescope-ready Word exam, an arrow-marked MC key, Gradescope tags, and parallel make-up versions. Use when Dave asks to write, revise, or rebalance a midterm, final, quiz, or exam version for NUTR630.
---

# NUTR630 exam writing

Workflow developed for Midterm 1, Fall 2026. The reference example is `exams/midterm1/`: `blueprint.md`, `midterm1-draft.md`, `midterm1-versionB-draft.md`, and the final `.docx` files.

**Exams are private until given.** Write into `exams/<exam>/` in the repo, but never commit or push; Dave pushes after the exam. Keep the skill and scripts free of real exam content.

## Instructor preferences (non-negotiable)

- **Sources = what students were assigned.** That means the custom notes in `tex/*.tex` (Dave calls these "the readings"), the assigned video transcripts in `transcripts/*.vtt`, and the assigned papers. Lecture sessions are for application practice and are *not* a source. Assigned papers are tested only as deep as the lecture's learning objectives go, never on incidental details.
- **Learning objectives drive coverage.** Students are told to use the objectives as their study guide. Try to cover every objective at least once, and list any that are missed. Drop videos that match no objective (e.g., purely definitional ones) unless Dave says otherwise.
- **Proportional across lectures, not across objectives.** Each lecture gets roughly equal points, no matter how many objectives it has.
- **Bloom split: 25% Remember / 50% Understand-Apply / 25% Analyze-Evaluate-Create**, computed on points.
- **Human-health framing.** Use clinical or population vignettes: patients, infants, trials, headlines.
- **No calculators.** Keep arithmetic to round numbers you can do in your head. Giving an equation and asking a comparison (e.g., "which has the higher BMR") is fine.
- **Format:** ~25 MC × 2 pts plus ~25–31 pts of multipart short answer. 80 minutes, with a handwritten 4 × 6 cue card allowed.
- **Short-answer rubrics: 1 point per key idea** in the ideal answer. Part values of 2–3 pts are typical. The key lists the key ideas.
- **Give a floor.** Open multipart short answers with an easy Remember-level part. The first 1–2 MC questions should be very easy recall to build confidence.
- **Cue-card awareness.** Small recall lists can end up on the card. That's acceptable, but prefer asking students to *use* the fact.

## MC item rules

- 4 options, one best answer. **No negatively worded stems** ("which is NOT…"). Use all/none of the above only if unavoidable.
- "Select all" is allowed and Gradescope can accept several answers. Mark every correct option in the key.
- **Answer-length equivalence (required).** The correct option must not be identifiable by length or specificity.
  - Write the correct option with the *same* level of detail as the distractors. Give distractors their own plausible "because…" clauses instead of trimming them to fragments.
  - Aim for the correct option to be the longest in only ~25% of sentence-length items, and never much longer than all distractors. Always-second-longest is also a cue.
  - **Run `scripts/check_mc.py draft.md` before sending any draft or building the docx.** Fix everything it flags.
  - (Midterm 1 Version A shipped with the correct option longest in 20/26 items. Don't repeat this.)
- Balance correct letters (~25% each).
- Distractors should be real misconceptions or near-misses from the same material, not absurd.
- Don't ask students to recall monosaccharide structures, or content the course de-emphasized that year (ask Dave if unsure, e.g., dietary vs functional fiber definitions in 2026).

## Workflow

### 1. Gather scope (ask; don't assume)
- The lectures in the unit, the learning objectives (Dave keeps them in a Google Doc; public docs export via `https://docs.google.com/document/d/<ID>/export?format=txt`), the required videos, and the required readings (PDFs usually arrive as uploads).
- Check memory for the current unit's scope before asking again.
- Convert transcripts to text: strip the VTT headers and timestamps, and de-duplicate repeated caption lines. Extract PDFs with `pdftotext`.
- Read everything before designing questions.

### 2. Blueprint (get approval before writing questions)
`exams/<exam>/blueprint.md` should contain:
- A points-per-lecture table (MC count, SA points, total).
- An MC table: # | lecture | objective | concept + health framing | Bloom | source.
- An SA table per question: part | prompt idea | Bloom | objective | source.
- Bloom totals vs target, objectives not covered, excluded videos.

### 3. Draft in markdown (review loop)
`exams/<exam>/<exam>-draft.md`. The scripts depend on this format:
```
## Part I — Multiple choice
**1.** [Lecture | Bloom | source] Stem text on one line.
- A. Distractor
- B. ✅ Correct option
- C. ...
- D. ...

## Part II — Short answer
### Short Answer 1 (9 pts)
Vignette paragraph(s)...
**a. (2 points)** Prompt text. [Lecture | Bloom]
> Key ideas: (1) ...; (2) ...
```
Lines starting with `>` are key-only and are never printed on the student exam. Mark new or changed items with ⚠️ while Dave reviews, and remove the marks once he approves. Expect several rounds of edits. Dave often hand-edits the draft or the Word file, so **re-read the current file before every change**.

### 4. Order the MC for the exam
- 1–2 very easy Remember items first.
- No two adjacent items from the same lecture.
- Space the Analyze/Evaluate items evenly (e.g., #8, 13, 17, 21, 25).
- Record the exam-order ↔ draft mapping (`mc-order.md`).

### 5. Build the student .docx
```bash
python3 scripts/parse_draft.py draft.md exam.json --order 5,15,3,... --title "Midterm Exam 1 — Fall 2026" --footer "NUTR 630 Midterm 1"
NODE_PATH=<dir with node_modules/docx> node scripts/build_exam.js exam.json exams/<exam>/<name>.docx
```
- `docx` is not globally installed: run `npm install docx` in the scratchpad and point `NODE_PATH` there.
- Layout: US Letter, and a cover page with a **UMID box only** (no name field, no points table), the instructions, and the point total.
- Each MC stem and its options are kept together, so no question splits across pages.
- Each SA question starts on a new page. Every part gets a fixed-height box (Gradescope).
- Footer reads "Page X of Y".

### 6. Verify the layout
```bash
bash scripts/render_check.sh <scratch-outdir> exam.docx        # exports via Microsoft Word; read the page JPGs
```
LibreOffice isn't installed, so rendering goes through Word via AppleScript, with copies staged in `~/Documents/_word_render_tmp`. Check page by page:
- no MC question split across a page
- boxes follow their prompts
- the point totals in the instructions match the parts

### 7. Gradescope MC key (from Dave's FINAL edited .docx)
```bash
python3 scripts/parse_draft.py draft.md exam.json --order ...   # same order as the exam
python3 scripts/make_mc_key.py final-exam.docx exam.json exams/<exam>/<name>-MC-Key.docx
bash scripts/render_check.sh <scratch-outdir> final-exam.docx key.docx   # every page must say "ok"
```
- The key is a copy of the exam with a small red Calibri "→" in the margin beside each correct letter. Short-answer boxes stay blank.
- Spacing must match the exam exactly (Gradescope aligns templates). Never use a fallback-font arrow such as ➜: it changes line height and shifts pages.
- The script verifies each marked option's text against the draft. If Dave reworded options in Word, confirm the mapping manually.

### 8. Gradescope tags
Give Dave a table for each question/part with a lecture tag and a Bloom tag. Use prefixes such as `L: Energy Balance` and `Bloom: Remember`. Tags are added on the assignment's Statistics page ("Click to Add Tags"). Short-answer parts must be separate subquestions in the Gradescope outline to be tagged individually.

### 9. Make-up / alternate versions
- Mirror each item: same position, lecture, objective, Bloom level, points, format, and roughly the same length (to keep pagination).
- Change the content. Avoid near-duplicate vignettes, and vary the theme of each short-answer question from the original (e.g., Version A fiber for LDL → Version B fiber for colon barrier and colorectal cancer).
- Don't let a new MC duplicate the content of a new SA part.
- Tag each item `mirrors A#: topic` in the draft. Run `check_mc.py`. Build and verify it the same way as the original.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/parse_draft.py` | Draft markdown → exam JSON. Checks that each MC has 4 options and a marked answer, and that SA parts sum to the header. Supports `--order`. |
| `scripts/check_mc.py` | Checks answer length and letter balance. Exits non-zero if an exploitable pattern exists. |
| `scripts/build_exam.js` | Exam JSON → student .docx (docx-js). |
| `scripts/make_mc_key.py` | Final exam .docx + JSON → arrow-marked MC key with identical pagination. |
| `scripts/render_check.sh` | Word → PDF → page images, plus a per-page text comparison of exam vs key. |
