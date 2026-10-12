import json
from collections import Counter
r = json.load(open("tmp-run/rb_oct12_results.json"))
sel_total = 0
gates = Counter(); markets = Counter(); passed = []
for m in r["matches"]:
    for c in m.get("all_candidates") or []:
        sel_total += 1
        markets[c["market"]] += 1
        gates[c["failed_gate"] or "ALLE POORTEN OPEN"] += 1
        if c["failed_gate"] is None: passed.append((m["match"], c["market"], c["selection"], c["edge_pp"]))
print("selecties doorgerekend:", sel_total)
print("per markt:", dict(markets.most_common()))
print("per poort:", dict(gates.most_common()))
print("alle poorten open:", len(passed))
for p in passed: print("   ", p)
print()
tiers = Counter(m["tier"] for m in r["matches"])
print("tiers:", dict(tiers))
# poort 7 / 8 / 9
p7 = [(m["match"], c["selection"], c["context_reason"]) for m in r["matches"] for c in (m.get("all_candidates") or []) if c["failed_gate"]=="context"]
p8 = [(m["match"], c["selection"], c["underdog_reason"]) for m in r["matches"] for c in (m.get("all_candidates") or []) if c["failed_gate"]=="underdog"]
p9 = [(m["match"], c["selection"]) for m in r["matches"] for c in (m.get("all_candidates") or []) if c["failed_gate"]=="doelpunten_onder"]
print("poort7 tegengehouden:", len(p7), {x[0] for x in p7})
print("poort8 tegengehouden:", len(p8), {x[0] for x in p8})
print("poort9 tegengehouden:", len(p9))
print("poort8_geblokkeerd-blokken:", [m["match"] for m in r["matches"] if m.get("poort8_geblokkeerd")])
print("poort9_geblokkeerd-blokken:", [m["match"] for m in r["matches"] if m.get("poort9_geblokkeerd")])
print("near_miss:", [(m["match"], m["near_miss"]["failed_gate"]) for m in r["matches"] if m.get("near_miss")])
# verplaatsing + opstellingen
lt = Counter((m.get("context") or {}).get("lineup_type") or "leeg" for m in r["matches"])
print("lineup_type:", dict(lt))
rel = [m["match"] for m in r["matches"] if ((m.get("context") or {}).get("venue") or {}).get("relocated")]
print("relocated:", rel)
# promovendi
for m in r["matches"]:
    if m.get("promovendi"): print("promo", m["match"], m["promovendi"])
    if m["tier"]=="NONE": print("NONE", m["match"], "|", m.get("reason"))
# seizoensweging
print("blend-notities bij:", [m["match"] for m in r["matches"] if m.get("seizoensweging")])
print("vroeg_seizoen:", json.dumps(r.get("vroeg_seizoen"), ensure_ascii=False))
