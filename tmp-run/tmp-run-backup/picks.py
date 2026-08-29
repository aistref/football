import pickle, json, sys, re, unicodedata
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
from scripts import fotmob
NL = timezone(timedelta(hours=2))
betmap = pickle.load(open('tmp-run/betmap.pkl','rb'))
up = json.load(open('tmp-run/uplift.json'))
FACTOR, MD = up['factor'], up['md']
CAPTURED = '2026-08-29T04:35:00+02:00'
MARKET_NAME = {'1X2':'1X2','OU':'Over/Under','AH':'Asian Handicap','DNB':'Draw No Bet'}
SLUG = {'Premier League (ENG)':'epl','Serie A (ITA)':'seriea','La Liga (ESP)':'laliga',
 'Ligue 1 (FRA)':'ligue1','Championship (ENG)':'championship','Eredivisie (NED)':'eredivisie',
 'Primeira Liga (POR)':'primeira','Süper Lig (TUR)':'superlig',
 'Scottish Premiership (SCO)':'spfl','Ekstraklasa (POL)':'ekstraklasa'}
def sl(s):
    s=s.translate(str.maketrans({'ł':'l','ø':'o','đ':'d','ß':'ss','æ':'ae'}))
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]','',s.lower())

LEAGUES = {}
prev = {}
for key,(r,top,second,best_rest,res,cname) in betmap.items():
    if cname not in prev:
        prev[cname]=fotmob.fetch_league_stats(r['league_id'],'2025/2026')

rows=[]
for key,(r,top,second,best_rest,res,cname) in betmap.items():
    p=prev[cname]; th=p['teams'][r['home_key']]; ta=p['teams'][r['away_key']]
    ko=datetime.fromisoformat(r['kickoff'].replace('Z','+00:00')).astimezone(NL)
    mkt=MARKET_NAME[top['market']]
    sel=top['label']
    if top['market']=='1X2':
        sel = {'home':r['home'],'away':r['away'],None:'Gelijkspel'}[top['side']]
        selslug='1x2-'+sl(sel)
    elif top['market']=='OU':
        selslug='ou-'+sl(sel)
    elif top['market']=='AH':
        selslug='ah-'+sl(sel)
    else:
        selslug='dnb-'+sl(sel)
    if top['book']:
        src=f"{top['book']} (beste prijs via The Odds API, uitgelezen {CAPTURED[11:16]} CEST)"
    else:
        src=(f"BetExplorer marktgemiddelde over {r['bex']['books']} boeken "
             f"(bookmaker niet herleidbaar)")
    ctx=res['ctx']
    ctxline=''
    if ctx:
        ctxline=(f"Fotmob wedstrijdcontext ({ctx.lineup_type or 'geen opstelling'}): "
                 f"thuis {len(ctx.home.out_names)} afwezig ({ctx.home.out_share*100:.1f}% selectiewaarde), "
                 f"uit {len(ctx.away.out_names)} afwezig ({ctx.away.out_share*100:.1f}%); "
                 f"vorm {ctx.home.form or '-'} tegen {ctx.away.form or '-'}; rust "
                 f"{ctx.home.rest_days:.1f} tegen {ctx.away.rest_days:.1f} dagen"
                 if ctx.home.rest_days is not None and ctx.away.rest_days is not None else
                 f"Fotmob wedstrijdcontext ({ctx.lineup_type or 'geen opstelling'}): "
                 f"thuis {len(ctx.home.out_names)} afwezig, uit {len(ctx.away.out_names)} afwezig; "
                 f"vorm {ctx.home.form or '-'} tegen {ctx.away.form or '-'}")
        ctxline += f"; poort 7 gepasseerd ({top['context_reason']})"
    probs=[
      (f"Fotmob {cname} 2025/2026 xG — {r['home_key']} {th['xg']:.1f} gemaakt en {th['xga']:.1f} tegen "
       f"in {th['mp']} duels, {r['away_key']} {ta['xg']:.1f} gemaakt en {ta['xga']:.1f} tegen in "
       f"{ta['mp']} duels, tegen een competitiegemiddelde van {p['avg_xg_per_match']:.3f} xG per ploeg per duel"),
      (f"Fotmob {cname} 2025/2026 thuis/uit-splits — {r['home_key']} thuis {th['home']['gf']} gemaakt en "
       f"{th['home']['ga']} tegen in {th['home']['played']} duels, {r['away_key']} uit {ta['away']['gf']} "
       f"gemaakt en {ta['away']['ga']} tegen in {ta['away']['played']} duels, tegen competitiegemiddelden "
       f"van {p['home_goals_per_match']:.3f} thuis- en {p['away_goals_per_match']:.3f} uitdoelpunten per duel"),
    ]
    if ctxline: probs.append(ctxline)
    probs.append(f"Vroeg-seizoenscorrectie x{FACTOR:.4f}, gemeten op elf competities uit de runlijst "
                 f"({up['total_md']} speeldagen, ruwe verhouding {up['pooled']:.4f}) — uitsluitend uit "
                 f"xG-waarnemingen, geen bookmakerprijs")
    lo=min(top['edge_xg'],top['edge_split'])
    conf = 'High' if (lo>=5 and top['robust']>=5) else ('Medium' if top['robust']>=2 else 'Low')
    tw = (f"Tweede gekwalificeerde selectie binnen dit duel: {second['market']} {second['label']} "
          f"@{second['odds']}, score {second['score']:.4f}."
          if second else
          (f"Geen tweede selectie haalde alle zeven poorten; de hoogste afgewezene was "
           f"{best_rest['market']} {best_rest['label']} @{best_rest['odds']} (score {best_rest['score']:.4f}), "
           f"afgevallen op {best_rest['failed']}." if best_rest else "Geen tweede selectie."))
    rows.append({
     'id': f"2026-08-29-{SLUG[cname]}-{sl(r['home'])}-{sl(r['away'])}-{selslug}",
     'run':'A','run_date':'2026-08-29','kickoff':ko.isoformat(),'competition':cname,
     'home':r['home'],'away':r['away'],'market':mkt,'selection':sel,'odds':top['odds'],
     'odds_source':src,'odds_captured_at':CAPTURED,
     'implied_prob':round(top['implied'],4),'my_prob':round(top['my_prob'],4),
     'edge_pp':round(top['edge'],2),'data_tier':'FULL','confidence':conf,
     'prob_sources':probs,'shortlisted':False,'result':'pending',
     'notes':(f"xG-methode {top['edge_xg']:+.2f} pp, splitsmethode {top['edge_split']:+.2f} pp, "
              f"gemiddelde {top['edge']:+.2f} pp. Zwakste stand van het (shrink, rho)-grid "
              f"{top['robust']:+.2f} pp. selection_score {top['score']:.4f} over "
              f"{top['aantal'] if 'aantal' in top else len(res['passing'])} gekwalificeerde selecties "
              f"uit {len(res['cands'])} doorgerekende. {tw}"),
     '_score': top['score'], 'settled_at': None,
    })
rows.sort(key=lambda x:-x['_score'])
for i,x in enumerate(rows): x['shortlisted'] = i < 5
for x in rows: x.pop('_score')
json.dump(rows, open('tmp-run/picks_new.json','w'), ensure_ascii=False, indent=1)
for x in rows: print(('*' if x['shortlisted'] else ' '), x['id'], x['market'], x['selection'], x['odds'], x['confidence'])
