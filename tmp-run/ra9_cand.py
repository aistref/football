"""Stage 3 vervolg: tier per wedstrijd, met promovendi-, degradanten- én kruis-grensomrekening.

Verschil met 8 sep: de Champions League-duels gaan niet meer blind naar NONE. Sinds
`scripts/interleague.py` (8 sep 2026, §4 "Kruis-grens") bestaat er een op 2111 Europese duels
gemeten aanval- en verdedigingsfactor per nationale competitie. Twee ploegen uit verschillende
landen worden daarmee naar dezelfde Europese schaal omgerekend; lukt dat voor beide en vallen
beide binnen het gemeten bereik, dan is het duel `LIGHT` (nooit FULL), anders `NONE`.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, promotion, interleague
from ra_names import resolve

s3 = json.load(open("tmp-run/ra9_stage3.json"))
fx, st = s3["fixtures"], s3["stats"]

XSEASON = "2025/2026"      # laatst AFGERONDE seizoen (§4)

cands = []
for name, v in fx.items():
    if not v["matches"]:
        continue
    if v.get("crossborder"):
        for m in v["matches"]:
            notes, ok = {}, True
            for rol, tid, tnaam in (("thuis", m["home_id"], m["home"]),
                                    ("uit", m["away_id"], m["away"])):
                try:
                    conv = interleague.convert_team(tid, tnaam, XSEASON)
                    notes[rol] = {"note": conv.note, "in_range": conv.in_range,
                                  "attack": round(conv.attack, 3),
                                  "defence": round(conv.defence, 3)}
                    if not conv.in_range:
                        ok = False
                except interleague.InterLeagueError as e:
                    notes[rol] = {"error": f"{e}"}
                    ok = False
                except Exception as e:
                    notes[rol] = {"error": f"{type(e).__name__}: {e}"}
                    ok = False
            cands.append({"competition": name, "season": XSEASON, "season_cur": None,
                          "primaryId": None, "betexplorer": v["betexplorer"],
                          "sportkey": v["sportkey"], "understat": None,
                          "tier": "LIGHT" if ok else "NONE", "crossborder": True,
                          "kruis_grens": notes,
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

json.dump(cands, open("tmp-run/ra9_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    if c.get("kruis_grens"):
        flag = "  " + json.dumps(c["kruis_grens"], ensure_ascii=False)[:150]
    print(f"  {c['tier']:6s} {c['competition']:24s} {c['home']} - {c['away']}{flag}")
