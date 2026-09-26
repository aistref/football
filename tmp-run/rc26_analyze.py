"""Run C, 26 sep 2026 — hoofdanalyse: alle duels, alle markten, alle poorten."""
import json, re, unicodedata, runpy
import sys
sys.path.insert(0, '.')
from datetime import date
from scripts import national, squadform, model, sides, oddsapi, recalibrate, betexplorer as bx

eng = runpy.run_path("tmp-run/rc26_engine.py")
DAY = date(2026, 9, 26)
MIN_ODDS, MAX_ODDS = eng["MIN_ODDS"], eng["MAX_ODDS"]
NEAR_LIGHT = eng["NEAR_LIGHT"]
WEIGHT_NAT = eng["WEIGHT_NAT"]
value_selector = eng["value_selector"]
robustness_for = eng["robustness_for"]
context_gate = eng["context_gate"]
nat_stats_ctx = eng["nat_stats_ctx"]
sq_stats_ctx = eng["sq_stats_ctx"]
nl_candidates = eng["nl_candidates"]
bx_candidates = eng["bx_candidates"]
avg_h2h_nl = eng["avg_h2h_nl"]

nf = national.load_fit()
sf = squadform.load_fit()
squads = squadform.load_squads()
recal = recalibrate.load_fit()

matches = json.load(open("tmp-run/rc26_matches.json"))
oddsapi_nl = json.load(open("tmp-run/rc26_oddsapi_nl.json"))
bx_data = {}
bx_data.update(json.load(open("tmp-run/rc26_bx.json")))
bx_data.update(json.load(open("tmp-run/rc26_bx2.json")))


