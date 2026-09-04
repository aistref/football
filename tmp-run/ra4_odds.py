"""Stage 3 vervolg — prijzen inkopen binnen het creditplafond (§1a)."""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import betexplorer, oddsapi
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget, fetch_spreads, fetch_totals, \
    fetch_event_markets, rotate_for_day

DAY = date(2026, 9, 4)
REMAINING, DAYS_LEFT = 19889, 27    # uit api_check.py van vanochtend (111 gebruikt deze maand)

cands = json.load(open("tmp-run/ra4_ctx.json"))
comps = []
for c in cands:
    if c["competition"] not in [x[0] for x in comps]:
        comps.append((c["competition"], c["sportkey"], c["betexplorer"]))

buyable = [c for c in comps if c[1]]
CAP = suggest_cap(REMAINING, DAYS_LEFT)
n_spreads, n_totals = split_budget(CAP, len(buyable))
guard = CreditGuard(cap=CAP)
print(f"plafond {CAP} credits ({REMAINING} over, {DAYS_LEFT} dag tot de maandwissel, 2 runs/dag)")
print(f"verdeling split_budget({CAP}, {len(buyable)}) -> {n_spreads} spreads / {n_totals} totals")

store = {"raw": {"spreads": {}, "totals": {}, "btts": {}}, "fixtures": {},
         "bought": {"spreads": [], "totals": [], "btts": []}, "errors": {}}

# --- 1X2, gratis, BetExplorer ---
for name, key, url in comps:
    if not url:
        store["errors"][f"1x2 {name}"] = "geen betexplorer-slug"
        continue
    try:
        rows = betexplorer.fetch_league_fixtures(url)
        store["fixtures"][name] = [{"home": r.home, "away": r.away, "odds": list(r.odds),
                                    "books": r.bookmakers, "is_today": r.is_today} for r in rows]
        print(f"1X2 {name:24s} {len(rows)} rijen ({sum(r.is_today for r in rows)} vandaag)")
    except Exception as e:
        store["errors"][f"1x2 {name}"] = f"{type(e).__name__}: {e}"
        print(f"1X2 {name:24s} FAIL {type(e).__name__}: {e}")

# --- stap 0: spreads (1 credit, levert AH + DNB + DC) ---
for name, key, _ in buyable[:n_spreads]:
    if not guard.can_afford(1):
        print("STOP spreads bij", name); break
    try:
        r = fetch_spreads(key); guard.record(r, f"spreads {name}")
        store["raw"]["spreads"][name] = r.data; store["bought"]["spreads"].append(name)
        print(f"spreads {name:22s} {len(r.data)} events")
    except Exception as e:
        store["errors"][f"spreads {name}"] = f"{type(e).__name__}: {e}"
        print(f"spreads {name:22s} FAIL {type(e).__name__}: {e}")

# --- stap 1: totals (1 credit), rotatie over de competities ---
beurt = rotate_for_day([n for n, _, _ in buyable], DAY, take=n_totals)
print("rotatie totals:", beurt)
for name in beurt:
    key = dict((n, k) for n, k, _ in buyable)[name]
    if not guard.can_afford(1):
        print("STOP totals bij", name); break
    try:
        r = fetch_totals(key); guard.record(r, f"totals {name}")
        store["raw"]["totals"][name] = r.data; store["bought"]["totals"].append(name)
        print(f"totals  {name:22s} {len(r.data)} events")
    except Exception as e:
        store["errors"][f"totals {name}"] = f"{type(e).__name__}: {e}"
        print(f"totals  {name:22s} FAIL {type(e).__name__}: {e}")

# --- stap 2: BTTS per wedstrijd (2 credits) — alleen als er nog ruimte is ---
from ra_names import best_pair, resolve
for c in cands:
    name, key = c["competition"], c["sportkey"]
    if not key or name not in store["raw"]["spreads"]:
        continue
    ev = None
    for e in store["raw"]["spreads"][name]:
        if resolve(c["home"], {e["home_team"]: 1}) and resolve(c["away"], {e["away_team"]: 1}):
            ev = e; break
    if ev is None:
        ev = best_pair(c["home"], c["away"], store["raw"]["spreads"][name],
                       lambda e: e["home_team"], lambda e: e["away_team"])
    if ev is None:
        continue
    if not guard.can_afford(2):
        print("STOP btts bij", c["home"]); break
    try:
        r = fetch_event_markets(key, ev["id"], ["btts"]); guard.record(r, f"btts {c['home']}")
        store["raw"]["btts"][str(c["match_id"])] = r.data
        store["bought"]["btts"].append(c["match_id"])
        print(f"btts    {c['home'][:16]:16s} - {c['away'][:16]:16s} ok")
    except Exception as e:
        store["errors"][f"btts {c['home']}"] = f"{type(e).__name__}: {e}"
        print(f"btts    {c['home'][:16]:16s} FAIL {type(e).__name__}: {e}")

store["guard"] = guard.report()
store["cap"] = CAP
store["split"] = [n_spreads, n_totals]
json.dump(store, open("tmp-run/ra4_odds.json", "w"), ensure_ascii=False, indent=1)
print("\n", guard.report())
