import type {
  BladApi,
  Dysponent,
  Mapowanie,
  ImportOut,
  PublikacjaOut,
  SchematOut,
  WalidacjaIn,
  WalidacjaOut,
} from "./types";

/** GET /api/zbiory/{slug}?token=… (KONTRAKT.md, „Edycja przez prywatny link”). Brak w types.ts, więc typ lokalnie. */
export interface ZbiorOut {
  slug: string;
  dysponent: Dysponent;
  utworzono: string;
  zaktualizowano: string;
  liczba_rekordow: number;
  mapowanie: Mapowanie;
}

export class ApiError extends Error {
  constructor(public status: number, public blad: BladApi) {
    super(blad.komunikat);
  }
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let blad: BladApi = { kod: "BLAD_HTTP", komunikat: `Błąd serwera (${res.status}).` };
    try {
      const body = await res.json();
      if (body?.detail?.kod) blad = body.detail;
    } catch {
      /* odpowiedź bez JSON */
    }
    throw new ApiError(res.status, blad);
  }
  return res.json() as Promise<T>;
}

export const api = {
  schemat: () => fetch("/api/schemat").then((r) => json<SchematOut>(r)),

  zbior: (slug: string, token: string) =>
    fetch(`/api/zbiory/${encodeURIComponent(slug)}?token=${encodeURIComponent(token)}`).then((r) => json<ZbiorOut>(r)),

  wgrajPlik: (plik: File, arkusz?: string, edycja?: { slug: string; token: string }) => {
    const fd = new FormData();
    fd.append("plik", plik);
    if (arkusz) fd.append("arkusz", arkusz);
    const url = edycja
      ? `/api/zbiory/${edycja.slug}/importy?token=${encodeURIComponent(edycja.token)}`
      : "/api/importy";
    return fetch(url, { method: "POST", body: fd }).then((r) => json<ImportOut>(r));
  },

  waliduj: (importId: string, body: WalidacjaIn) =>
    fetch(`/api/importy/${importId}/walidacja`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => json<WalidacjaOut>(r)),

  publikuj: (importId: string) =>
    fetch(`/api/importy/${importId}/publikacja`, { method: "POST" }).then((r) => json<PublikacjaOut>(r)),
};
