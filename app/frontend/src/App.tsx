// T0: szkielet kreatora 3 kroków. Ścieżka C rozbudowuje kroki w src/kroki/ (plan: app/PLAN.md, sekcja 4).
import { useState } from "react";
import type { Dysponent, ImportOut, PublikacjaOut, WalidacjaOut } from "./api/types";

type Krok = "start" | "dysponent" | "dane" | "publikacja";

export default function App() {
  const [krok, setKrok] = useState<Krok>("start");
  const [dysponent, setDysponent] = useState<Dysponent | null>(null);
  const [imp, setImp] = useState<ImportOut | null>(null);
  const [walidacja, setWalidacja] = useState<WalidacjaOut | null>(null);
  const [publikacja, setPublikacja] = useState<PublikacjaOut | null>(null);
  void [dysponent, setDysponent, imp, setImp, walidacja, setWalidacja, publikacja, setPublikacja];

  return (
    <>
      <a className="pomin" href="#tresc">Przejdź do treści</a>
      <header>
        <div className="kontener">
          <strong>Misja AED</strong>
        </div>
      </header>
      <main id="tresc">
        {krok === "start" && (
          <section aria-labelledby="tytul">
            <h1 id="tytul">Opublikuj dane o defibrylatorach na dane.gov.pl</h1>
            <p>
              Wgraj swój plik z AED (CSV lub XLSX). Przekształcimy go do wzorcowego formatu, sprawdzimy
              i damy Ci adres, który dodasz na dane.gov.pl.
            </p>
            <p>
              <a href="/szablon.xlsx">Pobierz szablon XLSX</a> · <a href="/szablon.csv">Pobierz szablon CSV</a>
            </p>
            <button onClick={() => setKrok("dysponent")}>Zacznij</button>
          </section>
        )}
        {krok !== "start" && <p>Krok: {krok} (do zrobienia w ścieżce C)</p>}
      </main>
    </>
  );
}
