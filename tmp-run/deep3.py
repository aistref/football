import json, pickle, sys
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
from scripts import fotmob, context as ctxmod, footballdata as fd
from scripts.model import (TeamStats, TeamSplits, LeagueContext, analyze_match,
                           analyze_match_from_splits, splits_from_fotmob, scale_level,
                           asian_prob, dnb_prob, totals_prob, selection_score, robustness_check)
from scripts.oddsapi import best_by_line
from scripts.calibration import devig

NL = timezone(timedelta(hours=2))
selected, truncated, FACTOR, POOLED, TOTAL_MD = pickle.load(open('tmp-run/sel2.pkl','rb'))
LEAGUES = {r['comp']: r['league_id'] for r in selected+truncated}
prev = {c: fotmob.fetch_league_stats(l,'2025/2026') for c,l in LEAGUES.items()}
CTXL = {c: scale_level(LeagueContext(prev[c]['home_goals_per_match'], prev[c]['away_goals_per_match'],
                                     prev[c]['avg_xg_per_match']), FACTOR) for c in LEAGUES}

# ---- omrekening voor de ene LIGHT-wedstrijd die de cap haalde ---------------
CONV = {'Troyes': ('F1','F2', 2025)}
def converted(comp, team_name):
    higher, lower, yr = CONV[team_name]
    tbl = fd.season_table(fd.fetch_division(lower, yr))
    key = next(n for n in tbl if team_name.lower() in n.lower())
    t = tbl[key]
    a, d = fd.relative_strength(t, tbl)
    ok, reden = fd.conversion_in_range(higher, lower, 'up', a, d)
    if not ok: return None, None, reden
    gap = fd.gap_for(higher, lower, 'up')
    na, nd = fd.convert_strength(a, d, gap)
    p = prev[comp]; avg = p['avg_xg_per_match']
    stats = TeamStats(na*avg*t.played, nd*avg*t.played, t.played)
    # splits: dezelfde omrekenfactoren op de thuis/uit-verhoudingen van de lagere divisie
    ms = fd.fetch_division(lower, yr)
    hgf=hga=hp=agf=aga=ap=0
    lhg=lag=lhp=lap=0
    for m in ms:
        lhg += m.hg; lag += m.ag; lhp += 1; lap += 1
        if m.home == key: hgf+=m.hg; hga+=m.ag; hp+=1
        if m.away == key: agf+=m.ag; aga+=m.hg; ap+=1
    lh, la = lhg/lhp, lag/lap
    fh, fa = p['home_goals_per_match'], p['away_goals_per_match']
    sp = TeamSplits(
        home_gf=round((hgf/hp)/lh*gap.attack*fh*hp), home_ga=round((hga/hp)/la*gap.defence*fa*hp),
        home_played=hp,
        away_gf=round((agf/ap)/la*gap.attack*fa*ap), away_ga=round((aga/ap)/lh*gap.defence*fh*ap),
        away_played=ap)
    return stats, sp, f"{reden}; {gap.summary()}"

def teamdata(r, side):
    comp = r['comp']; name = r[side]; key = r[side+'_key']
    if key:
        t = prev[comp]['teams'][key]
        return TeamStats(t['xg'], t['xga'], t['mp']), splits_from_fotmob(t), None
    st, sp, note = converted(comp, name)
    return st, sp, note

