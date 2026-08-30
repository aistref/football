import json, traceback
from scripts import fotmob

fx = json.load(open("tmp-run/rb_fixtures.json"))
res = {}
for name, v in fx.items():
    if not v["matches"]:
        continue
    pid, sp, sc = v["primaryId"], v["s_prev"], v["s_cur"]
    entry = {}
    for label, season in (("prev", sp), ("cur", sc)):
        try:
            st = fotmob.fetch_league_stats(pid, season)
            entry[label] = {"has_xg": st["has_xg"], "teams": len(st["teams"]),
                            "avg_xg": st.get("avg_xg_per_match"),
                            "hgpm": st.get("home_goals_per_match"), "agpm": st.get("away_goals_per_match"),
                            "played": max((t.get("played", 0) for t in st["teams"].values()), default=0)}
        except Exception as e:
            entry[label] = {"error": f"{type(e).__name__}: {e}"}
    res[name] = entry
    print(name, json.dumps(entry, ensure_ascii=False))
json.dump(res, open("tmp-run/rb_stats.json", "w"), ensure_ascii=False, indent=1)
