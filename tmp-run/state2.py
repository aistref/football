import pickle, json, sys
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
from scripts.progress import load_or_start, save
NL = timezone(timedelta(hours=2))
res = pickle.load(open('tmp-run/deep3.pkl','rb'))
sel, trunc, FACTOR, POOLED, TOTAL_MD = pickle.load(open('tmp-run/sel2.pkl','rb'))
up = json.load(open('tmp-run/uplift.json'))
odds2 = json.load(open('tmp-run/odds2.json'))
COMPN = {'Super Lig (TUR)':'Süper Lig (TUR)'}
cn = lambda c: COMPN.get(c, c)
SPREADS_COMPS = {cn(c) for c in odds2['spreads']}
def ko(r): return datetime.fromisoformat(r['kickoff'].replace('Z','+00:00')).astimezone(NL)
def tc(t):
    return None if t is None else {'naam':t.name,'afwezig':len(t.out_names),
        'afwezig_aandeel':round(t.out_share,4),'namen':t.out_names,'vorm':t.form,
        'rustdagen':t.rest_days,'druk_programma':t.congested}

NOT_BOUGHT = ('niet opgevraagd — creditplafond van de run (9) ging volledig naar stap 0, '
              'fetch_spreads voor negen competities in de dagrotatie')
BTTS_NOT = ('niet opgevraagd — §1a stap 2, kost 2 credits per wedstrijd en er stond na stap 0 '
            'nul credit open')
