import json, sys, math, unicodedata, re
from datetime import date, datetime
sys.path.insert(0, 'tmp-run')
from names import norm, resolve
from scripts import fotmob, context as ctxmod
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           splits_from_fotmob, scale_level, early_season_uplift, edge_pp,
                           asian_prob, dnb_prob, totals_prob, selection_score, robustness_check)
from scripts.betexplorer import fetch_league_fixtures
from scripts.oddsapi import best_by_line
from scripts.calibration import devig

DAY = date(2026, 8, 29)
EDGE_FULL, EDGE_LIGHT = 3.0, 6.0
MIN_ODDS, MAX_ODDS = 1.30, 6.00

LEAGUES = {
 'Premier League (ENG)': 47, 'Serie A (ITA)': 55, 'La Liga (ESP)': 87,
 'Bundesliga (GER)': 54, 'Ligue 1 (FRA)': 53, 'Championship (ENG)': 48,
 'Eredivisie (NED)': 57, 'Primeira Liga (POR)': 61, 'Super Lig (TUR)': 71,
 'Scottish Premiership (SCO)': 64, 'Ekstraklasa (POL)': 196,
}
BEX = {
 'Premier League (ENG)':'england/premier-league','Serie A (ITA)':'italy/serie-a',
 'La Liga (ESP)':'spain/laliga','Bundesliga (GER)':'germany/bundesliga',
 'Ligue 1 (FRA)':'france/ligue-1','Championship (ENG)':'england/championship',
 'Eredivisie (NED)':'netherlands/eredivisie','Primeira Liga (POR)':'portugal/liga-portugal',
 'Super Lig (TUR)':'turkey/super-lig','Scottish Premiership (SCO)':'scotland/premiership',
 'Ekstraklasa (POL)':'poland/ekstraklasa',
}

matches = json.load(open('tmp-run/matches.json'))
odds_store = json.load(open('tmp-run/odds.json'))['store']

# ---- league data -----------------------------------------------------------
prev, cur = {}, {}
for c, lid in LEAGUES.items():
    prev[c] = fotmob.fetch_league_stats(lid, '2025/2026')
    cur[c]  = fotmob.fetch_league_stats(lid, '2026/2027')

obs, md = [], {}
for c in LEAGUES:
    m = max((t.get('played') or 0) for t in cur[c]['teams'].values())
    md[c] = m
    if prev[c]['avg_xg_per_match'] and cur[c]['avg_xg_per_match'] and m:
        obs.append((prev[c]['avg_xg_per_match'], cur[c]['avg_xg_per_match'], m))
FACTOR, POOLED, TOTAL_MD = early_season_uplift(obs)
print(f'vroeg-seizoenscorrectie: factor={FACTOR:.4f} pooled={POOLED:.4f} speeldagen={TOTAL_MD}', flush=True)

LEAGUE_CTX = {}
for c in LEAGUES:
    p = prev[c]
    base = LeagueContext(p['home_goals_per_match'], p['away_goals_per_match'], p['avg_xg_per_match'])
    LEAGUE_CTX[c] = scale_level(base, FACTOR)

# ---- odds koppelen ---------------------------------------------------------
bex_rows = {}
for c, slug in BEX.items():
    bex_rows[c] = [r for r in fetch_league_fixtures(f'https://www.betexplorer.com/football/{slug}/') if r.is_today]

def match_name(target, candidates):
    r = resolve(target, candidates)
    if r: return r
    n = norm(target)
    best, score = None, 0
    for cnd in candidates:
        m = norm(cnd)
        s = len(set(n.split()) & set(m.split()))
        if s > score: best, score = cnd, s
    return best if score else None

for r in matches:
    c = r['comp']
    rows = bex_rows[c]
    homes = [x.home for x in rows]
    hk = match_name(r['home'], homes)
    row = next((x for x in rows if x.home == hk), None)
    if row and match_name(r['away'], [row.away]) is None:
        # kruiscontrole op de uitploeg
        pass
    r['bex'] = None if row is None else {'home': row.home, 'away': row.away,
                                          'odds': list(row.odds), 'books': row.bookmakers}
    ev = None
    for key in ('totals', 'spreads'):
        for e in odds_store.get(c, {}).get(key, []):
            if match_name(r['home'], [e['home_team']]) or norm(r['home']) in norm(e['home_team']) or norm(e['home_team']) in norm(r['home']):
                if match_name(r['away'], [e['away_team']]) or norm(r['away']) in norm(e['away_team']) or norm(e['away_team']) in norm(r['away']):
                    r.setdefault('oa', {})[key] = e
                    break

missing_bex = [(r['comp'], r['home'], r['away']) for r in matches if not r['bex']]
print('zonder BetExplorer-rij:', missing_bex, flush=True)
no_tot = [(r['comp'], r['home']) for r in matches if 'totals' not in r.get('oa', {})]
print('zonder totals-event:', len(no_tot), no_tot, flush=True)
no_spr = [(r['comp'], r['home']) for r in matches
          if r['comp'] in ('Super Lig (TUR)', 'La Liga (ESP)') and 'spreads' not in r.get('oa', {})]
print('zonder spreads-event (van de twee gefetchte comps):', no_spr, flush=True)
json.dump({'factor': FACTOR, 'pooled': POOLED, 'total_md': TOTAL_MD, 'md': md},
          open('tmp-run/uplift.json', 'w'))
json.dump([{k: v for k, v in r.items() if k != 'oa'} for r in matches],
          open('tmp-run/matches2.json', 'w'), ensure_ascii=False, indent=1)
import pickle
pickle.dump(matches, open('tmp-run/matches.pkl', 'wb'))
