import json
from datetime import date
from scripts import fotmob

LEAGUES = {
 'Premier League (ENG)': 47, 'Serie A (ITA)': 55, 'La Liga (ESP)': 87,
 'Bundesliga (GER)': 54, 'Ligue 1 (FRA)': 53, 'Championship (ENG)': 48,
 'Eredivisie (NED)': 57, 'Primeira Liga (POR)': 61, 'Super Lig (TUR)': 71,
 'Scottish Premiership (SCO)': 64, 'Ekstraklasa (POL)': 196,
}
FIND = {
 'Premier League (ENG)': ('Premier League','ENG',()),
 'Serie A (ITA)': ('Serie A','ITA',()),
 'La Liga (ESP)': ('LaLiga','ESP',('La Liga',)),
 'Bundesliga (GER)': ('Bundesliga','GER',()),
 'Ligue 1 (FRA)': ('Ligue 1','FRA',()),
 'Championship (ENG)': ('Championship','ENG',()),
 'Eredivisie (NED)': ('Eredivisie','NED',()),
 'Primeira Liga (POR)': ('Liga Portugal','POR',('Primeira Liga',)),
 'Super Lig (TUR)': ('Super Lig','TUR',('Süper Lig',)),
 'Scottish Premiership (SCO)': ('Premiership','SCO',()),
 'Ekstraklasa (POL)': ('Ekstraklasa','POL',()),
}
fx = fotmob.fetch_fixtures(date(2026,8,29))
out = []
for comp, lid in LEAGUES.items():
    name, cc, al = FIND[comp]
    lg = fotmob.find_league(fx, name, cc, al)
    prev = fotmob.fetch_league_stats(lid, '2025/2026')
    cur  = fotmob.fetch_league_stats(lid, '2026/2027')
    pteams = prev['teams']
    for m in lg['matches']:
        h, a = m['home']['name'], m['away']['name']
        out.append({'comp': comp, 'league_id': lid, 'match_id': m['id'],
                    'home': h, 'away': a, 'kickoff': m['status']['utcTime'],
                    'home_prev': h in pteams and 'xg' in pteams[h],
                    'away_prev': a in pteams and 'xg' in pteams[a]})
    print(f"--- {comp}: prev teams={len(pteams)} cur played={max((t.get('played') or 0) for t in cur['teams'].values())}", flush=True)
missing = sorted({(r['comp'], r['home']) for r in out if not r['home_prev']} | {(r['comp'], r['away']) for r in out if not r['away_prev']})
print('\nZONDER VORIG-SEIZOEN-HISTORIE:')
for c, t in missing: print('  ', c, '|', t)
print('\ntotaal duels:', len(out), '| FULL-kandidaten:', sum(1 for r in out if r['home_prev'] and r['away_prev']))
json.dump(out, open('tmp-run/matches.json','w'), ensure_ascii=False, indent=1)
