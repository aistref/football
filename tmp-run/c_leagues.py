import json, sys
sys.path.insert(0,'.'); sys.path.insert(0,'tmp-run')
from scripts.model import early_season_uplift
S = json.load(open("tmp-run/c_stage3.json"))
# Alleen de negen FULL-competities: de zes zonder Fotmob-xG vallen in Stage 4 volledig weg
# (tier LIGHT staat onder FULL en er zijn al 45 FULL-kandidaten voor 35 plekken).
CFG = {
 "2. Bundesliga (GER)":       {"base":"prev","level":"prev","uplift":True},
 "Segunda División (ESP)":    {"base":"prev","level":"prev","uplift":True},
 # Eliteserien en Allsvenskan zijn kalenderjaarcompetities: het lopende seizoen 2026 staat op
 # 18+ speeldagen en heeft eigen xG, dus het niveau komt daar rechtstreeks uit (gemeten, geen
 # correctie nodig). De teamsterkte blijft 2025 als prior en wordt met blend_seasons gewogen (§4).
 "Eliteserien (NOR)":         {"base":"prev","level":"cur","uplift":False},
 "Allsvenskan (SWE)":         {"base":"prev","level":"cur","uplift":False},
 "Swiss Super League (SUI)":  {"base":"prev","level":"prev","uplift":True},
 "Greek Super League (GRE)":  {"base":"prev","level":"prev","uplift":True},
 "Serie B (ITA)":             {"base":"prev","level":"prev","uplift":True},
 "English League One (ENG)":  {"base":"prev","level":"prev","uplift":True},
 "English League Two (ENG)":  {"base":"prev","level":"prev","uplift":True},
}
obs, detail, out = [], {}, {}
for comp, cfg in CFG.items():
    rec = S[comp]
    seasons = {"prev": rec["prev_season"], "cur": rec["cur_season"]}
    blk = dict(rec)
    blk["base_season"]  = seasons[cfg["base"]]
    blk["level_season"] = seasons[cfg["level"]]
    blk["uplift"] = cfg["uplift"]
    out[comp] = blk
    p, c = rec["prev"], rec["cur"]
    if cfg["uplift"] and p.get("has_xg") and c.get("has_xg") and c.get("matchdays"):
        obs.append((p["avg_xg_per_match"], c["avg_xg_per_match"], c["matchdays"]))
        detail[comp] = {"vorig": p["avg_xg_per_match"], "huidig": c["avg_xg_per_match"],
                        "speeldagen": c["matchdays"]}
    else:
        detail[comp] = {"vorig": p.get("avg_xg_per_match"), "huidig": c.get("avg_xg_per_match"),
                        "speeldagen": c.get("matchdays"),
                        "reden": "niveau uit het lopende seizoen zelf"}
factor, pooled, total_md = early_season_uplift(obs)
out["_uplift"] = {"factor": factor, "pooled": pooled, "total_md": total_md,
                  "n_obs": len(obs), "competities": detail}
print(f"uplift factor={factor:.6f} pooled={pooled:.6f} total_md={total_md} n_obs={len(obs)}")
for c, d in detail.items(): print(f"  {c:30s} {d}")
json.dump(out, open("tmp-run/c_leagues.json","w"), ensure_ascii=False, indent=1)
