"""Run B 24 sep 2026 — Stage 3 voor de enige competitie met een duel vandaag: MLS (id 130).
MLS loopt op kalenderjaar, dus vorig seizoen = 2025 en lopend = 2026 (zie prompts/run-b.md)."""
import json
from scripts import fotmob

PID, S_PREV, S_CUR = 130, "2025", "2026"
out = {}
for label, season in (("prev", S_PREV), ("cur", S_CUR)):
    st = fotmob.fetch_league_stats(PID, season)
    has_xg = any("xg" in t for t in st["teams"].values())
    played = max((t.get("played") or 0) for t in st["teams"].values()) if st["teams"] else 0
    print(f"{label} ({season}): {len(st['teams'])} ploegen, xG={has_xg}, "
          f"avg_xg={st.get('avg_xg_per_match')}, home_gpm={st.get('home_goals_per_match')}, "
          f"away_gpm={st.get('away_goals_per_match')}, speeldagen={played}")
    out[label] = {"season": season, "teams": st["teams"], "avg_xg_per_match": st.get("avg_xg_per_match"),
                  "home_goals_per_match": st.get("home_goals_per_match"),
                  "away_goals_per_match": st.get("away_goals_per_match"),
                  "has_xg": has_xg, "played": played, "table": st.get("table")}
    for name in ("Seattle Sounders", "Real Salt Lake"):
        hit = [k for k in st["teams"] if name.split()[0].lower() in k.lower()]
        print("   ", name, "->", hit, {k: st["teams"][k] for k in hit})
json.dump(out, open("tmp-run/rb24_stage3.json", "w"), ensure_ascii=False, indent=1)
