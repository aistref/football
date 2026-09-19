"""Stage 3, tweede ronde — BTTS kopen voor de duels met een kandidaat-edge (§1a stap 2).

Dit is openstaand punt 4 uit `runs/2026-09-12-run-a.md`. §1a stap 2 koopt BTTS alleen voor
wedstrijden "die al een kandidaat-edge tonen", maar zei niet op welke schaal. Van 6 t/m 12 sep is
dat als de **herijkte** edge gelezen; de duels die alleen op de **ruwe** schaal boven hun drempel
uitkwamen kregen BTTS dus niet, terwijl dat precies de rijen zijn waarmee §5a de herijking
beoordeelt. Sinds vandaag is het de **vereniging** van beide lezingen (`kandidaat_edge` in
`rb19_analyze.py`): nooit krapper dan voorheen, en de reeks van §5a wordt er scherper van.

Het plafond van `rb19_odds.py` wordt hier opnieuw opgebouwd met het al uitgegeven bedrag erin,
zodat `CreditGuard` over de hele run klopt en niet per script opnieuw begint.
"""
import json, re, sys
sys.path.insert(0, "tmp-run")
from scripts import oddsapi
from scripts.oddsapi import CreditGuard, fetch_event_markets
from ra_names import best_pair, resolve

store = json.load(open("tmp-run/rb19_odds.json"))
res = json.load(open("tmp-run/rb19_results.json"))
cands = {c["match_id"]: c for c in json.load(open("tmp-run/rb19_ctx.json"))}

al_uit = int(re.match(r"(\d+) van", store["guard"]).group(1))
guard = CreditGuard(cap=store["cap"] - al_uit)

wanted = [m for m in res["matches"] if m.get("kandidaat_edge")]
print(f"BTTS voor {len(wanted)} van {len(res['matches'])} duels met een kandidaat-edge "
      f"(plafond nog {store['cap'] - al_uit} credits)")

for m in wanted:
    c = cands[m["match_id"]]
    name, key = c["competition"], c["sportkey"]
    if not key or name not in store["raw"]["spreads"]:
        print(f"  overslaan {m['match']}: geen sportkey of geen spreads-respons")
        continue
    ev = None
    for e in store["raw"]["spreads"][name]:
        if resolve(c["home"], {e["home_team"]: 1}) and resolve(c["away"], {e["away_team"]: 1}):
            ev = e; break
    if ev is None:
        ev = best_pair(c["home"], c["away"], store["raw"]["spreads"][name],
                       lambda e: e["home_team"], lambda e: e["away_team"])
    if ev is None:
        print(f"  overslaan {m['match']}: wedstrijd niet in de spreads-respons")
        continue
    if not guard.can_afford(2):
        print("STOP btts bij", m["match"]); break
    try:
        r = fetch_event_markets(key, ev["id"], ["btts"]); guard.record(r, f"btts {c['home']}")
        store["raw"]["btts"][str(m["match_id"])] = r.data
        store["bought"]["btts"].append(m["match_id"])
        print(f"  btts {m['match'][:40]:40s} ok")
    except Exception as e:
        store["errors"][f"btts {c['home']}"] = f"{type(e).__name__}: {e}"
        print(f"  btts {m['match'][:40]:40s} FAIL {type(e).__name__}: {e}")

store["guard_btts"] = guard.report()
btts_spent = int(re.match(r"(\d+) van", guard.report()).group(1))
store["guard_totaal"] = (f"{al_uit} credits aan de bulk + {btts_spent} aan BTTS = "
                        f"{al_uit + btts_spent} van {store['cap']}")
store["btts_kandidaat_edge"] = [m["match"] for m in wanted]
json.dump(store, open("tmp-run/rb19_odds.json", "w"), ensure_ascii=False, indent=1)
print("\n" + str(guard.report()))
