import json, sys
from scripts import fotmob

LEAGUES = {
 'Premier League (ENG)': 47,
 'Serie A (ITA)': 55,
 'La Liga (ESP)': 87,
 'Bundesliga (GER)': 54,
 'Ligue 1 (FRA)': 53,
 'Championship (ENG)': 48,
 'Eredivisie (NED)': 57,
 'Primeira Liga (POR)': 61,
 'Super Lig (TUR)': 71,
 'Scottish Premiership (SCO)': 64,
 'Ekstraklasa (POL)': 196,
}
out = {}
for name, lid in LEAGUES.items():
    rec = {}
    for label, season in (('prev','2025/2026'), ('cur','2026/2027')):
        try:
            s = fotmob.fetch_league_stats(lid, season)
            rec[label] = {'has_xg': s['has_xg'], 'avg_xg': s['avg_xg_per_match'],
                          'teams': len(s['teams']),
                          'played': max((t.get('played') or 0) for t in s['teams'].values()) if s['teams'] else 0,
                          'hg': s['home_goals_per_match'], 'ag': s['away_goals_per_match']}
        except Exception as e:
            rec[label] = {'error': f'{type(e).__name__}: {e}'}
    out[name] = rec
    print(name, json.dumps(rec, ensure_ascii=False), flush=True)
