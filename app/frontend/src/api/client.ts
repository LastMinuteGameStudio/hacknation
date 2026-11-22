import type {
  BladApi,
  ImportOut,
  PublikacjaOut,
  SchematOut,
  SynchronizacjaIn,
  SynchronizacjaOut,
  WalidacjaIn,
  WalidacjaOut,
  ZbiorOut,
} from "./types";

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

  zrodlo: (slug: string, token: string) =>
    fetch(`/api/zbiory/${encodeURIComponent(slug)}/zrodlo?token=${encodeURIComponent(token)}`).then((r) =>
      json<SynchronizacjaOut>(r),
    ),

  ustawZrodlo: (slug: string, token: string, body: SynchronizacjaIn) =>
    fetch(`/api/zbiory/${encodeURIComponent(slug)}/zrodlo?token=${encodeURIComponent(token)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => json<SynchronizacjaOut>(r)),

  synchronizuj: (slug: string, token: string, wymus = false) =>
    fetch(
      `/api/zbiory/${encodeURIComponent(slug)}/synchronizacja?token=${encodeURIComponent(token)}${wymus ? "&wymus=true" : ""}`,
      { method: "POST" },
    ).then((r) => json<SynchronizacjaOut>(r)),

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