def normteam(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


# --- naammapping Fotmob <-> OddsAPI voor UEFA NL ---
ODDSAPI_ALIAS = {
    "czechia": "czechrepublic",
}


def find_oddsapi_event(home_fm, away_fm):
    hn, an = normteam(home_fm), normteam(away_fm)
    hn = ODDSAPI_ALIAS.get(hn, hn)
    an = ODDSAPI_ALIAS.get(an, an)
    for ev in oddsapi_nl:
        eh, ea = normteam(ev["home_team"]), normteam(ev["away_team"])
        if eh == hn and ea == an:
            return ev
    return None


BX_COMP_MAP = {
    "Vriendschappelijke interlands": "Friendly",
    "CAF Afrika Cup-kwalificatie": "AFCON-kwal-v2",
    "Arabian Gulf Cup": "Gulf-Cup-v2",
    "FIFA ASEAN Cup": "FIFA-ASEAN",
    "CONCACAF Nations League": "CONCACAF-NL",
}


def find_bx_row(comp_label, home_fm, away_fm):
    key = BX_COMP_MAP.get(comp_label)
    if not key:
        return None
    rows = bx_data.get(key)
    if not rows or isinstance(rows, str):
        return None
    hn, an = normteam(home_fm), normteam(away_fm)
    for row in rows:
        rh, ra, odds, when, nbooks = row
        if normteam(rh) == hn and normteam(ra) == an:
            return odds, nbooks
    return None


GATE_ORDER = ["odds", "edge", "anticirc", "tier", "tweede_methode", "robuustheid", "context", "underdog"]

results = {}   # comp -> list of match result dicts
btts_targets = []  # list of (comp, idx, event) for second pass

for comp, ms in matches.items():
    out = []
    for m in ms:
        home_id, away_id = str(m["home_id"]), str(m["away_id"])
        home_name, away_name = m["home"], m["away"]
        rec = {
            "competition": comp, "match": f"{home_name} – {away_name}",
            "home": home_name, "away": away_name, "home_id": home_id, "away_id": away_id,
            "match_id": m["match_id"], "kickoff_utc": m["kickoff_utc"], "kickoff_nl": m["kickoff_nl"],
            "source_day": m["source_day"], "groep_fotmob": None,
        }

        ok_h, note_h = national.in_range(home_id, nf)
        ok_a, note_a = national.in_range(away_id, nf)
        if not (ok_h and ok_a):
            rec["tier"] = "NONE"
            rec["data_reason"] = f"home: {note_h if not ok_h else 'ok'}; away: {note_a if not ok_a else 'ok'}"
            out.append(rec)
            continue
        rec["tier"] = "LIGHT"

        # --- prijsbron ---
        odds_source = None
        odds_event = None
        ev = None
        oddsapi_event = None
        if comp.startswith("UEFA Nations League"):
            oddsapi_event = find_oddsapi_event(home_name, away_name)
        bx_hit = find_bx_row(comp, home_name, away_name)

        if oddsapi_event is not None:
            odds_source = "oddsapi"
        elif bx_hit is not None:
            odds_source = "betexplorer"
        else:
            rec["odds_source"] = None
            rec["buiten_datadekking"] = True
            out.append(rec)
            continue

        nat_h, nat_a, nat_ctx = nat_stats_ctx(nf, home_id, away_id)
        probs_nat = model.analyze_match(nat_h, nat_a, nat_ctx)

        sq_h_ok, _ = squadform.usable(home_id, squads)
        sq_a_ok, _ = squadform.usable(away_id, squads)
        poort5_niet_gemeten = not (sq_h_ok and sq_a_ok)
        probs_sq = None
        if not poort5_niet_gemeten:
            sq_h, sq_a, sq_ctx = sq_stats_ctx(sf, squads, home_id, away_id)
            probs_sq = model.analyze_match(sq_h, sq_a, sq_ctx)

        inf_h = squadform.injuries(home_id, squads)
        inf_a = squadform.injuries(away_id, squads)
        poort7_meetbaar = inf_h.get("out_share") is not None and inf_a.get("out_share") is not None

        # --- kandidaten ---
        cands = []
        avg_odds_1x2 = None
        if oddsapi_event is not None:
            disp_home, disp_away = home_name, away_name
            cands = nl_candidates(oddsapi_event, oddsapi_event["home_team"], oddsapi_event["away_team"],
                                   disp_home, disp_away)
            avg_odds_1x2 = avg_h2h_nl(oddsapi_event, oddsapi_event["home_team"], oddsapi_event["away_team"])
            odds_event_id = oddsapi_event["id"]
        else:
            odds_arr, nbooks = bx_hit
            cands = bx_candidates(odds_arr, home_name, away_name, nbooks)
            avg_odds_1x2 = list(odds_arr)
            odds_event_id = None

        market_kinds_present = set(c["kind"] for c in cands)

        scored = []
        for c in cands:
            odds = c["net"]
            odds_gate = MIN_ODDS <= odds <= MAX_ODDS
            p_xg = value_selector(probs_nat, probs_nat.grid, c["kind"], c["side"], c["line"], odds)
            if probs_sq is not None:
                p_split = value_selector(probs_sq, probs_sq.grid, c["kind"], c["side"], c["line"], odds)
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
            rob = robustness_for(nat_h, nat_a, nat_ctx, c["kind"], c["side"], c["line"], odds)
            tweede_methode = True
            if p_split is not None:
                tweede_methode = (p_xg > implied) and (p_split > implied)
            robuustheid = rob.min_edge > 0
            edge_near = edge_pp >= NEAR_LIGHT
            side_for_gate = c["side"] if c["side"] in ("home", "away") else None
            ctx_pass, ctx_reason = context_gate(side_for_gate, inf_h.get("out_share"), inf_a.get("out_share"),
                                                 poort7_meetbaar)
            und = sides.check(side_for_gate, avg_odds_1x2, today=DAY) if avg_odds_1x2 else None
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
            scored.append({
                **{k: v for k, v in c.items() if k not in ("net",)},
                "odds": round(odds, 4), "odds_gross": c["price"],
                "my_prob": my_prob, "my_raw": my_raw, "implied": implied,
                "p_xg": p_xg, "p_split": p_split, "edge_pp": edge_pp, "edge_raw": edge_raw,
                "edge_xg": edge_xg, "edge_split": edge_split,
                "edge_robust_min": rob.min_edge, "edge_robust_max": rob.max_edge,
                "poorten": gates, "context_reason": ctx_reason, "underdog_reason": und_reason,
                "would_block_underdog": would_block, "failed_gate": failed_gate,
                "score": score, "score_ruw": score_ruw,
            })

        rec["poort5_niet_gemeten"] = poort5_niet_gemeten
        rec["odds_source"] = odds_source
        rec["odds_event_id"] = odds_event_id
        rec["avg_odds_1x2"] = avg_odds_1x2
        rec["market_kinds_present"] = sorted(market_kinds_present)
        rec["all_candidates"] = scored
        rec["context"] = {
            "poort7_bron": "squadform", "poort7_meetbaar": poort7_meetbaar,
            "poort7_rust_meetbaar": False,
            "home": {**inf_h, "squad_usable": sq_h_ok},
            "away": {**inf_a, "squad_usable": sq_a_ok},
        }
        rec["landenrating"] = {
            "home": f"{home_name}: {nat_h.matches_played:.1f} gewogen duels",
            "away": f"{away_name}: {nat_a.matches_played:.1f} gewogen duels",
        }
        if probs_sq is not None:
            rec["selectiewaarde"] = {"home": f"{home_name}: squadform ok", "away": f"{away_name}: squadform ok"}
        # calibration block
        cal_market = None
        if avg_odds_1x2:
            devig = sides.devig(avg_odds_1x2)
            if devig:
                cal_market = list(devig)
        rec["calibration"] = {
            "market": cal_market,
            "p_xg": [probs_nat.home, probs_nat.draw, probs_nat.away],
            "p_xg_label": "landenrating (national.py)",
            "p_split": ([probs_sq.home, probs_sq.draw, probs_sq.away] if probs_sq is not None else None),
            "p_split_label": "selectiewaarde (squadform.py)",
        }
        # kandidaat-edge voor BTTS (unie van beide schalen)
        max_edge_pp = max((s["edge_pp"] for s in scored), default=-999)
        max_edge_raw = max((s["edge_raw"] for s in scored), default=-999)
        cand_edge = (max_edge_pp >= NEAR_LIGHT) or (max_edge_raw >= eng["EDGE_THRESHOLD_LIGHT_RAW"])
        rec["kandidaat_edge_voor_btts"] = cand_edge
        if oddsapi_event is not None and cand_edge:
            btts_targets.append((comp, len(out), oddsapi_event["id"]))

        out.append(rec)
    results[comp] = out

json.dump(results, open("tmp-run/rc26_pass1.json", "w"), indent=1, ensure_ascii=False)
json.dump(btts_targets, open("tmp-run/rc26_btts_targets.json", "w"))
print("klaar met pass 1.")
for comp, ms in results.items():
    print(comp, len(ms), "duels verwerkt")
print("BTTS-kandidaten:", btts_targets)
