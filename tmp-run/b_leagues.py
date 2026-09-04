import json, sys
sys.path.insert(0,'.'); sys.path.insert(0,'tmp-run')
from scripts.model import early_season_uplift

S = json.load(open("tmp-run/b_stage3.json"))
# base_season = de tabel waar teamsterkte + thuis/uit-splits vandaan komen (§1d: splits blijven
# op vorig seizoen). level_season = de tabel waar het competitieniveau vandaan komt.
CFG = {
 "2. Bundesliga (GER)":           {"base":"prev","level":"prev","uplift":True},
 "Keuken Kampioen Divisie (NED)": {"base":"prev","level":"prev","uplift":True},
 # Eliteserien is een kalenderjaarcompetitie: het lopende seizoen 2026 staat op 18 speeldagen en
 # heeft eigen xG. Het niveau komt daar dus rechtstreeks uit (gemeten, geen correctie nodig);
 # de teamsterkte blijft op 2025 als prior en wordt met blend_seasons met 2026 gewogen (§4).
 "Eliteserien (NOR)":             {"base":"prev","level":"cur","uplift":False},
 "Croatian HNL (CRO)":            {"base":"prev","level":"prev","uplift":True},
 "Kategoria Superiore (ALB)":     {"base":"prev","level":"prev","uplift":True},
 "Segunda División (ESP)":        {"base":"prev","level":"prev","uplift":True},
 "Hungarian NB I (HUN)":          {"base":"prev","level":"prev","uplift":True},
 "Romanian SuperLiga (ROU)":      {"base":"prev","level":"prev","uplift":True},
}
obs, detail = [], {}
out = {}
for comp, rec in S.items():
    cfg = CFG[comp]
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
        reden = ("niveau uit het lopende seizoen zelf" if cfg["level"] == "cur"
                 else "geen xG bij Fotmob voor deze competitie")
        detail[comp] = {"vorig": p.get("avg_xg_per_match"), "huidig": c.get("avg_xg_per_match"),
                        "speeldagen": c.get("matchdays"), "reden": reden}
factor, pooled, total_md = early_season_uplift(obs)
out["_uplift"] = {"factor": factor, "pooled": pooled, "total_md": total_md,
                  "n_obs": len(obs), "competities": detail}
print(f"uplift factor={factor:.6f} pooled={pooled:.6f} total_md={total_md} n_obs={len(obs)}")
for c, d in detail.items(): print(f"  {c:32s} {d}")
json.dump(out, open("tmp-run/b_leagues.json","w"), ensure_ascii=False, indent=1)
