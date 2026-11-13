import json
from scripts import oddsapi, betexplorer as bx
from scripts.oddsapi import CreditGuard, suggest_cap
cap = suggest_cap(19430, 17); print("cap", cap)
guard = CreditGuard(cap=cap)
resp = oddsapi.fetch_bulk("soccer_uefa_nations_league", ["h2h","spreads","totals"])
guard.record(resp, "UEFA Nations League")
ev = resp.data
for e in ev: print(e["commence_time"], e["home_team"], "-", e["away_team"], len(e.get("bookmakers",[])))
json.dump(ev, open("tmp-run/rc_nov13_oddsapi_nl.json","w"), indent=1, ensure_ascii=False)
print("cost", resp.cost, "remaining", resp.requests_remaining)
print(guard.report())
out={}
for key in ["Vriendschappelijke interlands","CONCACAF Nations League","CAF Afrika Cup-kwalificatie"]:
    try:
        rows = bx.fetch_league_fixtures(bx.KNOWN_LEAGUE_URLS[key])
        out[key]=[[r.home,r.away,list(r.odds),r.when,r.bookmakers,r.is_today] for r in rows]
        print(key, len(rows))
    except Exception as e:
        out[key]=f"ERROR: {e}"; print(key,"ERROR",e)
for key,url in [("UEFA Nations League","https://www.betexplorer.com/football/europe/uefa-nations-league/")]:
    try:
        rows = bx.fetch_league_fixtures(url); out[key]=[[r.home,r.away,list(r.odds),r.when,r.bookmakers,r.is_today] for r in rows]; print(key,len(rows))
    except Exception as e:
        out[key]=f"ERROR: {e}"; print(key,"ERROR",e)
json.dump(out, open("tmp-run/rc_nov13_bx.json","w"), indent=1, ensure_ascii=False)
