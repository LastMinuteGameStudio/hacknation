// Kontrakt API (app/KONTRAKT.md, sekcja 2). Lustro: backend/app/api_models.py.

export type Poziom = "blad" | "ostrzezenie" | "info";

/** Specjalne wartości mapowania (nie są polami v0.5). */
export const POLA_SPECJALNE = ["_geometria", "_adres_pelny", "_godziny"] as const;

export interface Komunikat {
  poziom: Poziom;
  kod: string;
  komunikat: string;
  wiersz: number | null;
  pole: string | null;
}

export interface Dysponent {
  nazwa: string;
  typ: string;
  telefon?: string | null;
  email?: string | null;
}

export interface PoleSchematu {
  pole: string;
  nazwa: string;
  grupa: string;
  typ: string;
  format: string;
  wymagalnosc: "O" | "Z" | "F";
  publiczne: boolean;
  opis: string;
  przyklad: string;
  slownik: string | null;
}

export interface SchematOut {
  wersja: string;
  pola: PoleSchematu[];
  slowniki: Record<string, { kod: string; znaczenie: string }[]>;
}

export interface Kolumna {
  indeks: number;
  nazwa: string;
  przyklady: string[];
}

export interface PropozycjaMapowania {
  kolumna: string;
  pole: string | null;
  pewnosc: number;
  powod: string;
}

export interface ImportOut {
  import_id: string;
  plik_nazwa: string;
  liczba_wierszy: number;
  arkusze: string[];
  kolumny: Kolumna[];
  podglad: string[][];
  mapowanie_propozycja: PropozycjaMapowania[];
  komunikaty: Komunikat[];
}

export type Mapowanie = Record<string, string | null>;

export interface WalidacjaIn {
  mapowanie: Mapowanie;
  dysponent: Dysponent;
  /** pole v0.5 -> wartość dla wszystkich AED w pliku (pola O bez kolumny) */
  wartosci_stale?: Record<string, string>;
}

export interface WalidacjaOut {
  liczba_rekordow: number;
  /** rekordy niepublikowane (adres nieznaleziony przez geokoder) */
  liczba_pominietych: number;
  liczba_bledow: number;
  liczba_ostrzezen: number;
  komunikaty: Komunikat[];
  podglad_wyniku: Record<string, string>[];
  mozna_publikowac: boolean;
}

export interface PublikacjaOut {
  slug: string;
  token_edycji: string | null;
  url_csv: string;
  url_json: string;
  url_metadane: string;
  url_edycji: string;
}

export interface BladApi {
  kod: string;
  komunikat: string;
}
