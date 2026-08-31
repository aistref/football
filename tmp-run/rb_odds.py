import json
from scripts.oddsapi import CreditGuard, fetch_spreads, fetch_totals, SPORT_KEYS, rotate_for_day
from datetime import date
COMPS=[("Greek Super League (GRE)","soccer_greece_super_league"),
       ("Segunda Division (ESP)","soccer_spain_segunda_division"),
       ("Allsvenskan (SWE)","soccer_sweden_allsvenskan")]
guard=CreditGuard(cap=9944)
out={"spreads":{},"totals":{}}
n_spreads,n_totals=3,3
for comp,key in COMPS[:n_spreads]:
    if guard.can_afford(1):
        r=fetch_spreads(key)
        guard.record(r, comp)
        out['spreads'][comp]=r.payload if hasattr(r,'payload') else r.data
        print(f"spreads {comp}: {len(out['spreads'][comp])} events")
rot=rotate_for_day([c for c,_ in COMPS], date.today(), take=n_totals)
print("totals-rotatie vandaag:", rot)
for comp in rot:
    key=dict(COMPS)[comp]
    if guard.can_afford(1):
        r=fetch_totals(key)
        guard.record(r, comp)
        out['totals'][comp]=r.payload if hasattr(r,'payload') else r.data
        print(f"totals {comp}: {len(out['totals'][comp])} events")
json.dump(out, open('tmp-run/rb_odds.json','w'), ensure_ascii=False)
print()
print(guard.report())
