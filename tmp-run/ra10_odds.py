"""Stage 3 vervolg — prijzen inkopen (§1a, versie van 5 sep 2026: bulk met h2h erbij).

Nieuw ten opzichte van ra5 (dat nog op de oude regel draaide): de bulk-aanroep haalt
`h2h` mee, zodat 1X2 op de **beste prijs** komt in plaats van op het BetExplorer-
marktgemiddelde. Dat is +1.84 pp edge per selectie voor 2 extra credits per competitie.
BetExplorer blijft draaien, maar alleen voor de twee rollen die géén prijs zijn: het
kalibratieblok van §6e en poort 8 — daar hoort het consensusgemiddelde, niet de
gunstigste uitschieter.
"""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import betexplorer, oddsapi, ranking
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget, fetch_bulk, \
    fetch_spreads, fetch_totals, fetch_event_markets, rotate_for_day
from ra_names import best_pair, resolve

DAY = date(2026, 9, 10)
REMAINING, DAYS_LEFT = 19520, 21    # uit api_check.py van vanochtend (480 gebruikt deze maand)

cands = json.load(open("tmp-run/ra10_ctx.json"))
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
# Het plafond is ruim genoeg voor 3 credits per competitie: dan gaat h2h mee in de bulk en
# staat 1X2 op de beste prijs (§1a). Past dat niet, dan valt de run terug op los inkopen.
BULK = CAP >= 3 * len(buyable)
print(f"bulk (h2h+spreads+totals, 3 cr/competitie): {BULK} — {3*len(buyable)} van {CAP} credits")

DEEP = ranking.max_deep_analyses(DAY)
ranked = sorted([c for c in cands if c["tier"] != "NONE" and c.get("richness") is not None],
                key=lambda c: ranking.sort_key(
                    "FULL" if c["tier"] == "FULL" else "LIGHT", c["richness"], 0, c["kickoff_utc"]))
btts_ids = {c["match_id"] for c in ranked[:DEEP]}
print(f"BTTS voor de bovenste {min(DEEP, len(ranked))} van {len(ranked)} duels met dekking")

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

# --- stap 2: BTTS per wedstrijd (2 credits) ---
for c in cands:
    name, key = c["competition"], c["sportkey"]
    if not key or name not in store["raw"]["spreads"] or c["match_id"] not in btts_ids:
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
json.dump(store, open("tmp-run/ra10_odds.json", "w"), ensure_ascii=False, indent=1)
print("\n" + guard.report())
