import json, sys
sys.path.insert(0,'.')
from scripts import fotmob
M=json.load(open("tmp-run/matches.json")); L=json.load(open("tmp-run/leagues.json"))
for comp,blk in M.items():
    st=fotmob.fetch_league_stats(blk["league_id"], L[comp]["prev_season"])
    names=set(st["teams"])
    print(f"\n== {comp} prev={L[comp]['prev_season']} has_xg={st['has_xg']} teams={len(names)}")
    for m in blk["matches"]:
        for t in (m["home"],m["away"]):
            hit = t in names or [n for n in names if t.lower() in n.lower() or n.lower() in t.lower()]
            print(f"   {t:26s} -> {'OK' if t in names else (hit if hit else 'ONTBREEKT')}")
