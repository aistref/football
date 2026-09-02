import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob

day = date(2026,9,2)
fx = fotmob.fetch_fixtures(day)
LG = {38:"Austrian Bundesliga (AUT)",122:"Czech First League (CZE)",108:"English League One (ENG)",69:"Swiss Super League (SUI)"}
matches={}
for lg in fx.get("leagues",[]):
    pid = lg.get("primaryId") or lg.get("id")
    if pid in LG and lg.get("name") in ("Bundesliga","1. Liga","League One","Super League"):
        rows=[]
        for m in lg.get("matches",[]):
            rows.append({"id":m.get("id"),"home":m["home"]["name"],"home_id":m["home"].get("id"),
                         "away":m["away"]["name"],"away_id":m["away"].get("id"),
                         "utc":m.get("status",{}).get("utcTime")})
        matches[LG[pid]]={"league_id":pid,"matches":rows}
json.dump(matches, open("tmp-run/matches.json","w"), ensure_ascii=False, indent=1)
for k,v in matches.items():
    print(f"== {k} (id {v['league_id']}) {len(v['matches'])} duels")
    for m in v["matches"]: print("   ", m["utc"], m["home"],"-",m["away"], m["id"])

print("\n=== xG probe per season ===")
for k,v in matches.items():
    for season in ("2026/2027","2025/2026","2026"):
        try:
            st = fotmob.fetch_league_stats(v["league_id"], season)
            teams = st.get("teams") or {}
            n = len(teams)
            played = sorted({t.get("played",0) for t in teams.values()}) if isinstance(teams,dict) else []
            print(f"{k} {season}: has_xg={st.get('has_xg')} teams={n} played={played[:6]} avg_xg={st.get('avg_xg_per_match')}")
        except Exception as e:
            print(f"{k} {season}: ERROR {type(e).__name__}: {e}")
