import json, sys
sys.path.insert(0,'.')
from scripts import oddsapi

resp = oddsapi.fetch_bulk(oddsapi.SPORT_KEYS["UEFA Nations League" if "UEFA Nations League" in oddsapi.SPORT_KEYS else list(oddsapi.SPORT_KEYS)[0]] if False else "soccer_uefa_nations_league", ["h2h","spreads","totals"])
print("events:", len(resp.data), "remaining:", resp.requests_remaining, "cost:", resp.cost)
for e in resp.data:
    print(" ", e.get("commence_time"), e.get("home_team"), "-", e.get("away_team"), "id", e.get("id"))
with open("tmp-run/c25_odds_nl.json","w") as f:
    json.dump(resp.data, f, indent=1)
