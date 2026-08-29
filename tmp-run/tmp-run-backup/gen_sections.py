import pickle, json, sys
from datetime import datetime
sys.path.insert(0,'tmp-run')
results,_=pickle.load(open('tmp-run/deep.pkl','rb'))
picks=[json.loads(l) for l in open('data/picks.jsonl') if l.strip()]
picks=[p for p in picks if p['run_date']=='2026-08-29']
risk=json.load(open('tmp-run/risk.json'))
RISKNL={'low':'Low','med':'Medium','high':'High'}
COMP={'Super Lig (TUR)':'Süper Lig (TUR)'}
out=[]
out.append('| # | Wedstrijd | Bet | Odds | My prob | Edge | Score | Risico |')
out.append('|---|---|---|---|---|---|---|---|')
short=[p for p in picks if p['shortlisted']]
def find(p):
    return next(r for r in results if COMP.get(r['row']['comp'],r['row']['comp'])==p['competition']
                and r['row']['home']==p['home'] and r['row']['away']==p['away'])
for i,p in enumerate(short,1):
    t=find(p)['passing'][0]
    out.append(f"| {i} | {p['home']} – {p['away']} | {p['selection']} | {p['odds']} | "
               f"{p['my_prob']*100:.1f}% | {p['edge_pp']:+.1f} pp | **{t['score']:.2f}** | {RISKNL[risk[p['id']]]} |")
open('tmp-run/shortlist.md','w').write('\n'.join(out))

blocks=[]
for p in picks:
    res=find(p); t=res['passing'][0]; r=res['row']
    ko=datetime.fromisoformat(p['kickoff']).strftime('%H:%M')
    tw=p['notes'].split('. ',3)[-1]
    blocks.append(
f"""{p['home']} – {p['away']} · {ko} · {p['competition']}
Data: FULL
Bet: {p['market']} — {p['selection']} — Odds: {p['odds']} ({p['odds_source']})
Implied prob: {p['implied_prob']*100:.1f}%  •  My prob: {p['my_prob']*100:.1f}%
Edge: {p['edge_pp']:+.2f} pp  •  Confidence: {p['confidence']}  •  Risicoklasse: {RISKNL[risk[p['id']]]}
Methodes: xG {t['edge_xg']:+.2f} pp · splits {t['edge_split']:+.2f} pp · zwakste (shrink, rho)-stand {t['robust']:+.2f} pp
Lambdas: xG {res['lam_xg'][0]:.2f} – {res['lam_xg'][1]:.2f} · splits {res['lam_sp'][0]:.2f} – {res['lam_sp'][1]:.2f}
selection_score: {t['score']:.4f}
{tw}""")
open('tmp-run/bets.md','w').write('\n\n'.join(blocks))
print(open('tmp-run/shortlist.md').read())
print()
print(open('tmp-run/bets.md').read()[:1500])
