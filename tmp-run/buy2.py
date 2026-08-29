import json
from datetime import date
from scripts.oddsapi import CreditGuard, suggest_cap, fetch_spreads, rotate_for_day

COMPS = [
 ('Ekstraklasa (POL)', 'soccer_poland_ekstraklasa'),
 ('Eredivisie (NED)', 'soccer_netherlands_eredivisie'),
 ('Primeira Liga (POR)', 'soccer_portugal_primeira_liga'),
 ('Championship (ENG)', 'soccer_efl_champ'),
 ('Scottish Premiership (SCO)', 'soccer_spl'),
 ('Premier League (ENG)', 'soccer_epl'),
 ('Serie A (ITA)', 'soccer_italy_serie_a'),
 ('Ligue 1 (FRA)', 'soccer_france_ligue_one'),
 ('Bundesliga (GER)', 'soccer_germany_bundesliga'),
 ('Super Lig (TUR)', 'soccer_turkey_super_league'),
 ('La Liga (ESP)', 'soccer_spain_la_liga'),
]
cap = suggest_cap(79, 3)
guard = CreditGuard(cap=cap)
print('cap =', cap, flush=True)
beurt = rotate_for_day([n for n, _ in COMPS], date(2026, 8, 29), take=cap)
print('rotatie stap 0 (spreads):', beurt, flush=True)
keys = dict(COMPS)
store = {}
for name in beurt:
    if not guard.can_afford(1):
        print('STOP bij', name, '(plafond bereikt)', flush=True); break
    try:
        r = fetch_spreads(keys[name])
        guard.record(r, f'spreads {name}')
        store[name] = r.data
        print(f'spreads {name}: {len(r.data)} events', flush=True)
    except Exception as e:
        print(f'spreads {name}: FAIL {type(e).__name__}: {e}', flush=True)
print('REPORT:', guard.report(), flush=True)
json.dump({'spreads': store, 'report': guard.report(), 'cap': cap, 'rotatie': beurt},
          open('tmp-run/odds2.json', 'w'))
