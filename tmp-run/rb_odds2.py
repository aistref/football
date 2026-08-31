import json
from scripts.oddsapi import best_by_line
d=json.load(open('tmp-run/rb_odds.json'))
for kind in ('spreads','totals'):
    for comp, events in d[kind].items():
        print(f"=== {kind} {comp} ===")
        for e in events:
            print("  ", e.get('commence_time'), e.get('home_team'), '-', e.get('away_team'), 'books=',len(e.get('bookmakers',[])))
