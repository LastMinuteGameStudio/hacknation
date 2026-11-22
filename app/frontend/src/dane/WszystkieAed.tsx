import { useEffect, useMemo, useRef, useState } from "react";
import type { SchematOut } from "../api/types";
import { fmt, normalizuj, URL_DANYCH, wczytajAgregat, type Zakres } from "../lib/agregat";
import { etykietaSlownika } from "../lib/pola";
import { adres, godziny, pochodzenie, POCHODZENIE_NAZWA, type Pochodzenie } from "../mapa/popup";

const NA_STRONIE = 50;

interface Wiersz {
  id: string;
  nazwa: string;
  adres: string;
  dostepnosc: string;
  d247: string;
  godziny: string;
  pochodzenie: Pochodzenie;
  zrodlo: string;
  zrodloTekst: string;
  statusWal: string;
  data: string;
  szukaj: string;
}

export function WszystkieAed({ schemat }: { schemat: SchematOut | null }) {
  const [zakres, setZakres] = useState<Zakres>("z-osm");
  const [wiersze, setWiersze] = useState<Wiersz[] | null>(null);
  const [blad, setBlad] = useState(false);
  const [szukaj, setSzukaj] = useState("");
  const [szukajOpozn, setSzukajOpozn] = useState("");
  const [zrodlo, setZrodlo] = useState("");
  const [dostepnosc, setDostepnosc] = useState("");
  const [d247, setD247] = useState("");
  const [statusWal, setStatusWal] = useState("");
  const [strona, setStrona] = useState(1);
  const wynikiRef = useRef<HTMLHeadingElement>(null);
  // Ramka tabeli jest przystankiem Tab (region) tylko, gdy faktycznie przewija się w poziomie (od 700 px);
  // przy kartach nie ma czego przewijać, więc nie dokładamy pustego przystanku.
  const ramkaRef = useRef<HTMLDivElement>(null);
  const [przewijana, setPrzewijana] = useState(false);

  const slownik = (nazwa: string, kod: string | undefined) => {
    if (!kod) return "";
    const poz = schemat?.slowniki[nazwa]?.find((x) => x.kod === kod);
    return poz ? etykietaSlownika(poz.znaczenie) : kod;
  };

  useEffect(() => {
    let anulowane = false;
    setWiersze(null);
    setBlad(false);
    wczytajAgregat(zakres)
      .then((fc) => {
        if (anulowane) return;
        setWiersze(
          fc.features.map((f) => {
            const p = f.properties;
            const poch = pochodzenie(p.zrodlo);
            const nazwa = p.nazwa_obiektu || p.opis_lokalizacji || "Defibrylator AED";
            const adr = adres(p) ?? "";
            const zrodloTekst = poch === "tuaed" ? `AEDane: ${p.dysponent_nazwa ?? ""}` : poch === "osm" ? "OpenStreetMap" : p.zrodlo;
            return {
              id: f.id ?? p.id_aed,
              nazwa,
              adres: adr,
              dostepnosc: p.dostepnosc ?? "",
              d247: p.dostepny_24_7 ?? "",
              godziny: godziny(p) ?? "",
              pochodzenie: poch,
              zrodlo: p.zrodlo ?? "",
              zrodloTekst: poch !== "tuaed" && p.dysponent_nazwa ? `${zrodloTekst} (${p.dysponent_nazwa})` : zrodloTekst,
              statusWal: p.status_walidacji ?? "",
              data: p.data_aktualizacji || p.data_weryfikacji || "",
              szukaj: normalizuj([nazwa, adr, p.opis_lokalizacji, p.miejscowosc, p.nazwa_ulicy, p.dysponent_nazwa].filter(Boolean).join(" ")),
            };
          }),
        );
      })
      .catch(() => !anulowane && setBlad(true));
    return () => {
      anulowane = true;
    };
  }, [zakres]);

  // Wyszukiwanie z opóźnieniem: mniej przeliczeń i mniej komunikatów czytnika ekranu przy pisaniu.
  useEffect(() => {
    const t = window.setTimeout(() => setSzukajOpozn(szukaj), 350);
    return () => window.clearTimeout(t);
  }, [szukaj]);
  useEffect(() => setStrona(1), [szukajOpozn, zrodlo, dostepnosc, d247, statusWal, zakres]);

  const zrodla = useMemo(() => {
    const m = new Map<string, { etykieta: string; n: number }>();
    for (const w of wiersze ?? []) {
      if (w.pochodzenie === "osm") continue;
      const e = m.get(w.zrodlo) ?? { etykieta: w.pochodzenie === "tuaed" ? w.zrodloTekst : w.zrodlo, n: 0 };
      e.n++;
      m.set(w.zrodlo, e);
    }
    return [...m.entries()].sort((a, b) => b[1].n - a[1].n);
  }, [wiersze]);

  const wynik = useMemo(() => {
    if (!wiersze) return [];
    const slowa = normalizuj(szukajOpozn).split(/\s+/).filter(Boolean);
    return wiersze.filter(
      (w) =>
        (!zrodlo ||
          (zrodlo.startsWith("kat:") ? w.pochodzenie === zrodlo.slice(4) : w.zrodlo === zrodlo.slice(4))) &&
        (!dostepnosc || (dostepnosc === "_brak" ? !w.dostepnosc : w.dostepnosc === dostepnosc)) &&
        (!d247 || (d247 === "_brak" ? !w.d247 : w.d247 === d247)) &&
        (!statusWal || (statusWal === "_brak" ? !w.statusWal : w.statusWal === statusWal)) &&
        slowa.every((s) => w.szukaj.includes(s)),
    );
  }, [wiersze, szukajOpozn, zrodlo, dostepnosc, d247, statusWal]);

  const maTabele = !!wiersze && wynik.length > 0;
  useEffect(() => {
    const el = ramkaRef.current;
    if (!el) {
      setPrzewijana(false);
      return;
    }
    const sprawdz = () => setPrzewijana(el.scrollWidth > el.clientWidth + 1);
    sprawdz();
    const ro = new ResizeObserver(sprawdz);
    ro.observe(el);
    if (el.firstElementChild) ro.observe(el.firstElementChild);
    return () => ro.disconnect();
  }, [maTabele]);

  const stron = Math.max(1, Math.ceil(wynik.length / NA_STRONIE));
  const naStronie = wynik.slice((strona - 1) * NA_STRONIE, strona * NA_STRONIE);
  const przejdz = (s: number) => {
    setStrona(Math.min(stron, Math.max(1, s)));
    requestAnimationFrame(() => wynikiRef.current?.focus());
  };
  const filtryAktywne = !!(szukaj || zrodlo || dostepnosc || d247 || statusWal);
  const wyczysc = () => {
    setSzukaj("");
    setSzukajOpozn("");
    setZrodlo("");
    setDostepnosc("");
    setD247("");
    setStatusWal("");
  };

  const opcjeSlownika = (nazwa: string) =>
    (schemat?.slowniki[nazwa] ?? []).map((o) => (
      <option key={o.kod} value={o.kod}>
        {etykietaSlownika(o.znaczenie)}
      </option>
    ));

  return (
    <section aria-labelledby="aed-naglowek">
      <h2 id="aed-naglowek">Wszystkie AED</h2>
      <p>
        Te same dane co na mapie: zbiór zbiorczy z dostawców AEDane, otwartych danych urzędów i OpenStreetMap. Kliknij
        nazwę, żeby zobaczyć AED na mapie. Całość pobierzesz jako <a href={URL_DANYCH[zakres].csv}>CSV</a> lub{" "}
        <a href={URL_DANYCH[zakres].geojson}>GeoJSON</a>.
      </p>

      <form className="filtry" onSubmit={(e) => e.preventDefault()} role="search" aria-label="Filtry AED">
        <fieldset className="przelacznik filtry-pelne">
          <legend>Zakres danych</legend>
          <label>
            <input type="radio" name="zakres-dane" checked={zakres === "z-osm"} onChange={() => setZakres("z-osm")} />
            Wszystkie, także z OpenStreetMap
          </label>
          <label>
            <input type="radio" name="zakres-dane" checked={zakres === "bez-osm"} onChange={() => setZakres("bez-osm")} />
            Bez OpenStreetMap
          </label>
        </fieldset>
        <div className="pole filtry-pelne">
          <label htmlFor="f-szukaj">Szukaj</label>
          <span id="f-szukaj-podp" className="podpowiedz">
            Nazwa obiektu, miejscowość, ulica albo dysponent.
          </span>
          <input
            id="f-szukaj"
            type="search"
            value={szukaj}
            onChange={(e) => setSzukaj(e.target.value)}
            aria-describedby="f-szukaj-podp"
            autoComplete="off"
          />
        </div>
        <div className="pole">
          <label htmlFor="f-zrodlo">Źródło</label>
          <select id="f-zrodlo" value={zrodlo} onChange={(e) => setZrodlo(e.target.value)}>
            <option value="">Wszystkie</option>
            {(["tuaed", "urzad", "osm"] as const)
              .filter((k) => zakres === "z-osm" || k !== "osm")
              .map((k) => (
                <option key={k} value={`kat:${k}`}>
                  {POCHODZENIE_NAZWA[k]}
                </option>
              ))}
            {zrodla.length > 0 && (
              <optgroup label="Konkretne źródło">
                {zrodla.map(([kod, e]) => (
                  <option key={kod} value={`src:${kod}`}>
                    {e.etykieta} ({fmt(e.n)})
                  </option>
                ))}
              </optgroup>
            )}
          </select>
        </div>
        <div className="pole">
          <label htmlFor="f-dostepnosc">Kto ma dostęp</label>
          <select id="f-dostepnosc" value={dostepnosc} onChange={(e) => setDostepnosc(e.target.value)}>
            <option value="">Wszystkie</option>
            {opcjeSlownika("dostepnosc")}
            <option value="_brak">Brak informacji</option>
          </select>
        </div>
        <div className="pole">
          <label htmlFor="f-d247">Dostępny całą dobę</label>
          <select id="f-d247" value={d247} onChange={(e) => setD247(e.target.value)}>
            <option value="">Wszystkie</option>
            {opcjeSlownika("tak_nie_ograniczony")}
            <option value="_brak">Brak informacji</option>
          </select>
        </div>
        <div className="pole">
          <label htmlFor="f-status">Weryfikacja rekordu</label>
          <select id="f-status" value={statusWal} onChange={(e) => setStatusWal(e.target.value)}>
            <option value="">Wszystkie</option>
            {opcjeSlownika("status_walidacji")}
            <option value="_brak">Nie dotyczy (dane z innych źródeł)</option>
          </select>
        </div>
        {filtryAktywne && (
          <div className="filtry-pelne">
            <button type="button" className="drugorzedny maly" onClick={wyczysc}>
              Wyczyść filtry
            </button>
          </div>
        )}
      </form>

      <h3 id="wyniki-naglowek" ref={wynikiRef} tabIndex={-1}>
        Wyniki
      </h3>
      <p role="status" className="mapa-stan">
        {blad
          ? "Nie udało się wczytać danych. Pobierz je z linków wyżej."
          : !wiersze
            ? zakres === "z-osm"
              ? "Wczytuję ok. 19 tys. AED…"
              : "Wczytuję AED…"
            : `Znaleziono ${fmt(wynik.length)} AED${wynik.length > NA_STRONIE ? `, strona ${strona} z ${stron}` : ""}.`}
      </p>

      {wiersze && naStronie.length > 0 && (
        <div
          ref={ramkaRef}
          className="tabela-przewijana tabela-aed-ramka"
          {...(przewijana ? { tabIndex: 0, role: "region", "aria-label": "Tabela AED (przewijana w poziomie)" } : {})}
        >
          <table className="tabela-karty tabela-aed">
            <caption className="wizualnie-ukryte">
              AED, strona {strona} z {stron}. Nazwa prowadzi do punktu na mapie.
            </caption>
            <thead>
              <tr>
                <th scope="col">Nazwa obiektu</th>
                <th scope="col">Adres</th>
                <th scope="col">Kto ma dostęp</th>
                <th scope="col">Godziny</th>
                <th scope="col">Źródło</th>
                <th scope="col">Aktualizacja</th>
              </tr>
            </thead>
            <tbody>
              {naStronie.map((w) => {
                const href = `/mapa?aed=${encodeURIComponent(w.id)}`;
                return (
                  <tr
                    key={w.id}
                    className="wiersz-klikalny"
                    onClick={(e) => {
                      if (!(e.target as HTMLElement).closest("a")) window.location.href = href;
                    }}
                  >
                    <th scope="row" data-etykieta="Nazwa obiektu">
                      <a href={href}>{w.nazwa}</a>
                    </th>
                    <td data-etykieta="Adres">{w.adres || "—"}</td>
                    <td data-etykieta="Kto ma dostęp">{slownik("dostepnosc", w.dostepnosc) || "—"}</td>
                    <td data-etykieta="Godziny">
                      {w.d247 === "tak" ? "całą dobę" : w.godziny || (w.d247 ? `całą dobę: ${slownik("tak_nie_ograniczony", w.d247).toLowerCase()}` : "—")}
                    </td>
                    <td data-etykieta="Źródło">
                      {w.zrodloTekst}
                      {w.statusWal === "oczekuje" && <span className="drobny wiersz-pod">oczekuje na weryfikację</span>}
                    </td>
                    <td data-etykieta="Aktualizacja">{w.data || "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {wiersze && stron > 1 && (
        <nav className="stronicowanie" aria-label="Stronicowanie wyników">
          <button type="button" className="drugorzedny maly" disabled={strona === 1} onClick={() => przejdz(1)}>
            <span aria-hidden="true">«</span> Pierwsza
          </button>
          <button type="button" className="drugorzedny maly" disabled={strona === 1} onClick={() => przejdz(strona - 1)}>
            <span aria-hidden="true">‹</span> Poprzednia
          </button>
          <span className="stronicowanie-stan">
            Strona {strona} z {stron}
          </span>
          <button type="button" className="drugorzedny maly" disabled={strona === stron} onClick={() => przejdz(strona + 1)}>
            Następna <span aria-hidden="true">›</span>
          </button>
          <button type="button" className="drugorzedny maly" disabled={strona === stron} onClick={() => przejdz(stron)}>
            Ostatnia <span aria-hidden="true">»</span>
          </button>
        </nav>
      )}
    </section>
  );
}
