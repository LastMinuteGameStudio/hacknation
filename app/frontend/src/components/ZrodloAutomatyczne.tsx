// S1: synchronizacja zbioru z pliku pod stałym adresem (KONTRAKT.md, „Synchronizacja z URL źródła”).
import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError } from "../api/client";
import type { SchematOut, StatusSynchronizacji, SynchronizacjaOut } from "../api/types";
import { Komunikaty } from "./Komunikaty";

const CZESTOTLIWOSCI = [
  { h: 6, nazwa: "co 6 godzin" },
  { h: 12, nazwa: "co 12 godzin" },
  { h: 24, nazwa: "raz dziennie" },
  { h: 168, nazwa: "raz w tygodniu" },
];

const STATUS: Record<StatusSynchronizacji, { tekst: string; ramka: string }> = {
  brak: { tekst: "Nie ustawiono", ramka: "ramka-info" },
  aktywna: { tekst: "Aktywna", ramka: "ramka-ok" },
  wstrzymana: { tekst: "Wstrzymana: dane nie zostały podmienione, potrzebna Twoja decyzja", ramka: "ramka-ostrzezenie" },
  blad: { tekst: "Błąd pobierania: spróbujemy ponownie przy następnym terminie", ramka: "ramka-blad" },
};

const data = (iso: string | null) =>
  iso ? new Date(iso).toLocaleString("pl-PL", { dateStyle: "medium", timeStyle: "short" }) : "nigdy";

type Akcja = "zapisz" | "teraz" | "wymus" | "wylacz";
const AKCJA_TEKST: Record<Akcja, string> = {
  zapisz: "Zapisuję i pobieram plik…",
  teraz: "Pobieram plik…",
  wymus: "Publikuję zmienione dane…",
  wylacz: "Wyłączam…",
};

interface Props {
  slug: string;
  token: string;
  schemat: SchematOut | null;
}

