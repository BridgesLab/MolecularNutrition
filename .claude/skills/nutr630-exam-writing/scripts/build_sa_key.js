// Build a short-answer rubric key (.docx) from the Part II section of an exam draft.
// Usage: node build_sa_key.js draft.md out.docx "Title" firstGradescopeQ ["Footer text"]
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType, Footer, PageNumber, BorderStyle } = require('docx');
const [, , draftPath, outPath, title, firstQ, footer] = process.argv;
const FONT = 'Calibri', SZ = 22;

function runs(t, base = {}) {
  const out = []; const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g; let last = 0, m;
  while ((m = re.exec(t))) {
    if (m.index > last) out.push(new TextRun({ text: t.slice(last, m.index), font: FONT, size: SZ, ...base }));
    const s = m[0];
    if (s.startsWith('**')) out.push(new TextRun({ text: s.slice(2, -2), bold: true, font: FONT, size: SZ, ...base }));
    else out.push(new TextRun({ text: s.slice(1, -1), italics: !base.italics, font: FONT, size: SZ, ...base, ...(base.italics ? { italics: false } : {}) }));
    last = m.index + s.length;
  }
  if (last < t.length) out.push(new TextRun({ text: t.slice(last), font: FONT, size: SZ, ...base }));
  return out;
}
const P = (children, opts = {}) => new Paragraph({ children, spacing: { after: 100 }, ...opts });

const md = fs.readFileSync(draftPath, 'utf8');
const p2 = md.split('## Part II')[1];
const rule = (p2.match(/Scoring rule[^\n]*/) || [''])[0];
const sections = p2.split(/\n(?=### )/).slice(1);

const body = [];
body.push(P([new TextRun({ text: title, bold: true, font: FONT, size: 32 })], { alignment: AlignmentType.CENTER, spacing: { after: 80 } }));
body.push(P([new TextRun({ text: 'Instructor key — not for distribution', italics: true, font: FONT, size: SZ, color: 'C00000' })], { alignment: AlignmentType.CENTER, spacing: { after: 240 } }));
if (rule) body.push(P(runs(rule)));
body.push(P(runs('Each key idea is worth 1 point. Point values for each part are shown in the heading; tags show [lecture | Bloom level].'), { spacing: { after: 240 } }));

let q = parseInt(firstQ || '26', 10);
sections.forEach((sec, si) => {
  const lines = sec.split('\n');
  const head = lines[0].replace(/^###\s*/, '');
  body.push(P([new TextRun({ text: `${head}  —  Gradescope Q${q}`, bold: true, font: FONT, size: 28 })],
    { pageBreakBefore: si > 0, spacing: { before: 120, after: 120 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '808080', space: 2 } } }));
  let i = 1;
  // vignette: lines until first part
  const vign = [];
  while (i < lines.length && !/^\*\*[a-z]\. \(/.test(lines[i])) { if (lines[i].trim()) vign.push(lines[i].trim()); i++; }
  vign.forEach(v => body.push(P(runs(v), { spacing: { after: 160 } })));
  for (; i < lines.length; i++) {
    const l = lines[i];
    const mp = l.match(/^\*\*([a-z])\. \((\d+) points?\)\*\*\s*(.*?)\s*(\[[^\]]*\])?\s*$/);
    if (mp) {
      body.push(P([new TextRun({ text: `${mp[1]}. (${mp[2]} point${mp[2] === '1' ? '' : 's'})  `, bold: true, font: FONT, size: SZ }), ...runs(mp[3]),
        ...(mp[4] ? [new TextRun({ text: '  ' + mp[4], font: FONT, size: 18, color: '666666' })] : [])], { spacing: { before: 200, after: 80 } }));
      continue;
    }
    if (l.startsWith('>')) {
      let t = l.replace(/^>\s*/, '').trim();
      if (!t) continue;
      const note = /^\*[^*].*\*$/.test(t);
      if (note) { body.push(P(runs(t.slice(1, -1), { italics: true, color: '444444' }), { indent: { left: 360 } })); continue; }
      t = t.replace(/^Key ideas[^:]*:\s*/, '');
      const parts = t.split(/\s*(?=\(\d+\)\s)/).filter(x => x.trim());
      if (parts.length > 1 || /^\(\d+\)/.test(parts[0] || '')) {
        parts.forEach(pt => {
          const mm = pt.match(/^\((\d+)\)\s*(.*)$/s);
          if (mm) body.push(P([new TextRun({ text: `Key idea ${mm[1]} (1 pt):  `, bold: true, font: FONT, size: SZ, color: '1F4E79' }), ...runs(mm[2].trim())], { indent: { left: 360 } }));
          else body.push(P(runs(pt.trim()), { indent: { left: 360 } }));
        });
      } else body.push(P(runs(t), { indent: { left: 360 } }));
    }
  }
  q++;
});

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: `${footer || title} — Page `, font: FONT, size: 18 }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 }),
      new TextRun({ text: ' of ', font: FONT, size: 18 }),
      new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 18 })] })] }) },
    children: body
  }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(outPath, b); console.log('wrote', outPath); });
