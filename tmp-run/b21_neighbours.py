import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob
WANT = {122:"Czech",135:"Greek",59:"Eliteserien",67:"Allsvenskan",252:"Croatian",212:"Hungarian",
 189:"Romanian",140:"Segunda",56:"SerieB ITA",146:"2.Bundesliga",69:"Swiss",38:"Austrian",
 111:"KKD",108:"L1 ENG",109:"L2 ENG",130:"MLS",268:"Serie A BRA"}
for d in [date(2026,9,20), date(2026,9,22), date(2026,9,23)]:
    fx = fotmob.fetch_fixtures(d)
    found={}
    for lg in fx.get("leagues", []):
        lid = lg.get("primaryId") or lg.get("id")
        if lid in WANT:
            found[WANT[lid]] = [(m["status"].get("utcTime"), m["home"]["name"], m["away"]["name"]) for m in lg.get("matches",[])]
    print("==", d, "==")
    for k,v in found.items():
        print("  ", k, len(v), v[:3])
