import json, datetime
from scripts import fotmob
d = datetime.date(2026,8,31)
fx = fotmob.fetch_fixtures(d)
print(list(fx.keys()))
lg = fx.get('leagues') or []
print("leagues:", len(lg))
for L in lg[:3]:
    print(json.dumps({k:v for k,v in L.items() if k!='matches'}, ensure_ascii=False)[:300])
    print("  matches:", len(L.get('matches',[])))
    if L.get('matches'):
        print("  ", json.dumps(L['matches'][0], ensure_ascii=False)[:500])
    break
