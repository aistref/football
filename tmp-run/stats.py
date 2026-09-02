import json, sys
sys.path.insert(0,'.')
from scripts import fotmob
from scripts.model import early_season_uplift

M = json.load(open("tmp-run/matches.json"))
BASE = {"English League One (ENG)": ("2025/2026","2026/2027"),
        "Czech First League (CZE)": ("2025/2026","2026/2027"),
        "Austrian Bundesliga (AUT)": ("2025/2026","2026/2027"),
        "Swiss Super League (SUI)": ("2025/2026","2026/2027")}
out={}
obs=[]
for comp,(prev,cur) in BASE.items():
    lid = M[comp]["league_id"]
    p = fotmob.fetch_league_stats(lid, prev)
    c = fotmob.fetch_league_stats(lid, cur)
    md = max((t.get("played",0) for t in c["teams"].values()), default=0)
    out[comp]={"league_id":lid,"prev_season":prev,"cur_season":cur,
               "prev":{k:p[k] for k in ("home_goals_per_match","away_goals_per_match","avg_xg_per_match","has_xg")},
               "cur":{k:c[k] for k in ("home_goals_per_match","away_goals_per_match","avg_xg_per_match","has_xg")},
               "matchdays":md, "n_teams_prev":len(p["teams"])}
    print(comp, "prev avg_xg", p["avg_xg_per_match"], "cur avg_xg", c["avg_xg_per_match"], "md", md,
          "prev hg/ag", round(p["home_goals_per_match"],3), round(p["away_goals_per_match"],3))
    if p["avg_xg_per_match"] and c["avg_xg_per_match"] and md:
        obs.append((p["avg_xg_per_match"], c["avg_xg_per_match"], md))

factor, pooled, total_md = early_season_uplift(obs)
print("\nUPLIFT factor=%.4f pooled=%.4f total_md=%s  (n_obs=%d)" % (factor, pooled, total_md, len(obs)))
out["_uplift"]={"factor":factor,"pooled":pooled,"total_md":total_md,"n_obs":len(obs)}
json.dump(out, open("tmp-run/leagues.json","w"), ensure_ascii=False, indent=1)
