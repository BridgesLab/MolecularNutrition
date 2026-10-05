const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,BorderStyle,AlignmentType,Footer,PageNumber,HeightRule,ShadingType,PageBreak,TabStopType}=require('docx');
const data=JSON.parse(fs.readFileSync(process.argv[2]));
const FONT='Calibri', SZ=22;
// inline markdown: **bold**, *italic*
function runs(t,base={}){
  const out=[]; const re=/(\*\*[^*]+\*\*|\*[^*]+\*)/g; let last=0,m;
  while((m=re.exec(t))){ if(m.index>last) out.push(new TextRun({text:t.slice(last,m.index),font:FONT,size:SZ,...base}));
    const s=m[0]; if(s.startsWith('**')) out.push(new TextRun({text:s.slice(2,-2),bold:true,font:FONT,size:SZ,...base}));
    else out.push(new TextRun({text:s.slice(1,-1),italics:true,font:FONT,size:SZ,...base})); last=m.index+s.length;}
  if(last<t.length) out.push(new TextRun({text:t.slice(last),font:FONT,size:SZ,...base}));
  return out;}
const P=(children,opts={})=>new Paragraph({children,...opts});
const border={style:BorderStyle.SINGLE,size:6,color:'000000'};
const borders={top:border,bottom:border,left:border,right:border};
const W=9360; // 6.5in content width
const body=[];
// ---- Cover page ----
body.push(P([new TextRun({text:'NUTR 630: Principles of Nutritional Science',bold:true,font:FONT,size:32})],{alignment:AlignmentType.CENTER,spacing:{after:80}}));
body.push(P([new TextRun({text:data.title||'Midterm Exam',bold:true,font:FONT,size:28})],{alignment:AlignmentType.CENTER,spacing:{after:400}}));
function field(label){return new TableRow({height:{value:620,rule:HeightRule.ATLEAST},children:[
  new TableCell({width:{size:1800,type:WidthType.DXA},borders,verticalAlign:'center',margins:{left:120},children:[P([new TextRun({text:label,bold:true,font:FONT,size:24})])]}),
  new TableCell({width:{size:W-1800,type:WidthType.DXA},borders,children:[P([])]})]});}
body.push(new Table({width:{size:W,type:WidthType.DXA},columnWidths:[1800,W-1800],rows:[field('UMID')]}));
body.push(P([],{spacing:{after:240}}));
body.push(P([new TextRun({text:'Instructions',bold:true,font:FONT,size:26})],{spacing:{after:120}}));
const saPts=data.SA.map(x=>x.pts); const saTot=saPts.reduce((a,b)=>a+b,0); const mcTot=2*data.MC.length;
const instr=[`You have **${data.minutes||80} minutes** to complete this exam. It is worth ${mcTot+saTot} points total: ${mcTot} points for multiple choice (2 points per question) and ${saTot} points for short answer, with point distributions shown on the questions.`,
 'You may use **one 4 × 6 inch index card** with your own handwritten notes. **No calculators**, phones, or other electronic devices are allowed.',
 '**Part I (Multiple choice):** For each question, **circle the letter** of the single best answer. If a question says “Select all”, circle every correct answer.',
 '**Part II (Short answer):** Write your answers **inside the boxes** provided. Writing outside the boxes may not be graded.',
 'Read each question carefully. If a question seems unclear, ask me or state any assumptions you made to help me grade it.'];
instr.forEach((t,i)=>body.push(P([new TextRun({text:`${i+1}.\t`,font:FONT,size:SZ}),...runs(t)],{tabStops:[{type:TabStopType.LEFT,position:360}],indent:{left:360,hanging:360},spacing:{after:120}})));
body.push(P([],{spacing:{after:240}}));
body.push(P([new PageBreak()]));
// ---- Part I ----
body.push(P([new TextRun({text:'Part I: Multiple Choice (2 points each, circle the letter for the correct answer)',bold:true,font:FONT,size:26})],{spacing:{after:200}}));
data.MC.forEach((q,i)=>{
  body.push(P([new TextRun({text:`${i+1}.\t`,bold:true,font:FONT,size:SZ}),...runs(q.stem)],{keepNext:true,keepLines:true,tabStops:[{type:TabStopType.LEFT,position:440}],indent:{left:440,hanging:440},spacing:{before:160,after:80}}));
  q.opts.forEach((o,j)=>body.push(P([new TextRun({text:`${o.L}.\t`,font:FONT,size:SZ}),...runs(o.t)],{keepNext:j<q.opts.length-1,keepLines:true,tabStops:[{type:TabStopType.LEFT,position:1000}],indent:{left:1000,hanging:400},spacing:{after:60}})));
});
// ---- Part II ----
function box(lines){return new Table({width:{size:W,type:WidthType.DXA},columnWidths:[W],rows:[new TableRow({cantSplit:true,height:{value:lines,rule:HeightRule.EXACT},children:[new TableCell({width:{size:W,type:WidthType.DXA},borders,children:[P([])]})]})]});}
data.SA.forEach((sa,k)=>{
  body.push(P([new PageBreak()]));
  body.push(P([new TextRun({text:`Part II: Short Answer ${k+1} (${sa.pts} points)`,bold:true,font:FONT,size:26})],{spacing:{after:160},keepNext:true}));
  sa.items.forEach((it,idx)=>{
    if(it.type==='para') body.push(P(runs(it.t),{spacing:{after:120},keepNext:true}));
    else if(it.type==='bullet') body.push(P([new TextRun({text:'•\t',font:FONT,size:SZ}),...runs(it.t)],{tabStops:[{type:TabStopType.LEFT,position:720}],indent:{left:720,hanging:360},spacing:{after:80},keepNext:true}));
    else { body.push(P([new TextRun({text:`${it.L}. (${it.pts} points)  `,bold:true,font:FONT,size:SZ}),...runs(it.t)],{spacing:{before:200,after:100},keepNext:true,keepLines:true}));
      body.push(box(2880)); }
  });
});
const doc=new Document({styles:{default:{document:{run:{font:FONT,size:SZ}}}},
 sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:1080,bottom:1080,left:1440,right:1440}}},
  footers:{default:new Footer({children:[P([new TextRun({text:(data.footer||'NUTR 630 Exam')+' — Page ',font:FONT,size:18}),new TextRun({children:[PageNumber.CURRENT],font:FONT,size:18}),new TextRun({text:' of ',font:FONT,size:18}),new TextRun({children:[PageNumber.TOTAL_PAGES],font:FONT,size:18})],{alignment:AlignmentType.CENTER})]})},
  children:body}]});
if(!process.argv[3]){console.error('usage: node build_exam.js exam.json out.docx');process.exit(1)}
Packer.toBuffer(doc).then(b=>{fs.writeFileSync(process.argv[3],b);console.log('ok')});
