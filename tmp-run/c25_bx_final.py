import json, sys
sys.path.insert(0,'.')
from scripts import betexplorer as bx

urls = {
 "afcon": "https://www.betexplorer.com/football/africa/africa-cup-of-nations/",
 "concacaf_nl": "https://www.betexplorer.com/football/north-central-america/concacaf-nations-league/",
 "friendlies": "https://www.betexplorer.com/football/world/friendly-international/",
 "asean": "https://www.betexplorer.com/football/asia/asean-championship/",
}
out = {}
for k, u in urls.items():
    try:
        rows = bx.fetch_league_fixtures(u)
        print(f"{k}: {len(rows)} rows from {u}")
        out[k] = [r.__dict__ for r in rows]
    except Exception as e:
        print(f"{k}: FOUT {type(e).__name__} {e}")
        out[k] = []
with open("tmp-run/c25_bx.json","w") as f:
    json.dump(out, f, indent=1, default=str)
