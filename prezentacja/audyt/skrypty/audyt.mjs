// Audyt E2: axe-core + Lighthouse (user flow, snapshoty) + szerokości + cele dotyku.
import puppeteer from "puppeteer-core";
import { startFlow } from "lighthouse";
import fs from "fs";
import { createRequire } from "module";
const AXE_SRC = fs.readFileSync(createRequire(import.meta.url).resolve("axe-core/axe.min.js"), "utf8");
const [OUT, FIX, ETAP] = process.argv.slice(2); // ETAP: przed | po
const BASE = "http://localhost:4173";
const CHROME = process.env.HOME + "/Library/Caches/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const TAGI = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
fs.mkdirSync(OUT, { recursive: true });
const wyniki = [];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function stan(page, nazwa, szer) {
  await page.evaluate(AXE_SRC);
  const axe = await page.evaluate((tagi) => window.axe.run(document, { runOnly: { type: "tag", values: tagi }, resultTypes: ["violations"] }).then((r) => ({ violations: r.violations.map((v) => ({ id: v.id, impact: v.impact, tags: v.tags, help: v.help, nodes: v.nodes.map((n) => ({ target: n.target, summary: n.failureSummary })) })) })), [...TAGI, "best-practice"]);
  const wcag = axe.violations.filter((v) => v.tags.some((t) => TAGI.includes(t)));
  const bp = axe.violations.filter((v) => !v.tags.some((t) => TAGI.includes(t)));
  const uklad = await page.evaluate(() => {
    const sw = document.documentElement.scrollWidth, cw = document.documentElement.clientWidth;
    const male = [];
    for (const el of document.querySelectorAll("a[href],button,input,select,textarea,summary,[tabindex]:not([tabindex='-1'])")) {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height || getComputedStyle(el).visibility === "hidden") continue;
      // wyjątek WCAG 2.5.8: link w zdaniu (inline w akapicie/liście tekstowej)
      const inline = el.tagName === "A" && getComputedStyle(el).display === "inline" && el.parentElement && /\S/.test(el.parentElement.textContent.replace(el.textContent, ""));
      if ((r.width < 24 || r.height < 24) && !inline) male.push(`${el.tagName.toLowerCase()}${el.id ? "#" + el.id : ""} "${(el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 30)}" ${Math.round(r.width)}x${Math.round(r.height)}`);
    }
    return { przewijanie: sw > cw, sw, cw, male };
  });
  const w = { ekran: nazwa, szer, wcag: wcag.map((v) => ({ id: v.id, impact: v.impact, n: v.nodes.length, opis: v.help, cele: v.nodes.slice(0, 3).map((n) => n.target.join(" ")) })), bestPractice: bp.map((v) => ({ id: v.id, impact: v.impact, n: v.nodes.length, opis: v.help })), ...uklad };
  wyniki.push(w);
  console.log(`[${szer}] ${nazwa}: WCAG ${wcag.length ? wcag.map((v) => `${v.id}(${v.impact},${v.nodes.length})`).join(" ") : "0"} | BP ${bp.map((v) => v.id).join(",") || "0"} | poziome:${uklad.przewijanie ? "TAK " + uklad.sw : "nie"} | <24px: ${uklad.male.length ? uklad.male.join("; ") : "0"}`);
  await page.screenshot({ path: `${OUT}/${ETAP}-${szer}-${nazwa}.png`, fullPage: true });
}

