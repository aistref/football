"""failed_gate / failed_gate_ruw / bet_ruw / bet_beide toevoegen aan de kandidaten.

Zelfde poortvolgorde en zelfde regels als tmp-run/rb20_analyze.py (§1, §5b): `edge` staat op
plek twee en wordt per schaal apart getoetst, en een selectie die alléén op de herijking sneuvelt
krijgt het label `herijking` in plaats van het vagere `edge`.
"""
import json

ORDER = ("odds", "edge", "tweede_methode", "robuustheid", "context", "underdog")
THRESH = 8.0   # FULL

path = "data/run-state/2026-09-24-run-b.json"
st = json.load(open(path))
m = st["competitions"]["MLS (USA)"]["matches"][0]

for c in m["all_candidates"]:
    base = {k: c["poorten"][k] for k in ("odds", "tweede_methode", "context", "underdog")}
    rob = c["poorten"]["robuustheid"]
    def _fail(edge_value):
        g = dict(base); g["edge"] = edge_value >= THRESH; g["robuustheid"] = rob
        return next((k for k in ORDER if g.get(k) is False), None)
    fail, fail_raw = _fail(c["edge_pp"]), _fail(c["edge_raw"])
    if fail == "edge" and fail_raw is None:
        fail = "herijking"
    c["failed_gate"] = fail
    c["failed_gate_ruw"] = fail_raw
    c["bet_ruw"] = fail_raw is None
    c["bet_beide"] = fail is None and fail_raw is None
    print(f"{c['selection']:34s} edge {c['edge_pp']:+6.2f} / ruw {c['edge_raw']:+6.2f} -> "
          f"failed_gate {fail!s:16s} ruw {fail_raw!s:16s} bet_ruw {c['bet_ruw']}")

json.dump(st, open(path, "w"), ensure_ascii=False, indent=1)
print("bijgewerkt:", path)
