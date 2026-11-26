const {chromium}=require('playwright');
const C=[['manovra-2027','Amendments to Italy’s 2027 budget law','Who asks for money, for which places, and what gets ruled out','6,558 amendments · Chamber of Deputies'],
 ['manovre-2023-2027','Italian budget laws 2023–2027','Every amendment, Chamber and Senate: who asks, where the money would go, what passes','24,977 proposals · five budgets']];
(async()=>{const b=await chromium.launch();
for(const [slug,t,s,k] of C){
 const p=await b.newPage({viewport:{width:1300,height:1000}});
 await p.route('**/d3.min.js',r=>r.fulfill({path:'/tmp/claude-0/libs/node_modules/d3/dist/d3.min.js',contentType:'application/javascript'}));await p.route('**/topojson.min.js',r=>r.fulfill({path:'/tmp/claude-0/libs/node_modules/topojson/dist/topojson.min.js',contentType:'application/javascript'}));
 await p.goto(`http://localhost:8800/projects/${slug}/?lang=it#mappa`);await p.waitForTimeout(7000);
 await p.evaluate(()=>{try{document.documentElement.setAttribute('data-theme','light')}catch(e){}});
 const svg=await p.evaluate(()=>{const s=document.querySelector('#mapsvg');const c=s.cloneNode(true);c.querySelectorAll('text').forEach(x=>x.remove());
   const src=[...s.querySelectorAll('path')];[...c.querySelectorAll('path')].forEach((q,i)=>{const cs=getComputedStyle(src[i]);const fl=(cs.fill.startsWith('url')||cs.fill==='none')&&src[i].classList.contains('pv')?'#e3e6ec':cs.fill;q.setAttribute('style',`fill:${fl};stroke:${cs.stroke};stroke-width:${cs.strokeWidth}`)});
   c.setAttribute('width','100%');c.setAttribute('height','100%');return c.outerHTML});
 const q=await b.newPage({viewport:{width:1200,height:630}});
 await q.setContent(`<html><body style="margin:0;width:1200px;height:630px;background:#f5f6f8;font-family:'DejaVu Sans',Arial,sans-serif;color:#1b2130;display:grid;grid-template-columns:640px 560px;overflow:hidden">
 <div style="padding:56px 24px 48px 64px;display:flex;flex-direction:column;justify-content:space-between">
  <div><div style="font-size:18px;letter-spacing:.08em;text-transform:uppercase;color:#5d6678">Interactive explorer</div>
  <div style="font-size:50px;font-weight:700;line-height:1.08;margin:18px 0 20px">${t}</div>
  <div style="font-size:24px;line-height:1.35;color:#3b4456">${s}</div></div>
  <div style="font-size:20px;color:#5d6678"><b style="color:#1f4f8f">${k}</b><br>Tommaso Landi · landitommaso.github.io</div></div>
 <div style="padding:40px 32px 40px 0;box-sizing:border-box;height:630px">${svg}</div></body></html>`);
 await q.waitForTimeout(500);await q.screenshot({path:`/home/claude/landitommaso.github.io/projects/${slug}/preview.png`});
 await p.close();await q.close();console.log('ok',slug)}
await b.close()})();
