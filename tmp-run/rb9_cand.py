"""Run B, 9 sep 2026 — Stage 3 vervolg: tier per wedstrijd.

Gelijk aan `ra9_cand.py`; er zitten geen bekercompetities in de Run B-lijst, dus de
PROMO_COMP-omweg is hier niet nodig — elke wedstrijd hoort bij zijn eigen divisie.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob
from ra_names import resolve
from b_merge import merge_teams

s3 = json.load(open("tmp-run/rb9_stage3.json"))
fx, st = s3["fixtures"], s3["stats"]

cands = []
for name, v in fx.items():
    if not v["matches"]:
        continue
    season = v["s_prev"]
    full = st[name]["prev"].get("has_xg")
    # samenvoegen: Fotmob laat ploegen soms in twee half gevulde rijen uiteenvallen
    teams, _ = merge_teams(fotmob.fetch_league_stats(v["primaryId"], season)["teams"])
    for m in v["matches"]:
        rh, ra = resolve(m["home"], teams), resolve(m["away"], teams)
        missing = [t for t, r in ((m["home"], rh), (m["away"], ra)) if not r]
        cands.append({"competition": name, "season": season, "season_cur": v["s_cur"],
                      "primaryId": v["primaryId"],
                      "betexplorer": v["betexplorer"], "sportkey": v["sportkey"],
                      "understat": None,
                      "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
                      "table_home": rh, "table_away": ra, "missing": missing, **m})

json.dump(cands, open("tmp-run/rb9_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    print(f"  {c['tier']:6s} {c['competition']:30s} {c['home']} - {c['away']}{flag}")
