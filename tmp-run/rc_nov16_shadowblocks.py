import json
P = "data/run-state/2026-11-16-run-c.json"
s = json.load(open(P))
n_nm = n_p8 = 0
best = []
for comp in s["competitions"].values():
    for m in comp["matches"]:
        q = [c for c in (m.get("all_candidates") or []) if c["failed_gate"] is None]
        if q: best.append((max(c["score"] for c in q), m["match"]))
rank = {name: i + 1 for i, (_, name) in enumerate(sorted(best, reverse=True))}
print("rang", rank)
for comp in s["competitions"].values():
    for m in comp["matches"]:
        m.pop("poort8_vervallen", None)
        if isinstance(m.get("lambdas"), list):
            m["lambdas_landenrating"] = m.pop("lambdas")   # margins.py leest 'lambdas.xg' alleen voor clubduels
        cs = m.get("all_candidates") or []
        if not cs: continue
        p8 = [c for c in cs if c["failed_gate"] == "underdog"]
        if p8:
            b = max(p8, key=lambda c: c["score_ruw"])
            m["poort8_geblokkeerd"] = [{"market": b["market"], "selection": b["selection"], "odds": b["odds"],
                "my_prob": b["my_prob"], "edge_pp": b["edge_pp"], "my_prob_herijkt": b["my_prob"], "edge_pp_herijkt": b["edge_pp"],
                "edge_xg": b["edge_xg"], "edge_split": b["edge_split"], "edge_robust_min": b["edge_robust_min"],
                "failed_gate": "underdog", "underdog_reason": b["underdog_reason"], "ook_geblokkeerd": len(p8) - 1}]
            n_p8 += 1
        q = [c for c in cs if c["failed_gate"] is None]
        if not m.get("bet") and q:
            b = max(q, key=lambda c: c["score"])
            m["gekwalificeerd_niet_gepubliceerd"] = {"market": b["market"], "selection": b["selection"], "odds": b["odds"],
                "edge_pp": b["edge_pp"], "my_prob": b["my_prob"], "selection_score": b["score"], "rang": rank[m["match"]],
                "reden": f"haalt alle poorten, maar rang {rank[m['match']]} in de dagranglijst bij MAX_SHORTLIST = 3 (maandag) — §5b"}
            m["near_miss"] = {"market": b["market"], "selection": b["selection"], "odds": b["odds"], "edge_xg": b["edge_xg"],
                              "edge_split": b["edge_split"], "edge_robust_min": b["edge_robust_min"],
                              "failed_gate": "lijstlengte", "my_prob": b["my_prob"], "edge_pp": b["edge_pp"]}
            n_nm += 1
        elif not m.get("bet"):
            b = max(cs, key=lambda c: c["score_ruw"])
            m["near_miss"] = {"market": b["market"], "selection": b["selection"], "odds": b["odds"], "edge_xg": b["edge_xg"],
                              "edge_split": b["edge_split"], "edge_robust_min": b["edge_robust_min"],
                              "failed_gate": b["failed_gate"], "my_prob": b["my_prob"], "edge_pp": b["edge_pp"]}
            n_nm += 1
        else:
            m["near_miss"] = None
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False)
print("near_miss", n_nm, "poort8_geblokkeerd", n_p8)
