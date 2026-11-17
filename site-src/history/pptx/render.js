const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();
for (const name of ['web','server']) {
  fs.mkdirSync(name,{recursive:true});
  const p=await b.newPage({viewport:{width:1920,height:1080}});
  await p.goto(`http://localhost:8765/docs/history/${name}/slides.html`);
  await p.evaluate(()=>document.fonts.ready);
  const meta=await p.evaluate(()=>{
    const secs=[...document.querySelectorAll('.stage>section')];
    const m=secs.map(s=>({id:s.id,title:((s.querySelector('h1,h2')||{}).textContent||s.id).trim(),notes:((s.querySelector('aside')||{}).textContent||'').trim()}));
    window.__secs=secs.map(s=>s.outerHTML);
    document.querySelector('.bar').remove();document.querySelector('.notes').remove();
    document.body.style.display='block';
    document.querySelector('.stage-wrap').outerHTML='<div class="stage" id="one" style="position:absolute;left:0;top:0;transform:none"></div>';
    return m;});
  for(let i=0;i<meta.length;i++){
    await p.evaluate(i=>{const one=document.getElementById('one');one.innerHTML=window.__secs[i];one.firstElementChild.classList.add('on');},i);
    await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(100);
    await p.screenshot({path:`${name}/${String(i+1).padStart(2,'0')}.png`});
  }
  fs.writeFileSync(`${name}/meta.json`,JSON.stringify(meta));
  console.log(name,meta.length);
}
await b.close();})();
