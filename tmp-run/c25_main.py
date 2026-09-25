import json, sys, math, runpy
from datetime import date
sys.path.insert(0, '.')
from scripts import national, squadform, model, sides, oddsapi, recalibrate

eng = runpy.run_path("tmp-run/c25_engine.py")

DAY = date(2026, 9, 25)
NEAR_LIGHT = eng["NEAR_LIGHT"]
EDGE_THRESHOLD_LIGHT_RAW = eng["EDGE_THRESHOLD_LIGHT_RAW"]
MIN_ODDS, MAX_ODDS = eng["MIN_ODDS"], eng["MAX_ODDS"]
WEIGHT_NAT = eng["WEIGHT_NAT"]

nl_candidates = eng["nl_candidates"]
bx_candidates = eng["bx_candidates"]
avg_h2h_nl = eng["avg_h2h_nl"]
value_selector = eng["value_selector"]
robustness_for = eng["robustness_for"]
context_gate = eng["context_gate"]
nat_stats_ctx = eng["nat_stats_ctx"]
sq_stats_ctx = eng["sq_stats_ctx"]

nf = national.load_fit()
sf = squadform.load_fit()
squads = squadform.load_squads()
recal = recalibrate.load_fit()

matches = json.load(open("tmp-run/c25_matches_with_odds.json"))

GATE_ORDER = ["odds", "edge", "anticirc", "tier", "tweede_methode", "robuustheid", "context", "underdog"]


