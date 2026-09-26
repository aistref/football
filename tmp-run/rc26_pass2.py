import json, runpy
import sys
sys.path.insert(0, '.')
from datetime import date
from scripts import national, squadform, model, sides, oddsapi, recalibrate

eng = runpy.run_path("tmp-run/rc26_engine.py")
DAY = date(2026, 9, 26)
MIN_ODDS, MAX_ODDS = eng["MIN_ODDS"], eng["MAX_ODDS"]
NEAR_LIGHT = eng["NEAR_LIGHT"]
value_selector = eng["value_selector"]
robustness_for = eng["robustness_for"]
context_gate = eng["context_gate"]
nat_stats_ctx = eng["nat_stats_ctx"]
sq_stats_ctx = eng["sq_stats_ctx"]

nf = national.load_fit(); sf = squadform.load_fit(); squads = squadform.load_squads()
recal = recalibrate.load_fit()

results = json.load(open("tmp-run/rc26_pass1.json"))
btts = json.load(open("tmp-run/rc26_btts.json"))
targets = json.load(open("tmp-run/rc26_btts_targets.json"))

GATE_ORDER = ["odds", "edge", "anticirc", "tier", "tweede_methode", "robuustheid", "context", "underdog"]

for comp, idx, eid in targets:
    r = results[comp][idx]
    home_id, away_id = r["home_id"], r["away_id"]
    nat_h, nat_a, nat_ctx = nat_stats_ctx(nf, home_id, away_id)
    probs_nat = model.analyze_match(nat_h, nat_a, nat_ctx)
    probs_sq = None
    if not r["poort5_niet_gemeten"]:
        sq_h, sq_a, sq_ctx = sq_stats_ctx(sf, squads, home_id, away_id)
        probs_sq = model.analyze_match(sq_h, sq_a, sq_ctx)
    inf_h = squadform.injuries(home_id, squads)
    inf_a = squadform.injuries(away_id, squads)
    poort7_meetbaar = r["context"]["poort7_meetbaar"]
    avg_odds = r["avg_odds_1x2"]

    ev_btts = btts[eid]
    best = {}
    for bm in ev_btts.get("bookmakers", []):
        title = bm.get("title")
        for mk in bm.get("markets", []):
            if mk["key"] != "btts":
                continue
            for oc in mk["outcomes"]:
                price = oc["price"]
                net = oddsapi.net_price(price, title)
                key = oc["name"]
                if key not in best or net > best[key][0]:
                    best[key] = (net, price, title)
    new_cands = []
    for name, side in (("Yes", "yes"), ("No", "no")):
        if name not in best:
            continue
        net, price, book = best[name]
        odds = net
        odds_gate = MIN_ODDS <= odds <= MAX_ODDS
        p_xg = value_selector(probs_nat, probs_nat.grid, "btts", side, None, odds)
        if probs_sq is not None:
            p_split = value_selector(probs_sq, probs_sq.grid, "btts", side, None, odds)
            my_raw = model.combine_probs(p_xg, p_split, weight=eng["WEIGHT_NAT"])
        else:
            p_split = None
            my_raw = p_xg
        my_prob = recalibrate.apply(my_raw, recal)
        implied = 1.0 / odds
        edge_pp = model.edge_pp(my_prob, odds)
        edge_raw = model.edge_pp(my_raw, odds)
        edge_xg = model.edge_pp(p_xg, odds)
        edge_split = model.edge_pp(p_split, odds) if p_split is not None else None
        rob = robustness_for(nat_h, nat_a, nat_ctx, "btts", side, None, odds)
        tweede_methode = True
        if p_split is not None:
            tweede_methode = (p_xg > implied) and (p_split > implied)
        robuustheid = rob.min_edge > 0
        edge_near = edge_pp >= NEAR_LIGHT
        ctx_pass, ctx_reason = context_gate(None, inf_h.get("out_share"), inf_a.get("out_share"), poort7_meetbaar)
        und = sides.check(None, avg_odds, today=DAY) if avg_odds else None
        if und:
            und_pass, und_reason, would_block = und.passed, und.reason, und.would_block
        else:
            und_pass, und_reason, would_block = True, "geen kant om te benadelen", False
        gates = {"odds": odds_gate, "edge": edge_near, "anticirc": True, "tier": True,
                 "tweede_methode": tweede_methode, "robuustheid": robuustheid,
                 "context": ctx_pass, "underdog": und_pass}
        failed_gate = None
        for g in GATE_ORDER:
            if not gates[g]:
                failed_gate = g
                break
        score = model.selection_score(edge_pp, my_prob, "LIGHT") if failed_gate is None else None
        score_ruw = model.selection_score(edge_raw, my_raw, "LIGHT")
        new_cands.append({
            "market": "BTTS", "kind": "btts", "selection_label": f"BTTS {'Ja' if side=='yes' else 'Nee'}",
            "side": None, "sel_key": f"btts_{side}", "odds": round(odds, 4), "odds_gross": price,
            "book": f"The Odds API (beste prijs, netto; {book})",
            "my_prob": my_prob, "my_raw": my_raw, "implied": implied,
            "p_xg": p_xg, "p_split": p_split, "edge_pp": edge_pp, "edge_raw": edge_raw,
            "edge_xg": edge_xg, "edge_split": edge_split,
            "edge_robust_min": rob.min_edge, "edge_robust_max": rob.max_edge,
            "poorten": gates, "context_reason": ctx_reason, "underdog_reason": und_reason,
            "would_block_underdog": would_block, "failed_gate": failed_gate,
            "score": score, "score_ruw": score_ruw,
        })
    r["all_candidates"].extend(new_cands)
    r["market_kinds_present"] = sorted(set(r["market_kinds_present"]) | {"btts"})

json.dump(results, open("tmp-run/rc26_pass2.json", "w"), indent=1, ensure_ascii=False)
print("klaar met pass 2.")
