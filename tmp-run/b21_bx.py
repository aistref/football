import json, sys
sys.path.insert(0,'.')
from scripts import betexplorer as bx
COMPS=["Czech First League (CZE)","Greek Super League (GRE)","Eliteserien (NOR)","Allsvenskan (SWE)",
 "Croatian HNL (CRO)","Hungarian NB I (HUN)","Romanian SuperLiga (ROU)","Segunda División (ESP)",
 "Serie B (ITA)","2. Bundesliga (GER)","Swiss Super League (SUI)","Austrian Bundesliga (AUT)",
 "Keuken Kampioen Divisie (NED)","English League One (ENG)","English League Two (ENG)",
 "MLS (USA)","Série A (BRA)"]
out={}
for comp in COMPS:
    url=bx.KNOWN_LEAGUE_URLS[comp]
    try:
        ms=bx.fetch_league_fixtures(url)
        rows=[{"home":m.home,"away":m.away,"odds":list(m.odds),"is_today":m.is_today,"when":m.when,"books":m.bookmakers} for m in ms]
        out[comp]=rows
        today=[r for r in rows if r["is_today"]]
        nxt = rows[0]["when"] if rows else "-"
        print(f"{comp}: {len(rows)} rijen, vandaag {len(today)}, eerstvolgend label: {nxt!r}")
        for r in today: print("    TODAY", r["home"],"-",r["away"], r["odds"], r["books"])
    except Exception as e:
        out[comp]={"error":f"{type(e).__name__}: {e}"}
        print(f"{comp}: FOUT {type(e).__name__}: {e}")
json.dump(out, open("tmp-run/b21_bx.json","w"), ensure_ascii=False, indent=1)
