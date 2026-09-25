import json, sys, urllib.request
sys.path.insert(0,'.')
from scripts import betexplorer as bx

candidates = {
 "concacaf_nl": [
   "https://www.betexplorer.com/football/world/concacaf-nations-league-2025-2026/",
   "https://www.betexplorer.com/football/north-central-america/concacaf-nations-league/",
   "https://www.betexplorer.com/football/north-central-america/concacaf-nations-league-2025-2026/",
 ],
 "friendlies": [
   "https://www.betexplorer.com/football/world/friendly-international/",
   "https://www.betexplorer.com/football/world/international-friendlies/",
   "https://www.betexplorer.com/football/world/friendlies/",
 ],
 "asean": [
   "https://www.betexplorer.com/football/asia/asean-cup/",
   "https://www.betexplorer.com/football/asia/aff-championship/",
   "https://www.betexplorer.com/football/asia/asean-championship-2026/",
 ],
}
for k, urls in candidates.items():
    for u in urls:
        try:
            rows = bx.fetch_league_fixtures(u)
            print(f"{k}: {u} -> {len(rows)} rows")
            for r in rows[:6]:
                print("    ", r.when, r.home, "-", r.away, r.odds)
        except Exception as e:
            print(f"{k}: {u} -> FOUT {type(e).__name__} {e}")