export function ZrodloAutomatyczne({ slug, token, schemat }: Props) {
  const [sync, setSync] = useState<SynchronizacjaOut | null>(null);
  const [url, setUrl] = useState("");
  const [coIle, setCoIle] = useState(24);
  const [bladUrl, setBladUrl] = useState<string | null>(null);
  const [blad, setBlad] = useState<string | null>(null);
  const [akcja, setAkcja] = useState<Akcja | null>(null);

  const przyjmij = (s: SynchronizacjaOut) => {
    setSync(s);
    setUrl(s.url ?? "");
    if (s.co_ile_godzin) setCoIle(s.co_ile_godzin);
  };

  useEffect(() => {
    api
      .zrodlo(slug, token)
      .then(przyjmij)
      .catch(() => setBlad("Nie udało się wczytać ustawień źródła automatycznego."));
  }, [slug, token]);

  async function wykonaj(a: Akcja, wywolanie: () => Promise<SynchronizacjaOut>) {
    setBlad(null);
    setAkcja(a);
    try {
      przyjmij(await wywolanie());
    } catch (e) {
      if (e instanceof ApiError && e.blad.kod === "ZLY_URL") {
        setBladUrl(e.blad.komunikat || "Ten adres nie jest dozwolony. Podaj publiczny adres http lub https.");
        document.getElementById("zrodlo-url")?.focus();
      } else {
        setBlad(e instanceof ApiError ? e.blad.komunikat : "Brak połączenia z serwerem. Spróbuj ponownie.");
      }
    } finally {
      setAkcja(null);
    }
  }

  function zapisz(e: FormEvent) {
    e.preventDefault();
    const u = url.trim();
    if (!/^https?:\/\/\S+$/i.test(u)) {
      setBladUrl("Wpisz pełny adres pliku, zaczynający się od https:// lub http://.");
      document.getElementById("zrodlo-url")?.focus();
      return;
    }
    setBladUrl(null);
    void wykonaj("zapisz", () => api.ustawZrodlo(slug, token, { url: u, co_ile_godzin: coIle }));
  }

  const ustawione = !!sync && sync.status !== "brak" && !!sync.url;
  const zaDuzaZmiana = sync?.status === "wstrzymana" && sync.komunikaty.some((k) => k.kod === "ZA_DUZA_ZMIANA");
  const zajety = akcja !== null;

  return (
    <section aria-labelledby="zrodlo-naglowek" className="zrodlo">
      <h2 id="zrodlo-naglowek">Źródło automatyczne (opcjonalnie)</h2>
      <p>
        Jeśli Twój plik z AED leży pod stałym adresem (np. na stronie urzędu), podaj go tutaj. Będziemy go pobierać
        regularnie i publikować nową wersję pod tym samym adresem. Zmiana kolumn albo błędy w danych wstrzymują
        pobieranie, a dotychczasowe dane zostają bez zmian.
      </p>

      {!sync && !blad && (
        <p className="ladowanie" role="status">
          Wczytuję ustawienia…
        </p>
      )}

      {sync && (
        <>
          <div className={`ramka ${STATUS[sync.status].ramka}`}>
            <p>
              <strong>Stan: {STATUS[sync.status].tekst}.</strong>
            </p>
            {sync.status !== "brak" && (
              <p className="drobny">
                Ostatnia próba: {data(sync.ostatnia_proba)}. Ostatnia udana: {data(sync.ostatni_sukces)}. Opublikowanych
                AED: {sync.liczba_rekordow}.
              </p>
            )}
          </div>
          <Komunikaty komunikaty={sync.komunikaty} schemat={schemat} prefiks="ks" />
          {zaDuzaZmiana && (
            <div className="akcje">
              <button
                type="button"
                disabled={zajety}
                onClick={() => wykonaj("wymus", () => api.synchronizuj(slug, token, true))}
              >
                Potwierdź zmianę i opublikuj
              </button>
              <span className="drobny">Użyj, jeśli duża zmiana w pliku jest zamierzona.</span>
            </div>
          )}

          <form onSubmit={zapisz} noValidate>
            <div className="pole">
              <label htmlFor="zrodlo-url">Adres pliku CSV lub XLSX</label>
              <span id="zrodlo-url-podp" className="podpowiedz">
                Publiczny adres, np. https://www.krosno.pl/dane/aed.csv. Układ kolumn musi być taki jak w ostatnio
                wgranym pliku.
              </span>
              <input
                id="zrodlo-url"
                type="text"
                inputMode="url"
                autoComplete="url"
                spellCheck={false}
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  setBladUrl(null);
                }}
                aria-invalid={bladUrl ? true : undefined}
                aria-describedby={["zrodlo-url-podp", bladUrl ? "zrodlo-url-blad" : null].filter(Boolean).join(" ")}
              />
              {bladUrl && (
                <span id="zrodlo-url-blad" className="blad-pola">
                  {bladUrl}
                </span>
              )}
            </div>
            <div className="pole">
              <label htmlFor="zrodlo-co-ile">Jak często pobierać</label>
              <select id="zrodlo-co-ile" value={coIle} onChange={(e) => setCoIle(Number(e.target.value))}>
                {!CZESTOTLIWOSCI.some((c) => c.h === coIle) && <option value={coIle}>co {coIle} godz.</option>}
                {CZESTOTLIWOSCI.map((c) => (
                  <option key={c.h} value={c.h}>
                    {c.nazwa}
                  </option>
                ))}
              </select>
            </div>
            <div className="akcje">
              <button type="submit" disabled={zajety}>
                {ustawione ? "Zapisz i pobierz teraz" : "Włącz i pobierz teraz"}
              </button>
              {ustawione && (
                <>
                  <button
                    type="button"
                    className="drugorzedny"
                    disabled={zajety}
                    onClick={() => wykonaj("teraz", () => api.synchronizuj(slug, token))}
                  >
                    Synchronizuj teraz
                  </button>
                  <button
                    type="button"
                    className="drugorzedny"
                    disabled={zajety}
                    onClick={() => wykonaj("wylacz", () => api.ustawZrodlo(slug, token, { url: null }))}
                  >
                    Wyłącz
                  </button>
                </>
              )}
            </div>
          </form>
        </>
      )}

      <p role="status" className="ladowanie">
        {akcja ? `${AKCJA_TEKST[akcja]} Przy dużym pliku to potrwa do 2 minut.` : ""}
      </p>
      {blad && (
        <div className="ramka ramka-blad" role="alert">
          <p>{blad}</p>
        </div>
      )}
    </section>
  );
}
