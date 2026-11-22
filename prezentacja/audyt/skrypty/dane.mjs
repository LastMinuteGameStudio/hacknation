import { chromium } from "playwright";
import fs from "fs";
import { createRequire } from "module";
const S = process.argv[2];
const AXE = fs.readFileSync(createRequire(import.meta.url).resolve("axe-core/axe.min.js"), "utf8");
const TAGI = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"];
const b = await chromium.launch();
const axe = async (p, n) => { await p.evaluate(AXE); const v = await p.evaluate((t) => axe.run(document, { runOnly: { type: "tag", values: t } }).then((r) => r.violations.map((v) => `${v.id}(${v.impact},${v.nodes.length}: ${v.nodes.slice(0, 2).map((x) => x.target.join(" ")).join(" | ")})`)), TAGI); console.log(`   axe ${n}: ${v.length ? v.join("; ") : "0"}`); return v.length; };
const male = (p) => p.evaluate(() => [...document.querySelectorAll("a[href],button,input,select,summary")].filter((e) => { const r = e.getBoundingClientRect(); if (!r.width) return false; const inline = e.tagName === "A" && getComputedStyle(e).display === "inline" && /\S/.test(e.parentElement.textContent.replace(e.textContent, "")); return (r.width < 24 || r.height < 24) && !inline; }).map((e) => e.tagName + ":" + e.textContent.trim().slice(0, 20) + ` ${Math.round(e.getBoundingClientRect().width)}x${Math.round(e.getBoundingClientRect().height)}`));
const stan = (p) => p.locator("#wyniki-naglowek + p").innerText();
const czekaj = (p, re) => p.waitForFunction((r) => new RegExp(r).test(document.querySelector("#wyniki-naglowek + p")?.textContent ?? ""), re.source, { timeout: 60000 });
for (const w of [320, 768, 1440]) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  const bledy = []; p.on("pageerror", (e) => bledy.push(e.message));
  await p.goto("http://localhost:4173/dane");
  await czekaj(p, /Znaleziono/);
  await p.waitForSelector(".tabela-zbiory");
  console.log(`[${w}] ${await p.title()} | zbiory: ${await p.locator("#zbiory-naglowek ~ p[role=status]").innerText()} | ${await stan(p)} | strona: ${await p.evaluate(() => document.documentElement.scrollWidth)} | <24px: ${(await male(p)).join("; ") || 0}`);
  await axe(p, "start");
  await p.screenshot({ path: `${S}/audyt/dane-${w}.png`, fullPage: false });
  if (w === 1440 || w === 320) {
    await p.fill("#f-szukaj", "krosno jasna"); await czekaj(p, /Znaleziono \d+ AED\.$/);
    console.log("   szukaj 'krosno jasna':", await stan(p), "|", await p.locator(".tabela-aed tbody tr").first().innerText().then((t) => t.replace(/\s+/g, " ").slice(0, 120)));
    await p.fill("#f-szukaj", "lodz piotrkowska"); await p.waitForTimeout(600); console.log("   szukaj 'lodz piotrkowska' (bez ogonków):", await stan(p));
    await p.fill("#f-szukaj", ""); await p.selectOption("#f-zrodlo", "kat:tuaed"); await p.waitForTimeout(600); console.log("   źródło TuAED:", await stan(p));
    await p.selectOption("#f-dostepnosc", "publiczny"); await p.selectOption("#f-d247", "nie"); await p.waitForTimeout(300); console.log("   + publiczny + nie 24/7:", await stan(p));
    await p.click("text=Wyczyść filtry"); await p.waitForTimeout(600); console.log("   po wyczyszczeniu:", await stan(p));
    await p.selectOption("#f-status", "oczekuje"); await p.waitForTimeout(300); console.log("   status oczekuje:", await stan(p)); await p.selectOption("#f-status", "");
    await p.waitForTimeout(300);
    await p.click("button:has-text('Następna')"); await p.waitForTimeout(300);
    console.log("   po 'Następna':", await stan(p), "| fokus:", await p.evaluate(() => document.activeElement.id));
    await axe(p, "po filtrach i stronicowaniu");
    if (w === 320) await p.screenshot({ path: `${S}/audyt/dane-karty-320.png`, fullPage: false });
    // klik w nazwę → mapa
    await p.fill("#f-szukaj", "krosno jasna"); await czekaj(p, /Znaleziono \d+ AED\.$/);
    const link = p.locator(".tabela-aed tbody tr th a").first(); const nazwa = await link.innerText(); const href = await link.getAttribute("href");
    await link.click(); await p.waitForURL(/\/mapa\?aed=/);
    await p.waitForSelector(".popup-aed", { timeout: 60000 });
    console.log(`   klik '${nazwa}' → ${href} | ramka: ${await p.locator(".ramka").first().innerText()} | popup: ${(await p.locator(".popup-aed h2").innerText())} | fokus: ${await p.evaluate(() => document.activeElement.className)}`);
    await axe(p, "mapa z wybranym AED");
    if (w === 1440) await p.screenshot({ path: `${S}/audyt/mapa-wybrany-1440.png` });
    await p.goto("http://localhost:4173/mapa?aed=nie-ma-takiego"); await p.waitForSelector(".ramka-ostrzezenie", { timeout: 60000 }); console.log("   zły aed:", (await p.locator(".ramka-ostrzezenie").innerText()).slice(0, 60));
  }
  console.log("   błędy JS:", bledy);
  await p.close();
}
await b.close();
