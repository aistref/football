"""Run A, 31 okt 2026 — Stage 3 vervolg: tier per wedstrijd, met de bekertak erbij.

Overgenomen van `ra_oct26_cand.py`. De kruis-grenstak blijft staan maar komt vandaag niet aan de
orde (de drie Europese toernooien spelen niet). Wat vandaag de hoofdzaak is, is de **bekertak uit
`ra19_cand.py`**: negentien van de 22 duels zijn bekerwedstrijden, en daar ligt de basis per
WEDSTRIJD en niet per toernooi (§4, 15 sep 2026).

Staan beide ploegen van een bekerduel niet in de stand van de basisdivisie, dan loopt
`promotion.shared_lower_division` de `TIER2`-keten af en geeft de eerste divisie terug waarin
beide namen voorkomen. Is die er, dan wordt het duel daarin doorgerekend — geen omrekening, dus
`FULL` zodra die divisie xG heeft. Is die er niet, dan staan de twee ploegen op verschillende
niveaus en is juist dat niveauverschil de vraag: dan gaat het duel langs de promovendi-/
degradantenomrekening in de analyse, en anders op `NONE`.
"""


import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, interleague, promotion
from ra_names import resolve

s3 = json.load(open("tmp-run/ra_oct31_stage3.json"))
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
        row = {"competition": name, "season": season, "season_cur": v["s_cur"],
               "primaryId": v["primaryId"], "crossborder": False,
               "betexplorer": v["betexplorer"], "sportkey": v["sportkey"],
               "understat": v.get("understat"), "cup": bool(v.get("cup")),
               "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
               "table_home": rh, "table_away": ra, "missing": missing, **m}
        # Bekertak (§4, 15 sep 2026): staan BEIDE ploegen buiten de basisdivisie, dan is er
        # misschien een divisie eronder waarin ze allebei staan — dan valt er niets te
        # overbruggen en is het duel daarin gewoon door te rekenen.
        if len(missing) == 2 and name in promotion.CUP_BASE:
            base = promotion.CUP_BASE.get(name, name)
            try:
                sd = promotion.shared_lower_division(base, m["home"], m["away"], season)
            except Exception as e:
                sd = None
                row["basis_zoekfout"] = f"{type(e).__name__}: {e}"
            if sd is not None:
                sub = fotmob.fetch_league_stats(sd.fotmob_id, season)
                sub_full = any("xg" in t for t in sub["teams"].values())
                row.update({"primaryId": sd.fotmob_id, "basis_comp": sd.competition,
                            "basis_note": sd.note, "table_home": sd.home_key,
                            "table_away": sd.away_key, "missing": [],
                            "tier": "FULL" if sub_full else "LIGHT"})
        cands.append(row)

json.dump(cands, open("tmp-run/ra_oct31_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    if c.get("kruis_grens"):
        flag = "  " + json.dumps(c["kruis_grens"], ensure_ascii=False)[:160]
    print(f"  {c['tier']:6s} {c['competition']:30s} {c['home']} - {c['away']}{flag}")
