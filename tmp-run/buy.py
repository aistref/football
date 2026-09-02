import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget, rotate_for_day, fetch_spreads, fetch_totals

REMAIN, DAYS = 19935, 29
cap = suggest_cap(REMAIN, DAYS)
KEYS={"English League One (ENG)":"soccer_england_league1",
      "Austrian Bundesliga (AUT)":"soccer_austria_bundesliga",
      "Swiss Super League (SUI)":"soccer_switzerland_superleague"}
comps=list(KEYS)
n_spreads, n_totals = split_budget(cap, len(comps))
print(f"cap={cap}  split_budget({cap},{len(comps)}) -> spreads={n_spreads} totals={n_totals}")
guard=CreditGuard(cap=cap)
res={"cap":cap,"n_spreads":n_spreads,"n_totals":n_totals,"spreads":{},"totals":{},"markten_gekocht":{}}
for comp in comps[:n_spreads]:
    if guard.can_afford(1):
        r=fetch_spreads(KEYS[comp]); guard.record(r, comp)
        res["spreads"][comp]=r.data
        print(f"spreads {comp}: {len(r.data)} events")
tot = rotate_for_day(comps, date.today(), take=n_totals)
print("totals rotation today:", tot)
for comp in tot:
    if guard.can_afford(1):
        r=fetch_totals(KEYS[comp]); guard.record(r, comp)
        res["totals"][comp]=r.data
        print(f"totals  {comp}: {len(r.data)} events")
res["guard_report"]=guard.report()
res["used"]=getattr(guard,'used',None)
print("\n"+guard.report())
json.dump(res, open("tmp-run/odds_api.json","w"), ensure_ascii=False)
