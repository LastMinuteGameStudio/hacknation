// Treść popupu budowana przez DOM (textContent): dane pochodzą z wielu źródeł, nie wstrzykujemy HTML.
import type { SchematOut } from "../api/types";
import { etykietaSlownika } from "../lib/pola";

export type Pochodzenie = "tuaed" | "urzad" | "osm";

export function pochodzenie(zrodlo: string | undefined): Pochodzenie {
  if (!zrodlo) return "urzad";
  if (zrodlo.startsWith("tuaed:")) return "tuaed";
  if (zrodlo === "osm") return "osm";
  return "urzad";
}

export const POCHODZENIE_NAZWA: Record<Pochodzenie, string> = {
  tuaed: "Od dostawcy przez TuAED",
  urzad: "Otwarte dane urzędów i instytucji",
  osm: "OpenStreetMap",
};

const DNI: [string, string][] = [
  ["godziny_pn", "pn"], ["godziny_wt", "wt"], ["godziny_sr", "śr"], ["godziny_cz", "cz"],
  ["godziny_pt", "pt"], ["godziny_so", "so"], ["godziny_nd", "nd"],
];

/** „pn–pt 8:00-16:00; so 9:00-13:00”: łączy kolejne dni o tych samych godzinach. */
export function godziny(p: Record<string, string>): string | null {
  const wpisy = DNI.map(([k, d]) => [d, p[k]] as const);
  if (wpisy.every(([, v]) => !v)) return null;
  const czesci: string[] = [];
  let i = 0;
  while (i < wpisy.length) {
    let j = i;
    while (j + 1 < wpisy.length && wpisy[j + 1][1] === wpisy[i][1]) j++;
    if (wpisy[i][1]) czesci.push(`${wpisy[i][0]}${j > i ? "–" + wpisy[j][0] : ""} ${wpisy[i][1]}`);
    i = j + 1;
  }
  if (p.godziny_swieta) czesci.push(`święta ${p.godziny_swieta}`);
  return czesci.join("; ");
}

export function adres(p: Record<string, string>): string | null {
  const ulica = [p.nazwa_ulicy, p.nr_budynku].filter(Boolean).join(" ") + (p.nr_lokalu ? `/${p.nr_lokalu}` : "");
  const miasto = [p.kod_pocztowy, p.miejscowosc].filter(Boolean).join(" ");
  const s = [ulica, miasto].filter(Boolean).join(", ");
  return s || null;
}

export function tytul(p: Record<string, string>): string {
  return p.nazwa_obiektu || p.opis_lokalizacji || "Defibrylator AED";
}

export function budujPopup(p: Record<string, string>, schemat: SchematOut | null): HTMLElement {
  const slownik = (nazwa: string, kod: string | undefined) => {
    if (!kod) return null;
    const poz = schemat?.slowniki[nazwa]?.find((x) => x.kod === kod);
    return poz ? etykietaSlownika(poz.znaczenie) : kod;
  };
  const el = document.createElement("div");
  el.className = "popup-aed";
  el.tabIndex = -1;
  const h = document.createElement("h2");
  h.textContent = tytul(p);
  el.append(h);
  const dl = document.createElement("dl");
  const wiersz = (etykieta: string, wartosc: string | null | undefined) => {
    if (!wartosc) return;
    const dt = document.createElement("dt");
    dt.textContent = etykieta;
    const dd = document.createElement("dd");
    dd.textContent = wartosc;
    dl.append(dt, dd);
  };
  wiersz("Adres", adres(p));
  wiersz("Gdzie dokładnie", p.nazwa_obiektu ? p.opis_lokalizacji : null);
  wiersz("Położenie", p.wewnatrz_budynku === "true" ? "w budynku" : p.wewnatrz_budynku === "false" ? "na zewnątrz" : null);
  wiersz("Kto ma dostęp", slownik("dostepnosc", p.dostepnosc));
  wiersz("Całą dobę", slownik("tak_nie_ograniczony", p.dostepny_24_7));
  wiersz("Godziny", godziny(p));
  wiersz("Stan", p.status && p.status !== "nieznany" ? slownik("status", p.status) : null);
  const poch = pochodzenie(p.zrodlo);
  wiersz("Pochodzenie", poch === "urzad" ? `${POCHODZENIE_NAZWA[poch]} (${p.zrodlo})` : POCHODZENIE_NAZWA[poch]);
  wiersz("Dysponent", p.dysponent_nazwa);
  wiersz("Licencja", p.licencja_zrodla);
  wiersz("Aktualizacja", p.data_aktualizacji || p.data_weryfikacji);
  wiersz("Weryfikacja", p.status_walidacji === "oczekuje" ? "oczekuje na weryfikację" : slownik("status_walidacji", p.status_walidacji));
  wiersz("Uwaga", p.duplikat_id_aed ? "prawdopodobnie ten sam AED co inny wpis w pobliżu" : null);
  el.append(dl);
  return el;
}
