import pickle, json, sys
from datetime import datetime
sys.path.insert(0,'tmp-run')
res = pickle.load(open('tmp-run/deep3.pkl','rb'))
picks = [json.loads(l) for l in open('data/picks.jsonl') if l.strip()]
picks = [p for p in picks if p['run_date']=='2026-08-29' and p['run']=='A' and p['result']=='pending']
risk = json.load(open('tmp-run/risk2.json'))
RN = {'low':'Low','med':'Medium','high':'High'}
COMPN = {'Super Lig (TUR)':'Süper Lig (TUR)'}
def find(p):
    return next(r for r in res if COMPN.get(r['row']['comp'],r['row']['comp'])==p['competition']
                and r['row']['home']==p['home'] and r['row']['away']==p['away'])
out=['| # | Wedstrijd | Bet | Odds | My prob | Edge | Score | Risico |','|---|---|---|---|---|---|---|---|']
for i,p in enumerate([x for x in picks if x['shortlisted']],1):
    t=find(p)['passing'][0]
    out.append(f"| {i} | {p['home']} – {p['away']} | {p['market']}: {p['selection']} | {p['odds']} | "
               f"{p['my_prob']*100:.1f}% | {p['edge_pp']:+.1f} pp | **{t['score']:.2f}** | {RN[risk[p['id']]]} |")
open('tmp-run/short2.md','w').write('\n'.join(out))

blocks=[]
for p in picks:
    r=find(p); t=r['passing'][0]
    ko=datetime.fromisoformat(p['kickoff']).strftime('%H:%M')
    tw=p['notes'].split('doorgerekende.',1)[1].strip()
    blocks.append(f"""{p['home']} – {p['away']} · {ko} · {p['competition']}
Data: {p['data_tier']}
Bet: {p['market']} — {p['selection']} — Odds: {p['odds']} — {p['odds_source']}
Implied prob: {p['implied_prob']*100:.1f}%  •  My prob: {p['my_prob']*100:.1f}%
Edge: {p['edge_pp']:+.2f} pp  •  Confidence: {p['confidence']}  •  Risicoklasse: {RN[risk[p['id']]]}
Methodes: xG {t['edge_xg']:+.2f} pp · splits {t['edge_split']:+.2f} pp · zwakste (shrink, rho)-stand {t['robust']:+.2f} pp
Lambdas: xG {r['lam_xg'][0]:.2f} – {r['lam_xg'][1]:.2f} · splits {r['lam_sp'][0]:.2f} – {r['lam_sp'][1]:.2f}
Datarijkdom (Stage 4): {r['row']['rich']:.2f}/10 · selection_score {t['score']:.4f}
{tw}""")
open('tmp-run/bets2.md','w').write('\n\n'.join(blocks))

# net niet
nm=[]
for r in res:
    if r.get('passing') or not r.get('cands'): continue
    pool=[x for x in r['cands'] if x['edge']>0] or r['cands']
    n=max(pool,key=lambda x:x['edge'])
    nm.append((r['row'],n))
nm.sort(key=lambda x:-x[1]['edge'])
t=['| Wedstrijd | Kandidaat | Odds | xG-model | 2e methode | Zwakste stand | Valt af op |','|---|---|---|---|---|---|---|']
for w,n in nm:
    t.append(f"| {w['home']} – {w['away']} | {n['market']} {n['label']} | {n['odds']} | "
             f"{n['edge_xg']:+.2f} | {n['edge_split']:+.2f} | {n['robust']:+.2f} | {n['failed']} |")
open('tmp-run/nm2.md','w').write('\n'.join(t))
print(open('tmp-run/short2.md').read()); print(); print(open('tmp-run/nm2.md').read())
