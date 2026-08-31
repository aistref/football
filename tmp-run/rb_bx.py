import json
from scripts import betexplorer as bx
COMPS={"Greek Super League (GRE)":"Greek Super League (GRE)","Allsvenskan (SWE)":"Allsvenskan (SWE)",
 "Croatian HNL (CRO)":"Croatian HNL (CRO)","Romanian SuperLiga (ROU)":"Romanian SuperLiga (ROU)",
 "Segunda Division (ESP)":"Segunda División (ESP)","Keuken Kampioen Divisie (NED)":"Keuken Kampioen Divisie (NED)",
 "Kategoria Superiore (ALB)":"Kategoria Superiore (ALB)"}
res={}
for comp,key in COMPS.items():
    rows=bx.fetch_league_fixtures(bx.KNOWN_LEAGUE_URLS[key])
    res[comp]=[{"home":r.home,"away":r.away,"odds":list(r.odds) if r.odds else None,
                "is_today":r.is_today,"when":r.when,"bookmakers":r.bookmakers} for r in rows]
    print(f"== {comp} ({len(rows)} rijen, {sum(1 for r in rows if r.is_today)} vandaag)")
    for r in rows:
        if r.is_today:
            print(f"   {r.home} - {r.away}  {r.odds}  boeken={r.bookmakers}  {r.when}")
json.dump(res, open('tmp-run/rb_bx.json','w'), ensure_ascii=False, indent=1)
