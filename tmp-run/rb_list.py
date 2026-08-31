import json, datetime
from scripts import fotmob
d = datetime.date(2026,8,31)
fx = fotmob.fetch_fixtures(d)
for L in fx['leagues']:
    n=len(L.get('matches',[]))
    print(f"{L.get('ccode'):5} {L.get('primaryId') or L.get('id'):>7} {n:>3}  {L.get('name')}")
