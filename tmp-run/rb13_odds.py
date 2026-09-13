"""Run B, 13 sep 2026 — Stage 3 vervolg: prijzen inkopen (§1a, bulk met h2h erbij).

BTTS staat hier NIET meer bij: sinds 13 sep 2026 koopt `rb13_btts.py` die markt in een
tweede ronde, ná de eerste analyse, voor de duels met een kandidaat-edge op de ruwe OF de
herijkte schaal (§1a stap 2, vastgelegd in _shared-rules.md op 13 sep). Tot en met 12 sep
kocht Run B BTTS vooraf voor de bovenste `MAX_DEEP_ANALYSES` duels, en dan is "toont al een
kandidaat-edge" geen criterium maar een rangschikking.

Overgenomen van `rb12_odds.py` van gisteren; het enige Run B-verschil zit in de
inkoopbaarheid. Vijf van de dertien competities die vandaag spelen hebben **geen sportkey**
bij The Odds API — de Czech First League, de Croatian HNL, de Romanian SuperLiga, de Keuken
Kampioen Divisie en de Kategoria Superiore — dus daar is BetExplorer de enige 1X2-bron
(marktgemiddelde, bookmaker niet herleidbaar, §1a laatste alinea) en zijn AH/DNB/DC/OU/BTTS
niet in te kopen. Dat is geen creditplafond: er staat ruim 19.000 credits open. De acht
overige competities krijgen de volle bulk-aanroep.
"""
import json, sys
from datetime import date
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts import betexplorer, oddsapi, ranking
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget, fetch_bulk, \
    fetch_spreads, fetch_totals, fetch_event_markets, rotate_for_day
from ra_names import best_pair, resolve
import rb13_retry  # noqa: F401

DAY = date(2026, 9, 13)
REMAINING, DAYS_LEFT = 19261, 18    # uit api_check.py van deze run (739 gebruikt deze maand)

cands = json.load(open("tmp-run/rb13_ctx.json"))
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
store["spent"] = guard.spent
store["remaining_na"] = guard.remaining
store["calls"] = guard.calls
store["cap"] = CAP
store["split"] = [n_spreads, n_totals]
store["geen_sportkey"] = [n for n, k, _ in comps if not k]
json.dump(store, open("tmp-run/rb13_odds.json", "w"), ensure_ascii=False, indent=1)
print("\n" + guard.report())
