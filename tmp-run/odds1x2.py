import json, sys
sys.path.insert(0,'.')
from scripts.betexplorer import fetch_league_fixtures, KNOWN_LEAGUE_URLS
SLUG={"English League One (ENG)":"English League One (ENG)","Czech First League (CZE)":"Czech First League (CZE)",
      "Austrian Bundesliga (AUT)":"Austrian Bundesliga (AUT)","Swiss Super League (SUI)":"Swiss Super League (SUI)"}
out={}
for comp,k in SLUG.items():
    url=KNOWN_LEAGUE_URLS[k]
    try:
        rows=fetch_league_fixtures(url)
        out[comp]=[{"home":r.home,"away":r.away,"odds":list(r.odds),"is_today":r.is_today,"when":r.when,"books":r.bookmakers} for r in rows]
        print(f"{comp}: {len(rows)} rijen, {sum(1 for r in rows if r.is_today)} vandaag  [{url}]")
        for r in rows:
            if r.is_today: print("   ", r.when, r.home,"-",r.away, r.odds, f"({r.bookmakers} boeken)")
    except Exception as e:
        out[comp]={"error":f"{type(e).__name__}: {e}"}
        print(f"{comp}: FOUT {type(e).__name__}: {e}")
json.dump(out, open("tmp-run/odds1x2.json","w"), ensure_ascii=False, indent=1)
