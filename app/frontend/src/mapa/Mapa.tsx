// S2: mapa AED z agregatu (/d/aed-polska.geojson), Leaflet + markercluster. Ładowana leniwie (osobny chunk).
import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import type { AedFeatureCollection, SchematOut } from "../api/types";
import { budujPopup, pochodzenie, POCHODZENIE_NAZWA, tytul, type Pochodzenie } from "./popup";

// leaflet.markercluster (UMD) rozszerza globalne L.
(window as unknown as { L: typeof L }).L = L;
const klaster = import("leaflet.markercluster");

type Zakres = "z-osm" | "bez-osm";
const URL_DANYCH: Record<Zakres, { geojson: string; csv: string }> = {
  "z-osm": { geojson: "/d/aed-polska.geojson", csv: "/d/aed-polska.csv" },
  "bez-osm": { geojson: "/d/aed-polska-bez-osm.geojson", csv: "/d/aed-polska-bez-osm.csv" },
};
const KOLEJNOSC: Pochodzenie[] = ["tuaed", "urzad", "osm"];

const fmt = (n: number) => n.toLocaleString("pl-PL");

function ikonaPunktu(p: Record<string, string>, poch: Pochodzenie) {
  const etykieta = document.createElement("span");
  etykieta.className = "wizualnie-ukryte";
  etykieta.textContent = `AED: ${tytul(p)}`;
  const kropka = document.createElement("span");
  kropka.className = `punkt punkt-${poch}`;
  kropka.setAttribute("aria-hidden", "true");
  const html = document.createElement("span");
  html.append(kropka, etykieta);
  // 24×24 px cel dotyku (WCAG 2.5.8), widoczna kropka mniejsza.
  return L.divIcon({ className: "punkt-cel", html, iconSize: [24, 24], iconAnchor: [12, 12], popupAnchor: [0, -8] });
}

function ikonaKlastra(c: L.MarkerCluster) {
  const n = c.getChildCount();
  const r = n < 100 ? 36 : n < 1000 ? 44 : 52;
  const html = `<span aria-hidden="true">${fmt(n)}</span><span class="wizualnie-ukryte">${fmt(n)} AED w tym obszarze. Enter przybliża.</span>`;
  return L.divIcon({ className: "klaster", html, iconSize: [r, r] });
}

