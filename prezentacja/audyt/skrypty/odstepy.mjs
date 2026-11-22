import { chromium } from "playwright";
const [FIX] = process.argv.slice(2);
const CSS = "* { line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important; } p { margin-bottom: 2em !important; }";
const b = await chromium.launch();
for (const w of [320, 1440]) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  const spr = async (n) => { await p.addStyleTag({ content: CSS }); const r = await p.evaluate(() => { const ucięte = []; for (const e of document.querySelectorAll("button,label,a,h1,h2,h3,p,li,td,select,legend,span.pewnosc")) { if (e.closest(".tabela-przewijana") && e.tagName !== "SELECT") continue; if (e.classList.contains("przyklad-wartosc") || e.classList.contains("wizualnie-ukryte") || e.closest(".wizualnie-ukryte")) continue; if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== "visible" && e.tagName !== "SELECT") ucięte.push(e.tagName + ":" + e.textContent.trim().slice(0, 25)); } return { sw: document.documentElement.scrollWidth, ucięte }; }); console.log(`[${w}] ${n}: strona ${r.sw}px, ucięte: ${r.ucięte.length ? r.ucięte.join("; ") : "0"}`); };
  await p.goto("http://localhost:4173"); await spr("start");
  await p.click("text=Zacznij"); await spr("krok1");
  await p.fill("#d-nazwa", "Urząd Miasta Krosna"); await p.selectOption("#d-typ", "jst"); await p.click("text=Dalej: dane");
  await p.setInputFiles("#plik", FIX); await p.click("button:has-text('Wgraj plik')"); await p.waitForSelector("table.mapowanie"); await spr("krok2");
  await p.close();
}
await b.close();
