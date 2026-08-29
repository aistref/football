import pickle, json, sys, re
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
from scripts.progress import load_or_start, mark, save
from scripts.calibration import devig

NL = timezone(timedelta(hours=2))
results, truncated = pickle.load(open('tmp-run/deep.pkl','rb'))
up = json.load(open('tmp-run/uplift.json'))
odds_meta = json.load(open('tmp-run/odds.json'))
CAPTURED = '2026-08-29T04:35:00+02:00'

COMP_NAME = {'Super Lig (TUR)': 'Süper Lig (TUR)'}
def cn(c): return COMP_NAME.get(c, c)

RUNLIST = ['Premier League (ENG)','Serie A (ITA)','La Liga (ESP)','Bundesliga (GER)','Ligue 1 (FRA)',
 'Championship (ENG)','Eredivisie (NED)','Primeira Liga (POR)','Belgian Pro League (BEL)',
 'Süper Lig (TUR)','Scottish Premiership (SCO)','Danish Superliga (DEN)','Ekstraklasa (POL)',
 'UEFA Champions League','UEFA Europa League','UEFA Conference League','FA Cup (ENG)',
 'League Cup (ENG)','Coppa Italia (ITA)','KNVB Beker (NED)','DFB Pokal (GER)']

SPREAD_COMPS = {'Süper Lig (TUR)', 'La Liga (ESP)'}
AH_NOT = ('niet opgevraagd — creditplafond van de run bereikt (§1a stap 1): na stap 0 '
          '(fetch_totals voor elf competities, 11 credits) waren er nog 2 van de 13 over, en de '
          'rotatie van vandaag begon bij Süper Lig en La Liga')
DNB_NOT = 'niet opgevraagd — komt uit dezelfde spreads-call als AH; zie AH'
DC_NOT = 'niet opgevraagd — §1a stap 2, na stap 0 en stap 1 stond er nul credit open'
BTTS_NOT = DC_NOT

def team_ctx(tc):
    if tc is None: return None
    return {'naam': tc.name, 'afwezig': len(tc.out_names), 'afwezig_aandeel': round(tc.out_share,4),
            'namen': tc.out_names, 'vorm': tc.form, 'rustdagen': tc.rest_days,
            'druk_programma': tc.congested}

state = load_or_start('a', date(2026,8,29))
comps = {}
per_comp = {}
for res in results:
    per_comp.setdefault(cn(res['row']['comp']), []).append(res)

