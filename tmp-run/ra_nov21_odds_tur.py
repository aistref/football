"""Nabestelling: de bulk-aanroep voor de Süper Lig, die door de naamfout buiten de eerste ronde viel.

De sportkey stond in `oddsapi.SPORT_KEYS` onder "Süper Lig (TUR)" met trema en de runlijst
schrijft "Super Lig (TUR)" zonder; `SPORT_KEYS.get` gaf daarop stil None (zie `oddsapi.sport_key`,
toegevoegd vandaag). Deze aanroep haalt wat de eerste ronde daardoor niet kocht — 3 credits op een
plafond van 965, dus het plafond knelt niet — en voegt hem in hetzelfde `odds.json` samen, zodat
het creditverslag van de run één geheel blijft.
"""
import json, re
from scripts import oddsapi
from scripts.oddsapi import CreditGuard, fetch_bulk

store = json.load(open("tmp-run/ra_nov21_odds.json"))
al_uit = int(re.match(r"(\d+) van", store["guard"]).group(1))
guard = CreditGuard(cap=store["cap"] - al_uit)

NAAM = "Super Lig (TUR)"
key = oddsapi.sport_key(NAAM)
print("sportkey", NAAM, "->", key)
assert key and NAAM not in store["bought"]["spreads"]

r = fetch_bulk(key, ["h2h", "spreads", "totals"])
guard.record(r, f"bulk {NAAM}")
for kind in ("h2h", "spreads", "totals"):
    store["raw"][kind][NAAM] = r.data
    store["bought"][kind].append(NAAM)
print(f"bulk {NAAM}: {len(r.data)} events")

store["guard"] = f"{al_uit + 3} van {store['cap']} credits gebruikt in 11 aanroep(en), " \
                 f"nog {19324 - al_uit - 3} over"
store["nabestelling_tur"] = {"reden": "naamfout Süper Lig/Super Lig in SPORT_KEYS, "
                                      "gerepareerd met oddsapi.sport_key()",
                             "credits": 3, "events": len(r.data)}
json.dump(store, open("tmp-run/ra_nov21_odds.json", "w"), ensure_ascii=False, indent=1)
print(store["guard"])
