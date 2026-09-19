"""Run B — Stage 3 vervolg: tier per wedstrijd, met promovendi-, degradanten- en kruis-grensomrekening.

Ongewijzigd ten opzichte van 16 sep. Vandaag loopt de kruis-grenstak wél mee: de Europa League
speelt negen duels (speelronde 1 van de competitiefase), en die worden met `interleague.py` naar
de Europese schaal omgerekend.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, promotion, interleague
from ra_names import resolve

s3 = json.load(open("tmp-run/rb19_stage3.json"))
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
        row = {"competition": name, "season": season, "season_cur": v["s_cur"],
               "primaryId": v["primaryId"], "crossborder": False,
               "betexplorer": v["betexplorer"], "sportkey": v["sportkey"],
               "understat": v.get("understat"),
               "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
               "table_home": rh, "table_away": ra, "missing": missing, **m}

        # 15 sep 2026 — de basis per WEDSTRIJD in plaats van per beker (openstaand punt 1 van
        # 15 sep). Staan beide ploegen niet in de basisdivisie maar wél allebei in dezelfde
        # divisie eronder, dan is er niets om te overbruggen: het duel wordt gewoon in díe
        # divisie doorgerekend, net als een competitiewedstrijd daar. De omweg langs de
        # basisdivisie kostte op 8 sep Leyton Orient – Bradford en op 15 sep Peterborough
        # United – Barnsley, allebei twee League One-ploegen in een League Cup-tie.
        #
        # LET OP wat dit NIET doet: een duel tussen ploegen uit verschillende divisies blijft
        # gaan zoals het ging (Reading – Brentford is League One tegen Premier League, en dáár
        # is het niveauverschil wél de vraag die we niet kunnen beantwoorden).
        if len(missing) == 2:
            base = promotion.CUP_BASE.get(name, name)
            sd = promotion.shared_lower_division(base, m["home"], m["away"], season)
            if sd is not None:
                sub = fotmob.fetch_league_stats(sd.fotmob_id, season)
                sub_full = any("xg" in t for t in sub["teams"].values())
                row.update({"primaryId": sd.fotmob_id, "basis_comp": sd.competition,
                            "basis_note": sd.note, "table_home": sd.home_key,
                            "table_away": sd.away_key, "missing": [],
                            "tier": "FULL" if sub_full else "LIGHT"})
        cands.append(row)

json.dump(cands, open("tmp-run/rb19_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    if c.get("kruis_grens"):
        flag = "  " + json.dumps(c["kruis_grens"], ensure_ascii=False)[:150]
    print(f"  {c['tier']:6s} {c['competition']:24s} {c['home']} - {c['away']}{flag}")