bets_by_id = {}
for cname, reslist in per_comp.items():
    matches = []
    for res in sorted(reslist, key=lambda x: x['row']['kickoff']):
        r = res['row']
        ko = datetime.fromisoformat(r['kickoff'].replace('Z','+00:00')).astimezone(NL)
        passing = res['passing']
        top = passing[0] if passing else None
        ctx = res['ctx']
        ou = ', '.join(res['ou_desc']) or 'geen totals-lijnen in het event'
        mc = {
          '1X2': f"BetExplorer, marktgemiddelde over {r['bex']['books']} boeken (bookmaker niet herleidbaar): "
                 f"1 @{r['bex']['odds'][0]}, X @{r['bex']['odds'][1]}, 2 @{r['bex']['odds'][2]}",
          'OU': f'The Odds API totals, beste prijs per lijn/uitkomst: {ou}',
          'AH': (f"The Odds API spreads, beste prijs per lijn: {', '.join(res['ah_desc'])}"
                 if res['ah_desc'] else AH_NOT),
          'DNB': (f"0.0-lijn uit dezelfde spreads-call: {', '.join(res['dnb_desc'])}"
                  if res['dnb_desc'] else
                  ('geen 0.0-lijn in de spreads-respons van deze wedstrijd' if res['ah_desc'] else DNB_NOT)),
          'DC': DC_NOT, 'BTTS': BTTS_NOT,
          'context': 'Fotmob blessures/schorsingen + vorm + rust + stadioncontrole'
            if ctx else f"niet opgehaald ({res['cerr']}) — poort 7 blijft open bij ontbrekende data",
        }
        m = {'match': f"{r['home']} – {r['away']}", 'tier': 'FULL', 'bet': bool(passing),
             'kickoff_nl': ko.isoformat(), 'markets_checked': mc,
             'divisies': {'referentie': cname,
                          'toelichting': 'beide ploegen speelden 2025/2026 volledig in deze competitie'},
             'bereikcontrole': {'thuis': 'geen omrekening nodig — zelfde divisie',
                                'uit': 'geen omrekening nodig — zelfde divisie', 'binnen': True},
             'lambdas': {'xg': [round(x,3) for x in res['lam_xg']],
                         'split': [round(x,3) for x in res['lam_sp']]},
             'calibration': {'market': [round(x,4) for x in res['market']],
                             'p_xg': [round(x,4) for x in res['p_xg']],
                             'p_xg_noshrink': [round(x,4) for x in res['p_ns']],
                             'p_split': [round(x,4) for x in res['p_sp']]}}
        if ctx:
            m['context'] = {'thuis': team_ctx(ctx.home), 'uit': team_ctx(ctx.away),
                            'lineup_type': ctx.lineup_type,
                            'stadion': {'naam': ctx.venue.stadium, 'plaats': ctx.venue.city,
                                        'verplaatst': ctx.venue.relocated, 'toelichting': ctx.venue.note}}
        if passing:
            second = passing[1] if len(passing)>1 else None
            rest = [c for c in res['cands'] if c is not top]
            best_rest = max(rest, key=lambda x: x['score']) if rest else None
            m['gepubliceerd'] = {
              'market': f"{top['market']} — {top['label']}", 'odds': top['odds'],
              'bron': top['book'] or f"BetExplorer marktgemiddelde over {r['bex']['books']} boeken",
              'my_prob': round(top['my_prob'],4), 'implied': round(top['implied'],4),
              'edge_pp': round(top['edge'],2), 'edge_xg': round(top['edge_xg'],2),
              'edge_split': round(top['edge_split'],2), 'edge_robust_min': round(top['robust'],2),
              'score': round(top['score'],4),
              'tweede_gekwalificeerd': (None if second is None else
                   {'market': f"{second['market']} — {second['label']}", 'odds': second['odds'],
                    'score': round(second['score'],4)}),
              'hoogste_afgewezen': (None if best_rest is None else
                   {'market': f"{best_rest['market']} — {best_rest['label']}", 'odds': best_rest['odds'],
                    'score': round(best_rest['score'],4), 'valt_af_op': best_rest['failed']}),
              'robuustheid_grid': top['grid'],
              'aantal_gekwalificeerd': len(passing), 'aantal_doorgerekend': len(res['cands']),
            }
            bets_by_id[f"{r['home']} – {r['away']}"] = (r, top, second, best_rest, res, cname)
        else:
            pool = [c for c in res['cands'] if c['edge'] > 0] or res['cands']
            nm = max(pool, key=lambda x: x['edge'])
            m['near_miss'] = {'market': f"{nm['market']} — {nm['label']}", 'odds': nm['odds'],
                              'edge_xg': round(nm['edge_xg'],2), 'edge_split': round(nm['edge_split'],2),
                              'edge_robust_min': round(nm['robust'],2), 'failed_gate': nm['failed']}
            m['robuustheid_grid'] = nm['grid']
            m['geen_bet_reden'] = [
              f"{len(res['cands'])} selecties doorgerekend over "
              f"{', '.join(sorted({c['market'] for c in res['cands']}))}; de hoogste edge is "
              f"{nm['label']} @{nm['odds']} op {nm['edge']:+.2f} pp.",
              f"Die valt af op poort {nm['failed']}: xG-methode {nm['edge_xg']:+.2f} pp, "
              f"splitsmethode {nm['edge_split']:+.2f} pp, zwakste stand van het (shrink, rho)-grid "
              f"{nm['robust']:+.2f} pp." + (f" Contextpoort: {nm['context_reason']}." if nm['failed']=='context' else ""),
            ]
        matches.append(m)
    comps[cname] = {'status': 'GEANALYSEERD', 'matches': matches,
                    'wedstrijden_vandaag': None}
pickle.dump(bets_by_id, open('tmp-run/betmap.pkl','wb'))
json.dump(comps, open('tmp-run/comps.json','w'), ensure_ascii=False, indent=1)
print('competities met analyses:', {k: len(v['matches']) for k,v in comps.items()})
print('bets:', len(bets_by_id))
