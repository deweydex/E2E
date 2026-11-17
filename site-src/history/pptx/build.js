const pptxgen=require('pptxgenjs');const fs=require('fs');
(async()=>{
for (const [name,title] of [['web','How the Web Learned to Respond'],['server','Behind the Page']]) {
  const meta=JSON.parse(fs.readFileSync(`${name}/meta.json`));
  const pres=new pptxgen(); pres.layout='LAYOUT_16x9'; pres.title=title;
  meta.forEach((m,i)=>{
    const s=pres.addSlide();
    s.addImage({path:`${name}/${String(i+1).padStart(2,'0')}.png`,x:0,y:0,w:10,h:5.625,altText:m.title});
    if(m.notes) s.addNotes(m.notes);
  });
  const file = name==='web' ? 'how-the-web-learned-to-respond.pptx' : 'behind-the-page.pptx';
  await pres.writeFile({fileName:file}); console.log(file, meta.length);
}})();
