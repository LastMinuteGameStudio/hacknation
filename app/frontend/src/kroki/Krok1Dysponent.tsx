import { useState, type FormEvent } from "react";
import type { Dysponent, SchematOut } from "../api/types";

type Bledy = Partial<Record<"nazwa" | "typ" | "telefon" | "email", string>>;

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const TELEFON = /^\+?[0-9 ()-]{7,20}$/;

function sprawdz(d: Dysponent): Bledy {
  const b: Bledy = {};
  if (!d.nazwa.trim()) b.nazwa = "Wpisz nazwę instytucji.";
  if (!d.typ) b.typ = "Wybierz typ dysponenta.";
  if (d.telefon && !TELEFON.test(d.telefon.trim())) b.telefon = "Wpisz numer telefonu, np. 13 474 33 00.";
  if (d.email && !EMAIL.test(d.email.trim())) b.email = "Wpisz adres e-mail, np. aed@krosno.pl.";
  return b;
}

interface Props {
  schemat: SchematOut | null;
  bladSchematu: string | null;
  poczatkowy: Dysponent | null;
  onDalej: (d: Dysponent) => void;
  onWstecz: () => void;
}

export function Krok1Dysponent({ schemat, bladSchematu, poczatkowy, onDalej, onWstecz }: Props) {
  const [d, setD] = useState<Dysponent>(poczatkowy ?? { nazwa: "", typ: "", telefon: "", email: "" });
  const [bledy, setBledy] = useState<Bledy>({});
  const typy = schemat?.slowniki["dysponent_typ"] ?? [];

  const zmien = (k: keyof Dysponent) => (e: { target: { value: string } }) => {
    setD({ ...d, [k]: e.target.value });
    if (bledy[k]) setBledy({ ...bledy, [k]: undefined });
  };

  const wyslij = (e: FormEvent) => {
    e.preventDefault();
    const b = sprawdz(d);
    setBledy(b);
    const pierwszy = (["nazwa", "typ", "telefon", "email"] as const).find((k) => b[k]);
    if (pierwszy) {
      document.getElementById(`d-${pierwszy}`)?.focus();
      return;
    }
    onDalej({
      nazwa: d.nazwa.trim(),
      typ: d.typ,
      telefon: d.telefon?.trim() || null,
      email: d.email?.trim() || null,
    });
  };

  const opis = (k: keyof Bledy, podp?: string) =>
    [podp, bledy[k] ? `d-${k}-blad` : null].filter(Boolean).join(" ") || undefined;

  return (
    <section aria-labelledby="naglowek-kroku">
      <h1 id="naglowek-kroku" tabIndex={-1}>
        Kto odpowiada za urządzenia?
      </h1>
      <p>Te dane trafią do każdego AED w pliku jako dysponent.</p>
      {bladSchematu && (
        <div className="ramka ramka-blad" role="alert">
          <p>{bladSchematu}</p>
        </div>
      )}
      <form onSubmit={wyslij} noValidate>
        <div className="pole">
          <label htmlFor="d-nazwa">Nazwa instytucji</label>
          <span id="d-nazwa-podp" className="podpowiedz">
            Pełna nazwa, np. Urząd Miasta Krosna.
          </span>
          <input
            id="d-nazwa"
            type="text"
            autoComplete="organization"
            required
            aria-required="true"
            value={d.nazwa}
            onChange={zmien("nazwa")}
            aria-invalid={bledy.nazwa ? true : undefined}
            aria-describedby={opis("nazwa", "d-nazwa-podp")}
          />
          {bledy.nazwa && (
            <span id="d-nazwa-blad" className="blad-pola">
              {bledy.nazwa}
            </span>
          )}
        </div>

        <div className="pole">
          <label htmlFor="d-typ">Typ dysponenta</label>
          <select
            id="d-typ"
            required
            aria-required="true"
            value={d.typ}
            onChange={zmien("typ")}
            aria-invalid={bledy.typ ? true : undefined}
            aria-describedby={opis("typ")}
          >
            <option value="">{schemat ? "Wybierz…" : "Wczytuję listę…"}</option>
            {typy.map((t) => (
              <option key={t.kod} value={t.kod}>
                {t.znaczenie}
              </option>
            ))}
          </select>
          {bledy.typ && (
            <span id="d-typ-blad" className="blad-pola">
              {bledy.typ}
            </span>
          )}
        </div>

        <fieldset className="kontakt">
          <legend>Kontakt w sprawie danych (opcjonalnie)</legend>
          <p id="d-kontakt-podp" className="podpowiedz">
            <strong>Nie publikujemy</strong> tych danych. Służą tylko do kontaktu, gdy coś w pliku trzeba poprawić.
          </p>
          <div className="pole">
            <label htmlFor="d-telefon">
              Telefon <span className="opcjonalne">(nie publikujemy)</span>
            </label>
            <input
              id="d-telefon"
              type="tel"
              autoComplete="tel"
              inputMode="tel"
              value={d.telefon ?? ""}
              onChange={zmien("telefon")}
              aria-invalid={bledy.telefon ? true : undefined}
              aria-describedby={opis("telefon", "d-kontakt-podp")}
            />
            {bledy.telefon && (
              <span id="d-telefon-blad" className="blad-pola">
                {bledy.telefon}
              </span>
            )}
          </div>
          <div className="pole">
            <label htmlFor="d-email">
              E-mail <span className="opcjonalne">(nie publikujemy)</span>
            </label>
            <input
              id="d-email"
              type="email"
              autoComplete="email"
              value={d.email ?? ""}
              onChange={zmien("email")}
              aria-invalid={bledy.email ? true : undefined}
              aria-describedby={opis("email", "d-kontakt-podp")}
            />
            {bledy.email && (
              <span id="d-email-blad" className="blad-pola">
                {bledy.email}
              </span>
            )}
          </div>
        </fieldset>

        <div className="akcje akcje-miedzy">
          <button type="button" className="drugorzedny" onClick={onWstecz}>
            Wstecz
          </button>
          <button type="submit">Dalej: dane</button>
        </div>
      </form>
    </section>
  );
}
