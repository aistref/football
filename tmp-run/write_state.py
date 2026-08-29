import pickle, json, sys
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
from scripts.progress import load_or_start, save

NL = timezone(timedelta(hours=2))
results, truncated = pickle.load(open('tmp-run/deep.pkl','rb'))
comps = json.load(open('tmp-run/comps.json'))
up = json.load(open('tmp-run/uplift.json'))
odds = json.load(open('tmp-run/odds.json'))

COMP_NAME = {'Super Lig (TUR)':'Süper Lig (TUR)'}
def cn(c): return COMP_NAME.get(c,c)
def ko(r):
    return datetime.fromisoformat(r['kickoff'].replace('Z','+00:00')).astimezone(NL).strftime('%H:%M')

trunc_by_comp = {}
for r in truncated:
    trunc_by_comp.setdefault(cn(r['comp']), []).append(r)

NONE_REASON = {
 'Primeira Liga (POR)': 'promovendus uit de Liga Portugal 2; football-data.co.uk dekt de Portugese tweede divisie niet, dus er is geen gemeten omrekenfactor en dus geen onafhankelijke kansinput op het niveau waarop gespeeld wordt',
 'Ekstraklasa (POL)': 'beide ploegen promoveerden uit de I liga; football-data.co.uk dekt de Poolse tweede divisie niet',
}
NONE_MATCHES = {'Arouca – Marítimo','Académico Viseu – FC Porto','Wisła Kraków – Wieczysta Kraków'}
CAP_CUT = {'Köln – Hoffenheim','RB Leipzig – M\'gladbach','Union Berlin – Frankfurt','Dortmund – Hamburger SV'}

for c, rs in trunc_by_comp.items():
    block = comps.setdefault(c, {'status': None, 'matches': []})
    extra = []
    for r in rs:
        naam = f"{r['home']} – {r['away']}"
        if naam in NONE_MATCHES:
            extra.append({'match': naam, 'tier': 'NONE', 'bet': False, 'kickoff_nl': ko(r),
                          'reden': f"BUITEN DATADEKKING — {NONE_REASON[c]}"})
        elif naam in CAP_CUT:
            extra.append({'match': naam, 'tier': 'AFGEKAPT', 'bet': False, 'kickoff_nl': ko(r),
                          'reden': 'AFGEKAPT — FULL-dekking, maar buiten MAX_DEEP_ANALYSES gevallen; '
                                   'de Bundesliga heeft dit seizoen pas één speeldag gespeeld en zakte '
                                   'daarmee als laatste in de rangschikking op datakwaliteit'})
        else:
            extra.append({'match': naam, 'tier': 'AFGEKAPT', 'bet': False, 'kickoff_nl': ko(r),
                          'reden': 'AFGEKAPT — één van beide ploegen speelde 2025/2026 in een andere divisie; '
                                   'zo\'n duel wordt hooguit LIGHT (omrekening via football-data.co.uk) en '
                                   'FULL gaat vóór LIGHT bij het vullen van MAX_DEEP_ANALYSES'})
    block['matches'] = block.get('matches', []) + extra
    if block['status'] is None:
        block['status'] = 'AFGEKAPT'

GEEN = {
 'Bundesliga (GER)': None,
 'Belgian Pro League (BEL)': 'geen duel op de Fotmob-daglijst; de Pro League speelt dit weekend zondag en maandag',
 'Danish Superliga (DEN)': 'geen duel op de Fotmob-daglijst voor vandaag',
 'UEFA Champions League': 'play-offs afgerond; de loting was donderdag, de groepsfase begint half september',
 'UEFA Europa League': 'play-offs afgerond; groepsfase begint half september',
 'UEFA Conference League': 'play-offs afgerond; groepsfase begint half september',
 'FA Cup (ENG)': 'eerste ronde pas in november',
 'League Cup (ENG)': 'ronde 2 is deze week gespeeld; ronde 3 volgt eind september',
 'Coppa Italia (ITA)': 'geen duel op de Fotmob-daglijst',
 'KNVB Beker (NED)': 'eerste ronde pas in oktober',
 'DFB Pokal (GER)': 'ronde 1 is vorige week gespeeld; ronde 2 eind oktober',
}
for c, reden in GEEN.items():
    if reden is None: continue
    comps[c] = {'status': 'GEEN WEDSTRIJD', 'matches': [], 'toelichting': reden}

