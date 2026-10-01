"""Run B, 30 sep 2026 — Stage 3 vervolg: tier per wedstrijd.

Eén duel vandaag, in MLS. MLS kent **geen** promotie/degradatie (§ run-b.md), dus een ploeg
buiten de stand van vorig seizoen is daar een uitbreidingsploeg zonder historie op dit niveau en
dat wordt `NONE` — `promotion.py` heeft er niets te zoeken. Vandaar geen PROMO?-tak hier.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob
from ra_names import resolve

s3 = json.load(open("tmp-run/rb_oct01_stage3.json"))
fx, st = s3["fixtures"], s3["stats"]

cands = []
for name, v in fx.items():
    if not v["matches"]:
        continue
    season = v["s_prev"]
    full = (st.get(name, {}).get("prev") or {}).get("has_xg")
    teams = fotmob.fetch_league_stats(v["primaryId"], season)["teams"]
    for m in v["matches"]:
        rh, ra = resolve(m["home"], teams), resolve(m["away"], teams)
        missing = [t for t, r in ((m["home"], rh), (m["away"], ra)) if not r]
        cands.append({"competition": name, "season": season, "season_cur": v["s_cur"],
                      "primaryId": v["primaryId"], "crossborder": False,
                      "betexplorer": v["betexplorer"], "sportkey": v["sportkey"],
                      "understat": None,
                      # MLS: geen promotie/degradatie -> ontbreken in de stand = NONE
                      "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "NONE"),
                      "table_home": rh, "table_away": ra, "missing": missing, **m})

json.dump(cands, open("tmp-run/rb_oct01_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    print(f"  {c['tier']:6s} {c['competition']:30s} {c['home']} - {c['away']}{flag}")
    print(f"         stand-namen: {c['table_home']} / {c['table_away']}")
