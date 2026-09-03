"""Stage 0 (schaduw) 3 sep 2026: uitslagen van 2 sep bij Fotmob, 90-minutenstand."""
import json, re, sys, unicodedata
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob

DAY = date(2026, 9, 2)
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)

fx = fotmob.fetch_fixtures(DAY)
index = {}
for lg in fx.get("leagues", []):
    for m in lg.get("matches", []):
        st = m.get("status", {}) or {}
        index[(norm(m["home"]["name"]), norm(m["away"]["name"]))] = {
            "id": m.get("id"), "league": lg.get("name"), "score": st.get("scoreStr"),
            "finished": st.get("finished"), "cancelled": st.get("cancelled"),
            "home": m["home"]["name"], "away": m["away"]["name"]}
print("fixtures 2 sep:", len(index))
rows = [json.loads(l) for l in open("data/shadow.jsonl")]
todo = [r for r in rows if r["result"] == "pending" and r["date"] == "2026-09-02"]
out=[]
for r in todo:
    h, a = [x.strip() for x in r["match"].split("–")]
    hit = index.get((norm(h), norm(a)))
    if not hit:
        cand=[v for k,v in index.items() if k[0].startswith(norm(h)[:6]) and k[1].startswith(norm(a)[:6])]
        hit = cand[0] if len(cand)==1 else None
    out.append({"id": r["id"], "match": r["match"], "market": r["market"], "selection": r.get("selection"),
                "odds": r.get("odds"), "found": bool(hit), **(hit or {})})
    print(f"{'OK ' if hit else 'MIS'} {r['match']:36s} {r['market']:16s} {r.get('selection','')[:44]:46s} -> {hit['score'] if hit else '?'}")
json.dump(out, open("tmp-run/s0_shadow.json","w"), ensure_ascii=False, indent=1)
