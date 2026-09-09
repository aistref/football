"""Run B, 9 sep 2026 — Stage 3 vervolg: prijzen inkopen (§1a).

Vandaag staat er precies één competitie uit de runlijst op de kalender: de Czech First
League. Die heeft **geen sportkey** bij The Odds API (vastgelegd in `coverage.json` sinds
9 aug 2026), dus er valt niets in te kopen: `buyable` is leeg, de CreditGuard geeft nul uit
en BetExplorer is de enige 1X2-bron — marktgemiddelde, bookmaker niet herleidbaar (§1a,
laatste alinea).

Gevolg voor de marktbalans-controle (§1a): die eist minstens één competitie met een
doelpuntenmarkt én één met een uitkomstmarkt. Vandaag haalt hij het niet, en de reden is
**niet** een te krap plafond — er is 19.520 credits over — maar het ontbreken van een
sportkey voor de enige competitie die speelt. Dat verschil hoort expliciet in het runrapport.
"""
import json, sys
from datetime import date
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts import betexplorer, oddsapi, ranking
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget

DAY = date(2026, 9, 9)
REMAINING, DAYS_LEFT = 19520, 22    # uit api_check.py van deze run (480 gebruikt deze maand)

cands = json.load(open("tmp-run/rb9_ctx.json"))
comps = []
for c in cands:
    if c["competition"] not in [x[0] for x in comps]:
        comps.append((c["competition"], c["sportkey"], c["betexplorer"]))

buyable = [c for c in comps if c[1]]
CAP = suggest_cap(REMAINING, DAYS_LEFT)
n_spreads, n_totals = split_budget(CAP, len(buyable)) if buyable else (0, 0)
guard = CreditGuard(cap=CAP)
print(f"plafond {CAP} credits ({REMAINING} over, {DAYS_LEFT} dagen tot de maandwissel, 2 runs/dag)")
print(f"inkoopbare competities (met sportkey): {len(buyable)} van {len(comps)}")
print(f"verdeling split_budget -> {n_spreads} spreads / {n_totals} totals")

store = {"raw": {"spreads": {}, "totals": {}, "h2h": {}, "btts": {}}, "fixtures": {},
         "bought": {"spreads": [], "totals": [], "h2h": [], "btts": []}, "errors": {},
         "bulk": False}

# --- marktgemiddelde 1X2, gratis, BetExplorer ---
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

# --- stap 0/1/2: niets te kopen, geen sportkey ---
for name, key, _ in comps:
    if not key:
        store["errors"][f"odds {name}"] = "geen sportkey bij The Odds API — niets in te kopen"

store["guard"] = guard.report()
store["cap"] = CAP
store["split"] = [n_spreads, n_totals]
store["geen_sportkey"] = [n for n, k, _ in comps if not k]
json.dump(store, open("tmp-run/rb9_odds.json", "w"), ensure_ascii=False, indent=1)
print("\n" + guard.report())
