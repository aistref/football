import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget, rotate_for_day, fetch_spreads, fetch_totals

REMAIN, DAYS = 19783, 26
cap = suggest_cap(REMAIN, DAYS)
KEYS={"2. Bundesliga (GER)":"soccer_germany_bundesliga2",
      "Segunda División (ESP)":"soccer_spain_segunda_division",
      "Eliteserien (NOR)":"soccer_norway_eliteserien",
      "Allsvenskan (SWE)":"soccer_sweden_allsvenskan",
      "Swiss Super League (SUI)":"soccer_switzerland_superleague",
      "Greek Super League (GRE)":"soccer_greece_super_league",
      "Serie B (ITA)":"soccer_italy_serie_b",
      "English League One (ENG)":"soccer_england_league1",
      "English League Two (ENG)":"soccer_england_league2"}
comps=list(KEYS)
n_spreads, n_totals = split_budget(cap, len(comps))
print(f"cap={cap}  split_budget({cap},{len(comps)}) -> spreads={n_spreads} totals={n_totals}")
guard=CreditGuard(cap=cap)
res={"cap":cap,"n_spreads":n_spreads,"n_totals":n_totals,"spreads":{},"totals":{},
     "geen_sportkey":["Czech First League (CZE)","Croatian HNL (CRO)","Hungarian NB I (HUN)",
                      "Romanian SuperLiga (ROU)","Keuken Kampioen Divisie (NED)","Kategoria Superiore (ALB)"]}
for comp in comps[:n_spreads]:
    if guard.can_afford(1):
        r=fetch_spreads(KEYS[comp]); guard.record(r, comp)
        res["spreads"][comp]=r.data
        print(f"spreads {comp}: {len(r.data)} events", flush=True)
tot = rotate_for_day(comps, date(2026,9,5), take=n_totals)
print("totals rotatie vandaag:", tot)
for comp in tot:
    if guard.can_afford(1):
        r=fetch_totals(KEYS[comp]); guard.record(r, comp)
        res["totals"][comp]=r.data
        print(f"totals  {comp}: {len(r.data)} events", flush=True)
res["guard_report"]=guard.report()
res["sport_keys"]=KEYS
print("\n"+guard.report())
json.dump(res, open("tmp-run/c_oddsapi.json","w"), ensure_ascii=False)
