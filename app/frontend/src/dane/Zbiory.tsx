import { useEffect, useState } from "react";
import type { SchematOut, StatusSynchronizacji } from "../api/types";
import { etykietaSlownika } from "../lib/pola";
import { fmt } from "../lib/agregat";
import { pobierzZbiory, type ZbiorPubliczny } from "./zbioryApi";

const SYNC: Record<StatusSynchronizacji, string> = {
  brak: "ręcznie",
  aktywna: "automatyczna, aktywna",
  wstrzymana: "automatyczna, wstrzymana",
  blad: "automatyczna, błąd pobierania",
};

export const data = (iso: string | null | undefined) =>
  iso ? new Date(iso).toLocaleDateString("pl-PL", { day: "numeric", month: "short", year: "numeric" }) : "—";

export function Zbiory({ schemat }: { schemat: SchematOut | null }) {
  const [zbiory, setZbiory] = useState<ZbiorPubliczny[] | null>(null);
  const [blad, setBlad] = useState<"brak-api" | "inny" | null>(null);

  useEffect(() => {
    pobierzZbiory()
      .then((z) => setZbiory([...z].sort((a, b) => b.zaktualizowano.localeCompare(a.zaktualizowano))))
      .catch((e) => setBlad(e?.status === 404 || e?.status === 405 ? "brak-api" : "inny"));
  }, []);

  const typ = (kod: string | null) => {
    if (!kod) return null;
    const poz = schemat?.slowniki["dysponent_typ"]?.find((x) => x.kod === kod);
    return poz ? etykietaSlownika(poz.znaczenie) : kod;
  };
  const suma = zbiory?.reduce((s, z) => s + z.liczba_rekordow, 0) ?? 0;

  return (
    <section aria-labelledby="zbiory-naglowek">
      <h2 id="zbiory-naglowek">Zbiory dostawców</h2>
      <p>
        Dane opublikowane przez instytucje w AEDane. Każdy zbiór ma stały adres, który dostawca dodał na dane.gov.pl.
      </p>
      {!zbiory && !blad && (
        <p role="status" className="ladowanie">
          Wczytuję listę zbiorów…
        </p>
      )}
      {blad && (
        <div className="ramka ramka-info" role="status">
          <p>
            {blad === "brak-api"
              ? "Lista zbiorów będzie tu dostępna wkrótce."
              : "Nie udało się wczytać listy zbiorów. Spróbuj odświeżyć stronę."}
          </p>
        </div>
      )}
      {zbiory && (
        <>
          <p role="status">
            {zbiory.length
              ? `${fmt(zbiory.length)} ${zbiory.length === 1 ? "zbiór" : "zbiorów"}, razem ${fmt(suma)} AED.`
              : "Nikt jeszcze nie opublikował danych."}
          </p>
          {zbiory.length > 0 && (
            <div className="tabela-przewijana">
              <table className="tabela-karty tabela-zbiory">
                <caption className="wizualnie-ukryte">Zbiory dostawców, od ostatnio zaktualizowanych</caption>
                <thead>
                  <tr>
                    <th scope="col">Dysponent</th>
                    <th scope="col">AED</th>
                    <th scope="col">Aktualizacja</th>
                    <th scope="col">Aktualizowanie</th>
                    <th scope="col">Pliki</th>
                  </tr>
                </thead>
                <tbody>
                  {zbiory.map((z) => (
                    <tr key={z.slug}>
                      <th scope="row" data-etykieta="Dysponent">
                        {z.dysponent_nazwa}
                        {typ(z.dysponent_typ) && <span className="drobny wiersz-pod">{typ(z.dysponent_typ)}</span>}
                      </th>
                      <td data-etykieta="AED">{fmt(z.liczba_rekordow)}</td>
                      <td data-etykieta="Aktualizacja">{data(z.zaktualizowano)}</td>
                      <td data-etykieta="Aktualizowanie">
                        {z.synchronizacja ? SYNC[z.synchronizacja.status] : "ręcznie"}
                      </td>
                      <td data-etykieta="Pliki">
                        <ul className="pliki">
                          <li>
                            <a href={z.url_csv}>
                              CSV<span className="wizualnie-ukryte">: {z.dysponent_nazwa}</span>
                            </a>
                          </li>
                          <li>
                            <a href={z.url_json}>
                              JSON<span className="wizualnie-ukryte">: {z.dysponent_nazwa}</span>
                            </a>
                          </li>
                          <li>
                            <a href={z.url_geojson}>
                              GeoJSON<span className="wizualnie-ukryte">: {z.dysponent_nazwa}</span>
                            </a>
                          </li>
                          <li>
                            <a href={z.url_metadane}>
                              CSVW<span className="wizualnie-ukryte">: metadane, {z.dysponent_nazwa}</span>
                            </a>
                          </li>
                        </ul>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
      <p className="ramka ramka-ok">
        Twojej instytucji tu nie ma? <a href="/">Opublikuj dane o swoich AED</a>. Zajmie to kilka minut.
      </p>
    </section>
  );
}
