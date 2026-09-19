"""Stage 3 vervolg — prijzen inkopen (§1a, bulk met h2h erbij sinds 5 sep 2026).

Eén verschil met 11 sep, en het is het openstaande punt 4 uit `runs/2026-09-12-run-a.md`:
**BTTS wordt hier niet meer gekocht.** §1a stap 2 zegt BTTS pas op te vragen voor wedstrijden die
"al een kandidaat-edge tonen", en dat kan pas nadat de vijf gratis/gebulkte markten zijn
doorgerekend. Dit script koopt daarom alleen de bulk; `ra19_btts.py` doet de tweede ronde op basis
van de uitkomst van `ra19_analyze.py`. Welke schaal "kandidaat-edge" is, staat daar beschreven.
"""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import betexplorer, oddsapi, ranking
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget, fetch_bulk, \
    fetch_spreads, fetch_totals, rotate_for_day
from ra_names import best_pair, resolve

DAY = date(2026, 9, 19)
REMAINING, DAYS_LEFT = 19009, 12    # na de ochtendrun van vandaag

cands = json.load(open("tmp-run/ra19_ctx.json"))
comps = []
for c in cands:
    if c["competition"] not in [x[0] for x in comps]:
        comps.append((c["competition"], c["sportkey"], c["betexplorer"]))

buyable = [c for c in comps if c[1]]
CAP = suggest_cap(REMAINING, DAYS_LEFT)
n_spreads, n_totals = split_budget(CAP, len(buyable))
guard = CreditGuard(cap=CAP)
print(f"plafond {CAP} credits ({REMAINING} over, {DAYS_LEFT} dagen tot de maandwissel, 2 runs/dag)")
print(f"verdeling split_budget({CAP}, {len(buyable)}) -> {n_spreads} spreads / {n_totals} totals")
BULK = CAP >= 3 * len(buyable)
print(f"bulk (h2h+spreads+totals, 3 cr/competitie): {BULK} — {3*len(buyable)} van {CAP} credits")

store = {"raw": {"spreads": {}, "totals": {}, "h2h": {}, "btts": {}}, "fixtures": {},
         "bought": {"spreads": [], "totals": [], "h2h": [], "btts": []}, "errors": {},
         "bulk": BULK}

# --- marktgemiddelde 1X2, gratis, BetExplorer: alleen voor §6e en poort 8 ---
for name, key, url in comps:
    if not url:
        store["errors"][f"1x2 {name}"] = "geen betexplorer-slug"
        continue
    try:
        rows = betexplorer.fetch_league_fixtures(url)
        store["fixtures"][name] = [{"home": r.home, "away": r.away, "odds": list(r.odds),
                                    "books": r.bookmakers, "is_today": r.is_today} for r in rows]
        print(f"1X2-gem {name:24s} {len(rows)} rijen ({sum(r.is_today for r in rows)} vandaag)")
    except Exception as e:
        store["errors"][f"1x2 {name}"] = f"{type(e).__name__}: {e}"
        print(f"1X2-gem {name:24s} FAIL {type(e).__name__}: {e}")

# --- stap 0: de bulk-aanroep (3 credits: h2h + spreads + totals) ---
for name, key, _ in buyable[:n_spreads]:
    if BULK and guard.can_afford(3):
        try:
            r = fetch_bulk(key, ["h2h", "spreads", "totals"]); guard.record(r, f"bulk {name}")
            for kind in ("h2h", "spreads", "totals"):
                store["raw"][kind][name] = r.data
                store["bought"][kind].append(name)
            print(f"bulk    {name:22s} {len(r.data)} events (h2h+spreads+totals)")
        except Exception as e:
            store["errors"][f"bulk {name}"] = f"{type(e).__name__}: {e}"
            print(f"bulk    {name:22s} FAIL {type(e).__name__}: {e}")
    elif guard.can_afford(1):
        try:
            r = fetch_spreads(key); guard.record(r, f"spreads {name}")
            store["raw"]["spreads"][name] = r.data; store["bought"]["spreads"].append(name)
            print(f"spreads {name:22s} {len(r.data)} events")
        except Exception as e:
            store["errors"][f"spreads {name}"] = f"{type(e).__name__}: {e}"
    else:
        print("STOP bij", name); break

# --- stap 1: totals los, alleen voor wie buiten de bulk viel ---
if not BULK:
    beurt = [n for n in rotate_for_day([n for n, _, _ in buyable], DAY, take=n_totals)
             if n not in store["raw"]["totals"]]
    for name in beurt:
        key = dict((n, k) for n, k, _ in buyable)[name]
        if not guard.can_afford(1):
            break
        try:
            r = fetch_totals(key); guard.record(r, f"totals {name}")
            store["raw"]["totals"][name] = r.data; store["bought"]["totals"].append(name)
            print(f"totals  {name:22s} {len(r.data)} events")
        except Exception as e:
            store["errors"][f"totals {name}"] = f"{type(e).__name__}: {e}"

store["guard"] = guard.report()
store["cap"] = CAP
store["split"] = [n_spreads, n_totals]
json.dump(store, open("tmp-run/ra19h_odds.json", "w"), ensure_ascii=False, indent=1)
print("\n" + guard.report())
