import json, pickle, sys
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
from names import pair_match
from scripts import fotmob, context as ctxmod, ranking
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           splits_from_fotmob, scale_level, early_season_uplift,
                           asian_prob, dnb_prob, totals_prob, selection_score, robustness_check)
from scripts.betexplorer import fetch_league_fixtures
from scripts.oddsapi import best_by_line
from scripts.calibration import devig

DAY = date(2026, 8, 29)
NL = timezone(timedelta(hours=2))
MAX_DEEP = ranking.max_deep_analyses(DAY)
BEX = {
 'Premier League (ENG)':'england/premier-league','Serie A (ITA)':'italy/serie-a',
 'La Liga (ESP)':'spain/laliga','Bundesliga (GER)':'germany/bundesliga',
 'Ligue 1 (FRA)':'france/ligue-1','Championship (ENG)':'england/championship',
 'Eredivisie (NED)':'netherlands/eredivisie','Primeira Liga (POR)':'portugal/liga-portugal',
 'Super Lig (TUR)':'turkey/super-lig','Scottish Premiership (SCO)':'scotland/premiership',
 'Ekstraklasa (POL)':'poland/ekstraklasa'}

rows = pickle.load(open('tmp-run/ranked.pkl','rb'))
spreads_store = json.load(open('tmp-run/odds2.json'))['spreads']
totals_store = json.load(open('tmp-run/odds.json'))['store']       # 04:35 CEST, hergebruikt

LEAGUES = {r['comp']: r['league_id'] for r in rows}
prev = {c: fotmob.fetch_league_stats(l,'2025/2026') for c,l in LEAGUES.items()}
cur  = {c: fotmob.fetch_league_stats(l,'2026/2027') for c,l in LEAGUES.items()}
obs=[]
for c in LEAGUES:
    md = max((t.get('played') or 0) for t in cur[c]['teams'].values())
    if prev[c]['avg_xg_per_match'] and cur[c]['avg_xg_per_match'] and md:
        obs.append((prev[c]['avg_xg_per_match'], cur[c]['avg_xg_per_match'], md))
FACTOR, POOLED, TOTAL_MD = early_season_uplift(obs)
CTXL = {c: scale_level(LeagueContext(prev[c]['home_goals_per_match'], prev[c]['away_goals_per_match'],
                                     prev[c]['avg_xg_per_match']), FACTOR) for c in LEAGUES}
print(f'cap={MAX_DEEP} factor={FACTOR:.4f}', flush=True)

# ---- prijzen koppelen ------------------------------------------------------
bex = {c: [x for x in fetch_league_fixtures(f'https://www.betexplorer.com/football/{s}/') if x.is_today]
       for c, s in BEX.items()}
for r in rows:
    c = r['comp']
    hit, _ = pair_match(r['home'], r['away'], [(x.home, x.away, x) for x in bex[c]])
    r['bex'] = None if hit is None else {'odds': list(hit.odds), 'books': hit.bookmakers}
    for key, store in (('spreads', spreads_store), ('totals', totals_store)):
        evs = store.get(c) if key=='spreads' else (totals_store.get(c) or {}).get('totals', [])
        evs = evs or []
        cand = [(e['home_team'], e['away_team'], e) for e in evs
                if e['commence_time'][:10] == r['kickoff'][:10]]
        ev, _ = pair_match(r['home'], r['away'], cand)
        if ev is not None: r.setdefault('ev', {})[key] = ev
    r['n_markets'] = (1 if r['bex'] else 0) + (3 if r.get('ev',{}).get('spreads') else 0) \
                   + (1 if r.get('ev',{}).get('totals') else 0)

# ---- Stage 4: rangschikken en afkappen -------------------------------------
NONE_MATCHES = {'Arouca – Marítimo','Académico Viseu – FC Porto','Wisła Kraków – Wieczysta Kraków'}
for r in rows:
    naam = f"{r['home']} – {r['away']}"
    r['tier'] = 'FULL' if r['tier_pre']=='FULL' else ('NONE' if naam in NONE_MATCHES else 'LIGHT')
rows.sort(key=lambda r: ranking.sort_key(r['tier'], r['rich'], r['n_markets'], r['kickoff']))
selected = [r for r in rows if r['tier'] != 'NONE'][:MAX_DEEP]
truncated = [r for r in rows if r not in selected]
print(f'geselecteerd {len(selected)}, niet doorgerekend {len(truncated)}', flush=True)
print('laagste die het haalde :', f"{selected[-1]['home']} – {selected[-1]['away']}",
      selected[-1]['tier'], f"rich {selected[-1]['rich']:.2f}", f"markten {selected[-1]['n_markets']}")
hoogste_af = [t for t in truncated if t['tier'] != 'NONE']
if hoogste_af:
    print('hoogste die afviel     :', f"{hoogste_af[0]['home']} – {hoogste_af[0]['away']}",
          hoogste_af[0]['tier'], f"rich {hoogste_af[0]['rich']:.2f}", f"markten {hoogste_af[0]['n_markets']}")
pickle.dump((selected, truncated, FACTOR, POOLED, TOTAL_MD), open('tmp-run/sel2.pkl','wb'))