export default function Mapa({ schemat }: { schemat: SchematOut | null }) {
  const kontener = useRef<HTMLDivElement>(null);
  const mapa = useRef<L.Map | null>(null);
  const warstwa = useRef<L.MarkerClusterGroup | null>(null);
  const cache = useRef<Partial<Record<Zakres, AedFeatureCollection>>>({});
  const schematRef = useRef(schemat);
  schematRef.current = schemat;
  const [zakres, setZakres] = useState<Zakres>("z-osm");
  const [stan, setStan] = useState<"laduje" | "ok" | "blad">("laduje");
  const [liczby, setLiczby] = useState<Record<Pochodzenie, number> | null>(null);

  useEffect(() => {
    document.title = "Mapa AED | TuAED";
    if (!kontener.current || mapa.current) return;
    const waska = window.innerWidth < 600;
    const m = L.map(kontener.current, { center: [52.0, 19.3], zoom: waska ? 5 : 6, minZoom: 5, maxZoom: 19, keyboard: true });
    m.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">autorzy OpenStreetMap</a>',
    }).addTo(m);
    // Fokus do popupu po otwarciu (czytnik ekranu odczyta treść), po zamknięciu powrót na punkt.
    // Escape: Leaflet obsługuje go tylko przy fokusie na kontenerze mapy, więc dokładamy własny.
    let ostatni: HTMLElement | null = null;
    let otwarty: HTMLElement | null = null;
    m.on("popupopen", (e) => {
      ostatni = document.activeElement instanceof HTMLElement ? document.activeElement : null;
      otwarty = e.popup.getElement() ?? null;
      otwarty?.querySelector<HTMLElement>(".popup-aed")?.focus();
    });
    m.on("popupclose", (e) => {
      const wPopupie = e.popup.getElement()?.contains(document.activeElement);
      otwarty = null;
      if (ostatni && (wPopupie || document.activeElement === document.body)) ostatni.focus();
    });
    const escape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && otwarty) {
        e.preventDefault();
        m.closePopup();
      }
    };
    document.addEventListener("keydown", escape);
    mapa.current = m;
    return () => {
      document.removeEventListener("keydown", escape);
      m.remove();
      mapa.current = null;
    };
  }, []);

  useEffect(() => {
    let anulowane = false;
    (async () => {
      setStan("laduje");
      try {
        await klaster;
        let dane = cache.current[zakres];
        if (!dane) {
          const r = await fetch(URL_DANYCH[zakres].geojson);
          if (!r.ok) throw new Error(String(r.status));
          dane = (await r.json()) as AedFeatureCollection;
          cache.current[zakres] = dane;
        }
        if (anulowane || !mapa.current) return;
        const grupa = L.markerClusterGroup({
          chunkedLoading: true,
          showCoverageOnHover: false,
          maxClusterRadius: 60,
          iconCreateFunction: ikonaKlastra,
        });
        const zliczone: Record<Pochodzenie, number> = { tuaed: 0, urzad: 0, osm: 0 };
        const markery: L.Marker[] = [];
        for (const f of dane.features) {
          if (!f.geometry) continue;
          const [lon, lat] = f.geometry.coordinates;
          const p = f.properties;
          const poch = pochodzenie(p.zrodlo);
          zliczone[poch]++;
          const mk = L.marker([lat, lon], { icon: ikonaPunktu(p, poch), keyboard: true });
          mk.bindPopup(() => budujPopup(p, schematRef.current), { maxWidth: 280, autoPanPadding: [16, 16] });
          markery.push(mk);
        }
        grupa.addLayers(markery);
        warstwa.current?.remove();
        grupa.addTo(mapa.current);
        warstwa.current = grupa;
        setLiczby(zliczone);
        setStan("ok");
      } catch {
        if (!anulowane) setStan("blad");
      }
    })();
    return () => {
      anulowane = true;
    };
  }, [zakres]);

  const suma = liczby ? liczby.tuaed + liczby.urzad + liczby.osm : 0;

  return (
    <section aria-labelledby="naglowek-kroku">
      <h1 id="naglowek-kroku" tabIndex={-1}>
        Mapa defibrylatorów AED
      </h1>
      <p>
        Wszystkie AED z naszego zbioru zbiorczego: dane od dostawców opublikowane przez TuAED, otwarte dane urzędów i
        punkty z OpenStreetMap. Kliknij punkt, żeby zobaczyć adres, dostępność i pochodzenie danych.
      </p>

      <fieldset className="przelacznik">
        <legend>Pokaż</legend>
        <label>
          <input type="radio" name="zakres" value="z-osm" checked={zakres === "z-osm"} onChange={() => setZakres("z-osm")} />
          Wszystkie AED, także z OpenStreetMap
        </label>
        <label>
          <input
            type="radio"
            name="zakres"
            value="bez-osm"
            checked={zakres === "bez-osm"}
            onChange={() => setZakres("bez-osm")}
          />
          Bez OpenStreetMap (tylko urzędy i dostawcy)
        </label>
      </fieldset>

      <p role="status" className="mapa-stan">
        {stan === "laduje"
          ? zakres === "z-osm"
            ? "Wczytuję ok. 19 tys. punktów…"
            : "Wczytuję punkty…"
          : stan === "blad"
            ? "Nie udało się wczytać danych mapy. Dane możesz pobrać z linków niżej."
            : `Na mapie: ${fmt(suma)} AED.`}
      </p>

      <ul className="legenda" aria-label="Legenda">
        {KOLEJNOSC.filter((k) => zakres === "z-osm" || k !== "osm").map((k) => (
          <li key={k}>
            <span className={`punkt punkt-${k}`} aria-hidden="true" /> {POCHODZENIE_NAZWA[k]}
            {liczby && <span className="drobny"> ({fmt(liczby[k])})</span>}
          </li>
        ))}
      </ul>

      <div
        ref={kontener}
        className="mapa"
        role="region"
        aria-label="Mapa AED. Gdy jest aktywna: strzałki przesuwają, plus i minus przybliżają. Tab przechodzi po grupach i punktach."
        aria-describedby="mapa-alternatywa"
      />

      <h2 id="mapa-alternatywa">Te same dane bez mapy</h2>
      <p>
        Mapa pokazuje {liczby ? fmt(suma) : "wszystkie"} AED z pliku zbiorczego. Pełną listę z adresami, godzinami i
        pochodzeniem pobierzesz jako plik:
      </p>
      <ul className="lista-linkow">
        <li>
          <a href={URL_DANYCH[zakres].csv}>CSV (arkusz)</a>
        </li>
        <li>
          <a href={URL_DANYCH[zakres].geojson}>GeoJSON (dla map i GIS)</a>
        </li>
      </ul>
      {liczby && (
        <table className="tabela-liczb">
          <caption>Liczba AED według pochodzenia danych</caption>
          <thead>
            <tr>
              <th scope="col">Pochodzenie</th>
              <th scope="col">Liczba AED</th>
            </tr>
          </thead>
          <tbody>
            {KOLEJNOSC.filter((k) => liczby[k] > 0).map((k) => (
              <tr key={k}>
                <th scope="row">{POCHODZENIE_NAZWA[k]}</th>
                <td>{fmt(liczby[k])}</td>
              </tr>
            ))}
            <tr>
              <th scope="row">Razem</th>
              <td>{fmt(suma)}</td>
            </tr>
          </tbody>
        </table>
      )}
      <p className="drobny">
        Dane z OpenStreetMap są na licencji ODbL 1.0 (© współtwórcy OpenStreetMap). Dane od dostawców przez TuAED są na
        CC0 1.0. Licencje pozostałych źródeł są w kolumnie „licencja_zrodla”.
      </p>
    </section>
  );
}
