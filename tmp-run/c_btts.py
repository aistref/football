import json, sys, unicodedata, re
sys.path.insert(0,'.')
from scripts.oddsapi import fetch_event_markets, CreditGuard
# §1a stap 2: BTTS kost 2 credits per wedstrijd en wordt daarom alleen gekocht voor wedstrijden die
# in de gratis/goedkope markten al een kandidaat-edge lieten zien.
WANT=["Holstein Kiel – 1. FC Nürnberg","Degerfors – Halmstads BK","GAIS – Häcken",
      "Rosenborg – HamKam","Brann – Lillestrøm","Peterborough – Sheff Wed",
      "Wigan – Stockport County","Bradford – Mansfield","Tranmere – Oldham",
      "AEK Athens – Aris Thessaloniki"]
M=json.load(open("tmp-run/c_matches.json")); D=json.load(open("tmp-run/c_oddsapi.json"))
KEY=D["sport_keys"]
ALIAS={"Sheff Wed":"Sheffield Wednesday","MK Dons":"Milton Keynes Dons","HamKam":"Hamarkameratene"}
def norm(s):
    s=unicodedata.normalize("NFKD",(s or "").lower()).encode("ascii","ignore").decode()
    return "".join(ch for ch in s if ch.isalnum())
def words(s):
    s=unicodedata.normalize("NFKD",(s or "").lower()).encode("ascii","ignore").decode()
    return {w for w in re.split(r"[^a-z0-9]+",s) if len(w)>=4}
def same(a,b):
    A,B=norm(a),norm(b)
    return A==B or A in B or B in A or bool(words(a)&words(b))
kick={}
for comp,blk in M.items():
    for m in blk["matches"]:
        kick[f"{m['home']} – {m['away']}"]=(comp,m["home"],m["away"],m["utc"].replace(".000Z","Z"))
guard=CreditGuard(cap=362)
out={}
for name in WANT:
    comp,home,away,utc=kick[name]
    hn,an=ALIAS.get(home,home),ALIAS.get(away,away)
    ev=None
    for e in D["spreads"].get(comp,[]):
        if e.get("commence_time")!=utc: continue
        if (same(e["home_team"],home) and same(e["away_team"],away)) or \
           (same(e["home_team"],hn) and same(e["away_team"],an)):
            ev=e; break
    if not ev:
        out[name]={"error":"geen event-id in de spreads-respons"}; print(name,"GEEN EVENT"); continue
    r=fetch_event_markets(KEY[comp], ev["id"], ["btts"]); guard.record(r,name)
    out[name]=r.data
    best={}
    for b in (r.data or {}).get("bookmakers",[]):
        for mk in b.get("markets",[]):
            if mk.get("key")!="btts": continue
            for o in mk.get("outcomes",[]):
                n=o["name"].lower()
                if n not in best or o["price"]>best[n][0]: best[n]=(o["price"],b["title"])
    print(f"{name:36s} {best}", flush=True)
out["_reden"]="niet opgevraagd — geen kandidaat-edge in de goedkope markten (§1a stap 2)"
print(guard.report())
json.dump(out, open("tmp-run/c_btts.json","w"), ensure_ascii=False)
