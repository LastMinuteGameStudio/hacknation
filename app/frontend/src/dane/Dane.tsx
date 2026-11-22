// /dane: podgląd zebranych danych dla dysponentów i jury.
import { useEffect } from "react";
import type { SchematOut } from "../api/types";
import { WszystkieAed } from "./WszystkieAed";
import { Zbiory } from "./Zbiory";

export default function Dane({ schemat }: { schemat: SchematOut | null }) {
  useEffect(() => {
    document.title = "Zebrane dane o AED | AEDane";
  }, []);
  return (
    <div>
      <h1 id="naglowek-kroku" tabIndex={-1}>
        Zebrane dane o AED
      </h1>
      <p className="wstep">
        Co już jest w otwartych danych: zbiory opublikowane przez dostawców i pełna lista AED z pliku zbiorczego.
      </p>
      <Zbiory schemat={schemat} />
      <WszystkieAed schemat={schemat} />
    </div>
  );
}
