"""Stage 3 vervolg — prijzen inkopen (§1a), Run B 21 sep 2026.

Bijzonder aan deze dag: de enige competitie uit de runlijst die speelt is de Romanian SuperLiga,
en die heeft **geen sportkey** bij The Odds API (nagetrokken op de /sports/-lijst van vandaag: 30
actieve voetbalcompetities, Roemenie staat er niet bij). Er is dus niets inkoopbaars, het plafond
bindt nergens en de run geeft 0 credits uit. 1X2 komt van het BetExplorer-marktgemiddelde, precies
de terugval die §1a voor competities zonder sportkey voorschrijft; AH/DNB/DC/OU/BTTS zijn vandaag
in het geheel niet te koop.
"""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import betexplorer
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget

DAY = date(2026, 9, 21)
REMAINING, DAYS_LEFT = 18763, 10    # api_check.py van deze run: 1237 verbruikt deze maand

cands = json.load(open("tmp-run/rb21_ctx.json"))
comps = []
for c in cands:
    if c["competition"] not in [x[0] for x in comps]:
        comps.append((c["competition"], c["sportkey"], c["betexplorer"]))

buyable = [c for c in comps if c[1]]
CAP = suggest_cap(REMAINING, DAYS_LEFT)
n_spreads, n_totals = split_budget(CAP, len(buyable))
guard = CreditGuard(cap=CAP)
print(f"plafond {CAP} credits ({REMAINING} over, {DAYS_LEFT} dagen tot de maandwissel, 2 runs/dag)")
print(f"inkoopbare competities vandaag: {len(buyable)} van {len(comps)}")
print(f"verdeling split_budget({CAP}, {len(buyable)}) -> {n_spreads} spreads / {n_totals} totals")

store = {"raw": {"spreads": {}, "totals": {}, "h2h": {}, "btts": {}}, "fixtures": {},
         "bought": {"spreads": [], "totals": [], "h2h": [], "btts": []}, "errors": {},
         "bulk": False, "buyable": [c[0] for c in buyable]}

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

store["guard"] = guard.report()
store["cap"] = CAP
store["split"] = [n_spreads, n_totals]
json.dump(store, open("tmp-run/rb21_odds.json", "w"), ensure_ascii=False, indent=1)
print("\n" + guard.report())
