import json, datetime
from scripts import fotmob
d = datetime.date(2026,8,31)
fx = fotmob.fetch_fixtures(d)
WANT = {135:"Greek Super League (GRE)", 67:"Allsvenskan (SWE)", 252:"Croatian HNL (CRO)",
        189:"Romanian SuperLiga (ROU)", 140:"Segunda Division (ESP)",
        111:"Keuken Kampioen Divisie (NED)", 260:"Kategoria Superiore (ALB)"}
out=[]
for L in fx['leagues']:
    pid = L.get('primaryId') or L.get('id')
    if pid not in WANT: continue
    for m in L.get('matches',[]):
        out.append({"comp":WANT[pid],"league_id":pid,"match_id":m['id'],
                    "home":m['home']['longName'],"home_id":m['home']['id'],
                    "away":m['away']['longName'],"away_id":m['away']['id'],
                    "utc":m['status']['utcTime']})
out.sort(key=lambda x:(x['utc'],x['comp']))
json.dump(out, open('tmp-run/rb_fixtures.json','w'), ensure_ascii=False, indent=1)
from datetime import timezone, timedelta
for o in out:
    t=datetime.datetime.fromisoformat(o['utc'].replace('Z','+00:00')).astimezone(timezone(timedelta(hours=2)))
    print(f"{t:%H:%M} NL | {o['comp']:30} | {o['home']} - {o['away']} | {o['match_id']}")
print(len(out),"wedstrijden")
