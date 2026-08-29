import json, sys, urllib.request
from datetime import date
from scripts import fotmob

fx = fotmob.fetch_fixtures(date(2026,8,28))
want = [
 ('Racing Santander','Elche'),('Bayern','Stuttgart'),('Lille','PSG'),('Debrecen','MTK Budapest'),
 ('Crystal Palace','Man City'),('Milan','Venezia'),('Deportivo Alavés','Villarreal'),
 ('Wrexham','Birmingham'),('FC Groningen','Fortuna Sittard'),('Rio Ave','Sporting CP'),
 ('Wisła Płock','Korona Kielce'),('Universitatea Cluj','Petrolul Ploiești'),
 ('Cremonese','Modena'),('Eintracht Braunschweig','Hertha BSC'),('Jong Ajax','Helmond Sport'),
 ('RKC Waalwijk','Jong PSV'),('TOP Oss','Jong FC Utrecht'),
]
import unicodedata,re
def n(s):
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]','',s.lower())
allm=[]
for l in fx.get('leagues',[]):
    for m in l.get('matches',[]):
        allm.append((l.get('name'), m))
for wh,wa in want:
    hit=None
    for lname,m in allm:
        if n(wh) in n(m['home']['name']) or n(m['home']['name']) in n(wh):
            if n(wa) in n(m['away']['name']) or n(m['away']['name']) in n(wa):
                hit=(lname,m); break
    if hit:
        lname,m=hit
        st=m.get('status',{})
        print(f"{wh} – {wa} | {lname} | {st.get('scoreStr')} | finished={st.get('finished')} | id={m['id']}")
    else:
        print(f"{wh} – {wa} | NIET GEVONDEN")