comps = {}
for r in res:
    w = r['row']; c = cn(w['comp'])
    b = comps.setdefault(c, {'status':'GEANALYSEERD','matches':[]})
    has_spread = c in SPREADS_COMPS
    ou_cap = '08:05 CEST (opnieuw opgehaald)' if c=='La Liga (ESP)' else '04:35 CEST (uit de eerdere run van vandaag; drift gemeten op La Liga: maximaal +0.08)'
    mc = {
      '1X2': (f"BetExplorer marktgemiddelde over {w['bex']['books']} boeken (bookmaker niet herleidbaar)"
              + (f"; beste prijs waar de -0.5-handicap er lag: {', '.join(x for x in r['ah_desc'] if '1X2-zege' in x)}"
                 if any('1X2-zege' in x for x in r['ah_desc']) else '')),
      'AH':  (f"The Odds API spreads, beste prijs per lijn: {', '.join(r['ah_desc'])}" if r['ah_desc'] else
              ('geen bruikbare handicaplijn in de spreads-respons van dit duel' if has_spread else NOT_BOUGHT)),
      'DNB': (f"de 0.0-lijn uit dezelfde spreads-call: {', '.join(r['dnb_desc'])}" if r['dnb_desc'] else
              ('geen 0.0-lijn in de spreads-respons van dit duel' if has_spread else NOT_BOUGHT)),
      'DC':  (f"de ±0.5-lijn uit dezelfde spreads-call (§1a: AH +0.5 = Double Chance): {', '.join(r['dc_desc'])}" if r['dc_desc'] else
              ('geen ±0.5-lijn in de spreads-respons van dit duel' if has_spread else NOT_BOUGHT)),
      'OU':  (f"The Odds API totals, beste prijs per lijn, uitgelezen {ou_cap}: {', '.join(r['ou_desc'])}"
              if r['ou_desc'] else 'geen totals-lijnen in het event'),
      'BTTS': BTTS_NOT,
      'context': 'Fotmob blessures/schorsingen + vorm + rust + stadioncontrole' if w['ctx'] else
                 f"niet opgehaald ({w['cerr']}) — poort 7 blijft open bij ontbrekende data",
    }
    m = {'match': f"{w['home']} – {w['away']}", 'tier': r['tier'], 'bet': bool(r['passing']),
         'kickoff_nl': ko(w).isoformat(), 'markets_checked': mc,
         'datarijkdom': {'score': w['rich'], 'delen': {k: round(v,2) for k,v in w['rich_parts'].items()},
                         'opmerkingen': w['rich_notes'], 'markten_beschikbaar': w['n_markets'],
                         'duels_dit_seizoen': [w['played_h'], w['played_a']]},
         'selectieverloop': {
            'thuis': (w['turn_h'].summary() if w.get('turn_h') else 'niet gemeten'),
            'uit':   (w['turn_a'].summary() if w.get('turn_a') else 'niet gemeten')},
         'lambdas': {'xg':[round(x,3) for x in r['lam_xg']], 'split':[round(x,3) for x in r['lam_sp']]},
         'calibration': {'market':[round(x,4) for x in r['market']],
                         'p_xg':[round(x,4) for x in r['p_xg']],
                         'p_xg_noshrink':[round(x,4) for x in r['p_ns']],
                         'p_split':[round(x,4) for x in r['p_sp']]}}
    if r['conv_note']:
        m['divisies'] = {'referentie': c, 'omrekening': r['conv_note']}
        m['bereikcontrole'] = {'binnen': True, 'toelichting': r['conv_note']}
    else:
        m['divisies'] = {'referentie': c, 'toelichting': 'beide ploegen speelden 2025/2026 volledig in deze competitie'}
        m['bereikcontrole'] = {'thuis':'geen omrekening nodig','uit':'geen omrekening nodig','binnen':True}
    ctx = w['ctx']
    if ctx:
        m['context'] = {'thuis':tc(ctx.home),'uit':tc(ctx.away),'lineup_type':ctx.lineup_type,
            'stadion':{'naam':ctx.venue.stadium,'plaats':ctx.venue.city,
                       'verplaatst':ctx.venue.relocated,'toelichting':ctx.venue.note}}
    if r['passing']:
        t = r['passing'][0]; second = r['passing'][1] if len(r['passing'])>1 else None
        rest = [x for x in r['cands'] if x is not t]
        br = max(rest, key=lambda x: x['score']) if rest else None
        m['gepubliceerd'] = {'market': f"{t['market']} — {t['label']}", 'odds': t['odds'],
          'bron': t['book'] or f"BetExplorer marktgemiddelde over {w['bex']['books']} boeken",
          'my_prob': round(t['my_prob'],4), 'implied': round(t['implied'],4),
          'edge_pp': round(t['edge'],2), 'edge_xg': round(t['edge_xg'],2),
          'edge_split': round(t['edge_split'],2), 'edge_robust_min': round(t['robust'],2),
          'score': round(t['score'],4),
          'tweede_gekwalificeerd': None if second is None else
             {'market': f"{second['market']} — {second['label']}", 'odds': second['odds'], 'score': round(second['score'],4)},
          'hoogste_afgewezen': None if br is None else
             {'market': f"{br['market']} — {br['label']}", 'odds': br['odds'], 'score': round(br['score'],4), 'valt_af_op': br['failed']},
          'robuustheid_grid': t['grid'], 'aantal_gekwalificeerd': len(r['passing']),
          'aantal_doorgerekend': len(r['cands'])}
    else:
        pool = [x for x in r['cands'] if x['edge']>0] or r['cands']
        nm = max(pool, key=lambda x: x['edge'])
        m['near_miss'] = {'market': f"{nm['market']} — {nm['label']}", 'odds': nm['odds'],
            'edge_xg': round(nm['edge_xg'],2), 'edge_split': round(nm['edge_split'],2),
            'edge_robust_min': round(nm['robust'],2), 'failed_gate': nm['failed']}
        m['robuustheid_grid'] = nm['grid']
        m['geen_bet_reden'] = [
          f"{len(r['cands'])} selecties doorgerekend over {', '.join(sorted({x['market'] for x in r['cands']}))}; "
          f"de hoogste edge is {nm['label']} @{nm['odds']} op {nm['edge']:+.2f} pp.",
          f"Die valt af op poort {nm['failed']}: xG-methode {nm['edge_xg']:+.2f} pp, splitsmethode "
          f"{nm['edge_split']:+.2f} pp, zwakste stand van het (shrink, rho)-grid {nm['robust']:+.2f} pp."
          + (f" Contextpoort: {nm['context_reason']}." if nm['failed']=='context' else '')]
    b['matches'].append(m)

