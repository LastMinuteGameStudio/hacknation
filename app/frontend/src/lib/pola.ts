// Pomocnicze opisy pól v0.5 i pól specjalnych mapowania (app/KONTRAKT.md, sekcja 2).
import type { Komunikat, Mapowanie, SchematOut } from "../api/types";

/** Pola specjalne: jedna kolumna z pliku rozbijana na kilka pól v0.5. */
export const SPECJALNE: Record<string, { nazwa: string; pokrywa: string[] }> = {
  _adres_pelny: {
    nazwa: "Adres w jednym polu (rozbijemy na ulicę, numer, kod, miejscowość)",
    pokrywa: ["cecha_ulicy", "nazwa_ulicy", "nr_budynku", "nr_lokalu", "kod_pocztowy", "miejscowosc"],
  },
  _geometria: {
    nazwa: "Współrzędne w jednym polu (geometria: JSON lub WKT)",
    pokrywa: ["szerokosc_geograficzna", "dlugosc_geograficzna"],
  },
  _godziny: {
    nazwa: "Godziny w jednym polu (np. „pn-pt 8-16”, „24h”)",
    pokrywa: [
      "dostepny_24_7", "godziny_pn", "godziny_wt", "godziny_sr", "godziny_cz",
      "godziny_pt", "godziny_so", "godziny_nd", "godziny_swieta",
    ],
  },
};

/** Pola wypełniane automatycznie przez system: nie pokazujemy ich w liście mapowania. */
export const POLA_AUTOMATYCZNE = new Set(["id_aed", "data_aktualizacji", "status_walidacji", "duplikat_id_aed", "zrodlo_danych"]);

/** Pola O, które można ustawić jedną wartością dla wszystkich AED w pliku (wartosci_stale). */
export const KANDYDACI_STALE = ["wewnatrz_budynku", "dostepnosc", "dostepny_24_7", "status"];

export function nazwaPola(schemat: SchematOut | null, pole: string | null): string {
  if (!pole) return "Cały plik";
  if (SPECJALNE[pole]) return SPECJALNE[pole].nazwa;
  return schemat?.pola.find((p) => p.pole === pole)?.nazwa ?? pole;
}

/** Bez dopisków technicznych typu „(OSM: access=yes)”. */
export function etykietaSlownika(znaczenie: string): string {
  return znaczenie.replace(/\s*\(OSM:[^)]*\)\s*$/, "");
}

/** Pola v0.5 pokryte mapowaniem (bezpośrednio albo przez pole specjalne). */
export function polaPokryte(mapowanie: Mapowanie): Set<string> {
  const s = new Set<string>();
  for (const pole of Object.values(mapowanie)) {
    if (!pole) continue;
    s.add(pole);
    SPECJALNE[pole]?.pokrywa.forEach((p) => s.add(p));
  }
  return s;
}

/** Pola v0.5, których dotyczy wybór w liście mapowania (do powiązania z komunikatami). */
export function polaWyboru(pole: string | null): string[] {
  if (!pole) return [];
  return SPECJALNE[pole] ? [pole, ...SPECJALNE[pole].pokrywa] : [pole];
}

export const idGrupy = (prefiks: string, pole: string | null) => `${prefiks}-${pole ?? "plik"}`;

export interface GrupaKomunikatow {
  pole: string | null;
  bledy: number;
  ostrzezenia: number;
  pozycje: { poziom: Komunikat["poziom"]; kod: string; komunikat: string; wiersze: number[] }[];
}

const WAGA = { blad: 0, ostrzezenie: 1, info: 2 } as const;

/** Grupuje po polu; ten sam komunikat w wielu wierszach łączy w jedną pozycję z listą wierszy. */
export function grupuj(komunikaty: Komunikat[]): GrupaKomunikatow[] {
  const mapa = new Map<string, GrupaKomunikatow>();
  for (const k of komunikaty) {
    const klucz = k.pole ?? "";
    let g = mapa.get(klucz);
    if (!g) {
      g = { pole: k.pole, bledy: 0, ostrzezenia: 0, pozycje: [] };
      mapa.set(klucz, g);
    }
    if (k.poziom === "blad") g.bledy++;
    if (k.poziom === "ostrzezenie") g.ostrzezenia++;
    let poz = g.pozycje.find((p) => p.kod === k.kod && p.komunikat === k.komunikat && p.poziom === k.poziom);
    if (!poz) {
      poz = { poziom: k.poziom, kod: k.kod, komunikat: k.komunikat, wiersze: [] };
      g.pozycje.push(poz);
    }
    if (k.wiersz != null) poz.wiersze.push(k.wiersz);
  }
  const grupy = [...mapa.values()];
  grupy.forEach((g) => {
    g.pozycje.sort((a, b) => WAGA[a.poziom] - WAGA[b.poziom]);
    g.pozycje.forEach((p) => p.wiersze.sort((a, b) => a - b));
  });
  const ranga = (g: GrupaKomunikatow) => (g.bledy ? 0 : g.ostrzezenia ? 1 : 2);
  return grupy.sort((a, b) => ranga(a) - ranga(b) || (a.pole === null ? -1 : b.pole === null ? 1 : 0));
}
