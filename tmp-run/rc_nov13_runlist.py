import json, re
from datetime import date, datetime, timezone
from scripts.runwindow import belongs_to_run, kickoff_nl, playable
DAY=date(2026,11,13)
fx=json.load(open("tmp-run/rc_nov13_fixtures.json"))
RUN={114:"Vriendschappelijke interlands (id 114)",10608:"AFCON-kwalificatie (id 10608)",
 9806:"UEFA Nations League A (id 9806)",9807:"UEFA Nations League B (id 9807)",9808:"UEFA Nations League C (id 9808)",9809:"UEFA Nations League D (id 9809)",
 9821:"CONCACAF Nations League (id 9821)",9876:"SAFF Championship (id 9876)",329:"Arabian Gulf Cup (id 329)",13287:"ASEAN Cup (id 13287)",11038:"King's Cup (id 11038)"}
EXCL=re.compile(r"Women|W\.|U17|U19|U20|U21|U23|Olympic")
out={};excl=[];seen=set();other=[]
for d,f in fx.items():
    for lg in f.get("leagues",[]):
        name=lg.get("name","");pid=lg.get("primaryId")
        if EXCL.search(name):
            excl.append((d,pid,name,len(lg.get("matches",[])))); continue
        if pid not in RUN:
            if lg.get("ccode")=="INT": other.append((d,pid,name))
            continue
        for m in lg["matches"]:
            st=m.get("status",{})
            if st.get("cancelled") or not st.get("utcTime"): continue
            if not belongs_to_run(st["utcTime"],DAY): continue
            if m["id"] in seen: continue
            seen.add(m["id"])
            out.setdefault(RUN[pid],[]).append(dict(competition=RUN[pid],group=name,league_id=pid,match_id=m["id"],
              home=m["home"]["name"],away=m["away"]["name"],home_id=m["home"]["id"],away_id=m["away"]["id"],
              kickoff_utc=st["utcTime"],kickoff_nl=kickoff_nl(st["utcTime"]),source_day=d,playable=playable(st["utcTime"])))
for k,v in out.items():
    v.sort(key=lambda r:r["kickoff_utc"])
    print("==",k,len(v))
    for r in v: print("  ",r["kickoff_nl"],r["source_day"],r["group"],"|",r["home"],"–",r["away"],r["home_id"],r["away_id"])
print("excluded:",excl)
print("other INT (not runlist):",other)
json.dump(out,open("tmp-run/rc_nov13_runlist.json","w"),ensure_ascii=False,indent=1)
