import json, sys, pickle, math
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, 'tmp-run')
from scripts import fotmob, context as ctxmod
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           splits_from_fotmob, scale_level, edge_pp, asian_prob, dnb_prob,
                           totals_prob, selection_score, robustness_check)
from scripts.oddsapi import best_by_line
from scripts.calibration import devig

NL = timezone(timedelta(hours=2))
rows = pickle.load(open('tmp-run/linked.pkl', 'rb'))
up = json.load(open('tmp-run/uplift.json'))
FACTOR, MD = up['factor'], up['md']
LEAGUES = {r['comp']: r['league_id'] for r in rows}
prev = {c: fotmob.fetch_league_stats(l, '2025/2026') for c, l in LEAGUES.items()}

CTX = {}
for c in LEAGUES:
    p = prev[c]
    CTX[c] = scale_level(LeagueContext(p['home_goals_per_match'], p['away_goals_per_match'],
                                       p['avg_xg_per_match']), FACTOR)

# ---- Stage 4: rangschikken en afkappen -------------------------------------
MAX_DEEP = 30
for r in rows:
    r['tier_pre'] = 'FULL' if (r['home_key'] and r['away_key']) else 'CONV'
    r['md'] = MD[r['comp']]
full = [r for r in rows if r['tier_pre'] == 'FULL']
full.sort(key=lambda r: (-r['md'], r['comp'], r['kickoff']))
selected = full[:MAX_DEEP]
truncated = full[MAX_DEEP:] + [r for r in rows if r['tier_pre'] != 'FULL']
print(f'geselecteerd {len(selected)}, afgekapt {len(truncated)}')
from collections import Counter
print('geselecteerd per comp:', dict(Counter(r["comp"] for r in selected)))
print('afgekapt per comp:', dict(Counter(r["comp"] for r in truncated)))

def ts(comp, key):
    t = prev[comp]['teams'][key]
    return TeamStats(t['xg'], t['xga'], t['mp'])

