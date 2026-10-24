"""Run A, 24 okt 2026 — Stage 3 vervolg: tier per wedstrijd, met kruis-grensomrekening.

Overgenomen van `ra_oct12_cand.py`, met de kruis-grenstak van `ra10_cand.py` er weer in. Die tak
is vandaag de hoofdzaak: negen van de zeventien duels zijn Champions League-wedstrijden tussen
ploegen uit verschillende LANDEN, en hun sterktes staan dan op onvergelijkbare schalen (§4,
"Kruis-grens"). `scripts/interleague.py` rekent beide ploegen naar de Europese referentieschaal;
lukt dat voor beide en vallen beide binnen het gemeten bereik, dan is het duel `LIGHT` — nooit
`FULL`, want de omrekening haalt de systematische fout eruit en niet de onzekerheid.

De acht Championship-duels lopen de gewone weg: xG in beide seizoenen, dus `FULL` zolang beide
ploegen in de stand van 2025/2026 staan. Wie daar niet staat is promovendus of degradant en gaat
in de analyse langs §4 ("Promovendi: eerst omrekenen, dan pas NONE").
"""

import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, interleague
from ra_names import resolve

s3 = json.load(open("tmp-run/ra_oct24_stage3.json"))
fx, st = s3["fixtures"], s3["stats"]

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
                    conv = interleague.convert_team(tid, tnaam, "2025/2026")
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
            cands.append({"competition": name, "season": "2025/2026", "season_cur": None,
                          "primaryId": None, "betexplorer": v["betexplorer"],
                          "sportkey": v["sportkey"], "understat": None,
                          "tier": "LIGHT" if ok else "NONE", "crossborder": True,
                          "kruis_grens": notes,
                          "table_home": None, "table_away": None, "missing": [], **m})
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
                      "understat": v.get("understat"),
                      "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
                      "table_home": rh, "table_away": ra, "missing": missing, **m})

json.dump(cands, open("tmp-run/ra_oct24_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    if c.get("kruis_grens"):
        flag = "  " + json.dumps(c["kruis_grens"], ensure_ascii=False)[:160]
    print(f"  {c['tier']:6s} {c['competition']:30s} {c['home']} - {c['away']}{flag}")
