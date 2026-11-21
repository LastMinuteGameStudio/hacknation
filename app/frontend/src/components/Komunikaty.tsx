import type { Komunikat, SchematOut } from "../api/types";
import { grupuj, idGrupy, nazwaPola } from "../lib/pola";

const POZIOM = { blad: "Błąd", ostrzezenie: "Ostrzeżenie", info: "Informacja" } as const;

function wierszeTekst(w: number[]): string {
  if (!w.length) return "";
  return w.length === 1 ? `wiersz ${w[0]}` : `wiersze ${w.join(", ")}`;
}

/** Lista komunikatów pogrupowana po polach. Grupy mają id, do których odwołują się pola formularza (aria-describedby). */
export function Komunikaty({
  komunikaty,
  schemat,
  prefiks,
  poziomNaglowka = 3,
}: {
  komunikaty: Komunikat[];
  schemat: SchematOut | null;
  prefiks: string;
  poziomNaglowka?: 3 | 4;
}) {
  if (!komunikaty.length) return null;
  const H = `h${poziomNaglowka}` as "h3" | "h4";
  return (
    <div>
      {grupuj(komunikaty).map((g) => (
        <div key={g.pole ?? ""} className="grupa-komunikatow" id={idGrupy(prefiks, g.pole)}>
          <H>
            {nazwaPola(schemat, g.pole)}
            {g.pole && <span className="drobny"> ({g.pole})</span>}
          </H>
          <ul className="komunikaty">
            {g.pozycje.map((p, i) => (
              <li key={i} className={`kom-${p.poziom}`}>
                <span className="poziom">{POZIOM[p.poziom]}:</span> {p.komunikat}
                {p.wiersze.length > 0 && <span className="wiersze"> ({wierszeTekst(p.wiersze)})</span>}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
