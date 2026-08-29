import json, sys, pickle
sys.path.insert(0,'tmp-run')
from names import pair_match, sim
from scripts.betexplorer import fetch_league_fixtures

BEX = {
 'Premier League (ENG)':'england/premier-league','Serie A (ITA)':'italy/serie-a',
 'La Liga (ESP)':'spain/laliga','Bundesliga (GER)':'germany/bundesliga',
 'Ligue 1 (FRA)':'france/ligue-1','Championship (ENG)':'england/championship',
 'Eredivisie (NED)':'netherlands/eredivisie','Primeira Liga (POR)':'portugal/liga-portugal',
 'Super Lig (TUR)':'turkey/super-lig','Scottish Premiership (SCO)':'scotland/premiership',
 'Ekstraklasa (POL)':'poland/ekstraklasa',
}
rows = json.load(open('tmp-run/matches.json'))
store = json.load(open('tmp-run/odds.json'))['store']

bex = {}
for c, slug in BEX.items():
    bex[c] = [r for r in fetch_league_fixtures(f'https://www.betexplorer.com/football/{slug}/') if r.is_today]

for r in rows:
    c = r['comp']
    pairs = [(x.home, x.away, x) for x in bex[c]]
    hit, score = pair_match(r['home'], r['away'], pairs)
    r['bex'] = None if hit is None else {'home': hit.home, 'away': hit.away,
                                         'odds': list(hit.odds), 'books': hit.bookmakers, 'score': round(score,3)}
    r['oa'] = {}
    for key in ('totals','spreads'):
        evs = store.get(c, {}).get(key, [])
        # alleen events die vandaag om dezelfde tijd beginnen
        cand = [(e['home_team'], e['away_team'], e) for e in evs
                if e['commence_time'][:10] == r['kickoff'][:10]]
        hit2, s2 = pair_match(r['home'], r['away'], cand)
        if hit2 is not None:
            r['oa'][key] = {'id': hit2['id'], 'home': hit2['home_team'], 'away': hit2['away_team'],
                            'commence': hit2['commence_time'], 'score': round(s2,3)}
            r.setdefault('_ev', {})[key] = hit2

print(f"{'comp':26} {'duel':38} {'BetExplorer':34} {'OddsAPI totals':30} spr")
for r in rows:
    b = r['bex']; t = r['oa'].get('totals'); s = r['oa'].get('spreads')
    print(f"{r['comp'][:24]:26} {r['home'][:17]+' - '+r['away'][:17]:38} "
          f"{(b['home']+' - '+b['away'])[:32] if b else 'GEEN':34} "
          f"{(t['home']+' - '+t['away'])[:28] if t else 'GEEN':30} {'ja' if s else '-'}")
pickle.dump(rows, open('tmp-run/linked.pkl','wb'))
