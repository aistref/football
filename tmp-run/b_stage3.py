import json, sys
sys.path.insert(0,'.')
from scripts import fotmob

COMPS = {
 "2. Bundesliga (GER)":            {"league_id":146, "prev_season":"2025/2026", "cur_season":"2026/2027"},
 "Keuken Kampioen Divisie (NED)":  {"league_id":111, "prev_season":"2025/2026", "cur_season":"2026/2027"},
 "Eliteserien (NOR)":              {"league_id":59,  "prev_season":"2025", "cur_season":"2026"},
 "Croatian HNL (CRO)":             {"league_id":252, "prev_season":"2025/2026", "cur_season":"2026/2027"},
 "Kategoria Superiore (ALB)":      {"league_id":260, "prev_season":"2025/2026", "cur_season":"2026/2027"},
 "Segunda División (ESP)":         {"league_id":140, "prev_season":"2025/2026", "cur_season":"2026/2027"},
 "Hungarian NB I (HUN)":           {"league_id":212, "prev_season":"2025/2026", "cur_season":"2026/2027"},
 "Romanian SuperLiga (ROU)":       {"league_id":189, "prev_season":"2025/2026", "cur_season":"2026/2027"},
}
out={}
for comp, c in COMPS.items():
    rec=dict(c)
    for tag, season in (("prev", c["prev_season"]), ("cur", c["cur_season"])):
        try:
            st = fotmob.fetch_league_stats(c["league_id"], season)
            teams = st["teams"]
            played = sum(t.get("played",0) for t in teams.values())
            rec[tag]={"home_goals_per_match":st["home_goals_per_match"],
                      "away_goals_per_match":st["away_goals_per_match"],
                      "avg_xg_per_match":st["avg_xg_per_match"],
                      "has_xg":st["avg_xg_per_match"] is not None,
                      "n_teams":len(teams), "played":played/2 if played else 0,
                      "matchdays": round(played/len(teams),1) if teams else 0}
            print(f"{comp:32s} {tag} {season:10s} teams={len(teams):3d} md={rec[tag]['matchdays']:5.1f} xg={st['avg_xg_per_match']}")
        except Exception as e:
            rec[tag]={"error":f"{type(e).__name__}: {e}"}
            print(f"{comp:32s} {tag} {season:10s} ERROR {e}")
    out[comp]=rec
json.dump(out, open("tmp-run/b_stage3.json","w"), ensure_ascii=False, indent=1)
