import pickle, json, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'tmp-run')
NL=timezone(timedelta(hours=2))
results,truncated=pickle.load(open('tmp-run/deep.pkl','rb'))
picks=json.load(open('tmp-run/picks_new.json'))
byid={}
COMP={'Super Lig (TUR)':'Süper Lig (TUR)'}
print('=== BETS (op score) ===')
for p in picks:
    res=next(r for r in results if COMP.get(r['row']['comp'],r['row']['comp'])==p['competition']
             and r['row']['home']==p['home'] and r['row']['away']==p['away'])
    t=res['passing'][0]
    ko=datetime.fromisoformat(p['kickoff']).strftime('%H:%M')
    print(f"{'TOP5' if p['shortlisted'] else '    '} {p['competition'][:22]:24} {p['home']} – {p['away']} · {ko}")
    print(f"      {p['market']}: {p['selection']} @ {p['odds']} | src={p['odds_source'][:60]}")
    print(f"      my {p['my_prob']*100:.1f}% impl {p['implied_prob']*100:.1f}% edge {p['edge_pp']:+.2f} "
          f"| xg {t['edge_xg']:+.2f} split {t['edge_split']:+.2f} robuust {t['robust']:+.2f} "
          f"| score {t['score']:.4f} | conf {p['confidence']}")
    print(f"      lam_xg={[round(x,2) for x in res['lam_xg']]} lam_split={[round(x,2) for x in res['lam_sp']]}")
print()
print('=== NEAR MISS ===')
for res in results:
    if res['passing']: continue
    r=res['row']
    pool=[c for c in res['cands'] if c['edge']>0] or res['cands']
    nm=max(pool,key=lambda x:x['edge'])
    print(f"{COMP.get(r['comp'],r['comp'])[:22]:24} {r['home']} – {r['away']:22} | {nm['market']} {nm['label'][:24]:26} "
          f"@{nm['odds']:5.2f} | xg {nm['edge_xg']:+6.2f} split {nm['edge_split']:+6.2f} robuust {nm['robust']:+6.2f} "
          f"| gem {nm['edge']:+6.2f} | valt af op {nm['failed']}")
print()
print('=== CONTEXT-POORT AFWIJZINGEN ===')
for res in results:
    for c in res['cands']:
        if c['failed']=='context':
            print(f"  {res['row']['home']} – {res['row']['away']}: {c['market']} {c['label']} — {c['context_reason']}")
            break
print()
print('=== STADIONS ===')
for res in results:
    if res['ctx'] and res['ctx'].venue.relocated:
        print('  VERPLAATST:', res['row']['home'], res['ctx'].venue.stadium, res['ctx'].venue.note)
print('  relocated=true bij', sum(1 for r in results if r['ctx'] and r['ctx'].venue.relocated), 'van', len(results))
print('  context niet opgehaald bij', sum(1 for r in results if r['ctx'] is None))