results = []
for r in selected:
    c = r['comp']; lg = CTXL[c]
    (h, hs, hn) = teamdata(r, 'home'); (a, as_, an) = teamdata(r, 'away')
    if h is None or a is None:
        r['tier'] = 'NONE'; results.append({'row': r, 'skip': hn or an}); continue
    p_xg = analyze_match(h, a, lg)
    p_ns = analyze_match(h, a, lg, shrink=1.0)
    p_sp = analyze_match_from_splits(hs, as_, league=lg)
    ctx = r['ctx']
    o1, ox, o2 = r['bex']['odds']
    cands = []
    def add(market, label, side, odds, book, sx, ss, sel, extra=''):
        cands.append(dict(market=market, label=label, side=side, odds=odds, book=book,
                          p_xg=sx, p_split=ss, sel=sel, extra=extra))

    ah_desc, dnb_desc, dc_desc, ou_desc = [], [], [], []
    ev_s = r.get('ev', {}).get('spreads')
    best_1x2 = {'home': (o1, None), 'away': (o2, None)}
    spread_lines = {}
    if ev_s:
        for (name, point), (price, book) in best_by_line(ev_s, 'spreads').items():
            if point is None: continue
            side = 'home' if name == ev_s['home_team'] else 'away'
            spread_lines[(side, round(point, 2))] = (price, book)
    for (side, point), (price, book) in sorted(spread_lines.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        team = r['home'] if side == 'home' else r['away']
        if abs(point + 0.5) < 1e-9:                      # AH -0.5 == de 1X2-zege, beste prijs
            if price > best_1x2[side][0]:
                best_1x2[side] = (price, book)
            ah_desc.append(f'{team} -0.5 @{price} ({book}) = 1X2-zege')
        elif abs(point) < 1e-9:                          # AH 0.0 == Draw No Bet
            add('DNB', f'Draw No Bet — {team}', side, price, book,
                dnb_prob(p_xg.grid, side, price), dnb_prob(p_sp.grid, side, price),
                (lambda s, pr: (lambda x: dnb_prob(x.grid, s, pr)))(side, price))
            dnb_desc.append(f'{team} @{price} ({book})')
        elif abs(point - 0.5) < 1e-9:                    # AH +0.5 == Double Chance
            lbl = f'Double Chance — {team} of gelijkspel'
            add('DC', lbl, side, price, book,
                asian_prob(p_xg.grid, 0.5, side, price), asian_prob(p_sp.grid, 0.5, side, price),
                (lambda s, pr: (lambda x: asian_prob(x.grid, 0.5, s, pr)))(side, price),
                extra='via de +0.5-handicap')
            dc_desc.append(f'{team} of gelijkspel @{price} ({book}, +0.5-lijn)')
        else:
            add('AH', f'{team} {point:+g}', side, price, book,
                asian_prob(p_xg.grid, point, side, price), asian_prob(p_sp.grid, point, side, price),
                (lambda pt, s, pr: (lambda x: asian_prob(x.grid, pt, s, pr)))(point, side, price))
            ah_desc.append(f'{team} {point:+g} @{price} ({book})')

    add('1X2', f'1 ({r["home"]} wint)', 'home', best_1x2['home'][0], best_1x2['home'][1],
        p_xg.home, p_sp.home, lambda x: x.home)
    add('1X2', 'X (gelijkspel)', None, ox, None, p_xg.draw, p_sp.draw, lambda x: x.draw)
    add('1X2', f'2 ({r["away"]} wint)', 'away', best_1x2['away'][0], best_1x2['away'][1],
        p_xg.away, p_sp.away, lambda x: x.away)

    ev_t = r.get('ev', {}).get('totals')
    if ev_t:
        for (name, point), (price, book) in sorted(best_by_line(ev_t, 'totals').items(),
                                                   key=lambda kv: (kv[0][1], kv[0][0])):
            if point is None: continue
            side = 'over' if name.lower().startswith('over') else 'under'
            add('OU', f'{side.capitalize()} {point}', None, price, book,
                totals_prob(p_xg.grid, point, side, price), totals_prob(p_sp.grid, point, side, price),
                (lambda pt, s, pr: (lambda x: totals_prob(x.grid, pt, s, pr)))(point, side, price))
            ou_desc.append(f'{side} {point} @{price} ({book})')

    tier = r['tier']; thr = 3.0 if tier == 'FULL' else 6.0
    for cd in cands:
        imp = 1/cd['odds']
        cd['my_prob'] = (cd['p_xg']+cd['p_split'])/2
        cd['implied'] = imp
        cd['edge'] = (cd['my_prob']-imp)*100
        cd['edge_xg'] = (cd['p_xg']-imp)*100
        cd['edge_split'] = (cd['p_split']-imp)*100
        cd['score'] = selection_score(cd['edge'], cd['my_prob'], tier)
        g = {'data': True, 'odds': 1.30 <= cd['odds'] <= 6.00, 'edge': cd['edge'] >= thr,
             'tweede_methode': cd['p_xg'] > imp and cd['p_split'] > imp}
        rb = robustness_check(h, a, lg, cd['sel'], cd['odds'])
        cd['robust'] = rb.min_edge
        cd['grid'] = {f'{s},{rho}': round(v,2) for (s,rho),v in rb.edges.items()}
        g['robuustheid'] = rb.min_edge > 0
        gate = ctxmod.check(ctx, cd['side']) if ctx else None
        g['context'] = gate.passed if gate else True
        cd['context_reason'] = gate.reason if gate else 'context niet opgehaald — poort open'
        cd['gates'] = g
        cd['failed'] = next((k for k in ('data','odds','edge','tweede_methode','robuustheid','context')
                             if not g[k]), None)
        cd.pop('sel')
    passing = sorted([x for x in cands if x['failed'] is None], key=lambda x: -x['score'])
    results.append(dict(row=r, cands=cands, passing=passing, tier=tier,
                        p_xg=[p_xg.home,p_xg.draw,p_xg.away], p_ns=[p_ns.home,p_ns.draw,p_ns.away],
                        p_sp=[p_sp.home,p_sp.draw,p_sp.away],
                        lam_xg=[p_xg.lambda_home,p_xg.lambda_away],
                        lam_sp=[p_sp.lambda_home,p_sp.lambda_away],
                        market=devig([o1,ox,o2]), conv_note=hn or an,
                        ah_desc=ah_desc, dnb_desc=dnb_desc, dc_desc=dc_desc, ou_desc=ou_desc))
    top = passing[0] if passing else max(cands, key=lambda x: x['edge'])
    print(f"{c[:17]:19}{r['home'][:14]:15}-{r['away'][:14]:15}{'BET ' if passing else 'geen'} "
          f"{top['market']:4}{top['label'][:26]:28}@{top['odds']:5.2f} e{top['edge']:+6.2f} "
          f"xg{top['edge_xg']:+6.2f} sp{top['edge_split']:+6.2f} rb{top['robust']:+6.2f} "
          f"{'' if passing else top['failed']}", flush=True)
pickle.dump(results, open('tmp-run/deep3.pkl','wb'))
