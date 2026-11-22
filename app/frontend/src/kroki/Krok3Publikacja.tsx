import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api/client";
import type { PublikacjaOut, WalidacjaOut } from "../api/types";
import { Kopiuj } from "../components/Kopiuj";

const CC0_URL = "https://creativecommons.org/publicdomain/zero/1.0/deed.pl";
const META_SLOWA = "AED, defibrylator, pierwsza pomoc";

function aedLiczba(n: number) {
  const m10 = n % 10, m100 = n % 100;
  return n === 1 ? "1 defibrylator AED" : m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14) ? `${n} defibrylatory AED` : `${n} defibrylatorów AED`;
}

interface Props {
  importId: string;
  dysponentNazwa: string;
  walidacja: WalidacjaOut;
  edycja: boolean;
  publikacja: PublikacjaOut | null;
  setPublikacja: (p: PublikacjaOut) => void;
  onWstecz: () => void;
}

export function Krok3Publikacja({ importId, dysponentNazwa, walidacja, edycja, publikacja, setPublikacja, onWstecz }: Props) {
  const [zgoda, setZgoda] = useState(false);
  const [publikuje, setPublikuje] = useState(false);
  const [blad, setBlad] = useState<string | null>(null);
  const gotoweRef = useRef<HTMLHeadingElement>(null);
  const poPublikacji = useRef(false);
  const metaTytul = `Defibrylatory AED: ${dysponentNazwa}`;
  const metaOpis =
    `Wykaz obejmuje ${aedLiczba(walidacja.liczba_rekordow)} (automatyczne defibrylatory zewnętrzne), ` +
    `za które odpowiada ${dysponentNazwa}: położenie, adres, kto ma dostęp, godziny dostępności i stan urządzenia. ` +
    "Format zgodny z zakresem danych AED v0.5 (CSV UTF-8, jeden wiersz to jedno urządzenie, metadane CSVW). " +
    "Dane aktualizowane automatycznie.";

  // Fokus na nagłówek „Dane opublikowane” dopiero po wyrenderowaniu (przycisk był wyłączony, fokus by przepadł).
  useEffect(() => {
    if (publikacja && poPublikacji.current) gotoweRef.current?.focus();
  }, [publikacja]);

  async function publikuj() {
    if (!zgoda) return;
    setBlad(null);
    setPublikuje(true);
    try {
      const p = await api.publikuj(importId);
      poPublikacji.current = true;
      setPublikacja(p);
    } catch (e) {
      setBlad(
        e instanceof ApiError
          ? e.blad.kod === "SA_BLEDY"
            ? "Dane mają błędy. Wróć do kroku 2 i sprawdź je ponownie."
            : e.blad.komunikat
          : "Brak połączenia z serwerem. Spróbuj ponownie.",
      );
    } finally {
      setPublikuje(false);
    }
  }

  if (publikacja) {
    return (
      <section aria-labelledby="naglowek-kroku">
        <h1 id="naglowek-kroku" ref={gotoweRef} tabIndex={-1}>
          {edycja ? "Dane zaktualizowane" : "Dane opublikowane"}
        </h1>
        <div className="ramka ramka-ok">
          <p>
            {edycja
              ? "Nowa wersja jest już pod tym samym adresem. Na dane.gov.pl nie musisz nic zmieniać, portal pobierze ją sam."
              : `Opublikowano ${walidacja.liczba_rekordow} AED. Został jeden krok: dodaj adres na dane.gov.pl.`}
          </p>
        </div>

        <h2>Adres pliku z danymi</h2>
        <p>Ten adres się nie zmienia. Pod nim zawsze jest najnowsza wersja Twoich danych.</p>
        <Kopiuj id="url-csv" etykieta="adres pliku CSV" wartosc={publikacja.url_csv} />

        {publikacja.token_edycji && (
          <>
            <h2>Prywatny link do aktualizacji</h2>
            <div className="ramka ramka-ostrzezenie">
              <p>
                <strong>Zachowaj ten link i nie udostępniaj go nikomu.</strong> Kto go ma, może zmienić Twoje dane.
                Pokazujemy go tylko teraz. Zapisz go np. w notatkach albo w dokumentacji urzędu.
              </p>
            </div>
            <p>
              Przez ten link wgrasz nową wersję pliku pod ten sam adres. Możesz tam też podać adres swojego pliku na
              stronie urzędu, a będziemy go pobierać automatycznie.
            </p>
            <Kopiuj id="url-edycji" etykieta="prywatny link do aktualizacji" wartosc={publikacja.url_edycji} />
          </>
        )}

        {!edycja && (
          <>
            <h2>Dodaj dane na dane.gov.pl</h2>
            <ol className="instrukcja">
              <li>
                Zaloguj się na <a href="https://dane.gov.pl">dane.gov.pl</a> jako dostawca i otwórz swój zbiór danych
                o AED albo utwórz nowy. Tytuł, opis i słowa kluczowe skopiujesz z sekcji „Metadane zbioru” niżej.
              </li>
              <li>
                Wybierz <strong>Dodaj zasób</strong>.
              </li>
              <li>
                Jako sposób dodania wybierz <strong>link</strong> (zasób zdalny).
              </li>
              <li>Wklej adres pliku z danymi (skopiowany wyżej).</li>
              <li>
                Zaznacz <strong>Aktualizacja automatyczna</strong> i ustaw <strong>powtarzać co: dziennie</strong>.
              </li>
              <li>
                Zaznacz pole <strong>„Wykaz AED”</strong> przy zasobie, żeby portal dołączył Twoje dane do
                ogólnopolskiego wykazu AED.
              </li>
              <li>
                Jako licencję wybierz <strong>CC0 1.0</strong> i zapisz zasób.
              </li>
            </ol>
            <p className="ramka ramka-info">
              <strong>Po co „Wykaz AED”?</strong> Portal co noc łączy wszystkie zaznaczone wykazy w jeden zbiór dla całej
              Polski. Dyspozytor medyczny i aplikacje ratunkowe pobierają wtedy jeden plik zamiast setek osobnych.
            </p>

            <h2>Metadane zbioru do skopiowania</h2>
            <p>Wklej je przy tworzeniu albo edycji zbioru na dane.gov.pl.</p>
            <dl className="metadane">
              <dt>Tytuł</dt>
              <dd>
                <Kopiuj id="meta-tytul" etykieta="tytuł zbioru" wartosc={metaTytul} tekst />
              </dd>
              <dt>Opis</dt>
              <dd>
                <Kopiuj id="meta-opis" etykieta="opis zbioru" wartosc={metaOpis} tekst />
              </dd>
              <dt>Słowa kluczowe</dt>
              <dd>
                <Kopiuj id="meta-slowa" etykieta="słowa kluczowe" wartosc={META_SLOWA} tekst />
              </dd>
              <dt>Kategoria</dt>
              <dd>Zdrowie</dd>
              <dt>Częstotliwość aktualizacji</dt>
              <dd>codziennie (zasób aktualizuje się automatycznie z AEDane)</dd>
              <dt>Licencja</dt>
              <dd>CC0 1.0</dd>
            </dl>
          </>
        )}

        <h2>Inne formaty</h2>
        <ul className="lista-linkow">
          <li>
            <a href={publikacja.url_json}>Dane w JSON</a>
          </li>
          <li>
            <a href={publikacja.url_metadane}>Metadane (CSVW)</a>
          </li>
          <li>
            <a href={publikacja.url_csv}>Dane w CSV</a>
          </li>
        </ul>
      </section>
    );
  }

  return (
    <section aria-labelledby="naglowek-kroku">
      <h1 id="naglowek-kroku" tabIndex={-1}>
        Opublikuj dane
      </h1>
      <p>
        Opublikujemy <strong>{walidacja.liczba_rekordow} AED</strong>
        {walidacja.liczba_pominietych > 0 && <> (pominiętych: {walidacja.liczba_pominietych})</>}. Publikujemy tylko pola
        publiczne. Telefon i e-mail kontaktowy zostają u nas.
      </p>
      {edycja && <p>Nowa wersja zastąpi poprzednią pod tym samym adresem.</p>}

      <div className="zgoda">
        <input
          id="zgoda-cc0"
          type="checkbox"
          checked={zgoda}
          required
          aria-required="true"
          aria-describedby="zgoda-opis"
          onChange={(e) => setZgoda(e.target.checked)}
        />
        <label htmlFor="zgoda-cc0">Udostępniam dane na licencji CC0 1.0</label>
      </div>
      <p id="zgoda-opis" className="podpowiedz">
        CC0 to domena publiczna: każdy może używać danych bez ograniczeń, także w aplikacjach ratunkowych.{" "}
        <a href={CC0_URL} rel="noopener">
          Czym jest CC0 1.0
        </a>
      </p>

      {blad && (
        <div className="ramka ramka-blad" role="alert">
          <p>{blad}</p>
        </div>
      )}

      <div className="akcje akcje-miedzy">
        <button type="button" className="drugorzedny" onClick={onWstecz} disabled={publikuje}>
          Wstecz
        </button>
        <button type="button" onClick={publikuj} disabled={!zgoda || publikuje}
          aria-describedby={zgoda ? undefined : "opublikuj-podp"}>
          {publikuje ? "Publikuję…" : "Opublikuj"}
        </button>
      </div>
      {!zgoda && (
        <p id="opublikuj-podp" className="drobny" style={{ textAlign: "right" }}>
          Najpierw zaznacz zgodę na licencję CC0 1.0.
        </p>
      )}
    </section>
  );
}
