import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob

day = date(2026,9,21)
fx = fotmob.fetch_fixtures(day)
WANT = {
 122:"Czech First League (CZE)",
 135:"Greek Super League (GRE)",
 59:"Eliteserien (NOR)",
 67:"Allsvenskan (SWE)",
 252:"Croatian HNL (CRO)",
 212:"Hungarian NB I (HUN)",
 189:"Romanian SuperLiga (ROU)",
 140:"Segunda División (ESP)",
 56:"Serie B (ITA)",
 146:"2. Bundesliga (GER)",
 69:"Swiss Super League (SUI)",
 38:"Austrian Bundesliga (AUT)",
 111:"Keuken Kampioen Divisie (NED)",
 108:"English League One (ENG)",
 109:"English League Two (ENG)",
 130:"MLS (USA)",
 268:"Série A (BRA)",
}
out={}
seen_ids=set()
for lg in fx.get("leagues", []):
    lid = lg.get("primaryId") or lg.get("id")
    seen_ids.add((lid, lg.get("ccode"), lg.get("name")))
    if lid not in WANT: continue
    comp=WANT[lid]
    ms=[]
    for m in lg.get("matches", []):
        st=m.get("status",{}) or {}
        ms.append({"id":m.get("id"),"home":m["home"]["name"],"away":m["away"]["name"],
                   "home_id":m["home"].get("id"),"away_id":m["away"].get("id"),
                   "utc":st.get("utcTime"),"started":st.get("started"),"cancelled":st.get("cancelled")})
    out[comp]={"league_id":lid,"ccode":lg.get("ccode"),"matches":ms}
    print(comp, len(ms))
    for m in ms: print("   ", m["utc"], m["home"], "-", m["away"], m["id"], "cancelled" if m["cancelled"] else "")
print("TOTAAL duels:", sum(len(v["matches"]) for v in out.values()))
print("GEEN WEDSTRIJD:", sorted(set(WANT.values())-set(out)))
print("aantal competities in de daglijst:", len(seen_ids))
json.dump(out, open("tmp-run/b21_matches.json","w"), ensure_ascii=False, indent=1)
json.dump(sorted([[a,b,c] for a,b,c in seen_ids], key=lambda r:(r[1] or "",r[2] or "")), open("tmp-run/b21_daylist.json","w"), ensure_ascii=False, indent=1)
