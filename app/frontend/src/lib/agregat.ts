// Agregat AED (/d/aed-polska[-bez-osm].geojson): wspólne wczytywanie dla /mapa i /dane.
import type { AedFeatureCollection } from "../api/types";

export type Zakres = "z-osm" | "bez-osm";

export const URL_DANYCH: Record<Zakres, { geojson: string; csv: string }> = {
  "z-osm": { geojson: "/d/aed-polska.geojson", csv: "/d/aed-polska.csv" },
  "bez-osm": { geojson: "/d/aed-polska-bez-osm.geojson", csv: "/d/aed-polska-bez-osm.csv" },
};

const cache: Partial<Record<Zakres, Promise<AedFeatureCollection>>> = {};

export function wczytajAgregat(zakres: Zakres): Promise<AedFeatureCollection> {
  if (!cache[zakres]) {
    cache[zakres] = fetch(URL_DANYCH[zakres].geojson).then((r) => {
      if (!r.ok) throw new Error(String(r.status));
      return r.json() as Promise<AedFeatureCollection>;
    });
    cache[zakres]!.catch(() => delete cache[zakres]);
  }
  return cache[zakres]!;
}

export const fmt = (n: number) => n.toLocaleString("pl-PL");

/** Do wyszukiwania bez polskich znaków i wielkości liter. */
export const normalizuj = (s: string) =>
  s.toLocaleLowerCase("pl-PL").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");
