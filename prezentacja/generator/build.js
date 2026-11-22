const pptxgen = require('pptxgenjs');
const fs = require('fs');
const spec = JSON.parse(fs.readFileSync('spec.json'));
const imgs = JSON.parse(fs.readFileSync('images.json'));
const imap = JSON.parse(fs.readFileSync('imgmap.json'));
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.title = 'AEDane – Misja AED (HackNation 2026)';
pres.theme = { headFontFace: 'Noto Sans', bodyFontFace: 'Noto Sans' };
const hx = c => c.replace('#','').toUpperCase();
for (const sl of spec.slides) {
  const s = pres.addSlide();
  s.background = { color: 'FFFFFF' };
  for (const el of sl.elements) {
    const pos = { x: el.x, y: el.y, w: el.w, h: el.h, objectName: el.id };
    if (el.type === 'rect' || el.type === 'round_rect') {
      s.addShape(el.type === 'rect' ? pres.shapes.RECTANGLE : pres.shapes.ROUNDED_RECTANGLE,
        { ...pos, fill: { color: hx(el.fill) }, line: { type: 'none' }, ...(el.type==='round_rect'?{rectRadius:0.12}:{}) });
    } else if (el.type === 'text') {
      const base = { fontFace: 'Noto Sans', fontSize: el.size, bold: !!el.bold, color: hx(el.color||'#101820'),
                     align: (el.align||'START')==='START'?'left':el.align.toLowerCase(), valign: 'top', margin: 6 };
      if (el.bullets || el.space_below) {
        const lines = el.text.split('\n');
        const runs = lines.map((t,i) => ({ text: t, options: { bullet: !!el.bullets, paraSpaceAfter: el.space_below||0, ...(i<lines.length-1?{breakLine:true}:{}) } }));
        s.addText(runs, { ...pos, ...base, isTextBox: true });
      } else {
        s.addText(el.text, { ...pos, ...base, isTextBox: true });
      }
    } else if (el.type === 'table') {
      const rows = el.rows.map((r,ri) => r.map((c,ci) => ({ text: c, options: {
        bold: ri===0 || ci===0, fontFace: 'Noto Sans', fontSize: el.size, color: '101820', valign: 'middle',
        border: [{type:'none'},{type:'none'},{ pt: ri===0?1.5:0.75, color: ri===0?'5F6B66':'D1E0D7' },{type:'none'}],
        margin: [4,6,4,6] } })));
      s.addTable(rows, { x: el.x, y: el.y, w: el.w, colW: el.col_widths, rowH: 0.42 });
    }
  }
  const key = 's' + sl.id.slice(3);
  for (const [oid, url, x, y, w, h] of (imgs[key]||[])) {
    s.addImage({ path: imap[oid], x, y, w, h, objectName: oid, altText: oid });
  }
}
pres.writeFile({ fileName: 'AEDane-Misja-AED.pptx' }).then(f => console.log('zapisano', f));
