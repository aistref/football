import json, sys, unicodedata, re
sys.path.insert(0,'.')
from scripts.oddsapi import fetch_event_markets, CreditGuard

# BTTS is de duurste markt (2 credits per wedstrijd, §1a stap 2) en wordt daarom pas gekocht
# voor wedstrijden die al een kandidaat-edge lieten zien in de gratis/goedkope markten.
WANT = ["Arminia Bielefeld – St. Pauli","Hannover 96 – Karlsruher SC",
        "Fredrikstad – Bodø/Glimt","Sandefjord – Viking","Las Palmas – Leganés"]
KEY={"2. Bundesliga (GER)":"soccer_germany_bundesliga2",
     "Segunda División (ESP)":"soccer_spain_segunda_division",
     "Eliteserien (NOR)":"soccer_norway_eliteserien"}
M=json.load(open("tmp-run/b_matches.json")); D=json.load(open("tmp-run/b_oddsapi.json"))

def norm(s):
    s=unicodedata.normalize("NFKD",(s or "").lower()).encode("ascii","ignore").decode()
    return "".join(ch for ch in s if ch.isalnum())
def words(s):
    s=unicodedata.normalize("NFKD",(s or "").lower()).encode("ascii","ignore").decode()
    return {w for w in re.split(r"[^a-z0-9]+",s) if len(w)>=4}
def same(a,b):
    A,B=norm(a),norm(b)
    return A==B or A in B or B in A or bool(words(a)&words(b))

kickoff={}
for comp,blk in M.items():
    for m in blk["matches"]:
        kickoff[f"{m['home']} – {m['away']}"]=(comp,m["home"],m["away"],m["utc"].replace(".000Z","Z"))

guard=CreditGuard(cap=375)
out={}
for name in WANT:
    comp,home,away,utc = kickoff[name]
    ev=None
    for e in D["spreads"].get(comp,[]):
        if e.get("commence_time")==utc and same(e["home_team"],home) and same(e["away_team"],away):
            ev=e; break
    if not ev:
        out[name]={"error":"geen event-id in de spreads-respons"}; print(name,"GEEN EVENT"); continue
    r=fetch_event_markets(KEY[comp], ev["id"], ["btts"]); guard.record(r, name)
    out[name]=r.data
    best={}
    for b in (r.data or {}).get("bookmakers",[]):
        for m in b.get("markets",[]):
            if m.get("key")!="btts": continue
            for o in m.get("outcomes",[]):
                n=o["name"].lower()
                if n not in best or o["price"]>best[n][0]: best[n]=(o["price"],b["title"])
    print(f"{name:38s} {best}")
out["_reden"]="geen sportkey bij The Odds API voor deze competitie"
print(guard.report())
json.dump(out, open("tmp-run/b_btts.json","w"), ensure_ascii=False)
