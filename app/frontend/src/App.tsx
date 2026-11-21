// Kreator 3 kroków (app/PLAN.md, sekcja 4). Ścieżka /edycja/{slug}?token=… pomija krok 1.
import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "./api/client";
import type { Dysponent, PublikacjaOut, SchematOut } from "./api/types";
import { Logo } from "./components/Logo";
import { Postep, type KrokOpis } from "./components/Postep";
import { Krok1Dysponent } from "./kroki/Krok1Dysponent";
import { Krok2Dane, PUSTY_STAN, type StanDanych } from "./kroki/Krok2Dane";
import { Krok3Publikacja } from "./kroki/Krok3Publikacja";
import { Start } from "./kroki/Start";

type Krok = "start" | "dysponent" | "dane" | "publikacja" | "edycja-wczytywanie";
type Edycja = { slug: string; token: string };

function edycjaZAdresu(): Edycja | null {
  const m = window.location.pathname.match(/^\/edycja\/([^/]+)\/?$/);
  const token = new URLSearchParams(window.location.search).get("token");
  return m && token ? { slug: decodeURIComponent(m[1]), token } : null;
}

const KROKI: KrokOpis[] = [
  { id: "dysponent", nazwa: "Dysponent" },
  { id: "dane", nazwa: "Dane" },
  { id: "publikacja", nazwa: "Publikacja" },
];
const KROKI_EDYCJI: KrokOpis[] = [
  { id: "dane", nazwa: "Nowe dane" },
  { id: "publikacja", nazwa: "Publikacja" },
];

export default function App() {
  const [edycja] = useState<Edycja | null>(edycjaZAdresu);
  const [krok, setKrok] = useState<Krok>(edycja ? "edycja-wczytywanie" : "start");
  const [dysponent, setDysponent] = useState<Dysponent | null>(null);
  const [dane, setDane] = useState<StanDanych>(PUSTY_STAN);
  const [publikacja, setPublikacja] = useState<PublikacjaOut | null>(null);
  const [schemat, setSchemat] = useState<SchematOut | null>(null);
  const [bladSchematu, setBladSchematu] = useState<string | null>(null);
  const [bladEdycji, setBladEdycji] = useState<string | null>(null);
  const pierwszyRender = useRef(true);

  useEffect(() => {
    api
      .schemat()
      .then(setSchemat)
      .catch(() => setBladSchematu("Nie udało się wczytać słowników z serwera. Odśwież stronę za chwilę."));
  }, []);

  // Wejście przez prywatny link: dysponent z zapisanego zbioru, od razu krok 2.
  useEffect(() => {
    if (!edycja) return;
    api
      .zbior(edycja.slug, edycja.token)
      .then((z) => {
        setDysponent(z.dysponent);
        setKrok("dane");
      })
      .catch((e) =>
        setBladEdycji(
          e instanceof ApiError && (e.status === 403 || e.blad.kod === "ZLY_TOKEN")
            ? "Ten link do aktualizacji jest nieprawidłowy. Sprawdź, czy skopiowano go w całości."
            : e instanceof ApiError && e.status === 404
              ? "Nie znaleźliśmy tego zbioru danych."
              : "Nie udało się wczytać zbioru. Spróbuj ponownie za chwilę.",
        ),
      );
  }, [edycja]);

  const numer = edycja
    ? KROKI_EDYCJI.findIndex((k) => k.id === krok) + 1
    : KROKI.findIndex((k) => k.id === krok) + 1;
  const kroki = edycja ? KROKI_EDYCJI : KROKI;
  const nazwaKroku = kroki.find((k) => k.id === krok)?.nazwa;
  const tytul = nazwaKroku ? `Krok ${numer} z ${kroki.length}: ${nazwaKroku}` : edycja ? "Aktualizacja danych" : "Opublikuj dane o defibrylatorach";

  // WCAG 2.4.2 / 2.4.3: tytuł strony i fokus na nagłówek po zmianie kroku.
  useEffect(() => {
    document.title = `${tytul} | TuAED`;
    if (pierwszyRender.current) {
      pierwszyRender.current = false;
      return;
    }
    document.getElementById("naglowek-kroku")?.focus();
    window.scrollTo(0, 0);
  }, [krok, tytul]);

  return (
    <>
      <a className="pomin" href="#tresc">
        Przejdź do treści
      </a>
      <header className="naglowek">
        <div className="kontener naglowek-wnetrze">
          <Logo />
          <span className="naglowek-podpis">Otwarte dane o AED</span>
        </div>
      </header>
      <main id="tresc" className="kontener">
        {nazwaKroku && <Postep kroki={kroki} biezacy={krok} />}

        {krok === "start" && <Start onZacznij={() => setKrok("dysponent")} />}

        {krok === "edycja-wczytywanie" && (
          <section aria-labelledby="naglowek-kroku">
            <h1 id="naglowek-kroku" tabIndex={-1}>
              Aktualizacja danych
            </h1>
            {bladEdycji ? (
              <div className="ramka ramka-blad" role="alert">
                <p>{bladEdycji}</p>
                <p>
                  <a href="/">Przejdź do strony głównej</a>
                </p>
              </div>
            ) : (
              <p className="ladowanie" role="status">
                Wczytuję zbiór…
              </p>
            )}
          </section>
        )}

        {krok === "dysponent" && (
          <Krok1Dysponent
            schemat={schemat}
            bladSchematu={bladSchematu}
            poczatkowy={dysponent}
            onWstecz={() => setKrok("start")}
            onDalej={(d) => {
              setDysponent(d);
              setKrok("dane");
            }}
          />
        )}

        {krok === "dane" && dysponent && (
          <Krok2Dane
            schemat={schemat}
            dysponent={dysponent}
            edycja={edycja}
            stan={dane}
            setStan={setDane}
            onWstecz={edycja ? null : () => setKrok("dysponent")}
            onDalej={() => setKrok("publikacja")}
          />
        )}

        {krok === "publikacja" && dane.imp && dane.walidacja && (
          <Krok3Publikacja
            importId={dane.imp.import_id}
            walidacja={dane.walidacja}
            edycja={!!edycja}
            publikacja={publikacja}
            setPublikacja={setPublikacja}
            onWstecz={() => setKrok("dane")}
          />
        )}
      </main>
      <footer className="stopka">
        <div className="kontener">
          Dane publikowane na licencji{" "}
          <a href="https://creativecommons.org/publicdomain/zero/1.0/deed.pl" rel="noopener">
            CC0 1.0
          </a>
          . Zakres danych v0.5. Projekt HackNation 2026.
        </div>
      </footer>
    </>
  );
}
