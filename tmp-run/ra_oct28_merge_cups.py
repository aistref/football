"""Run A, 28 okt 2026 — de drie bekers in het Stage 3-record zetten.

`ra_oct28_stage3.py` filtert op de `fotmob_id`'s uit `coverage.json` en die hebben de bekers niet
(zie `ra_oct28_cupmatches.py`). Hier gaan de 22 bekerduels alsnog het record in, met als
`primaryId` de **basisdivisie** uit `promotion.CUP_BASE`: een beker heeft geen eigen stand en dus
geen competitiegemiddelde om ploegen op te normaliseren (§4, "In een beker ligt de basis per
WEDSTRIJD"). `shared_lower_division` mag die basis in `ra_oct28_cand.py` per wedstrijd overrulen.
"""
import json
from scripts import fotmob

s3 = json.load(open("tmp-run/ra_oct28_stage3.json"))
cups = json.load(open("tmp-run/ra_oct28_cupmatches.json"))["cups"]

for name, v in cups.items():
    s3["fixtures"][name] = v
    if v["status"] != "?":
        continue
    prev = fotmob.fetch_league_stats(v["primaryId"], v["s_prev"])
    cur = fotmob.fetch_league_stats(v["primaryId"], v["s_cur"])
    has_xg = any("xg" in t for t in prev["teams"].values())
    played = max((t.get("played") or 0) for t in cur["teams"].values()) if cur["teams"] else 0
    played_prev = max((t.get("played") or 0) for t in prev["teams"].values()) if prev["teams"] else 0
    s3["stats"][name] = {
        "prev": {"teams": len(prev["teams"]), "has_xg": has_xg,
                 "avg_xg": prev.get("avg_xg_per_match"),
                 "home_gpm": prev.get("home_goals_per_match"),
                 "away_gpm": prev.get("away_goals_per_match"), "played": played_prev},
        "cur": {"played": played, "has_xg": any("xg" in t for t in cur["teams"].values()),
                "avg_xg": cur.get("avg_xg_per_match"),
                "home_gpm": cur.get("home_goals_per_match"),
                "away_gpm": cur.get("away_goals_per_match"), "teams": len(cur["teams"])},
    }
    print(f"{name:20s} basis {v['primaryId']:4d}  xG={has_xg}  vorig {played_prev} speeldagen, "
          f"lopend {played}  avg_xg vorig {prev.get('avg_xg_per_match')}")

# De twee bekers zonder ronde vandaag houden hun BetExplorer-uitkomst als toelichting.
cupstat = json.load(open("tmp-run/ra_oct28_cups.json"))["cups"]
for name in ("FA Cup (ENG)", "Coppa Italia (ITA)"):
    s3["fixtures"][name] = {"status": "GEEN WEDSTRIJD", "matches": [],
                            "eerste_ronde": cupstat[name]["betexplorer"]["eerste_ronde"]}

json.dump(s3, open("tmp-run/ra_oct28_stage3.json", "w"), ensure_ascii=False, indent=1)
actief = [k for k, v in s3["fixtures"].items() if v["status"] == "?"]
print("\nactief:", actief)
print("totaal wedstrijden:", sum(len(v["matches"]) for v in s3["fixtures"].values()))
