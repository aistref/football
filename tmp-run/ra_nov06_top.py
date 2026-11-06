"""§5b/§5a — de twee dagranglijsten van 6 nov 2026, uit `ra_nov06_results.json`.

Dit is dezelfde `toplist.build` die `ra_nov06_publiceer.py` straks gebruikt; hier alleen om te
zien wat de rangorde oplevert voordat er iets wordt vastgelegd.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import toplist

res = json.load(open("tmp-run/ra_nov06_results.json"))
st = {"date": "2026-11-06", "run": "A", "competitions": {}}
for m in res["matches"]:
    st["competitions"].setdefault(m["competition"],
                                  {"status": "GEANALYSEERD", "matches": []})["matches"].append(m)

top = toplist.build(st)
for lijst in ("herijkt", "ruw"):
    print(f"=== {lijst} ===")
    for i, r in enumerate(top[lijst], 1):
        print(f" {i}. {r['match']:44} {r['market']:16} {r['selection']:24} "
              f"@{r['odds']:<7.3f} {r['tier']:5} edge {r['edge_pp']:+6.2f} "
              f"score {r['score']:6} | {r['status']}")
json.dump(top, open("tmp-run/ra_nov06_top_a.json", "w"), ensure_ascii=False, indent=1)
