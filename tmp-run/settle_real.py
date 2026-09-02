"""Stage 0, tweede doorloop: de echte picks van 1 sep afwikkelen.

Om 02:10 stonden ze op 10,9-11,4 uur en gaf `ledger.py open` ze niet terug
(SETTLE_AFTER_HOURS = 12). De wedstrijden waren toen al ruim vier uur uit.
"""
import json, re, unicodedata
from datetime import date
from scripts import fotmob

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)

fx = fotmob.fetch_fixtures(date(2026, 9, 1))
index = {}
for lg in fx.get("leagues", []):
    for m in lg.get("matches", []):
        st = m.get("status", {}) or {}
        index[(norm(m["home"]["name"]), norm(m["away"]["name"]))] = {
            "id": m.get("id"), "league": lg.get("name"), "score": st.get("scoreStr"),
            "finished": st.get("finished"), "cancelled": st.get("cancelled")}

rows = [json.loads(l) for l in open("data/picks.jsonl")]
todo = [r for r in rows if r["result"] == "pending" and r["run_date"] == "2026-09-01"]
out = []
for r in todo:
    hit = index.get((norm(r["home"]), norm(r["away"])))
    if not hit:
        cand = [v for k, v in index.items()
                if k[0].startswith(norm(r["home"])[:6]) and k[1].startswith(norm(r["away"])[:6])]
        hit = cand[0] if len(cand) == 1 else None
    out.append({"id": r["id"], "run": r["run"], "match": f"{r['home']} – {r['away']}",
                "market": r["market"], "selection": r["selection"], "odds": r["odds"],
                **(hit or {})})
    print(f"{'OK ' if hit else 'MIS'} {r['run']} {r['home']} – {r['away']:20s} "
          f"{r['market']:15s} {r['selection'][:30]:30s} @{r['odds']:5} -> "
          f"{hit['score'] if hit else '?'}  finished={hit['finished'] if hit else '?'}")
json.dump(out, open("tmp-run/real_results.json", "w"), ensure_ascii=False, indent=1)