TOELICHTING = {
 'Premier League (ENG)': '4 wedstrijden vandaag, 3 doorgerekend; Coventry – Hull afgekapt (beide ploegen promoveerden uit de Championship)',
 'Serie A (ITA)': '4 wedstrijden vandaag, 2 doorgerekend; Fiorentina – Frosinone en Monza – Udinese afgekapt (promovendus uit de Serie B)',
 'La Liga (ESP)': '3 wedstrijden, alle drie doorgerekend; enige competitie naast de Süper Lig met spreads deze run',
 'Bundesliga (GER)': '6 wedstrijden vandaag, geen enkele doorgerekend — vier vielen buiten MAX_DEEP_ANALYSES, twee hebben een promovendus (Elversberg, Paderborn)',
 'Ligue 1 (FRA)': '5 wedstrijden, 4 doorgerekend; Lorient – Troyes afgekapt (Troyes promoveerde uit de Ligue 2)',
 'Championship (ENG)': '11 wedstrijden, 6 doorgerekend; 5 afgekapt wegens een ploeg uit een andere divisie',
 'Eredivisie (NED)': '3 wedstrijden, alle drie doorgerekend',
 'Primeira Liga (POR)': '3 wedstrijden, 1 doorgerekend; 2 buiten datadekking (Marítimo en Académico Viseu uit de Liga Portugal 2)',
 'Süper Lig (TUR)': '3 wedstrijden, alle drie doorgerekend',
 'Scottish Premiership (SCO)': '3 wedstrijden, 2 doorgerekend; Hearts – St. Johnstone afgekapt (St. Johnstone promoveerde uit de Championship)',
 'Ekstraklasa (POL)': '4 wedstrijden, 3 doorgerekend; Wisła Kraków – Wieczysta Kraków buiten datadekking',
}
STATUS = {'Bundesliga (GER)': 'AFGEKAPT'}
for c, t in TOELICHTING.items():
    if c in comps:
        comps[c]['toelichting'] = t
        comps[c]['status'] = STATUS.get(c, 'GEANALYSEERD')
        comps[c].pop('wedstrijden_vandaag', None)

ORDER = ['Premier League (ENG)','Serie A (ITA)','La Liga (ESP)','Bundesliga (GER)','Ligue 1 (FRA)',
 'Championship (ENG)','Eredivisie (NED)','Primeira Liga (POR)','Belgian Pro League (BEL)',
 'Süper Lig (TUR)','Scottish Premiership (SCO)','Danish Superliga (DEN)','Ekstraklasa (POL)',
 'UEFA Champions League','UEFA Europa League','UEFA Conference League','FA Cup (ENG)',
 'League Cup (ENG)','Coppa Italia (ITA)','KNVB Beker (NED)','DFB Pokal (GER)']

state = load_or_start('a', date(2026,8,29))
state['competitions'] = {c: comps[c] for c in ORDER if c in comps}
state['parameters'] = {
 'MAX_DEEP_ANALYSES':30,'MAX_SHORTLIST':5,'EDGE_THRESHOLD_FULL':3.0,'EDGE_THRESHOLD_LIGHT':6.0,
 'MAX_LIGHT_IN_SHORTLIST':2,'MIN_ODDS':1.3,'MAX_ODDS':6.0,'SETTLE_AFTER_HOURS':12,
 'afgekapt':19,
 'toelichting':('49 wedstrijden op de runlijst vandaag, 34 met beide ploegen in de competitie van '
   '2025/2026 (FULL). Die 34 zijn gerangschikt op datakwaliteit — FULL boven de rest, en binnen '
   'FULL op het aantal speeldagen dat de competitie dit seizoen al gespeeld heeft, want dat is de '
   'enige onafhankelijke input die per competitie verschilt. De bovenste 30 zijn doorgerekend. '
   'Afgekapt: 4 FULL-duels uit de Bundesliga (één speeldag gespeeld, dus onderaan de rangschikking), '
   '12 duels met een ploeg uit een andere divisie en 3 duels zonder omrekenbare divisie.')}
state['credits'] = {
 'plafond': odds['cap'], 'gebruikt': 13, 'over_na_run': 90, 'report': odds['report'],
 'rotatie_stap1': odds['rotatie'],
 'verdeling': ('stap 0 (§1a): fetch_totals voor alle elf competities met duels vandaag = 11 credits; '
   'stap 1: fetch_spreads voor Süper Lig en La Liga = 2 credits, waarna het plafond op was en de '
   'rotatie bij Scottish Premiership stopte; stap 2 (double_chance/btts): 0 credits, geen ruimte.')}
state['vroeg_seizoen'] = {
 'factor': round(up['factor'],4), 'pooled': round(up['pooled'],4), 'speeldagen': up['total_md'],
 'speeldagen_per_competitie': up['md'],
 'controle_tegen_de_markt': {
   'duels': 30,
   'zonder_correctie_pp': -4.28, 'met_correctie_pp': 1.24,
   'gem_abs_zonder_pp': 7.55, 'gem_abs_met_pp': 6.53,
   'boven_de_markt_met': '19 van 30', 'boven_de_markt_zonder': '8 van 30',
   'toelichting': ('gemeten op P(Over 2.5) tegen de de-vigde marktkans van The Odds API. Dit is '
     'controleren, niet fitten: de factor komt volledig uit xG-waarnemingen (§5).')}}
save(state)
print('geschreven; competities:', len(state['competitions']))
