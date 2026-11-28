"""Run B, 27 nov 2026 — poort 'bevestiging door een tweede methode' (§1) op de RUNLIJST zelf.
Fotmob levert de daglijst, BetExplorer de fixturepagina per competitie — twee losse bronnen.
TIJDZONE: `MatchOdds.when` is UK-tijd (§5), dus NL −1 uur (wintertijd: NL=UTC+1, UK=UTC+0).
Inzetvenster [27.11 08:00 NL, 28.11 08:00 NL) = [27.11 07:00 UK, 28.11 07:00 UK)."""
import json, re
from scripts import betexplorer

st3 = json.load(open("tmp-run/rb_nov28_stage3.json"))
URLS = {n: v["betexplorer"] for n, v in st3["fixtures"].items() if v.get("betexplorer")}
src = open("tmp-run/rb_nov28_stage3.py").read()
for n, u in re.findall(r'"([^"]+)":\s*\("[A-Z]{3}", "[\d/]+", "[\d/]+",\s*\n?\s*"(https://[^"]+)"', src):
    URLS.setdefault(n, u)

DAY_D, DAY_M, NEXT_D, NEXT_M = 28, 11, 29, 11

def in_window(when: str) -> bool:
    if not when:
        return False
    m = re.match(r"(?:Today|Tomorrow|(\d{2})\.(\d{2})\.)\s+(\d{2}):(\d{2})", when)
    if not m:
        return False
    if m.group(1) is None:
        hh = int(m.group(3))
        return hh >= 7 if when.startswith("Today") else hh < 7
    d, mo, hh, mm = (int(x) for x in m.groups())
    if (d, mo) == (DAY_D, DAY_M):
        return hh >= 7
    if (d, mo) == (NEXT_D, NEXT_M):
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
        print(f"{'OK ' if ok else 'AFW'} {naam:32s} fotmob={fm} bx={len(venster)}  eerste={whens[:2]}")
    except Exception as e:
        out[naam] = {"fotmob": fm, "error": f"{type(e).__name__}: {e}"}
        print(f"FAIL {naam:32s} {type(e).__name__}: {e}")

json.dump(out, open("tmp-run/rb_nov28_bevestiging.json", "w"), ensure_ascii=False, indent=1)
print("\neens:", sum(1 for v in out.values() if v.get("eens")), "van", len(out))
print("fotmob totaal:", sum(v.get("fotmob", 0) for v in out.values()),
      " bx totaal:", sum(v.get("betexplorer", 0) or 0 for v in out.values()))
