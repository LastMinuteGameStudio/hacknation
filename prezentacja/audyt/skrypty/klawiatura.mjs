import { chromium } from "playwright";
const [S, PRZ, KRO] = process.argv.slice(2);
const BASE = "http://localhost:4173";
const b = await chromium.launch();
if (0) // 1) mapowanie z długimi przykładami
for (const w of []) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  await p.goto(BASE); await p.click("text=Zacznij"); await p.fill("#d-nazwa", "Przemyśl"); await p.selectOption("#d-typ", "jst");
  await p.click("text=Dalej: dane"); await p.setInputFiles("#plik", PRZ); await p.click("button:has-text('Wgraj plik')");
  await p.waitForSelector("table.mapowanie");
  const sel = await p.$$eval("table.mapowanie select", (els) => els.map((e) => Math.round(e.getBoundingClientRect().width)));
  const tab = await p.$eval(".tabela-przewijana", (e) => ({ sw: e.scrollWidth, cw: e.clientWidth }));
  const doc = await p.evaluate(() => document.documentElement.scrollWidth);
  const wys = await p.$$eval(".przyklad-wartosc", (els) => Math.max(...els.map((e) => Math.round(e.getBoundingClientRect().height))));
  console.log(`[${w}] przemysl: select min ${Math.min(...sel)} px | tabela ${tab.sw}/${tab.cw} | strona ${doc} | najwyższy przykład ${wys} px`);
  await p.locator("table.mapowanie").screenshot({ path: `${S}/audyt/mapowanie-przemysl-${w}.png` });
  await p.close();
}
// 2) klawiatura
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
const fokus = () => p.evaluate(() => {
  const e = document.activeElement; const cs = getComputedStyle(e);
  const widoczny = (cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) >= 2) || cs.boxShadow !== "none";
  return { el: `${e.tagName.toLowerCase()}${e.id ? "#" + e.id : ""} "${(e.textContent || e.value || "").trim().slice(0, 28)}"`, widoczny, y: Math.round(e.getBoundingClientRect().top + scrollY) };
});
async function tabuj(n, nazwa) {
  const seq = []; let niewidoczne = 0, cofniecia = 0, prevY = -1;
  for (let i = 0; i < n; i++) { await p.keyboard.press("Tab"); const f = await fokus(); if (f.el.startsWith("body")) break; seq.push(f.el); if (!f.widoczny) niewidoczne++; if (f.y < prevY - 5) cofniecia++; prevY = f.y; }
  console.log(`TAB ${nazwa}: ${seq.length} elementów, bez widocznego fokusu: ${niewidoczne}, skoki w górę: ${cofniecia}\n   ${seq.join(" → ")}`);
}
await p.goto(BASE);
await p.keyboard.press("Tab"); console.log("1. Tab:", (await fokus()).el, "| widoczny:", (await fokus()).widoczny);
await p.keyboard.press("Enter"); await p.waitForTimeout(200); console.log("   Enter na skip link → hash:", await p.evaluate(() => location.hash));
await p.goto(BASE); await tabuj(15, "start");
await p.locator("button:has-text('Zacznij')").focus(); await p.keyboard.press("Enter"); await p.waitForTimeout(300);
console.log("po Zacznij (Enter) fokus:", (await fokus()).el);
await tabuj(10, "krok 1");
await p.locator("button:has-text('Dalej: dane')").focus(); await p.keyboard.press("Enter"); await p.waitForTimeout(200);
const f1 = await fokus(); console.log("pusty formularz → fokus:", f1.el, "| aria-invalid:", await p.getAttribute("#d-nazwa", "aria-invalid"));
await p.keyboard.type("Urząd Miasta Krosna"); await p.keyboard.press("Tab"); await p.keyboard.press("Tab"); // telefon? nie: select typ
const tf = await fokus(); console.log("po 2×Tab z nazwy:", tf.el);
await p.selectOption("#d-typ", "jst"); // natywny select: obsługa klawiaturą po stronie systemu
await p.focus("button:has-text('Dalej: dane')"); await p.keyboard.press("Enter"); await p.waitForTimeout(300);
console.log("krok 2 fokus:", (await fokus()).el);
await p.setInputFiles("#plik", KRO); await p.focus("button:has-text('Wgraj plik')"); await p.keyboard.press("Enter");
await p.waitForSelector("table.mapowanie"); await p.waitForTimeout(300);
console.log("po wgraniu fokus:", (await fokus()).el);
await tabuj(25, "krok 2 (mapowanie)");
await p.focus("button:has-text('Sprawdź dane')"); await p.keyboard.press("Enter");
await p.waitForFunction(() => document.body.innerText.includes("Wynik sprawdzenia")); await p.waitForTimeout(400);
console.log("po sprawdzeniu fokus:", (await fokus()).el);
for (const [id, v] of [["stala-wewnatrz_budynku", "true"], ["stala-dostepnosc", "publiczny"], ["stala-dostepny_24_7", "nie"]]) await p.selectOption("#" + id, v);
await p.focus("button:has-text('Sprawdź ponownie')"); await p.keyboard.press("Enter"); await p.waitForTimeout(1500);
await p.focus("button:has-text('Dalej: publikacja')"); await p.keyboard.press("Enter"); await p.waitForTimeout(300);
console.log("krok 3 fokus:", (await fokus()).el);
await tabuj(6, "krok 3");
await p.focus("#zgoda-cc0"); await p.keyboard.press("Space"); console.log("CC0 spacją:", await p.isChecked("#zgoda-cc0"));
await p.focus("button:has-text('Opublikuj')"); await p.keyboard.press("Enter"); await p.waitForSelector("text=Dane opublikowane"); await p.waitForTimeout(300);
console.log("po publikacji fokus:", (await fokus()).el);
await tabuj(12, "opublikowane");
await p.focus("button:has-text('Kopiuj')"); await p.keyboard.press("Enter"); await p.waitForTimeout(300);
console.log("Kopiuj (Enter) status:", await p.locator("[role=status]").first().innerText());
await b.close();
