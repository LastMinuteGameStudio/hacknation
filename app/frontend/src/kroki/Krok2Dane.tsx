import { useMemo, useRef, useState, type FormEvent, type ReactNode } from "react";
import { api, ApiError } from "../api/client";
import type { Dysponent, ImportOut, Mapowanie, PoleSchematu, SchematOut, WalidacjaOut } from "../api/types";
import { Komunikaty } from "../components/Komunikaty";
import {
  etykietaSlownika,
  idGrupy,
  KANDYDACI_STALE,
  nazwaPola,
  POLA_AUTOMATYCZNE,
  polaPokryte,
  polaWyboru,
  SPECJALNE,
} from "../lib/pola";

export interface StanDanych {
  plik: File | null;
  arkusz: string | null;
  imp: ImportOut | null;
  mapowanie: Mapowanie;
  wartosciStale: Record<string, string>;
  walidacja: WalidacjaOut | null;
  /** false, gdy po walidacji zmieniono mapowanie albo wartości stałe */
  aktualna: boolean;
}

export const PUSTY_STAN: StanDanych = {
  plik: null,
  arkusz: null,
  imp: null,
  mapowanie: {},
  wartosciStale: {},
  walidacja: null,
  aktualna: false,
};

const MAX_MB = 10;
const PREFIKS = "kw"; // id grup komunikatów walidacji

interface Props {
  schemat: SchematOut | null;
  dysponent: Dysponent;
  edycja: { slug: string; token: string } | null;
  stan: StanDanych;
  setStan: (s: StanDanych) => void;
  onWstecz: (() => void) | null;
  onDalej: () => void;
  /** Dodatkowa sekcja nad wgraniem pliku (w edycji: źródło automatyczne). */
  dodatek?: ReactNode;
}

function opisPewnosci(p: number): { klasa: string; tekst: string } {
  if (p >= 0.85) return { klasa: "pewnosc-wysoka", tekst: "pewne" };
  if (p >= 0.6) return { klasa: "pewnosc-srednia", tekst: "sprawdź" };
  return { klasa: "pewnosc-niska", tekst: "niepewne" };
}

function bladTekst(e: unknown): string {
  if (e instanceof ApiError) return e.blad.komunikat;
  return "Brak połączenia z serwerem. Sprawdź internet i spróbuj ponownie.";
}

function liczba(n: number, jeden: string, kilka: string, wiele: string) {
  const m10 = n % 10, m100 = n % 100;
  const slowo = n === 1 ? jeden : m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14) ? kilka : wiele;
  return `${n} ${slowo}`;
}

