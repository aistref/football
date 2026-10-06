"""Per groep nazoeken waar de tien FA Cup-clubs in staan — met group=, niet met de stille greep."""
import json
from scripts import fotmob

CLUBS = ["Atherton", "Trafford", "Halesowen", "Stafford", "Scarborough",
         "Macclesfield", "Spalding", "Bury Town", "Wingate", "Bedford"]
TARGETS = [(117, None), (8944, "National League North"), (8944, "National League South"),
           (8947, "Southern Premier Division Central"), (8947, "Southern Premier Division South"),
           (8947, "Northern Premier Division"), (8947, "Isthmian Premier Division")]

where = {c: [] for c in CLUBS}
tables = {}
for lid, grp in TARGETS:
    for season in ("2025/2026", "2026/2027"):
        try:
            st = fotmob.fetch_league_stats(lid, season, group=grp)
        except Exception as e:
            print(f"{lid}/{grp}/{season}: FOUT {type(e).__name__}: {e}")
            continue
        names = sorted(st["teams"])
        tables[f"{lid}|{grp}|{season}"] = {
            "n": len(names), "has_xg": st["has_xg"],
            "home_gpm": st["home_goals_per_match"], "away_gpm": st["away_goals_per_match"]}
        print(f"{lid} {str(grp):36s} {season}  {len(names):3d} ploegen  xG={st['has_xg']}  "
              f"thuis {st['home_goals_per_match']}  uit {st['away_goals_per_match']}")
        for c in CLUBS:
            for n in names:
                if c.lower() in n.lower():
                    where[c].append({"league_id": lid, "group": grp, "season": season,
                                     "team": n, "played": st["teams"][n].get("played")})

print()
for c in CLUBS:
    print(f"  {c:20s}")
    for w in where[c]:
        print(f"      {w['season']}  id={w['league_id']}  {w['group']}  -> {w['team']} ({w['played']} duels)")
json.dump({"where": where, "tables": tables}, open("tmp-run/ra_oct06_groups.json", "w"),
          ensure_ascii=False, indent=1)