def analyze_one(comp, m):
    home_id = str(m["home_id"]); away_id = str(m["away_id"])
    ok_h, reason_h = national.in_range(home_id, nf)
    ok_a, reason_a = national.in_range(away_id, nf)
    price_kind = "nl" if m.get("odds_event") else ("bx" if m.get("bx_odds") else None)

    rec = {
        "competition": comp, "match": f"{m['home']} – {m['away']}", "match_id": m.get("match_id"),
        "home": m["home"], "away": m["away"], "home_id": m["home_id"], "away_id": m["away_id"],
        "kickoff_utc": m["kickoff_utc"], "kickoff_nl": m["kickoff_nl"], "source_day": m["source_day"],
        "groep_fotmob": m.get("group"),
    }

    if price_kind is None:
        rec["tier"] = "BUITEN_DATADEKKING"
        rec["bet"] = False
        rec["reden"] = "geen prijsbron (geen sportkey bij The Odds API, geen BetExplorer-pagina/koersen)"
        rec["landenrating"] = {"home": reason_h, "away": reason_a}
        return rec

    if not (ok_h and ok_a):
        rec["tier"] = "NONE"
        rec["bet"] = False
        rec["reden"] = f"landenrating buiten bereik: home={reason_h} | away={reason_a}"
        rec["landenrating"] = {"home": reason_h, "away": reason_a}
        return rec

    tier = "LIGHT"
    nat_h, nat_a, nat_ctx = nat_stats_ctx(nf, home_id, away_id)
    probs_nat = model.analyze_match(nat_h, nat_a, nat_ctx)

    sq_h_ok, sq_h_reason = squadform.usable(home_id, squads)
    sq_a_ok, sq_a_reason = squadform.usable(away_id, squads)
    poort5_niet_gemeten = not (sq_h_ok and sq_a_ok)
    probs_sq = None
    if not poort5_niet_gemeten:
        sq_h, sq_a, sq_ctx = sq_stats_ctx(sf, squads, home_id, away_id)
        probs_sq = model.analyze_match(sq_h, sq_a, sq_ctx)

    inf_h = squadform.injuries(home_id, squads)
    inf_a = squadform.injuries(away_id, squads)
    poort7_meetbaar = bool(inf_h.get("measurable")) and bool(inf_a.get("measurable"))

    if price_kind == "nl":
        ev = m["odds_event"]
        cands_spec = nl_candidates(ev, ev.get("home_team"), ev.get("away_team"), m["home"], m["away"])
        avg_odds = avg_h2h_nl(ev, ev.get("home_team"), ev.get("away_team"))
        odds_src_1x2 = "The Odds API (beste prijs, netto)"
    else:
        row = m["bx_odds"]
        cands_spec = bx_candidates(row, m["home"], m["away"])
        avg_odds = list(row["odds"])
        odds_src_1x2 = f"BetExplorer marktgemiddelde ({row.get('bookmakers', 0)} boeken)"

    def build_candidates(specs):
        out = []
        for spec in specs:
            kind, side, line = spec["kind"], spec["side"], spec["line"]
            odds = spec["net"]
            odds_gate = MIN_ODDS <= odds <= MAX_ODDS
            p_xg = value_selector(probs_nat, probs_nat.grid, kind, side, line, odds)
            if probs_sq is not None:
                p_split = value_selector(probs_sq, probs_sq.grid, kind, side, line, odds)
                my_raw = model.combine_probs(p_xg, p_split, weight=WEIGHT_NAT)
            else:
                p_split = None
                my_raw = p_xg
            my_prob = recalibrate.apply(my_raw, recal)
            implied = 1.0 / odds
            edge_pp = model.edge_pp(my_prob, odds)
            edge_raw = model.edge_pp(my_raw, odds)
            edge_xg = model.edge_pp(p_xg, odds)
            edge_split = model.edge_pp(p_split, odds) if p_split is not None else None
            rob = robustness_for(nat_h, nat_a, nat_ctx, kind, side, line, odds)

            anticirc = True
            tier_gate = True
            tweede_methode = True
            if p_split is not None:
                tweede_methode = (p_xg > implied) and (p_split > implied)
            robuustheid = rob.min_edge > 0
            edge_near = edge_pp >= NEAR_LIGHT
            ctx_pass, ctx_reason = context_gate(side, inf_h.get("out_share"), inf_a.get("out_share"),
                                                poort7_meetbaar)
            und = sides.check(side, avg_odds, today=DAY) if avg_odds else sides.SideCheckStub if False else None
            if avg_odds:
                und = sides.check(side, avg_odds, today=DAY)
                und_pass, und_reason, would_block = und.passed, und.reason, und.would_block
            else:
                und_pass, und_reason, would_block = True, "geen 1X2-prijzen — geen marktoordeel", False

            gates = {"odds": odds_gate, "edge": edge_near, "anticirc": anticirc, "tier": tier_gate,
                     "tweede_methode": tweede_methode, "robuustheid": robuustheid,
                     "context": ctx_pass, "underdog": und_pass}
            failed_gate = None
            for g in GATE_ORDER:
                if not gates[g]:
                    failed_gate = g
                    break

            score = model.selection_score(edge_pp, my_prob, tier) if failed_gate is None else None
            score_ruw = model.selection_score(edge_raw, my_raw, tier)

            out.append({
                "market": spec["market"], "selection": spec["selection_label"], "sel_key": spec["sel_key"],
                "odds": round(odds, 4), "odds_raw": spec["price"], "odds_source": (
                    f"{odds_src_1x2}; {spec['book']}" if price_kind == "nl" else odds_src_1x2),
                "side": side if side in ("home", "away") else None,
                "my_prob": my_prob, "my_raw": my_raw, "implied": implied,
                "p_xg": p_xg, "p_split": p_split,
                "edge_pp": edge_pp, "edge_raw": edge_raw, "edge_xg": edge_xg, "edge_split": edge_split,
                "edge_robust_min": rob.min_edge, "edge_robust_max": rob.max_edge,
                "poorten": gates,
                "context_reason": ctx_reason, "underdog_reason": und_reason,
                "would_block_underdog": would_block,
                "failed_gate": failed_gate, "score": score, "score_ruw": score_ruw,
            })
        return out

    all_candidates = build_candidates(cands_spec)

    # BTTS second pass criterion (union of scales)
    kandidaat_edge = any(
        (MIN_ODDS <= c["odds"] <= MAX_ODDS) and
        (c["edge_pp"] >= NEAR_LIGHT or c["edge_raw"] >= EDGE_THRESHOLD_LIGHT_RAW)
        for c in all_candidates)

    rec["tier"] = tier
    rec["poort5_niet_gemeten"] = poort5_niet_gemeten
    rec["calibration"] = {
        "market": (lambda o: [1/o[0]/(1/o[0]+1/o[1]+1/o[2]), 1/o[1]/(1/o[0]+1/o[1]+1/o[2]),
                              1/o[2]/(1/o[0]+1/o[1]+1/o[2])])(avg_odds) if avg_odds else None,
        "p_xg": [probs_nat.home, probs_nat.draw, probs_nat.away],
        "p_xg_label": "landenrating (national.py)",
        "p_split_label": "selectiewaarde (squadform.py)",
    }
    if probs_sq is not None:
        rec["calibration"]["p_split"] = [probs_sq.home, probs_sq.draw, probs_sq.away]
    rec["context"] = {
        "poort7_bron": "squadform", "poort7_meetbaar": poort7_meetbaar,
        "poort7_rust_meetbaar": False,
        "home": {"squad_usable": sq_h_ok, "out_share": inf_h.get("out_share"),
                 "out_count": inf_h.get("count"), "out_value": inf_h.get("out_value"),
                 "squad_value": inf_h.get("squad_value"), "name": inf_h.get("team") or m["home"],
                 "out_names": inf_h.get("names")},
        "away": {"squad_usable": sq_a_ok, "out_share": inf_a.get("out_share"),
                 "out_count": inf_a.get("count"), "out_value": inf_a.get("out_value"),
                 "squad_value": inf_a.get("squad_value"), "name": inf_a.get("team") or m["away"],
                 "out_names": inf_a.get("names")},
    }
    rec["landenrating"] = {"home": reason_h, "away": reason_a}
    rec["selectiewaarde"] = {"home": sq_h_reason, "away": sq_a_reason}
    rec["prob_sources"] = ["scripts/national.py — landenrating (6784 interlands, gefit 20 sep 2026)"]
    if probs_sq is not None:
        rec["prob_sources"].append("scripts/squadform.py — selectiewaarde (tweede methode, 0.30)")
    rec["odds_source"] = odds_src_1x2
    rec["kandidaat_edge_btts"] = kandidaat_edge
    rec["_price_kind"] = price_kind
    rec["_event_id"] = m.get("odds_event", {}).get("id") if price_kind == "nl" else None
    rec["all_candidates"] = all_candidates
    return rec


results = {}
for comp, mlist in matches.items():
    results[comp] = [analyze_one(comp, m) for m in mlist]

with open("tmp-run/c25_pass1.json", "w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)

# report which NL matches need BTTS
need_btts = []
for comp, mlist in results.items():
    for r in mlist:
        if r.get("_price_kind") == "nl" and r.get("kandidaat_edge_btts"):
            need_btts.append((comp, r["match"], r["_event_id"]))
print("NL-duels met kandidaat-edge (BTTS ophalen):", len(need_btts))
for x in need_btts:
    print(" ", x)

n_tier = {}
for comp, mlist in results.items():
    for r in mlist:
        n_tier[r["tier"]] = n_tier.get(r["tier"], 0) + 1
print("tiers:", n_tier)