NONE_R = {'Primeira Liga (POR)':'promovendus uit de Liga Portugal 2; football-data.co.uk dekt die divisie niet',
          'Ekstraklasa (POL)':'beide ploegen promoveerden uit de I liga; football-data.co.uk dekt die divisie niet'}
for r in trunc:
    c = cn(r['comp']); b = comps.setdefault(c, {'status':'GEANALYSEERD','matches':[]})
    naam = f"{r['home']} – {r['away']}"
    reden = (f"BUITEN DATADEKKING — {NONE_R[c]}" if r['tier']=='NONE' else
             f"AFGEKAPT — buiten MAX_DEEP_ANALYSES (35). Datarijkdom {r['rich']:.2f}; de laagste die "
             f"het nog haalde stond op 5.83. Eén van beide ploegen speelde 2025/2026 in een andere "
             f"divisie, dus dit duel wordt hooguit LIGHT en FULL gaat voor.")
    b.setdefault('niet_doorgerekend',[]).append(
        {'match':naam,'tier':r['tier'],'bet':False,'kickoff_nl':ko(r).isoformat(),
         'datarijkdom':{'score':r['rich'],'markten_beschikbaar':r['n_markets']},'reden':reden})

GEEN = {'Belgian Pro League (BEL)':'geen duel op de Fotmob-daglijst; speelt dit weekend zondag en maandag',
 'Danish Superliga (DEN)':'geen duel op de Fotmob-daglijst voor vandaag',
 'UEFA Champions League':'play-offs afgerond; groepsfase begint half september',
 'UEFA Europa League':'play-offs afgerond; groepsfase begint half september',
 'UEFA Conference League':'play-offs afgerond; groepsfase begint half september',
 'FA Cup (ENG)':'eerste ronde pas in november',
 'League Cup (ENG)':'ronde 2 is deze week gespeeld; ronde 3 eind september',
 'Coppa Italia (ITA)':'geen duel op de Fotmob-daglijst',
 'KNVB Beker (NED)':'eerste ronde pas in oktober',
 'DFB Pokal (GER)':'ronde 1 is vorige week gespeeld'}
for c, reden in GEEN.items():
    comps[c] = {'status':'GEEN WEDSTRIJD','matches':[],'toelichting':reden}

ORDER = ['Premier League (ENG)','Serie A (ITA)','La Liga (ESP)','Bundesliga (GER)','Ligue 1 (FRA)',
 'Championship (ENG)','Eredivisie (NED)','Primeira Liga (POR)','Belgian Pro League (BEL)',
 'Süper Lig (TUR)','Scottish Premiership (SCO)','Danish Superliga (DEN)','Ekstraklasa (POL)',
 'UEFA Champions League','UEFA Europa League','UEFA Conference League','FA Cup (ENG)',
 'League Cup (ENG)','Coppa Italia (ITA)','KNVB Beker (NED)','DFB Pokal (GER)']
for c, b in comps.items():
    n_an = len(b.get('matches',[])); n_no = len(b.get('niet_doorgerekend',[]))
    if b['status'] == 'GEANALYSEERD':
        b['toelichting'] = (f"{n_an + n_no} wedstrijd{'en' if n_an+n_no!=1 else ''} vandaag, "
                            f"{n_an} doorgerekend" + (f", {n_no} niet" if n_no else ''))

from collections import Counter
mk = Counter(); comps_mk = {}
for r in res:
    for x in r.get('cands', []):
        mk[x['market']] += 1
        comps_mk.setdefault(x['market'], set()).add(cn(r['row']['comp']))
bets_mk = Counter(r['passing'][0]['market'] for r in res if r.get('passing'))

