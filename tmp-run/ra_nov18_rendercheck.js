const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  const errs = [];
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file:///home/user/football/runs/2026-11-18-run-a.html', { waitUntil: 'load' });
  const r = await p.evaluate(() => ({
    scrollHeight: document.body.scrollHeight,
    textLen: document.body.innerText.length,
    blocks: document.querySelectorAll('h1,h2,p,table,div.bet').length,
    title: document.title,
  }));
  console.log(JSON.stringify({ ...r, consoleErrors: errs.length, errs: errs.slice(0, 3) }, null, 1));
  await b.close();
})();