export function Krok2Dane({ schemat, dysponent, edycja, stan, setStan, onWstecz, onDalej, dodatek }: Props) {
  const [wybranyPlik, setWybranyPlik] = useState<File | null>(stan.plik);
  const [bladPliku, setBladPliku] = useState<string | null>(null);
  const [wgrywam, setWgrywam] = useState(false);
  const [sprawdzam, setSprawdzam] = useState(false);
  const [bladApi, setBladApi] = useState<string | null>(null);
  const [arkuszWybor, setArkuszWybor] = useState<string>(stan.arkusz ?? "");
  const wynikRef = useRef<HTMLHeadingElement>(null);
  const mapowanieRef = useRef<HTMLHeadingElement>(null);
  const { imp, mapowanie, wartosciStale, walidacja, aktualna } = stan;

  const polaDoWyboru = useMemo(() => {
    const grupy = new Map<string, PoleSchematu[]>();
    for (const p of schemat?.pola ?? []) {
      if (POLA_AUTOMATYCZNE.has(p.pole)) continue;
      if (!grupy.has(p.grupa)) grupy.set(p.grupa, []);
      grupy.get(p.grupa)!.push(p);
    }
    return [...grupy.entries()];
  }, [schemat]);

  const pokryte = polaPokryte(mapowanie);
  const doStalych = KANDYDACI_STALE.filter((p) => !pokryte.has(p));
  const zajete = new Map<string, string>(); // pole -> kolumna
  Object.entries(mapowanie).forEach(([kol, pole]) => pole && zajete.set(pole, kol));

  // Pola, dla których walidacja zwróciła komunikat (żeby powiązać je z listami wyboru).
  const komPola = new Map<string, "blad" | "ostrzezenie">();
  if (walidacja && aktualna) {
    for (const k of walidacja.komunikaty) {
      if (!k.pole || k.poziom === "info") continue;
      if (k.poziom === "blad" || !komPola.has(k.pole)) komPola.set(k.pole, k.poziom);
    }
  }
  const opisDla = (pola: string[], extra?: string) => {
    const ids = pola.filter((p) => komPola.has(p)).map((p) => idGrupy(PREFIKS, p));
    return [extra, ...ids].filter(Boolean).join(" ") || undefined;
  };
  const maBlad = (pola: string[]) => pola.some((p) => komPola.get(p) === "blad");

  async function wgraj(plik: File, arkusz?: string) {
    setBladApi(null);
    setWgrywam(true);
    try {
      const wynik = await api.wgrajPlik(plik, arkusz, edycja ?? undefined);
      const map: Mapowanie = {};
      const uzyte = new Set<string>();
      for (const p of wynik.mapowanie_propozycja) {
        // Jedno pole = jedna kolumna: wygrywa pierwsza propozycja.
        map[p.kolumna] = p.pole && !uzyte.has(p.pole) ? p.pole : null;
        if (p.pole) uzyte.add(p.pole);
      }
      wynik.kolumny.forEach((k) => {
        if (!(k.nazwa in map)) map[k.nazwa] = null;
      });
      setStan({
        plik,
        arkusz: arkusz ?? wynik.arkusze[0] ?? null,
        imp: wynik,
        mapowanie: map,
        wartosciStale: stan.wartosciStale,
        walidacja: null,
        aktualna: false,
      });
      setArkuszWybor(arkusz ?? wynik.arkusze[0] ?? "");
      requestAnimationFrame(() => mapowanieRef.current?.focus());
    } catch (e) {
      setBladApi(bladTekst(e));
    } finally {
      setWgrywam(false);
    }
  }

  function wyslijPlik(e: FormEvent) {
    e.preventDefault();
    const plik = wybranyPlik;
    let blad: string | null = null;
    if (!plik) blad = "Wybierz plik CSV, XLSX lub GeoJSON.";
    else if (!/\.(csv|xlsx|geojson|json)$/i.test(plik.name)) blad = "Ten plik ma inny format. Wgraj plik CSV, XLSX albo GeoJSON.";
    else if (plik.size > MAX_MB * 1024 * 1024) blad = `Plik jest większy niż ${MAX_MB} MB. Podziel go na mniejsze części.`;
    setBladPliku(blad);
    if (blad || !plik) {
      document.getElementById("plik")?.focus();
      return;
    }
    void wgraj(plik);
  }

  function zmienMapowanie(kolumna: string, pole: string | null) {
    setStan({ ...stan, mapowanie: { ...mapowanie, [kolumna]: pole }, aktualna: false });
  }

  function zmienStala(pole: string, wartosc: string) {
    const w = { ...wartosciStale };
    if (wartosc) w[pole] = wartosc;
    else delete w[pole];
    setStan({ ...stan, wartosciStale: w, aktualna: false });
  }

  async function sprawdz() {
    if (!imp) return;
    setBladApi(null);
    setSprawdzam(true);
    // Wysyłamy tylko wartości stałe dla pól bez kolumny. W edycji backend bierze wartości zbioru jako domyślne,
    // więc pole ustawione na „— nie ustawiaj —” wysyłamy jawnie jako "" (usuwa wartość ze zbioru).
    const stale: Record<string, string> = Object.fromEntries(
      Object.entries(wartosciStale).filter(([p]) => !pokryte.has(p)),
    );
    if (edycja) for (const p of doStalych) if (!(p in stale)) stale[p] = "";
    try {
      const w = await api.waliduj(imp.import_id, { mapowanie, dysponent, wartosci_stale: stale });
      setStan({ ...stan, walidacja: w, aktualna: true });
      requestAnimationFrame(() => wynikRef.current?.focus());
    } catch (e) {
      setBladApi(bladTekst(e));
    } finally {
      setSprawdzam(false);
    }
  }

  const moznaDalej = !!walidacja && aktualna && walidacja.mozna_publikowac;
  const ileZgodnosc = imp?.mapowanie_propozycja ?? [];

  return (
    <section aria-labelledby="naglowek-kroku">
      <h1 id="naglowek-kroku" tabIndex={-1}>
        {edycja ? "Wgraj nową wersję danych" : "Wgraj dane o AED"}
      </h1>
      {edycja && (
        <div className="ramka ramka-info">
          <p>
            Aktualizujesz zbiór <strong>{dysponent.nazwa}</strong>. Po publikacji nowe dane zastąpią stare pod tym samym
            adresem.
          </p>
        </div>
      )}

      {dodatek}
      {dodatek && <h2>Albo wgraj nowy plik ręcznie</h2>}

      <form onSubmit={wyslijPlik}>
        <div className="pole">
          <label htmlFor="plik">Plik z listą AED</label>
          <span id="plik-podp" className="podpowiedz">
            CSV, XLSX lub GeoJSON, do {MAX_MB} MB i 20 000 wierszy. W arkuszu pierwszy wiersz tabeli to nazwy kolumn.
          </span>
          <input
            id="plik"
            type="file"
            accept=".csv,.xlsx,.geojson,.json,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/geo+json,application/json"
            onChange={(e) => {
              setWybranyPlik(e.target.files?.[0] ?? null);
              setBladPliku(null);
            }}
            aria-invalid={bladPliku ? true : undefined}
            aria-describedby={["plik-podp", bladPliku ? "plik-blad" : null].filter(Boolean).join(" ")}
          />
          {bladPliku && (
            <span id="plik-blad" className="blad-pola">
              {bladPliku}
            </span>
          )}
        </div>
        <button type="submit" disabled={wgrywam}>
          {wgrywam ? "Wczytuję…" : imp ? "Wgraj inny plik" : "Wgraj plik"}
        </button>
      </form>

      <div aria-live="polite" className="wizualnie-ukryte">
        {wgrywam ? "Wczytuję plik." : sprawdzam ? "Sprawdzam dane." : ""}
      </div>
      {bladApi && (
        <div className="ramka ramka-blad" role="alert">
          <p>{bladApi}</p>
        </div>
      )}

      {imp && (
        <>
          <h2 id="mapowanie-naglowek" ref={mapowanieRef} tabIndex={-1}>
            Dopasuj kolumny
          </h2>
          <p>
            Plik <strong>{imp.plik_nazwa}</strong>: {liczba(imp.liczba_wierszy, "wiersz", "wiersze", "wierszy")} danych.
            Dla każdej kolumny wybierz, co zawiera. Podpowiedzi oznaczone „sprawdź” albo „niepewne” obejrzyj uważnie.
          </p>

          {imp.arkusze.length > 1 && (
            <div className="pole">
              <label htmlFor="arkusz">Arkusz z danymi</label>
              <div className="akcje" style={{ margin: 0 }}>
                <select
                  id="arkusz"
                  value={arkuszWybor}
                  onChange={(e) => setArkuszWybor(e.target.value)}
                  style={{ flex: "1 1 12rem", width: "auto" }}
                >
                  {imp.arkusze.map((a) => (
                    <option key={a} value={a}>
                      {a}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  className="drugorzedny"
                  disabled={wgrywam || !stan.plik || arkuszWybor === stan.arkusz}
                  onClick={() => stan.plik && wgraj(stan.plik, arkuszWybor)}
                >
                  Wczytaj arkusz
                </button>
              </div>
            </div>
          )}

          {imp.komunikaty.length > 0 && (
            <Komunikaty komunikaty={imp.komunikaty} schemat={schemat} prefiks="ki" />
          )}

          <div className="tabela-przewijana">
            <table className="mapowanie">
              <caption className="wizualnie-ukryte">Dopasowanie kolumn z pliku do pól danych</caption>
              <thead>
                <tr>
                  <th scope="col">Kolumna w pliku</th>
                  <th scope="col">Co zawiera</th>
                  <th scope="col">Podpowiedź</th>
                </tr>
              </thead>
              <tbody>
                {imp.kolumny.map((k) => {
                  const id = `kol-${k.indeks}`;
                  const wybor = mapowanie[k.nazwa] ?? null;
                  const prop = ileZgodnosc.find((p) => p.kolumna === k.nazwa);
                  const zgodna = prop && (prop.pole ?? null) === wybor;
                  const pew = prop ? opisPewnosci(prop.pewnosc) : null;
                  const dotyczy = polaWyboru(wybor);
                  return (
                    <tr key={k.indeks}>
                      <td data-etykieta="Kolumna w pliku">
                        <span id={`${id}-nazwa`}>{k.nazwa}</span>
                        {k.przyklady.length > 0 && (
                          <span id={`${id}-prz`} className="przyklady">
                            <span className="przyklady-etykieta">Pierwsze wartości z Twojego pliku:</span>
                            {k.przyklady.filter(Boolean).length > 0 ? (
                              k.przyklady
                                .filter(Boolean)
                                .slice(0, 3)
                                .map((w, i) => (
                                  <span key={i} className="przyklad-wartosc">
                                    {w}
                                  </span>
                                ))
                            ) : (
                              <span className="przyklad-pusty">kolumna pusta</span>
                            )}
                          </span>
                        )}
                      </td>
                      <td data-etykieta="Co zawiera">
                        <label htmlFor={id} className="wizualnie-ukryte">
                          Pole dla kolumny {k.nazwa}
                        </label>
                        <select
                          id={id}
                          value={wybor ?? ""}
                          onChange={(e) => zmienMapowanie(k.nazwa, e.target.value || null)}
                          aria-invalid={maBlad(dotyczy) ? true : undefined}
                          aria-describedby={opisDla(dotyczy, `${id}-prz ${id}-pod`)}
                        >
                          <option value="">— nie importuj —</option>
                          <optgroup label="Kilka pól w jednej kolumnie">
                            {Object.entries(SPECJALNE).map(([pole, s]) => (
                              <option key={pole} value={pole} disabled={zajete.has(pole) && zajete.get(pole) !== k.nazwa}>
                                {s.nazwa}
                                {zajete.has(pole) && zajete.get(pole) !== k.nazwa ? " (już wybrane)" : ""}
                              </option>
                            ))}
                          </optgroup>
                          {polaDoWyboru.map(([grupa, pola]) => (
                            <optgroup key={grupa} label={grupa}>
                              {pola.map((p) => {
                                const inna = zajete.has(p.pole) && zajete.get(p.pole) !== k.nazwa;
                                return (
                                  <option key={p.pole} value={p.pole} disabled={inna}>
                                    {p.nazwa}
                                    {p.wymagalnosc === "O" ? " (obowiązkowe)" : ""}
                                    {inna ? " (już wybrane)" : ""}
                                  </option>
                                );
                              })}
                            </optgroup>
                          ))}
                        </select>
                      </td>
                      <td data-etykieta="Podpowiedź" id={`${id}-pod`}>
                        {prop && zgodna && pew ? (
                          <>
                            <span className={`pewnosc ${pew.klasa}`}>
                              {pew.tekst}: {Math.round(prop.pewnosc * 100)}%
                            </span>
                            <span className="powod">{prop.powod}</span>
                          </>
                        ) : prop && !zgodna ? (
                          <span className="powod">
                            Zmieniono ręcznie. Podpowiedź: {prop.pole ? nazwaPola(schemat, prop.pole) : "nie importuj"}.
                          </span>
                        ) : (
                          <span className="powod">Brak podpowiedzi.</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {doStalych.length > 0 && (
            <>
              <h2>Ustaw dla wszystkich AED w pliku</h2>
              <p>
                Tych pól obowiązkowych nie ma w Twoim pliku. Jeśli odpowiedź jest taka sama dla wszystkich urządzeń,
                wybierz ją tutaj. Jeśli się różni, dodaj kolumnę w pliku.
              </p>
              {doStalych.map((pole) => {
                const def = schemat?.pola.find((p) => p.pole === pole);
                if (!def) return null;
                const opcje =
                  def.typ === "logiczny"
                    ? [
                        { kod: "true", znaczenie: "Tak" },
                        { kod: "false", znaczenie: "Nie" },
                      ]
                    : schemat?.slowniki[def.slownik ?? ""] ?? [];
                const id = `stala-${pole}`;
                return (
                  <div className="pole" key={pole}>
                    <label htmlFor={id}>{def.nazwa}</label>
                    <span id={`${id}-podp`} className="podpowiedz">
                      {def.opis}
                    </span>
                    <select
                      id={id}
                      value={wartosciStale[pole] ?? ""}
                      onChange={(e) => zmienStala(pole, e.target.value)}
                      aria-invalid={maBlad([pole]) ? true : undefined}
                      aria-describedby={opisDla([pole], `${id}-podp`)}
                    >
                      <option value="">— nie ustawiaj —</option>
                      {opcje.map((o) => (
                        <option key={o.kod} value={o.kod}>
                          {etykietaSlownika(o.znaczenie)}
                        </option>
                      ))}
                    </select>
                  </div>
                );
              })}
            </>
          )}

          <div className="akcje">
            <button type="button" onClick={sprawdz} disabled={sprawdzam || wgrywam}>
              {sprawdzam ? "Sprawdzam…" : walidacja ? "Sprawdź ponownie" : "Sprawdź dane"}
            </button>
            {sprawdzam && (
              <span className="ladowanie">Szukamy adresów na mapie. Przy dużym pliku to potrwa do 2 minut.</span>
            )}
          </div>
          {walidacja && !aktualna && !sprawdzam && (
            <div className="ramka ramka-info">
              <p>Zmieniono ustawienia. Sprawdź dane ponownie, zanim przejdziesz dalej.</p>
            </div>
          )}

          {walidacja && (
            <>
              <h2 ref={wynikRef} tabIndex={-1}>
                Wynik sprawdzenia
              </h2>
              <ul className="liczniki">
                <li>
                  Do publikacji: <strong>{walidacja.liczba_rekordow}</strong>
                </li>
                <li>
                  Pominięte: <strong>{walidacja.liczba_pominietych}</strong>
                </li>
                <li>
                  Błędy: <strong>{walidacja.liczba_bledow}</strong>
                </li>
                <li>
                  Ostrzeżenia: <strong>{walidacja.liczba_ostrzezen}</strong>
                </li>
              </ul>
              {walidacja.mozna_publikowac ? (
                <div className="ramka ramka-ok">
                  <p>
                    <strong>Dane są gotowe do publikacji.</strong>
                    {walidacja.liczba_ostrzezen > 0 && " Ostrzeżenia nie blokują publikacji, ale warto je poprawić w pliku."}
                  </p>
                </div>
              ) : (
                <div className="ramka ramka-blad">
                  <p>
                    <strong>
                      Popraw {liczba(walidacja.liczba_bledow, "błąd", "błędy", "błędów")}, zanim opublikujesz.
                    </strong>{" "}
                    Zmień dopasowanie kolumn albo popraw plik i wgraj go ponownie.
                  </p>
                </div>
              )}
              {walidacja.liczba_pominietych > 0 && (
                <div className="ramka ramka-ostrzezenie">
                  <p>
                    <strong>
                      {liczba(walidacja.liczba_pominietych, "rekord pominiemy", "rekordy pominiemy", "rekordów pominiemy")}
                    </strong>
                    : nie znaleźliśmy adresu na mapie albo plik ma ponad 200 adresów bez współrzędnych. Te AED nie
                    trafią do publikacji. Dodaj w pliku współrzędne, żeby je uwzględnić.
                  </p>
                </div>
              )}
              <Komunikaty komunikaty={walidacja.komunikaty} schemat={schemat} prefiks={PREFIKS} />

              {walidacja.podglad_wyniku.length > 0 && (
                <details>
                  <summary>Podgląd wyniku (pierwsze {walidacja.podglad_wyniku.length} rekordów)</summary>
                  <PodgladWyniku wiersze={walidacja.podglad_wyniku} schemat={schemat} />
                </details>
              )}
            </>
          )}
        </>
      )}

      <div className="akcje akcje-miedzy">
        {onWstecz ? (
          <button type="button" className="drugorzedny" onClick={onWstecz}>
            Wstecz
          </button>
        ) : (
          <span />
        )}
        <button type="button" onClick={onDalej} disabled={!moznaDalej} aria-describedby={moznaDalej ? undefined : "dalej-podp"}>
          Dalej: publikacja
        </button>
      </div>
      {!moznaDalej && (
        <p id="dalej-podp" className="drobny" style={{ textAlign: "right" }}>
          {!imp
            ? "Najpierw wgraj plik."
            : !walidacja || !aktualna
              ? "Najpierw sprawdź dane."
              : "Popraw błędy, aby przejść dalej."}
        </p>
      )}
    </section>
  );
}

function PodgladWyniku({ wiersze, schemat }: { wiersze: Record<string, string>[]; schemat: SchematOut | null }) {
  const kolumny = [...new Set(wiersze.flatMap((w) => Object.keys(w)))];
  return (
    <div className="tabela-przewijana" tabIndex={0} role="region" aria-label="Podgląd wyniku, przewijana tabela">
      <table className="podglad-tabela">
        <thead>
          <tr>
            {kolumny.map((k) => (
              <th key={k} scope="col">
                {nazwaPola(schemat, k)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {wiersze.map((w, i) => (
            <tr key={i}>
              {kolumny.map((k) => (
                <td key={k}>{w[k] ?? ""}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
