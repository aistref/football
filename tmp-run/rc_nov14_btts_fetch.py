import json
from scripts import oddsapi
ids = json.load(open("tmp-run/rc_nov14_btts_targets.json")); out = {}; cost = 0
for eid in ids:
    r = oddsapi.fetch_event_markets("soccer_uefa_nations_league", eid, ["btts"])
    out[eid] = r.data; cost += (r.cost or 0); print(eid, r.cost, r.requests_remaining)
json.dump(out, open("tmp-run/rc_nov14_btts.json", "w"), indent=1); print("totaal", cost)