results = []
for r in selected:
    c = r['comp']
    lg = CTX[c]
    h, a = ts(c, r['home_key']), ts(c, r['away_key'])
    hs, as_ = (splits_from_fotmob(prev[c]['teams'][r['home_key']]),
               splits_from_fotmob(prev[c]['teams'][r['away_key']]))
    p_xg = analyze_match(h, a, lg)
    p_ns = analyze_match(h, a, lg, shrink=1.0)
    p_sp = analyze_match_from_splits(hs, as_, league=lg)

    # context (poort 7)
    try:
        ctx = ctxmod.fetch_match_context(r['match_id'], r['kickoff'])
        cerr = None
    except Exception as e:
        ctx, cerr = None, f'{type(e).__name__}: {e}'

    o1, ox, o2 = r['bex']['odds']
    cands = []
    def add(market, label, side, odds, book, sel_xg, sel_sp, sel_grid):
        cands.append(dict(market=market, label=label, side=side, odds=odds, book=book,
                          p_xg=sel_xg, p_split=sel_sp, sel=sel_grid))
    add('1X2', f'1 ({r["home"]} wint)', 'home', o1, None, p_xg.home, p_sp.home, lambda x: x.home)
    add('1X2', 'X (gelijkspel)', None, ox, None, p_xg.draw, p_sp.draw, lambda x: x.draw)
    add('1X2', f'2 ({r["away"]} wint)', 'away', o2, None, p_xg.away, p_sp.away, lambda x: x.away)

    ou_desc, ah_desc, dnb_desc = [], [], []
    ev_t = r.get('_ev', {}).get('totals')
    if ev_t:
        for (name, point), (price, book) in sorted(best_by_line(ev_t, 'totals').items(), key=lambda kv: (kv[0][1], kv[0][0])):
            if point is None: continue
            side = 'over' if name.lower().startswith('over') else 'under'
            add('OU', f'{side.capitalize()} {point}', None, price, book,
                totals_prob(p_xg.grid, point, side, price), totals_prob(p_sp.grid, point, side, price),
                (lambda pt, sd, pr: (lambda x: totals_prob(x.grid, pt, sd, pr)))(point, side, price))
            ou_desc.append(f'{side} {point} @{price} ({book})')
    ev_s = r.get('_ev', {}).get('spreads')
    if ev_s:
        for (name, point), (price, book) in sorted(best_by_line(ev_s, 'spreads').items(), key=lambda kv: (kv[0][1] or 0, kv[0][0])):
            if point is None: continue
            side = 'home' if name == ev_s['home_team'] else 'away'
            team = r['home'] if side == 'home' else r['away']
            if abs(point) < 1e-9:
                add('DNB', f'Draw No Bet — {team}', side, price, book,
                    dnb_prob(p_xg.grid, side, price), dnb_prob(p_sp.grid, side, price),
                    (lambda sd, pr: (lambda x: dnb_prob(x.grid, sd, pr)))(side, price))
                dnb_desc.append(f'{team} @{price} ({book})')
            else:
                add('AH', f'{team} {point:+g}', side, price, book,
                    asian_prob(p_xg.grid, point, side, price), asian_prob(p_sp.grid, point, side, price),
                    (lambda pt, sd, pr: (lambda x: asian_prob(x.grid, pt, sd, pr)))(point, side, price))
            ah_desc.append(f'{team} {point:+g} @{price} ({book})')

    for cd in cands:
        implied = 1 / cd['odds']
        cd['my_prob'] = (cd['p_xg'] + cd['p_split']) / 2
        cd['implied'] = implied
        cd['edge'] = (cd['my_prob'] - implied) * 100
        cd['edge_xg'] = (cd['p_xg'] - implied) * 100
        cd['edge_split'] = (cd['p_split'] - implied) * 100
        cd['score'] = selection_score(cd['edge'], cd['my_prob'], 'FULL')
        gates = {}
        gates['edge'] = cd['edge'] >= 3.0
        gates['odds'] = 1.30 <= cd['odds'] <= 6.00
        gates['data'] = True
        gates['tweede_methode'] = (cd['p_xg'] > implied) and (cd['p_split'] > implied)
        rb = robustness_check(h, a, lg, cd['sel'], cd['odds'])
        cd['robust'] = rb.min_edge
        cd['grid'] = {f'{s},{rho}': round(v, 2) for (s, rho), v in rb.edges.items()}
        gates['robuustheid'] = rb.min_edge > 0
        if ctx is not None:
            g = ctxmod.check(ctx, cd['side'])
            gates['context'] = g.passed
            cd['context_reason'] = g.reason
        else:
            gates['context'] = True
            cd['context_reason'] = f'context niet opgehaald ({cerr}) — poort open, ontbrekende data houdt niet tegen'
        cd['gates'] = gates
        order = ['data', 'odds', 'edge', 'tweede_methode', 'robuustheid', 'context']
        cd['failed'] = next((k for k in order if not gates[k]), None)
        cd.pop('sel')

    passing = [c_ for c_ in cands if c_['failed'] is None]
    passing.sort(key=lambda x: -x['score'])
    results.append(dict(row=r, cands=cands, passing=passing, ctx=ctx, cerr=cerr,
                        p_xg=[p_xg.home, p_xg.draw, p_xg.away],
                        p_ns=[p_ns.home, p_ns.draw, p_ns.away],
                        p_sp=[p_sp.home, p_sp.draw, p_sp.away],
                        lam_xg=[p_xg.lambda_home, p_xg.lambda_away],
                        lam_sp=[p_sp.lambda_home, p_sp.lambda_away],
                        market=devig([o1, ox, o2]),
                        ou_desc=ou_desc, ah_desc=ah_desc, dnb_desc=dnb_desc))
    top = passing[0] if passing else max(cands, key=lambda x: x['edge'])
    print(f"{r['comp'][:20]:22} {r['home'][:15]:16}-{r['away'][:15]:16} "
          f"{'BET ' if passing else 'geen'} {top['market']:4} {top['label'][:26]:28} "
          f"@{top['odds']:5.2f} edge {top['edge']:+6.2f} xg {top['edge_xg']:+6.2f} sp {top['edge_split']:+6.2f} "
          f"rb {top['robust']:+6.2f} {'' if passing else 'valt af op '+str(top['failed'])}", flush=True)

pickle.dump((results, truncated), open('tmp-run/deep.pkl', 'wb'))
