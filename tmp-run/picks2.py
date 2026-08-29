import pickle, json, sys, re, unicodedata
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
from scripts import fotmob
NL = timezone(timedelta(hours=2))
res = pickle.load(open('tmp-run/deep3.pkl','rb'))
up  = json.load(open('tmp-run/uplift.json'))
bets = sorted([r for r in res if r.get('passing')], key=lambda r:-r['passing'][0]['score'])
CAP_SPREADS = '2026-08-29T07:52:00+02:00'   # fetch_spreads deze run
CAP_TOTALS  = '2026-08-29T04:35:00+02:00'   # totals van de eerdere run van vandaag
CAP_LALIGA  = '2026-08-29T08:05:00+02:00'   # La Liga totals opnieuw opgehaald
CAP_BEX     = '2026-08-29T07:55:00+02:00'
MARKET = {'OU':'Over/Under','DC':'Double Chance','DNB':'Draw No Bet','AH':'Asian Handicap','1X2':'1X2'}
COMPN = {'Super Lig (TUR)':'Süper Lig (TUR)'}
SLUG = {'Premier League (ENG)':'epl','Serie A (ITA)':'seriea','La Liga (ESP)':'laliga',
 'Ligue 1 (FRA)':'ligue1','Championship (ENG)':'championship','Eredivisie (NED)':'eredivisie',
 'Primeira Liga (POR)':'primeira','Süper Lig (TUR)':'superlig','Bundesliga (GER)':'bundesliga',
 'Scottish Premiership (SCO)':'spfl','Ekstraklasa (POL)':'ekstraklasa'}
def sl(s):
    s=s.translate(str.maketrans({'ł':'l','ø':'o','đ':'d','ß':'ss','æ':'ae'}))
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]','',s.lower())
def risk(t):
    lo=min(t['edge_xg'],t['edge_split'])
    if t['robust']<2 or lo<3: return 'high'
    if lo>=6 and t['robust']>=6: return 'low'
    return 'med'
CONF={'low':'High','med':'Medium','high':'Low'}

