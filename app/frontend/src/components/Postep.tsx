// Wskaźnik kroków kreatora. Stan kroku podany tekstem, nie tylko kolorem.
export interface KrokOpis {
  id: string;
  nazwa: string;
}

export function Postep({ kroki, biezacy }: { kroki: KrokOpis[]; biezacy: string }) {
  const idx = kroki.findIndex((k) => k.id === biezacy);
  return (
    <nav aria-label="Postęp">
      <ol className="postep">
        {kroki.map((k, i) => {
          const stan = i < idx ? "zrobione" : i === idx ? "biezacy" : "dalej";
          return (
            <li key={k.id} className={`postep-krok ${stan}`} aria-current={stan === "biezacy" ? "step" : undefined}>
              <span className="postep-nr" aria-hidden="true">
                {stan === "zrobione" ? "✓" : i + 1}
              </span>
              <span>
                {k.nazwa}
                {stan === "zrobione" && <span className="wizualnie-ukryte"> (zrobione)</span>}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
