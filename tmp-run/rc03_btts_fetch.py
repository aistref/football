import json
from scripts import oddsapi

targets = json.load(open("tmp-run/rc03_btts_targets.json"))
event_ids = sorted(set(t[2] for t in targets))
print("event ids:", event_ids)

out = {}
total_cost = 0
for eid in event_ids:
    resp = oddsapi.fetch_event_markets("soccer_uefa_nations_league", eid, ["btts", "double_chance"])
    out[eid] = resp.data
    total_cost += (resp.cost or 0)
    print(eid, "cost=", resp.cost, "remaining=", resp.requests_remaining)

json.dump(out, open("tmp-run/rc03_btts.json", "w"), indent=1, ensure_ascii=False)
print("totaal besteed:", total_cost)
