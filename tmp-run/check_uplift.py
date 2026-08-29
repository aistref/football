import pickle, json, sys, statistics
sys.path.insert(0,'tmp-run')
from scripts import fotmob
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           splits_from_fotmob, scale_level, totals_prob)
from scripts.oddsapi import best_by_line
from scripts.calibration import devig

results, truncated = pickle.load(open('tmp-run/deep.pkl','rb'))
up = json.load(open('tmp-run/uplift.json')); FACTOR = up['factor']
LEAGUES = {res['row']['comp']: res['row']['league_id'] for res in results}
prev = {c: fotmob.fetch_league_stats(l,'2025/2026') for c,l in LEAGUES.items()}

diffs_on, diffs_off, n = [], [], 0
for res in results:
    r = res['row']; c = r['comp']; p = prev[c]
    base = LeagueContext(p['home_goals_per_match'], p['away_goals_per_match'], p['avg_xg_per_match'])
    ev = r.get('_ev',{}).get('totals')
    if not ev: continue
    bl = best_by_line(ev,'totals')
    o_over = bl.get(('Over',2.5)); o_under = bl.get(('Under',2.5))
    if not (o_over and o_under): continue
    mkt = devig([o_over[0], o_under[0]])[0]
    h = TeamStats(*[p['teams'][r['home_key']][k] for k in ('xg','xga','mp')])
    a = TeamStats(*[p['teams'][r['away_key']][k] for k in ('xg','xga','mp')])
    hs, as_ = splits_from_fotmob(p['teams'][r['home_key']]), splits_from_fotmob(p['teams'][r['away_key']])
    for label, lg, acc in (('on', scale_level(base, FACTOR), diffs_on), ('off', base, diffs_off)):
        px = analyze_match(h,a,lg); ps = analyze_match_from_splits(hs,as_,league=lg)
        my = (px.over_2_5 + ps.over_2_5)/2
        acc.append((my - mkt)*100)
    n += 1
print(f'P(Over 2.5) t.o.v. de de-vigde markt, over {n} duels:')
print(f'  zonder vroeg-seizoenscorrectie: gemiddeld {statistics.mean(diffs_off):+.2f} pp, '
      f'gem. abs. {statistics.mean(abs(x) for x in diffs_off):.2f} pp')
print(f'  met correctie (x{FACTOR:.4f}):      gemiddeld {statistics.mean(diffs_on):+.2f} pp, '
      f'gem. abs. {statistics.mean(abs(x) for x in diffs_on):.2f} pp')
print(f'  boven de markt: {sum(1 for x in diffs_on if x>0)} van {n} (met), '
      f'{sum(1 for x in diffs_off if x>0)} van {n} (zonder)')