prev={}
rows=[]
for r in bets:
    w=r['row']; c=COMPN.get(w['comp'], w['comp']); t=r['passing'][0]
    if c not in prev: prev[c]=fotmob.fetch_league_stats(w['league_id'],'2025/2026')
    p=prev[c]
    ko=datetime.fromisoformat(w['kickoff'].replace('Z','+00:00')).astimezone(NL)
    m=t['market']
    if m=='OU': sel=t['label']
    elif m=='DC':
        team = w['home'] if t['side']=='home' else w['away']
        sel = ('1X' if t['side']=='home' else 'X2') + f' — {team} of gelijkspel'
    elif m=='DNB': sel = w['home'] if t['side']=='home' else w['away']
    elif m=='AH': sel = t['label']
    else: sel = t['label']
    cap = CAP_SPREADS if m in ('AH','DNB','DC') else (CAP_LALIGA if c=='La Liga (ESP)' else CAP_TOTALS)
    src = f"{t['book']} (beste prijs via The Odds API, uitgelezen {cap[11:16]} CEST)" if t['book'] \
          else f"BetExplorer marktgemiddelde over {w['bex']['books']} boeken (bookmaker niet herleidbaar), uitgelezen {CAP_BEX[11:16]} CEST"
    ctx=w['ctx']
    probs=[]
    if w['home_key'] and w['away_key']:
        th,ta=p['teams'][w['home_key']],p['teams'][w['away_key']]
        probs.append(f"Fotmob {c} 2025/2026 xG — {w['home_key']} {th['xg']:.1f} voor en {th['xga']:.1f} tegen in {th['mp']} duels, "
                     f"{w['away_key']} {ta['xg']:.1f} voor en {ta['xga']:.1f} tegen in {ta['mp']} duels, competitiegemiddelde {p['avg_xg_per_match']:.3f} xG per ploeg per duel")
        probs.append(f"Fotmob {c} 2025/2026 thuis/uit-splits — {w['home_key']} thuis {th['home']['gf']}-{th['home']['ga']} in {th['home']['played']}, "
                     f"{w['away_key']} uit {ta['away']['gf']}-{ta['away']['ga']} in {ta['away']['played']}, tegen {p['home_goals_per_match']:.3f} thuis- en {p['away_goals_per_match']:.3f} uitdoelpunten per duel")
    else:
        probs.append(f"football-data.co.uk: {r['conv_note']}")
        probs.append(f"Fotmob {c} 2025/2026 xG en thuis/uit-splits voor de ploeg die wél in deze competitie speelde")
    if ctx:
        probs.append(f"Fotmob wedstrijdcontext ({ctx.lineup_type or 'geen opstelling'}): thuis {len(ctx.home.out_names)} afwezig "
                     f"({ctx.home.out_share*100:.1f}% selectiewaarde), uit {len(ctx.away.out_names)} afwezig ({ctx.away.out_share*100:.1f}%); "
                     f"vorm {ctx.home.form or '-'} tegen {ctx.away.form or '-'}; poort 7 gepasseerd ({t['context_reason']})")
    th_t, ta_t = w.get('turn_h'), w.get('turn_a')
    if th_t is not None and ta_t is not None:
        probs.append(f"Fotmob transfers sinds 1 juni (selectiecontinuïteit, Stage 4): thuis {th_t.summary()}; uit {ta_t.summary()}")
    probs.append(f"Vroeg-seizoenscorrectie x{up['factor']:.4f} over elf competities ({up['total_md']} speeldagen, ruwe verhouding {up['pooled']:.4f}) — uitsluitend uit xG-waarnemingen, geen enkele marktprijs (§2)")
    rk=risk(t)
    second = r['passing'][1] if len(r['passing'])>1 else None
    rest=[x for x in r['cands'] if x is not t]
    best_rest = max(rest,key=lambda x:x['score']) if rest else None
    tw = (f"Tweede gekwalificeerde selectie: {second['market']} {second['label']} @{second['odds']}, score {second['score']:.4f}."
          if second else (f"Geen tweede selectie haalde alle zeven poorten; hoogste afgewezene {best_rest['market']} {best_rest['label']} "
                          f"@{best_rest['odds']} (score {best_rest['score']:.4f}), afgevallen op {best_rest['failed']}." if best_rest else 'Geen tweede selectie.'))
    extra = f" Gekocht als de {t['extra']} in de spreads-respons (§1a)." if t.get('extra') else ''
    rows.append({'id': f"2026-08-29-{SLUG[c]}-{sl(w['home'])}-{sl(w['away'])}-{m.lower()}-{sl(sel)[:24]}",
     'run':'A','run_date':'2026-08-29','kickoff':ko.isoformat(),'competition':c,
     'home':w['home'],'away':w['away'],'market':MARKET[m],'selection':sel,'odds':t['odds'],
     'odds_source':src,'odds_captured_at':cap,
     'implied_prob':round(t['implied'],4),'my_prob':round(t['my_prob'],4),
     'edge_pp':round(t['edge'],2),'data_tier':r['tier'],'confidence':CONF[rk],
     'prob_sources':probs,'shortlisted':False,'result':'pending',
     'notes':(f"xG-methode {t['edge_xg']:+.2f} pp, splitsmethode {t['edge_split']:+.2f} pp, gemiddelde {t['edge']:+.2f} pp. "
              f"Zwakste stand van het (shrink, rho)-grid {t['robust']:+.2f} pp. selection_score {t['score']:.4f} over "
              f"{len(r['passing'])} gekwalificeerde selecties uit {len(r['cands'])} doorgerekende.{extra} {tw}"),
     'settled_at':None,'_risk':rk,'_score':t['score']})
for i,x in enumerate(rows): x['shortlisted']= i<5
risks={x['id']:x.pop('_risk') for x in rows}
for x in rows: x.pop('_score')
json.dump(rows, open('tmp-run/picks2.json','w'), ensure_ascii=False, indent=1)
json.dump(risks, open('tmp-run/risk2.json','w'))
for x in rows: print(('*' if x['shortlisted'] else ' '), x['market'],'|',x['selection'][:34],'|',x['odds'],'|',x['confidence'],'|',x['id'][:60])
