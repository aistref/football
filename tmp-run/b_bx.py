import json, sys
sys.path.insert(0,'.')
from scripts import betexplorer as bx

COMPS=["Allsvenskan (SWE)","Hungarian NB I (HUN)","Swiss Super League (SUI)"]
out={}
for comp in COMPS:
    url=bx.KNOWN_LEAGUE_URLS[comp]
    try:
        ms=bx.fetch_league_fixtures(url)
        out[comp]=[{"home":m.home,"away":m.away,"odds":list(m.odds),"is_today":m.is_today,
                    "kickoff":getattr(m,'kickoff',None),"books":getattr(m,'books',None)} for m in ms]
        print(f"{comp}: {len(ms)} rijen")
        for m in ms:
            if m.is_today: print("   TODAY", m.home,"-",m.away, m.odds, getattr(m,'books',None))
    except Exception as e:
        out[comp]={"error":f"{type(e).__name__}: {e}"}
        print(f"{comp}: FOUT {type(e).__name__}: {e}")
json.dump(out, open("tmp-run/b_bx.json","w"), ensure_ascii=False, indent=1, default=str)
