import json
from scripts import fotmob
LEAGUES = {135:"Greek Super League (GRE)", 67:"Allsvenskan (SWE)", 252:"Croatian HNL (CRO)",
        189:"Romanian SuperLiga (ROU)", 140:"Segunda Division (ESP)",
        111:"Keuken Kampioen Divisie (NED)", 260:"Kategoria Superiore (ALB)"}
SEASONS = {135:["2026/2027","2025/2026"], 67:["2026"], 252:["2026/2027","2025/2026"],
           189:["2026/2027","2025/2026"], 140:["2026/2027","2025/2026"],
           111:["2026/2027","2025/2026"], 260:["2026/2027","2025/2026","2026"]}
res={}
for lid,name in LEAGUES.items():
    res[name]={}
    for s in SEASONS[lid]:
        try:
            d = fotmob.fetch_league_stats(lid, s)
            teams=d.get('teams',{})
            played = max([t.get('played',0) or 0 for t in teams.values()], default=0)
            res[name][s]={"has_xg":d.get('has_xg'),"n_teams":len(teams),"max_played":played,
                          "avg_xg":d.get('avg_xg_per_match'),
                          "hg":d.get('home_goals_per_match'),"ag":d.get('away_goals_per_match')}
            print(f"{name:32} {s:10} has_xg={d.get('has_xg')!s:5} teams={len(teams):3} played={played:3} avg_xg={d.get('avg_xg_per_match')}")
        except Exception as e:
            res[name][s]={"error":str(e)[:200]}
            print(f"{name:32} {s:10} FOUT: {str(e)[:120]}")
json.dump(res, open('tmp-run/rb_probe.json','w'), ensure_ascii=False, indent=1)
