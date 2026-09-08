"""Stage 3 vervolg: tier per wedstrijd, met promovendi- én degradanten-omrekening (§4).

Twee toernooien vandaag, en ze vragen om verschillende behandeling:
  * League Cup (ENG) — één land, meerdere divisies. De basis is de Premier League 2025/2026;
    Championship-ploegen worden omgerekend (promotion.convert), gedegradeerde ploegen met
    convert_relegated. Ploegen uit League One/Two liggen twee divisies lager en vallen dus
    buiten het gemeten bereik: NONE.
  * UEFA Champions League — meerdere landen. Er bestaat geen gemeten factor tussen twee
    nationale competities, dus de sterktes staan op onvergelijkbare schalen: NONE zonder
    verdere poging (`crossborder`).
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, promotion
from ra_names import resolve

s3 = json.load(open("tmp-run/ra8_stage3.json"))
fx, st = s3["fixtures"], s3["stats"]

cands = []
for name, v in fx.items():
    if not v["matches"]:
        continue
    if v.get("crossborder"):
        for m in v["matches"]:
            cands.append({"competition": name, "season": None, "season_cur": None,
                          "primaryId": None, "betexplorer": v["betexplorer"],
                          "sportkey": v["sportkey"], "understat": None,
                          "tier": "NONE", "crossborder": True,
                          "table_home": None, "table_away": None, "missing": [], **m})
        continue
    season = v["s_prev"]
    full = st[name]["prev"].get("has_xg")
    teams = fotmob.fetch_league_stats(v["primaryId"], season)["teams"]
    for m in v["matches"]:
        rh, ra = resolve(m["home"], teams), resolve(m["away"], teams)
        missing = [t for t, r in ((m["home"], rh), (m["away"], ra)) if not r]
        cands.append({"competition": name, "season": season, "season_cur": v["s_cur"],
                      "primaryId": v["primaryId"], "crossborder": False,
                      "betexplorer": v["betexplorer"], "sportkey": v["sportkey"],
                      "understat": v.get("understat"),
                      "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
                      "table_home": rh, "table_away": ra, "missing": missing, **m})

json.dump(cands, open("tmp-run/ra8_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    print(f"  {c['tier']:6s} {c['competition']:24s} {c['home']} - {c['away']}{flag}")
