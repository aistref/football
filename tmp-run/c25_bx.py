import json, sys
sys.path.insert(0,'.')
from scripts import betexplorer as bx

urls = {
 "afcon": "https://www.betexplorer.com/football/africa/africa-cup-of-nations/",
 "concacaf_nl": "https://www.betexplorer.com/football/world/concacaf-nations-league/",
 "friendlies": "https://www.betexplorer.com/football/world/friendly-internationals/",
 "asean": "https://www.betexplorer.com/football/asia/asean-championship/",
}
out = {}
for k, u in urls.items():
    try:
        rows = bx.fetch_league_fixtures(u)
        print(f"{k}: {len(rows)} rows from {u}")
        for r in rows[:40]:
            print("   ", r.when, r.home, "-", r.away, r.odds, "books", r.bookmakers, "today" if r.is_today else "")
        out[k] = [r.__dict__ for r in rows]
    except Exception as e:
        print(f"{k}: FOUT {type(e).__name__} {e}")
        out[k] = {"error": str(e)}
with open("tmp-run/c25_bx.json","w") as f:
    json.dump(out, f, indent=1, default=str)
