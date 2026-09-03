import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget, rotate_for_day, fetch_spreads, fetch_totals

REMAIN, DAYS = 19896, 28
cap = suggest_cap(REMAIN, DAYS)
KEYS={"Allsvenskan (SWE)":"soccer_sweden_allsvenskan",
      "Swiss Super League (SUI)":"soccer_switzerland_superleague"}
comps=list(KEYS)
n_spreads, n_totals = split_budget(cap, len(comps))
print(f"cap={cap}  split_budget({cap},{len(comps)}) -> spreads={n_spreads} totals={n_totals}")
guard=CreditGuard(cap=cap)
res={"cap":cap,"n_spreads":n_spreads,"n_totals":n_totals,"spreads":{},"totals":{}}
for comp in comps[:n_spreads]:
    if guard.can_afford(1):
        r=fetch_spreads(KEYS[comp]); guard.record(r, comp)
        res["spreads"][comp]=r.data
        print(f"spreads {comp}: {len(r.data)} events")
tot = rotate_for_day(comps, date(2026,9,3), take=n_totals)
print("totals rotation today:", tot)
for comp in tot:
    if guard.can_afford(1):
        r=fetch_totals(KEYS[comp]); guard.record(r, comp)
        res["totals"][comp]=r.data
        print(f"totals  {comp}: {len(r.data)} events")
res["guard_report"]=guard.report()
print("\n"+guard.report())
json.dump(res, open("tmp-run/b_oddsapi.json","w"), ensure_ascii=False)
