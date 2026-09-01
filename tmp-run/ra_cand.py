"""Stage 3 vervolg: tier per wedstrijd, met promovendi- én degradanten-omrekening (§4).

Nieuw op 1 sep 2026: de runlijst bestaat vandaag voor de helft uit bekerduels (Coppa Italia,
DFB Pokal) waarin ploegen uit verschillende divisies tegen elkaar staan, en de Championship
telt zes ploegen die vorig seizoen elders speelden — drie promovendi uit League One en drie
degradanten uit de Premier League. `promotion.convert_relegated` doet die tweede groep.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, promotion
from ra_names import resolve

s3 = json.load(open("tmp-run/ra_stage3.json"))
fx, st = s3["fixtures"], s3["stats"]

cands = []
for name, v in fx.items():
    if not v["matches"]:
        continue
    season = v["s_prev"]
    full = st[name]["prev"].get("has_xg")
    teams = fotmob.fetch_league_stats(v["primaryId"], season)["teams"]
    for m in v["matches"]:
        rh, ra = resolve(m["home"], teams), resolve(m["away"], teams)
        missing = [t for t, r in ((m["home"], rh), (m["away"], ra)) if not r]
        cands.append({"competition": name, "season": season, "primaryId": v["primaryId"],
                      "betexplorer": v["betexplorer"], "sportkey": v["sportkey"],
                      "understat": v.get("understat"),
                      "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
                      "table_home": rh, "table_away": ra, "missing": missing, **m})

json.dump(cands, open("tmp-run/ra_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    print(f"  {c['tier']:6s} {c['competition']:24s} {c['home']} - {c['away']}{flag}")
