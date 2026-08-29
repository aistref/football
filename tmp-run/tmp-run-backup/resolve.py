import json, sys
sys.path.insert(0,'tmp-run')
from names import resolve
from scripts import fotmob
rows = json.load(open('tmp-run/matches.json'))
LEAGUES = {r['comp']: r['league_id'] for r in rows}
prevs = {c: fotmob.fetch_league_stats(l,'2025/2026')['teams'] for c,l in LEAGUES.items()}
unres = []
for r in rows:
    tn = list(prevs[r['comp']].keys())
    for side in ('home','away'):
        r[side+'_key'] = resolve(r[side], tn)
        if r[side+'_key'] is None:
            unres.append((r['comp'], r[side]))
print('ONOPGELOST:')
for c,t in sorted(set(unres)): print('  ',c,'|',t)
full = [r for r in rows if r['home_key'] and r['away_key']]
print(f'\nopgelost: {len(full)} van {len(rows)} duels beide ploegen met vorig-seizoen-historie')
json.dump(rows, open('tmp-run/matches.json','w'), ensure_ascii=False, indent=1)
