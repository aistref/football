"""Run A, 17 okt 2026 — kan de FA Cup-ronde van vandaag worden doorgerekend?

32 ties in het inzetvenster, alle via BetExplorer gevonden (de daglijst van Fotmob kent de
beker niet). §4, "In een beker ligt de basis per WEDSTRIJD": een beker heeft geen eigen stand,
dus de basis is `CUP_BASE` (hier de Premier League) en een ploeg die daar niet in staat wordt
uit de divisie eronder omgerekend — één divisie diep. Staan beide ploegen in dezelfde lagere
divisie, dan is er niets te overbruggen en rekent het duel door in die divisie
(`shared_lower_division`, keten standaard drie diep: Championship, League One, League Two).
"""
import json
from scripts import promotion

DAY = "2026-10-17"
SEASON = "2025/2026"
BASE = "Premier League (ENG)"

pairs = [(r["home"], r["away"]) for r in
         json.load(open("tmp-run/ra_oct17_cups.json"))["cups"]["FA Cup (ENG)"]["in_venster"]]

out = []
for home, away in pairs:
    try:
        sd = promotion.shared_lower_division(BASE, home, away, SEASON)
    except Exception as e:
        sd, err = None, f"{type(e).__name__}: {e}"
    else:
        err = None
    row = {"home": home, "away": away,
           "shared": None if sd is None else {"id": sd.fotmob_id, "competition": sd.competition},
           "error": err}
    out.append(row)
    print(f"{home:22s} - {away:20s} -> "
          f"{'geen gedeelde divisie' if sd is None else sd.competition}"
          + (f"  [{err}]" if err else ""))

json.dump({"day": DAY, "base": BASE, "rows": out},
          open("tmp-run/ra_oct17_cupcheck.json", "w"), ensure_ascii=False, indent=1)
n = sum(1 for r in out if r["shared"])
print(f"\n{n} van de {len(out)} ties heeft een gedeelde lagere divisie.")
