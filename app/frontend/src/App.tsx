// Kreator 3 kroków (app/PLAN.md, sekcja 4). Ścieżka /edycja/{slug}?token=… pomija krok 1.
import { useEffect, useRef, useState } from "react";
import { api } from "./api/client";
import type { Dysponent, ImportOut, PublikacjaOut, SchematOut, WalidacjaOut } from "./api/types";
import { Logo } from "./components/Logo";
import { Postep, type KrokOpis } from "./components/Postep";
import { Krok1Dysponent } from "./kroki/Krok1Dysponent";
import { Start } from "./kroki/Start";

type Krok = "start" | "dysponent" | "dane" | "publikacja";

const KROKI: KrokOpis[] = [
  { id: "dysponent", nazwa: "Dysponent" },
  { id: "dane", nazwa: "Dane" },
  { id: "publikacja", nazwa: "Publikacja" },
];

const TYTULY: Record<Krok, string> = {
  start: "Opublikuj dane o defibrylatorach",
  dysponent: "Krok 1 z 3: Dysponent",
  dane: "Krok 2 z 3: Dane",
  publikacja: "Krok 3 z 3: Publikacja",
};

export default function App() {
  const [krok, setKrok] = useState<Krok>("start");
  const [dysponent, setDysponent] = useState<Dysponent | null>(null);
  const [imp, setImp] = useState<ImportOut | null>(null);
  const [walidacja, setWalidacja] = useState<WalidacjaOut | null>(null);
  const [publikacja, setPublikacja] = useState<PublikacjaOut | null>(null);
  void [dysponent, setDysponent, imp, setImp, walidacja, setWalidacja, publikacja, setPublikacja];
  const pierwszyRender = useRef(true);
  const [schemat, setSchemat] = useState<SchematOut | null>(null);
  const [bladSchematu, setBladSchematu] = useState<string | null>(null);

  useEffect(() => {
    api
      .schemat()
      .then(setSchemat)
      .catch(() => setBladSchematu("Nie udało się wczytać słowników z serwera. Odśwież stronę za chwilę."));
  }, []);

  // WCAG 2.4.2 / 2.4.3: tytuł strony i fokus na nagłówek po zmianie kroku.
  useEffect(() => {
    document.title = `${TYTULY[krok]} | TuAED`;
    if (pierwszyRender.current) {
      pierwszyRender.current = false;
      return;
    }
    document.getElementById("naglowek-kroku")?.focus();
  }, [krok]);

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
        {krok !== "start" && <Postep kroki={KROKI} biezacy={krok} />}
        {krok === "start" && <Start onZacznij={() => setKrok("dysponent")} />}
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
        {(krok === "dane" || krok === "publikacja") && (
          <section aria-labelledby="naglowek-kroku">
            <h1 id="naglowek-kroku" tabIndex={-1}>
              {TYTULY[krok]}
            </h1>
            <p>Do zrobienia.</p>
          </section>
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
