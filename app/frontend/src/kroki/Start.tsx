export function Start({ onZacznij }: { onZacznij: () => void }) {
  return (
    <section aria-labelledby="naglowek-kroku">
      <h1 id="naglowek-kroku" tabIndex={-1}>
        Opublikuj dane o defibrylatorach na dane.gov.pl
      </h1>
      <p className="wstep">
        Masz listę AED w arkuszu? W kilka minut zamienisz ją na otwarte dane w jednym, wspólnym formacie.
        Dzięki temu dyspozytor, aplikacja ratunkowa i każdy przechodzień szybciej znajdą najbliższy defibrylator.
      </p>

      <h2>Jak to działa</h2>
      <ol className="lista-krokow">
        <li>
          <strong>Podaj, kto odpowiada za urządzenia.</strong> Nazwa instytucji i jej typ.
        </li>
        <li>
          <strong>Wgraj plik CSV, XLSX lub GeoJSON.</strong> Twój własny układ kolumn wystarczy. Podpowiemy, która kolumna
          to które pole, i sprawdzimy dane.
        </li>
        <li>
          <strong>Opublikuj.</strong> Dostaniesz stały adres pliku. Dodasz go na dane.gov.pl, a portal sam pobierze
          każdą aktualizację.
        </li>
      </ol>

      <h2>Nie masz jeszcze pliku?</h2>
      <p>Pobierz szablon, uzupełnij go i wróć tutaj.</p>
      <ul className="lista-linkow">
        <li>
          <a href="/szablon.xlsx" download>
            Szablon XLSX (Excel)
          </a>
        </li>
        <li>
          <a href="/szablon.csv" download>
            Szablon CSV
          </a>
        </li>
      </ul>

      <p className="akcje">
        <button type="button" onClick={onZacznij}>
          Zacznij
        </button>
      </p>
      <p className="drobny">
        Publikujesz na licencji CC0 1.0 (domena publiczna). Dane kontaktowe, które podasz, nie są publikowane.
      </p>
    </section>
  );
}