state = load_or_start('a', date(2026,8,29))
state['competitions'] = {c: comps[c] for c in ORDER if c in comps}
state['herdraai'] = {
 'reden': ('Tweede Run A van 29 aug 2026. De eerste (04:10 CEST, 14 bets) is op verzoek van de '
           'gebruiker overgedaan na drie regelwijzigingen: §1a koopt spreads eerst (AH+DNB+DC voor '
           '1 credit), Stage 4 rangschikt op gemeten datarijkdom in plaats van op speeldagen van de '
           'competitie, en MAX_DEEP_ANALYSES gaat in het weekend naar 35.'),
 'vervangen_picks': 14, 'vervangen_status': 'void, vóór aftrap',
 'eerste_run_artifact': 'https://claude.ai/code/artifact/1467067e-6503-4289-9ec3-3d578a2a7174'}
state['parameters'] = {'MAX_DEEP_ANALYSES':35,'MAX_SHORTLIST':5,'EDGE_THRESHOLD_FULL':3.0,
 'EDGE_THRESHOLD_LIGHT':6.0,'MAX_LIGHT_IN_SHORTLIST':2,'MIN_ODDS':1.3,'MAX_ODDS':6.0,
 'SETTLE_AFTER_HOURS':12,'afgekapt':len(trunc),
 'toelichting':('49 duels op de runlijst; 34 met beide ploegen in deze competitie in 2025/2026 (FULL), '
   '12 met een ploeg uit een andere divisie (hooguit LIGHT) en 3 zonder omrekenbare divisie (NONE). '
   'Alle 34 FULL passen nu binnen de weekendcap van 35; de 35e plek ging naar het best gedocumenteerde '
   'LIGHT-duel, Lorient – Troyes (datarijkdom 5.83). Hoogste dat afviel: Mainz – Paderborn (5.50).')}
state['credits'] = {'plafond': odds2['cap'], 'gebruikt': 9, 'extra_buiten_plafond': 1,
 'over_na_run': 68, 'report': odds2['report'], 'rotatie_stap0': odds2['rotatie'],
 'markten_gekocht': {'spreads (AH+DNB+DC)': sorted(cn(c) for c in odds2['spreads']),
                     'totals (OU)': 'hergebruikt uit de eerdere run van vandaag (04:35 CEST) voor tien competities; La Liga opnieuw opgehaald om 08:05 voor 1 credit'},
 'verdeling': ('stap 0 (§1a nieuw): fetch_spreads voor negen competities in de dagrotatie = 9 credits, '
   'waarna het plafond op was en Scottish Premiership en Premier League geen spreads kregen; '
   'stap 1 (totals): 0 credits, de totals van 04:35 waren er al; stap 2 (BTTS): 0 credits. '
   'Eén credit buiten het plafond besteed aan het opnieuw ophalen van de La Liga-totals, om te '
   'meten hoeveel de prijzen van 04:35 waren bewogen — antwoord: maximaal +0.08 op vijf lijnen.')}
state['marktbalans'] = {
 'selecties_doorgerekend': dict(mk), 'competities_met_prijzen': {k: len(v) for k,v in comps_mk.items()},
 'bets': dict(bets_mk),
 'toelichting': ('Alle vijf betaalde/gratis markten hebben in elke doorgerekende wedstrijd meegedaan '
   'waar er prijzen voor lagen. 1X2 leverde 105 doorgerekende selecties op en nul bets — dat is '
   'deze keer de analyse die spreekt, niet de inkoop.')}
state['vroeg_seizoen'] = {'factor': round(FACTOR,4), 'pooled': round(POOLED,4),
 'speeldagen': TOTAL_MD, 'speeldagen_per_competitie': up['md'],
 'controle_tegen_de_markt': {'duels':30,'zonder_correctie_pp':-4.28,'met_correctie_pp':1.24,
   'gem_abs_zonder_pp':7.55,'gem_abs_met_pp':6.53,
   'toelichting':'gemeten in de eerste run van vandaag op dezelfde competities; factor ongewijzigd'}}
save(state)
print('geschreven:', len(state['competitions']), 'competities;',
      sum(len(b.get('matches',[])) for b in state['competitions'].values()), 'geanalyseerd')
