"""Stage 5a — inkoop van prijzen. §1a: spreads eerst (1 credit = AH + DNB + DC), daarna totals
volgens de rotatie. 1X2 komt gratis van BetExplorer."""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import betexplorer, oddsapi

DAY = date(2026, 8, 30)
CAP = 9                       # suggest_cap(56, 2) na api_check.py van deze run

cands = json.load(open("tmp-run/rb_ctx.json"))
# competities met wedstrijden die een tier != NONE hebben, op datakwaliteit
order, seen = [], set()
for c in cands:
    k = c["competition"]
    if c["tier"] == "NONE" or k in seen:
        continue
    seen.add(k)
    order.append((0 if c["tier"] == "FULL" else 1, k, c["sportkey"], c["slug"]))
order.sort()
with_key = [(k, sk) for _, k, sk, _ in order if sk]
print("competities met sportkey, op datakwaliteit:", [k for k, _ in with_key])

guard = oddsapi.CreditGuard(cap=CAP)
totals_for = oddsapi.rotate_for_day([k for k, _ in with_key], DAY, take=1)
print("rotatie totals ->", totals_for)

bought = {"spreads": [], "totals": [], "btts": []}
raw = {"spreads": {}, "totals": {}}
errors = {}

# stap 0: spreads voor zoveel mogelijk competities (1 credit, drie markten)
for comp, sk in with_key:
    if comp in totals_for:
        continue
    if not guard.can_afford(1):
        break
    try:
        r = oddsapi.fetch_spreads(sk)
        guard.record(r, f"spreads {comp}")
        raw["spreads"][comp] = r.data
        bought["spreads"].append(comp)
    except Exception as e:
        errors[f"spreads {comp}"] = f"{type(e).__name__}: {e}"

# stap 1: totals voor de competitie(s) die vandaag aan de beurt zijn
for comp in totals_for:
    sk = dict(with_key)[comp]
    if not guard.can_afford(1):
        errors[f"totals {comp}"] = "creditplafond bereikt"
        break
    try:
        r = oddsapi.fetch_totals(sk)
        guard.record(r, f"totals {comp}")
        raw["totals"][comp] = r.data
        bought["totals"].append(comp)
    except Exception as e:
        errors[f"totals {comp}"] = f"{type(e).__name__}: {e}"

print(guard.report(), "| fouten:", errors)

# 1X2, gratis, voor elke competitie met een slug
fixtures = {}
for _, comp, _, slug in order:
    if not slug:
        continue
    try:
        rows = betexplorer.fetch_league_fixtures(f"https://www.betexplorer.com/football/{slug}/")
        fixtures[comp] = [{"home": m.home, "away": m.away, "odds": list(m.odds),
                           "is_today": m.is_today, "when": m.when, "books": m.bookmakers} for m in rows]
        print(f"{comp:32s} betexplorer {len(rows)} rijen, {sum(m.is_today for m in rows)} vandaag")
    except Exception as e:
        errors[f"1X2 {comp}"] = f"{type(e).__name__}: {e}"
        print(f"{comp:32s} betexplorer FOUT {e}")

json.dump({"bought": bought, "raw": raw, "fixtures": fixtures, "errors": errors,
           "guard": {"cap": CAP, "spent": guard.spent, "remaining": guard.remaining,
                     "report": guard.report(), "calls": guard.calls},
           "totals_rotation": totals_for},
          open("tmp-run/rb_odds.json", "w"), ensure_ascii=False)
