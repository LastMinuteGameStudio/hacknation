"""Kopiuje obrazy do generator/img/ (zmniejszone do 1800 px) i zapisuje imgmap.json.
Logo pobiera z branchu kvba (visual/*.png). Uruchom z katalogu prezentacja/generator po `python3 gen.py`."""
import json, subprocess, urllib.request
from pathlib import Path
PREZ = Path(__file__).resolve().parents[1]
Path("img").mkdir(exist_ok=True)
m = {}
for lst in json.load(open("images.json")).values():
    for oid, url, *_ in lst:
        dst = Path("img") / f"{oid}.png"
        if "/kvba/visual/" in url:
            urllib.request.urlretrieve(url, dst)
        else:
            dst.write_bytes((PREZ / url.split("/prezentacja/")[1]).read_bytes())
        subprocess.run(["sips", "-Z", "1800", str(dst)], capture_output=True)  # macOS; gdzie indziej pomiń
        m[oid] = str(dst)
json.dump(m, open("imgmap.json", "w"))
print(len(m), "obrazów")
