import json, sys
from datetime import date
from scripts.oddsapi import CreditGuard, suggest_cap, fetch_totals, fetch_spreads, rotate_for_day

# volgorde = datakwaliteit (alle 11 hebben xG beide seizoenen; sorteer op aantal duels vandaag
# en op hoeveel speeldagen er dit seizoen al gespeeld zijn -> meer historie = betere invoer)
COMPS = [
 ('Ekstraklasa (POL)', 'soccer_poland_ekstraklasa'),
 ('Eredivisie (NED)', 'soccer_netherlands_eredivisie'),
 ('Primeira Liga (POR)', 'soccer_portugal_primeira_liga'),
 ('Championship (ENG)', 'soccer_efl_champ'),
 ('Super Lig (TUR)', 'soccer_turkey_super_league'),
 ('La Liga (ESP)', 'soccer_spain_la_liga'),
 ('Scottish Premiership (SCO)', 'soccer_spl'),
 ('Premier League (ENG)', 'soccer_epl'),
 ('Serie A (ITA)', 'soccer_italy_serie_a'),
 ('Ligue 1 (FRA)', 'soccer_france_ligue_one'),
 ('Bundesliga (GER)', 'soccer_germany_bundesliga'),
]
cap = suggest_cap(103, 3)
guard = CreditGuard(cap=cap)
print('cap =', cap, flush=True)

store = {}
# stap 0 — totals voor zoveel mogelijk competities
for name, key in COMPS:
    if not guard.can_afford(1):
        print('STOP totals bij', name, '(plafond bereikt)', flush=True)
        break
    try:
        r = fetch_totals(key)
        guard.record(r, f'totals {name}')
        store.setdefault(name, {})['totals'] = r.data
        print(f'totals {name}: {len(r.data)} events', flush=True)
    except Exception as e:
        print(f'totals {name}: FAIL {type(e).__name__}: {e}', flush=True)

# stap 1 — spreads voor de competities die vandaag aan de beurt zijn
beurt = rotate_for_day([n for n, _ in COMPS], date(2026, 8, 29), take=max(1, cap // 2))
print('rotatie spreads:', beurt, flush=True)
keys = dict(COMPS)
for name in beurt:
    if not guard.can_afford(1):
        print('STOP spreads bij', name, '(plafond bereikt)', flush=True)
        break
    try:
        r = fetch_spreads(keys[name])
        guard.record(r, f'spreads {name}')
        store.setdefault(name, {})['spreads'] = r.data
        print(f'spreads {name}: {len(r.data)} events', flush=True)
    except Exception as e:
        print(f'spreads {name}: FAIL {type(e).__name__}: {e}', flush=True)

print('REPORT:', guard.report(), flush=True)
json.dump({'store': store, 'report': guard.report(), 'cap': cap,
           'rotatie': beurt, 'spent': getattr(guard, 'spent', None)},
          open('tmp-run/odds.json', 'w'))
