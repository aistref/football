import json
P = "data/run-state/2026-11-13-run-c.json"
s = json.load(open(P))
n_nm = n_p8 = 0
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
        if not m.get("bet"):
            b = max(cs, key=lambda c: c["score_ruw"])
            m["near_miss"] = {"market": b["market"], "selection": b["selection"], "odds": b["odds"], "edge_xg": b["edge_xg"],
                              "edge_split": b["edge_split"], "edge_robust_min": b["edge_robust_min"],
                              "failed_gate": b["failed_gate"], "my_prob": b["my_prob"], "edge_pp": b["edge_pp"]}
            n_nm += 1
        else:
            m["near_miss"] = None
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False)
print("near_miss", n_nm, "poort8_geblokkeerd", n_p8)
