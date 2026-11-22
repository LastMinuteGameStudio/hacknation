import { chromium } from "playwright";
import fs from "fs";
import { createRequire } from "module";
const S = process.argv[2];
const AXE = fs.readFileSync(createRequire(import.meta.url).resolve("axe-core/axe.min.js"), "utf8");
const TAGI = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"];
const b = await chromium.launch();
const axe = async (p, n) => { await p.evaluate(AXE); const v = await p.evaluate((t) => axe.run(document, { runOnly: { type: "tag", values: t } }).then((r) => r.violations.map((v) => `${v.id}(${v.impact},${v.nodes.length}: ${v.nodes.slice(0, 2).map((x) => x.target.join(" ")).join(" | ")})`)), TAGI); console.log(`   axe ${n}: ${v.length ? v.join("; ") : "0"}`); };
for (const w of (process.argv[3] ? [Number(process.argv[3])] : [320, 768, 1440])) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  const bledy = []; p.on("pageerror", (e) => bledy.push(e.message)); p.on("console", (m) => m.type() === "error" && bledy.push(m.text()));
  const t0 = Date.now();
  await p.goto("http://localhost:4173/mapa");
  await p.waitForFunction(() => /Na mapie: /.test(document.querySelector(".mapa-stan")?.textContent ?? ""), null, { timeout: 120000 });
  console.log(`[${w}] ${await p.locator(".mapa-stan").innerText()} w ${Date.now() - t0} ms | tytuł: ${await p.title()} | klastrów: ${await p.locator(".klaster").count()} | strona: ${await p.evaluate(() => document.documentElement.scrollWidth)}`);
  await p.waitForTimeout(1500);
  await axe(p, "z OSM");
  await p.screenshot({ path: `${S}/audyt/mapa-${w}.png`, fullPage: true });
  if (w === 1440) {
    // klawiatura: Tab do pierwszego klastra, Enter
    let el = ""; for (let i = 0; i < 40; i++) { await p.keyboard.press("Tab"); el = await p.evaluate(() => document.activeElement.className + "|" + document.activeElement.textContent.slice(0, 50)); if (el.includes("klaster")) break; }
    console.log("   Tab → klaster:", el);
    const z0 = await p.evaluate(() => document.querySelector(".mapa").__z ?? 0);
    for (let k = 0; k < 8; k++) { // Enter na klastrze aż do punktu
      await p.keyboard.press("Enter"); await p.waitForTimeout(900);
      const cel = await p.evaluate(() => { const c = [...document.querySelectorAll(".leaflet-marker-icon")].filter((e) => { const r = e.getBoundingClientRect(); const m = document.querySelector(".mapa").getBoundingClientRect(); return r.top > m.top && r.bottom < m.bottom && r.left > m.left && r.right < m.right; }); const pkt = c.find((e) => e.classList.contains("punkt-cel")); return pkt ? "punkt" : c.find((e) => e.classList.contains("klaster")) ? "klaster" : "nic"; });
      if (cel === "punkt") { await p.evaluate(() => { const m = document.querySelector(".mapa").getBoundingClientRect(); [...document.querySelectorAll(".punkt-cel")].find((e) => { const r = e.getBoundingClientRect(); return r.top > m.top && r.bottom < m.bottom && r.left > m.left && r.right < m.right; }).focus(); }); break; }
      await p.evaluate(() => { const m = document.querySelector(".mapa").getBoundingClientRect(); [...document.querySelectorAll(".klaster")].find((e) => { const r = e.getBoundingClientRect(); return r.top > m.top && r.bottom < m.bottom && r.left > m.left && r.right < m.right; })?.focus(); });
    }
    const f = await p.evaluate(() => ({ cls: document.activeElement.className, name: document.activeElement.textContent, role: document.activeElement.getAttribute("role"), r: document.activeElement.getBoundingClientRect() }));
    console.log(`   fokus na punkcie: ${f.cls.includes("punkt-cel")} "${f.name}" role=${f.role} ${Math.round(f.r.width)}x${Math.round(f.r.height)}`);
    await p.keyboard.press("Enter"); await p.waitForTimeout(600);
    console.log("   popup:", (await p.locator(".popup-aed").innerText().catch(() => "BRAK")).replace(/\n/g, " | ").slice(0, 300));
    console.log("   fokus w popupie:", await p.evaluate(() => document.activeElement.className));
    await axe(p, "z otwartym popupem");
    await p.screenshot({ path: `${S}/audyt/mapa-popup-${w}.png` });
    await p.keyboard.press("Escape"); await p.waitForTimeout(300);
    console.log("   po Escape fokus:", await p.evaluate(() => document.activeElement.className));
    await p.check("input[value=bez-osm]");
    await p.waitForFunction(() => /Na mapie: /.test(document.querySelector(".mapa-stan")?.textContent ?? ""), null, { timeout: 60000 });
    await p.waitForTimeout(500);
    console.log("   bez OSM:", await p.locator(".mapa-stan").innerText(), "|", (await p.locator(".tabela-liczb").innerText()).replace(/\n/g, " ").replace(/\t/g, " "));
    await axe(p, "bez OSM");
  }
  console.log("   błędy JS:", bledy.filter((x) => !x.includes("tile.openstreetmap")).slice(0, 3));
  await p.close();
}
await b.close();
