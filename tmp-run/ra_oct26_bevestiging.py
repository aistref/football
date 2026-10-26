"""Run A, 26 okt 2026 — poort 'bevestiging door een tweede methode' (§1) op de RUNLIJST zelf.

Niet op het totaal maar per competitie, zoals Run A op 11 oktober deed: de twee duurste fouten
van oktober zaten in de vraag wélke wedstrijden er zijn en niet in de analyse. Fotmob levert de
daglijst, BetExplorer de fixturepagina per competitie — twee losse bronnen.

TIJDZONE. `MatchOdds.when` is "26.10. 20:00" in **UK-tijd** (§5 Aftraptijden), dus NL −1 uur. Het
inzetvenster [26.10. 08:00 NL, 27.10. 08:00 NL) is in UK-tijd [26.10. 07:00, 27.10. 07:00).
"""
import json
from scripts import betexplorer

st3 = json.load(open("tmp-run/ra_oct26_stage3.json"))
URLS = {n: v["betexplorer"] for n, v in st3["fixtures"].items() if v.get("betexplorer")}
# ook de competities die vandaag GEEN WEDSTRIJD hebben, want juist daar moet de tweede bron kijken
import re
src = open("tmp-run/ra_oct26_stage3.py").read()
# `\s+` in plaats van `\s*` liet op 14 okt 2026 stil ÉÉN competitie wegvallen: de regel
# "Scottish Premiership (SCO)":("SCO", ... in de META-tabel heeft geen ruimte na de dubbele punt,
# dus die competitie werd door geen tweede bron bevestigd en het totaal (15 van 15) zag er intact
# uit. Dat is dezelfde stille faalstand als §6b-5b beschrijft: een controle die groen staat omdat
# hij één rij niet meet. Vandaar `\s*`.
for n, u in re.findall(r'"([^"]+)":\s*\("[A-Z]{3}", "[\d/]+", "[\d/]+",\s+"(https://[^"]+)"', src):
    URLS.setdefault(n, u)


def in_window(when: str) -> bool:
    if not when:
        return False
    # BetExplorer labelt de eigen pagina-datum als "Today HH:MM" in plaats van "23.10. HH:MM"
    m = re.match(r"(?:Today|Tomorrow|(\d{2})\.(\d{2})\.)\s+(\d{2}):(\d{2})", when)
    if not m:
        return False
    if m.group(1) is None:
        hh = int(m.group(3))
        return hh >= 7 if when.startswith("Today") else hh < 7
    d, mo, hh, mm = (int(x) for x in m.groups())
    if (d, mo) == (26, 10):
        return hh >= 7
    if (d, mo) == (27, 10):
        return hh < 7
    return False


out = {}
for naam, url in sorted(URLS.items()):
    fm = len(st3["fixtures"].get(naam, {}).get("matches", []) or [])
    try:
        fx = betexplorer.fetch_league_fixtures(url)
        whens = sorted({f.when for f in fx if f.when})
        venster = [f"{f.home} - {f.away} ({f.when} UK)" for f in fx if in_window(f.when)]
        ok = len(venster) == fm
        out[naam] = {"fotmob": fm, "betexplorer": len(venster), "eens": ok,
                     "duels": venster, "eerste_rondes": whens[:3], "n_fixtures": len(fx)}
        print(f"{'OK ' if ok else 'AFW'} {naam:28s} fotmob={fm} bx={len(venster)}  "
              f"eerste={whens[:2]}")
    except Exception as e:
        out[naam] = {"fotmob": fm, "error": f"{type(e).__name__}: {e}"}
        print(f"FAIL {naam:28s} {type(e).__name__}: {e}")

json.dump(out, open("tmp-run/ra_oct26_bevestiging.json", "w"), ensure_ascii=False, indent=1)
print("\neens:", sum(1 for v in out.values() if v.get("eens")), "van", len(out))
print("fotmob totaal:", sum(v.get("fotmob", 0) for v in out.values()),
      " bx totaal:", sum(v.get("betexplorer", 0) or 0 for v in out.values()))
