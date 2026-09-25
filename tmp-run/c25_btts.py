import json, sys
sys.path.insert(0, '.')
from scripts import oddsapi

need = [
 ("UEFA Nations League A (id 9806)", "Turkiye – France", "2b7592be536420c10378dd7522466f6a"),
 ("UEFA Nations League B (id 9807)", "Poland – Bosnia and Herzegovina", "bd6aee3c71bd9b3897ae6bc55bd43de4"),
 ("UEFA Nations League C (id 9808)", "Montenegro – Cyprus", "8d8af5c471bb4fbf8f3dd85dbd414227"),
]
out = {}
total_cost = 0
for comp, match, eid in need:
    resp = oddsapi.fetch_event_markets("soccer_uefa_nations_league", eid, ["btts", "double_chance"])
    out[eid] = resp.data
    total_cost += resp.cost or 0
    print(match, "cost", resp.cost, "remaining", resp.requests_remaining)
    for bm in resp.data.get("bookmakers", []):
        for mk in bm.get("markets", []):
            if mk["key"] == "btts":
                print("  ", bm["title"], mk["outcomes"])
print("totale kosten BTTS/DC-ophaal:", total_cost)
with open("tmp-run/c25_btts.json", "w") as f:
    json.dump(out, f, indent=1)
