import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob

day = date(2026,9,3)
fx = fotmob.fetch_fixtures(day)
WANT = {(67,"SWE"):"Allsvenskan (SWE)", (212,"HUN"):"Hungarian NB I (HUN)", (69,"SUI"):"Swiss Super League (SUI)"}
out={}
for lg in fx.get("leagues", []):
    key=(lg.get("primaryId") or lg.get("id"), lg.get("ccode"))
    if key not in WANT: continue
    comp=WANT[key]
    ms=[]
    for m in lg.get("matches", []):
        st=m.get("status",{}) or {}
        ms.append({"id":m.get("id"),"home":m["home"]["name"],"away":m["away"]["name"],
                   "home_id":m["home"].get("id"),"away_id":m["away"].get("id"),
                   "utc":st.get("utcTime"),"started":st.get("started"),"cancelled":st.get("cancelled")})
    out[comp]={"league_id":key[0],"ccode":key[1],"matches":ms}
    print(comp, len(ms))
    for m in ms: print("   ", m["utc"], m["home"], "–", m["away"], m["id"])
json.dump(out, open("tmp-run/b_matches.json","w"), ensure_ascii=False, indent=1)
