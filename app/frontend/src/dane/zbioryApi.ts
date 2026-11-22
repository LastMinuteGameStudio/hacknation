// GET /api/zbiory: publiczna lista zbiorów dostawców (KONTRAKT.md, ścieżka B).
import type { ZbiorPublicznyOut } from "../api/types";

export type ZbiorPubliczny = ZbiorPublicznyOut;

export async function pobierzZbiory(): Promise<ZbiorPublicznyOut[]> {
  const r = await fetch("/api/zbiory");
  if (!r.ok) throw Object.assign(new Error(String(r.status)), { status: r.status });
  return r.json();
}
