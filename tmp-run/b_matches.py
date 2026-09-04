import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob

day = date(2026,9,4)
fx = fotmob.fetch_fixtures(day)
WANT = {
 (59,"NOR"):"Eliteserien (NOR)",
 (252,"CRO"):"Croatian HNL (CRO)",
 (212,"HUN"):"Hungarian NB I (HUN)",
 (189,"ROU"):"Romanian SuperLiga (ROU)",
 (140,"ESP"):"Segunda División (ESP)",
 (146,"GER"):"2. Bundesliga (GER)",
 (111,"NED"):"Keuken Kampioen Divisie (NED)",
 (260,"ALB"):"Kategoria Superiore (ALB)",
 (122,"CZE"):"Czech First League (CZE)",
 (135,"GRE"):"Greek Super League (GRE)",
 (67,"SWE"):"Allsvenskan (SWE)",
 (56,"ITA"):"Serie B (ITA)",
 (69,"SUI"):"Swiss Super League (SUI)",
 (38,"AUT"):"Austrian Bundesliga (AUT)",
 (108,"ENG"):"English League One (ENG)",
 (109,"ENG"):"English League Two (ENG)",
}
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
    for m in ms: print("   ", m["utc"], m["home"], "-", m["away"], m["id"], "cancelled" if m["cancelled"] else "")
print("TOTAAL duels:", sum(len(v["matches"]) for v in out.values()))
print("GEEN WEDSTRIJD:", sorted(set(WANT.values())-set(out)))
json.dump(out, open("tmp-run/b_matches.json","w"), ensure_ascii=False, indent=1)
