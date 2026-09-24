import json, datetime as dt
from scripts.betexplorer import KNOWN_LEAGUE_URLS, fetch_league_fixtures

RUNLIST = ["Czech First League (CZE)","Greek Super League (GRE)","Eliteserien (NOR)",
 "Allsvenskan (SWE)","Croatian HNL (CRO)","Hungarian NB I (HUN)","Romanian SuperLiga (ROU)",
 "Segunda División (ESP)","Serie B (ITA)","2. Bundesliga (GER)","Swiss Super League (SUI)",
 "Austrian Bundesliga (AUT)","Keuken Kampioen Divisie (NED)","English League One (ENG)",
 "English League Two (ENG)","MLS (USA)","Série A (BRA)"]

out={}
for name in RUNLIST:
    url = KNOWN_LEAGUE_URLS.get(name)
    if not url:
        print(f"{name}: GEEN SLUG"); out[name]={"error":"geen slug"}; continue
    try:
        ms = fetch_league_fixtures(url)
    except Exception as e:
        print(f"{name}: FOUT {e}"); out[name]={"error":str(e)}; continue
    today=[m for m in ms if m.is_today]
    nxt = ms[0].when if ms else ""
    print(f"{name}: {len(ms)} rijen, {len(today)} vandaag, eerstvolgende '{nxt}'")
    for m in today: print("    *", m.home, "-", m.away, m.odds, m.when, "books", m.bookmakers)
    out[name]={"rows":len(ms),"today":[{"home":m.home,"away":m.away,"odds":list(m.odds),"when":m.when,"books":m.bookmakers} for m in today],"next":nxt,
               "all":[{"home":m.home,"away":m.away,"when":m.when,"odds":list(m.odds),"books":m.bookmakers} for m in ms[:6]]}
json.dump(out, open("tmp-run/rb24_bex.json","w"), ensure_ascii=False, indent=1)
