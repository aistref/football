import pickle, json, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
results, truncated = pickle.load(open('tmp-run/deep.pkl','rb'))
NL = timezone(timedelta(hours=2))
bets=[]
for res in results:
    r=res['row']
    if not res['passing']: continue
    top=res['passing'][0]
    second=res['passing'][1] if len(res['passing'])>1 else None
    if second is None:
        rest=[c for c in res['cands'] if c is not top]
        second=max(rest,key=lambda x:x['score']) if rest else None
    bets.append((r,top,second,res))
bets.sort(key=lambda b:-b[1]['score'])
print(f"{'#':3}{'duel':38}{'markt':30}{'odds':>7}{'my':>8}{'edge':>8}{'score':>8}  tweede keuze")
for i,(r,t,s,res) in enumerate(bets,1):
    ko=datetime.fromisoformat(r['kickoff'].replace('Z','+00:00')).astimezone(NL).strftime('%H:%M')
    print(f"{i:<3}{(r['home']+' - '+r['away'])[:36]:38}{(t['market']+' '+t['label'])[:28]:30}"
          f"{t['odds']:7.2f}{t['my_prob']*100:7.1f}%{t['edge']:+8.2f}{t['score']:8.3f}  "
          f"{(s['market']+' '+s['label'])[:24] if s else '-'} {s['score']:.3f}" if s else '')
print()
print('BETS:',len(bets))