async function przebieg(szer, zLighthouse) {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: "shell", protocolTimeout: 300000, args: ["--lang=pl-PL", "--disable-dev-shm-usage"], defaultViewport: { width: szer, height: 900 } });
  const page = await browser.newPage();
  const bledyJs = []; page.on("pageerror", (e) => bledyJs.push(e.message)); page.on("error", (e) => console.log("PAGE CRASH", e.message)); page.on("close", () => console.log("PAGE CLOSE")); browser.on("disconnected", () => console.log("BROWSER DISCONNECTED"));
  const flow = zLighthouse ? await startFlow(page, { name: `TuAED: dostępność ${szer}px`, config: { extends: "lighthouse:default", settings: { onlyCategories: ["accessibility"], screenEmulation: { disabled: true }, formFactor: szer < 700 ? "mobile" : "desktop", throttlingMethod: "provided" } } }) : null;
  const snap = async (nazwa) => { await sleep(200); await stan(page, nazwa, szer); if (flow) { try { await flow.snapshot({ name: nazwa }); } catch (e) { console.log("  LH BŁĄD", nazwa, e.message); } } };
  const klik = async (sel) => { await page.locator(sel).click(); await sleep(250); };
  await page.goto(BASE + "/");
  await page.setViewport({ width: szer, height: 900 });
  await snap("01-start");
  await klik("button::-p-text(Zacznij)");
  await snap("02-krok1");
  await klik("button::-p-text(Dalej: dane)");
  await snap("03-krok1-bledy");
  await page.type("#d-nazwa", "Urząd Miasta Krosna");
  await page.select("#d-typ", "jst");
  await klik("button::-p-text(Dalej: dane)");
  await snap("04-krok2-pusty");
  await (await page.$("#plik")).uploadFile(FIX);
  await klik("button::-p-text(Wgraj plik)");
  await page.waitForSelector("table.mapowanie");
  await snap("05-krok2-mapowanie");
  await klik("button::-p-text(Sprawdź dane)");
  await page.waitForFunction(() => document.body.innerText.includes("Wynik sprawdzenia") && !document.body.innerText.includes("Sprawdzam…"), { timeout: 180000 });
  await snap("06-krok2-walidacja-bledy");
  for (const [id, v] of [["stala-wewnatrz_budynku", "true"], ["stala-dostepnosc", "publiczny"], ["stala-dostepny_24_7", "nie"], ["stala-status", "sprawny"]]) if (await page.$("#" + id)) await page.select("#" + id, v);
  await klik("button::-p-text(Sprawdź ponownie)");
  await page.waitForFunction(() => !document.body.innerText.includes("Sprawdzam…") && !document.querySelector("button:disabled")?.textContent.includes("Sprawdzam"), { timeout: 180000 });
  await sleep(300);
  await page.evaluate(() => document.querySelector("details")?.setAttribute("open", ""));
  await snap("07-krok2-walidacja-ok");
  await klik("button::-p-text(Dalej: publikacja)");
  await snap("08-krok3-zgoda");
  await klik("#zgoda-cc0");
  await klik("button::-p-text(Opublikuj)");
  await page.waitForFunction(() => document.body.innerText.includes("Dane opublikowane"), { timeout: 30000 });
  await snap("09-krok3-opublikowane");
  const urlEd = new URL(await page.$eval("#url-edycji", (e) => e.textContent));
  const edycja = BASE + urlEd.pathname + urlEd.search;
  await page.goto(edycja);
  await page.setViewport({ width: szer, height: 900 });
  await page.waitForSelector("#zrodlo-url");
  await snap("10-edycja-zrodlo");
  await page.type("#zrodlo-url", "https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/app/backend/tests/fixtury/legionowo.csv");
  await klik("button::-p-text(Włącz i pobierz)");
  await page.waitForFunction(() => /Stan: (Aktywna|Wstrzymana|Błąd)/.test(document.querySelector(".zrodlo")?.innerText ?? ""), { timeout: 120000 });
  await snap("11-edycja-wstrzymana");
  if (flow) {
    fs.writeFileSync(`${OUT}/lighthouse-${ETAP}-${szer}.html`, await flow.generateReport());
    const fr = await flow.createFlowResult();
    fs.writeFileSync(`${OUT}/lighthouse-${ETAP}-${szer}.json`, JSON.stringify(fr));
    for (const s of fr.steps) {
      const kat = s.lhr.categories.accessibility;
      const nie = kat.auditRefs.filter((r) => r.weight > 0 && s.lhr.audits[r.id].score === 0).map((r) => r.id);
      console.log(`LH [${szer}] ${s.name}: ${Math.round(kat.score * 100)}${nie.length ? " | nieudane: " + nie.join(",") : ""}`);
      wyniki.push({ lighthouse: true, szer, ekran: s.name, wynik: Math.round(kat.score * 100), nieudane: nie });
    }
  }
  if (bledyJs.length) console.log("BŁĘDY JS:", bledyJs);
  await browser.close();
}

for (const szer of [320, 768, 1440]) await przebieg(szer, szer !== 768);
fs.writeFileSync(`${OUT}/axe-${ETAP}.json`, JSON.stringify(wyniki, null, 1));
