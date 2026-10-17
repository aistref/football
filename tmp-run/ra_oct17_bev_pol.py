"""Run A, 17 okt 2026 — de ene competitie die de tweede bron niet haalde, opnieuw.

`ra_oct17_bevestiging.py` kreeg voor de Ekstraklasa een `TimeoutError` van BetExplorer, dus de
runlijst stond op 15 van 16 bevestigd. Een timeout is geen afwijking maar een ontbrekende meting,
en het verschil tussen die twee moet in het runrapport staan in plaats van als "15 van 16" te
worden afgedaan. Deze aanroep doet alleen die ene competitie opnieuw, met een ruimere timeout.
"""
import json, re, urllib.request
from scripts import betexplorer as bx

URL = "https://www.betexplorer.com/football/poland/ekstraklasa/"


def in_window(when: str) -> bool:
    m = re.match(r"(?:Today|Tomorrow|(\d{2})\.(\d{2})\.)\s+(\d{2}):(\d{2})", when or "")
    if not m:
        return False
    if m.group(1) is None:
        hh = int(m.group(3))
        return hh >= 7 if when.startswith("Today") else hh < 7
    d, mo, hh, mm = (int(x) for x in m.groups())
    if (d, mo) == (17, 10):
        return hh >= 7
    if (d, mo) == (18, 10):
        return hh < 7
    return False


fu = URL.rstrip("/") + "/fixtures/"
raw = urllib.request.urlopen(urllib.request.Request(fu, headers=bx.HEADERS), timeout=120).read()
text = raw.decode(errors="replace")
carried, rijen = "", []
for row in bx._FIX_ROW_RE.findall(text):
    w = bx._WHEN_RE.search(row)
    if w and w.group(1).strip() and w.group(1).strip() != "&nbsp;":
        carried = w.group(1).strip()
    tm = bx._TEAMS_RE.search(row)
    if tm:
        rijen.append({"home": tm.group(1), "away": tm.group(2), "when": carried})
venster = [f"{r['home']} - {r['away']} ({r['when']} UK)" for r in rijen if in_window(r["when"])]
uit = {"fotmob": 3, "betexplorer": len(venster), "eens": len(venster) == 3,
       "duels": venster, "n_fixtures": len(rijen),
       "eerste_rondes": sorted({r["when"] for r in rijen if r["when"]})[:3]}
print(json.dumps(uit, ensure_ascii=False, indent=1))

d = json.load(open("tmp-run/ra_oct17_bevestiging.json"))
d["Ekstraklasa (POL)"] = uit
json.dump(d, open("tmp-run/ra_oct17_bevestiging.json", "w"), ensure_ascii=False, indent=1)
print("eens:", sum(1 for v in d.values() if isinstance(v, dict) and v.get("eens")), "van", len(d))
