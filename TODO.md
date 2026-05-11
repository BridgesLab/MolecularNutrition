# NUTR630 Notes Review — TODO

Pedagogical-structure and accessibility review of the MolecularNutrition teaching notes.

This file is **synced with the Notion database** [NUTR630 Notes Review 2026](https://www.notion.so/6b1d601c42df42f8b0314c1b29d2269a) and mapped to the [GitHub issue tracker](https://github.com/BridgesLab/MolecularNutrition/issues). Each row carries a stable `Item ID`; update both surfaces together.

_Last audit: 2026-05-06 against `tex/*.tex` (23 chapters, 53 `\includegraphics`, 5 with `\alttext`)._

## Pedagogy

- [ ] **PED-01 — Add Learning Objectives to `endocrine-handout`** _(Medium · [#7](https://github.com/BridgesLab/MolecularNutrition/issues/7))_
  - Only chapter without an objectives section; opens with "Key Terms and Concepts" instead.
  - Action: insert `\section{Learning Objectives}` after `\maketitle` (4–6 items covering insulin/glucagon signaling, counterregulatory hormones, T2DM, endocrine control of protein/lipid metabolism). Model on `metabolic-control-systems.tex`.
  - [Notion](https://www.notion.so/358711ec4bd98163a35ad96395af463e)

- [ ] **PED-02 — Add Reflection Questions to `nitrogen-compounds`** _(High · [#8](https://github.com/BridgesLab/MolecularNutrition/issues/8), [#13](https://github.com/BridgesLab/MolecularNutrition/issues/13))_
  - Only chapter without a Reflection Questions section.
  - Action: 3–5 items at end of chapter, before bibliography. Mirror format from `protein-oxidation.tex`. Topics: GSH redox, creatine for high-intensity exercise, choline/one-carbon flux, neurotransmitter precursor competition.
  - [Notion](https://www.notion.so/358711ec4bd98185b2c6ef9b6e5a87ce)

- [ ] **PED-03 — Add Protein/Nitrogen Unit Integration Questions** _(High · [#8](https://github.com/BridgesLab/MolecularNutrition/issues/8), [#13](https://github.com/BridgesLab/MolecularNutrition/issues/13))_
  - Carbs and Lipids each end with unit-level integration sets (in `gluconeogenesis.tex` and `lipid-transport.tex`); Protein/Nitrogen has none.
  - Action: add `\section{Protein and Nitrogen Unit Integration Questions}` to the last chapter (`nitrogen-compounds.tex`), 4–6 capstone scenarios spanning digestion → AA pool → synthesis vs. breakdown → urea cycle → NPN compounds. Consider whether a final cross-macronutrient capstone belongs here or as a stand-alone wrap chapter.
  - [Notion](https://www.notion.so/358711ec4bd981c193efc158b419cd81)

- [ ] **PED-04 — Expand `nitrogen-compounds`: heme, polyamines, BH4, neurotransmitter biosynthesis** _(High · [#8](https://github.com/BridgesLab/MolecularNutrition/issues/8))_
  - Shortest chapter (110 lines, 7 sections). Currently covers GSH, carnitine, choline, creatine, and a one-line Neurotransmitter Synthesis section.
  - Missing classes: heme/porphyrins, polyamines (ornithine → putrescine → spermidine/spermine), BH4 cofactor, melanin, melatonin, histamine, GABA, full catecholamine + serotonin biosynthesis, NO from arginine.
  - Action: draft new subsections; add `\index{}` and `\nomenclature{}` entries; pair with figure work (PED-05).
  - [Notion](https://www.notion.so/358711ec4bd9819590dac52a1f2da4c6)

- [ ] **PED-05 — Add figures to Protein/Nitrogen part (currently 0 across 5 chapters)** _(High · [#7](https://github.com/BridgesLab/MolecularNutrition/issues/7), New issue?)_
  - All 5 Part-4 chapters have zero `\includegraphics` calls.
  - Proposed first pass: AA classification + titration curve (`proteins-amino-acids-overview`); brush-border peptidase + PepT1/AA-transporter map (`protein-digestion`); ribosome / leucine-mTORC1 (`proteins-amino-acids-synthesis`); urea cycle + glucogenic vs. ketogenic AA fates + Cahill cycle (`protein-oxidation`); heme biosynthesis + polyamine pathway + catecholamine chain (`nitrogen-compounds`).
  - `tex/figures/cahill-cycle.pdf` and `tex/figures/asparagine-oxidation.pdf` already exist — wire them in before commissioning new artwork.
  - [Notion](https://www.notion.so/358711ec4bd981178a68eefc017d8258)

- [ ] **PED-06 — Expand figure coverage in Lipid part (most chapters 0–1 figures)** _(Medium · [#7](https://github.com/BridgesLab/MolecularNutrition/issues/7), New issue?)_
  - `lipid-synthesis` 0; `lipids-introduction`, `lipid-digestion`, `lipid-catabolism`, `lipid-transport` each 1.
  - Proposed: lipid-class structures, pancreatic lipase + bile-salt micelle, SREBP1c/ChREBP regulation, β-oxidation cycle + CPTI/II, lipoprotein composition wheel.
  - Reuse `Angptl4-PPARa.pdf` and `fatty-acid-oxidation.png` if not already wired in.
  - [Notion](https://www.notion.so/358711ec4bd981fab1cecc633e11aa45)

- [ ] **PED-07 — Standardize reflection-question count across chapters (3–5)** _(Low · [#13](https://github.com/BridgesLab/MolecularNutrition/issues/13))_
  - 21 chapters at 3 each; `carb-digestion` and `lipid-digestion` at 4; `microbiome` at 7.
  - Action: decide between strict 3 baseline or 3–5 range; either trim `microbiome` or document the range in `CONTRIBUTING.md`.
  - [Notion](https://www.notion.so/358711ec4bd9812ab54be8da9fc9f058)

## Accessibility

- [ ] **ACC-01 — Add `\alttext` to 48 figures across 17 chapters** _(High · [#12](https://github.com/BridgesLab/MolecularNutrition/issues/12))_
  - Of 53 `\includegraphics` calls in `tex/*.tex`, only 5 have alt text (all in `microbiome`). `\alttext` is now defined in the master preamble — chapters just need to call it.
  - Per-chapter figure counts (figs / alt-text):
    - `gluconeogenesis` 9/0 — start here
    - `metabolic-control-systems` 6/0
    - `carb-structure` 6/0
    - `glycolysis` 5/0
    - `energy-balance` 4/0
    - `glycogen-metabolism` 4/0
    - `pentose-phosphate-pathway` 3/0
    - `endocrine-handout` 2/0
    - `digestive-tract-introduction` 2/0
    - `carb-digestion` 1/0
    - `tca-cycle` 1/0
    - `lipids-introduction` 1/0
    - `lipid-digestion` 1/0
    - `lipid-catabolism` 1/0
    - `lipid-transport` 1/0
  - Style guidance for alt text: describe the *information conveyed*, not the visual layout.
  - [Notion](https://www.notion.so/358711ec4bd98194b8e3cb25355d1b4a)

- [x] **ACC-02 — Replace 5 placeholder microbiome figures with real images** _(Medium · [#9](https://github.com/BridgesLab/MolecularNutrition/issues/9))_
  - Placeholders: `microbiome-body-sites`, `microbiome-phyla-composition`, `microbiome-16S-workflow`, `microbiome-life-course`, `microbiome-scfa-metabolism`. Alt text is already in place; only artwork is missing.
  - Verify CC-license compatibility for any imported figure before commit.
  - [Notion](https://www.notion.so/358711ec4bd9811fb208dea05595efbd)

- [ ] **ACC-03 — Add `\nomenclature` entries to `digestive-tract-introduction` (currently 0)** _(Medium · [#7](https://github.com/BridgesLab/MolecularNutrition/issues/7))_
  - 45 `\index` entries but 0 `\nomenclature` entries. Candidates: CCK, GIP, GLP-1, GLP-2, PYY, CFTR, MMC, ENS, CNS, ANS, ICC, IF, HCl, NaHCO3.
  - Verify against the bookwide List of Abbreviations to avoid duplicates.
  - [Notion](https://www.notion.so/358711ec4bd9811e97adc93638ee43ff)

- [ ] **ACC-04 — Beef up nomenclature/index in light chapters (`energy-balance`, `protein-digestion`, `proteins-amino-acids-overview`)** _(Low · [#7](https://github.com/BridgesLab/MolecularNutrition/issues/7))_
  - Counts (`\nomenclature` / `\index`): `energy-balance` 7/7, `protein-digestion` 2/11, `proteins-amino-acids-overview` 4/7. For comparison, `pentose-phosphate-pathway` (similar length) is 6/28; `lipid-transport` is 18/50.
  - Suggested abbreviations: RMR, TEF, PAL, NEAT, PYY (`energy-balance`); CCK, ZG, PepT1, NHE3 (`protein-digestion`); BCAA, EAA, NEAA, AA, pI (`proteins-amino-acids-overview`).
  - [Notion](https://www.notion.so/358711ec4bd98159bda7d5cf87e0ff61)

## Notes confirmed clean

- Tufte HTML macro bridge (`\ifdefined\htmlversion` + `\def\newthought` / `\marginnote` / `\sidenote`) is present in **all 23 chapters**.
- Every chapter except `endocrine-handout` (PED-01) and `nitrogen-compounds` (PED-02) has both a Learning Objectives section and a Reflection Questions section.
- Reflection-question coverage is essentially complete (issue [#13](https://github.com/BridgesLab/MolecularNutrition/issues/13)) modulo PED-02 / PED-07.
- Index/abbreviation work from issues [#10](https://github.com/BridgesLab/MolecularNutrition/issues/10) and [#11](https://github.com/BridgesLab/MolecularNutrition/issues/11) is mostly landed; ACC-03 / ACC-04 are residual gaps.

## Out of scope for this audit

The following review dimensions were **not** part of this pass; flag separately if you want to tackle them:

- **Content currency** — re-verifying citations and updating any dated science (e.g., GLP-1 era treatments, microbiome consensus, ApoB-vs-LDL framing).
- **Build/infra hygiene** — committed binary `.pdf`/`.aux`/`.log` artifacts at the repo root and inside `tex/`, dead `tstex_modules/`, missing CI triggers on `scripts/`, `.gitignore` tightening.
