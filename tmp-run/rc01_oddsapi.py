import json
from scripts import oddsapi

resp = oddsapi.fetch_bulk("soccer_uefa_nations_league", ["h2h", "spreads", "totals"])
events = resp.data
print("events:", len(events))
for e in events:
    print(e["commence_time"], e["home_team"], "-", e["away_team"], e["id"])
json.dump(events, open("tmp-run/rc01_oddsapi_nl.json", "w"), indent=1, ensure_ascii=False)
print("remaining credits (headers):", resp.requests_remaining, resp.requests_used, resp.cost)
