import json, sys
sys.path.insert(0,'tmp-run')
from scripts import fotmob, oddsapi
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           scale_level, splits_from_fotmob, totals_prob, early_season_uplift)
from rb_names import resolve, best_pair
res=json.load(open('tmp-run/rb_results.json'))
cands=json.load(open('tmp-run/rb_cands.json'))
S3=json.load(open('tmp-run/rb_stage3.json'))['stats']
odds=json.load(open('tmp-run/rb_odds_all.json'))
F=res['vroeg_seizoen']['factor']
CURRENT={"Allsvenskan (SWE)"}
def build(comp,pid,season,tier,factor):
    st=fotmob.fetch_league_stats(pid,season); t=st['teams']
    if tier=="FULL":
        lg=LeagueContext(st['home_goals_per_match'],st['away_goals_per_match'],st['avg_xg_per_match'])
    else:
        pl=sum(x.get('played',0) for x in t.values()); g=sum(x.get('gf',0) for x in t.values())
        lg=LeagueContext(st['home_goals_per_match'],st['away_goals_per_match'], g/pl if pl else 1.35)
    if comp not in CURRENT: lg=scale_level(lg,factor)
    return lg,t
def ts(r,tier):
    if tier=="FULL" and r.get('xg') is not None: return TeamStats(r['xg'],r['xga'],r['mp'])
    return TeamStats(r['gf'],r['ga'],r['played'])
def devig2(o_over,o_under):
    a,b=1/o_over,1/o_under; return a/(a+b)
rows=[]
for c in cands:
    if c['tier']=='NONE': continue
    comp=c['competition']
    if comp not in odds['bought']['totals']: continue
    evs=odds['raw']['totals'][comp]
    ev=best_pair(c['home'],c['away'],evs,lambda e:e['home_team'],lambda e:e['away_team'])
    if not ev: continue
    lines=oddsapi.best_by_line(ev,'totals')
    o_ov=lines.get(('Over',2.5)) or lines.get(('over',2.5))
    o_un=lines.get(('Under',2.5)) or lines.get(('under',2.5))
    if not(o_ov and o_un): continue
    mkt=devig2(o_ov[0],o_un[0])
    tier=S3[comp]['tier']
    out={}
    for tag,fac in (('voor',1.0),('na',F)):
        lg,t=build(comp,c['primaryId'],c['season'],tier,fac)
        h,a=t[c['table_home']],t[c['table_away']]
        p1=analyze_match(ts(h,tier),ts(a,tier),lg)
        p2=analyze_match_from_splits(splits_from_fotmob(h),splits_from_fotmob(a),league=lg)
        my=(totals_prob(p1.grid,2.5,'over',o_ov[0])+totals_prob(p2.grid,2.5,'over',o_ov[0]))/2
        out[tag]=(my-mkt)*100
    rows.append((c['competition'],f"{c['home']} – {c['away']}",mkt,out['voor'],out['na'],comp in CURRENT))
print(f"{'wedstrijd':44} {'markt':>7} {'voor':>8} {'na':>8}")
for comp,m,mkt,v,n,cur in rows:
    print(f"{m[:44]:44} {mkt*100:6.1f}% {v:+7.2f} {n:+7.2f}"+("  (lopend seizoen, geen correctie)" if cur else ""))
corr=[r for r in rows if not r[5]]
if corr:
    print(f"\nalleen competities MET correctie ({len(corr)}): voor {sum(r[3] for r in corr)/len(corr):+.2f} pp -> na {sum(r[4] for r in corr)/len(corr):+.2f} pp")
    print(f"  gem. abs. fout: voor {sum(abs(r[3]) for r in corr)/len(corr):.2f} -> na {sum(abs(r[4]) for r in corr)/len(corr):.2f}")
print(f"alle {len(rows)}: voor {sum(r[3] for r in rows)/len(rows):+.2f} pp -> na {sum(r[4] for r in rows)/len(rows):+.2f} pp")
