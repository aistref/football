import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob

day = date(2026,9,2)
fx = fotmob.fetch_fixtures(day)
leagues = fx.get("leagues", [])
print("total leagues today:", len(leagues))
WANT = [
 ("Czech First League","CZE"),("Super League","GRE"),("Eliteserien","NOR"),
 ("Allsvenskan","SWE"),("HNL","CRO"),("NB I","HUN"),("SuperLiga","ROU"),
 ("Segunda","ESP"),("Serie B","ITA"),("2. Bundesliga","GER"),("Super League","SUI"),
 ("Bundesliga","AUT"),("Eerste Divisie","NED"),("League One","ENG"),("League Two","ENG"),
 ("Kategoria Superiore","ALB"),("Superleague","KOS"),
]
ccodes = set(c for _,c in WANT)
out=[]
for lg in leagues:
    cc = lg.get("ccode")
    if cc in ccodes or cc in ("ALB","KOS"):
        out.append((cc, lg.get("name"), lg.get("primaryId") or lg.get("id"), len(lg.get("matches",[]))))
for o in sorted(out): print(o)
print("---- ALL ccodes today ----")
print(sorted(set(l.get('ccode') for l in leagues)))
