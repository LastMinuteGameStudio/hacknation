import { useState } from "react";

/** Adres z przyciskiem „Kopiuj”. Wynik ogłaszany przez region aria-live. */
export function Kopiuj({ wartosc, etykieta, id }: { wartosc: string; etykieta: string; id: string }) {
  const [stan, setStan] = useState<"" | "ok" | "blad">("");

  async function kopiuj() {
    try {
      await navigator.clipboard.writeText(wartosc);
      setStan("ok");
    } catch {
      // Zapas: zaznacz tekst, żeby użytkownik skopiował go sam (Ctrl+C).
      const el = document.getElementById(id);
      if (el) {
        const r = document.createRange();
        r.selectNodeContents(el);
        const sel = window.getSelection();
        sel?.removeAllRanges();
        sel?.addRange(r);
      }
      setStan("blad");
    }
    window.setTimeout(() => setStan(""), 4000);
  }

  return (
    <div className="adres">
      <span id={id} className="url">
        {wartosc}
      </span>
      <button type="button" className="drugorzedny maly" onClick={kopiuj} aria-describedby={id}>
        Kopiuj<span className="wizualnie-ukryte"> {etykieta}</span>
      </button>
      <span role="status" className="drobny">
        {stan === "ok" ? "Skopiowano." : stan === "blad" ? "Zaznaczono adres. Skopiuj go skrótem Ctrl+C." : ""}
      </span>
    </div>
  );
}
