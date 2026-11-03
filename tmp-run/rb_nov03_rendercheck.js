// Sec. 6c, 15 okt 2026 — de rendercontrole die een volgende run bij een onbereikbaar dagrapport
// EERST moet draaien in plaats van de diagnose over te doen. Chromium staat voorgeinstalleerd in
// /opt/pw-browsers. Draait hier preventief: als de pagina lokaal volledig rendert zonder fouten,
// dan is een onbereikbare Artifact een probleem van de sandbox-host en is opnieuw publiceren
// zinloos — dan is de Markdown-route het antwoord.
const { chromium } = require('playwright');
const file = process.argv[2];
(async () => {
  const b = await chromium.launch();
  const out = {};
  for (const scheme of ['light', 'dark']) {
    const ctx = await b.newContext({ colorScheme: scheme });
    const p = await ctx.newPage();
    const errs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    p.on('pageerror', e => errs.push(String(e)));
    await p.goto('file://' + file, { waitUntil: 'load' });
    out[scheme] = await p.evaluate(() => ({
      scrollHeight: document.body.scrollHeight,
      textLen: document.body.innerText.length,
      blocks: document.querySelectorAll('h1,h2,p,table,div.bet').length,
      bg: getComputedStyle(document.body).backgroundColor,
      fg: getComputedStyle(document.body).color,
      title: document.title,
      tables: document.querySelectorAll('table').length,
      bets: document.querySelectorAll('div.bet').length,
    }));
    out[scheme].errors = errs;
    await ctx.close();
  }
  await b.close();
  console.log(JSON.stringify(out, null, 1));
})();
