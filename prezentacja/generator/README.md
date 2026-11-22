# Generator prezentacji TuAED

Buduje `prezentacja/AEDane-Misja-AED.pptx` (15 slajdów, Noto Sans, kolory TuAED).

```bash
cd prezentacja/generator
python3 gen.py                 # treść i układ slajdów → spec.json, images.json
python3 przygotuj_obrazy.py    # obrazy → img/, imgmap.json
npm install pptxgenjs@3.12.0
node build.js                  # → AEDane-Misja-AED.pptx
mv AEDane-Misja-AED.pptx ..
```

Treść slajdów zmieniasz w `gen.py` (wymiary w calach, slajd 10 × 5,625 in).
Import do Google Slides: Plik → Importuj slajdy → Prześlij → Wszystkie.
