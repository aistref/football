"""Run C 12 nov 2026 — analyse. Basis rc06_analyze/pass2 (6 okt), bijgewerkt: scale=1.0 + today
(run-c.md, 2 nov), poort 9 (unders.check), sides.check met today, BTTS-ronde ingebouwd."""
import json, re, sys, unicodedata, runpy
from datetime import date
from scripts import national, squadform, model, sides, oddsapi, recalibrate, unders

DAY = date(2026, 11, 12)
eng = runpy.run_path("tmp-run/rc06_engine.py")
nl_candidates, bx_candidates, avg_h2h_nl = eng["nl_candidates"], eng["bx_candidates"], eng["avg_h2h_nl"]
value_selector, context_gate = eng["value_selector"], eng["context_gate"]
MIN_ODDS, MAX_ODDS, NEAR_LIGHT, W = 1.30, 6.00, 6.0, 0.70

nf, sf, squads = national.load_fit(), squadform.load_fit(), squadform.load_squads()
recal = recalibrate.load_fit()
runlist = json.load(open("tmp-run/rc_nov12_runlist.json"))
nl_events = json.load(open("tmp-run/rc_nov12_oddsapi_nl.json"))
bxd = json.load(open("tmp-run/rc_nov12_bx.json"))
btts_data = json.load(open("tmp-run/rc_nov12_btts.json")) if len(sys.argv) > 1 else {}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)
ALIAS = {"czechia": "czechrepublic", "turkiye": "turkey", "drcongo": "drcongo",
         "centralafricanrepublic": "centralafrica", "guineabissau": "guineabissau",
         "bosniaandherzegovina": "bosniaherzegovina", "ireland": "republicofireland"}
def n2(s):
    x = norm(s); return ALIAS.get(x, x)

def find_event(m):
    for ev in nl_events:
        if n2(ev["home_team"]) == n2(m["home"]) and n2(ev["away_team"]) == n2(m["away"]) \
           and ev["commence_time"][:13] == m["kickoff_utc"][:13]:
            return ev
    return None

BXKEY = {"Vriendschappelijke interlands (id 114)": "Vriendschappelijke interlands",
         "AFCON-kwalificatie (id 10608)": "CAF Afrika Cup-kwalificatie",
         "CONCACAF Nations League (id 9821)": "CONCACAF Nations League"}
def find_bx(comp, m):
    rows = bxd.get(BXKEY.get(comp, "UEFA Nations League"))
    if not isinstance(rows, list): return None
    for rh, ra, odds, when, nb, today in rows:
        if n2(rh) == n2(m["home"]) and n2(ra) == n2(m["away"]):
            return odds, nb
    return None

GATE_ORDER = ["odds", "edge", "anticirc", "tier", "tweede_methode", "robuustheid", "context",
              "underdog", "doelpunten_onder"]

def score_cands(cands, P, inf, avg, rec_src):
    nat_h, nat_a, nat_ctx, probs_nat, probs_sq, p7 = P
    out = []
    for c in cands:
        odds = c["net"]
        p_xg = value_selector(probs_nat, probs_nat.grid, c["kind"], c["side"], c["line"], odds)
        p_split = (value_selector(probs_sq, probs_sq.grid, c["kind"], c["side"], c["line"], odds)
                   if probs_sq is not None else None)
        my_raw = model.combine_probs(p_xg, p_split, weight=W) if p_split is not None else p_xg
        my_prob = recalibrate.apply(my_raw, recal)
        implied = 1 / odds
        edge_pp_, edge_raw = model.edge_pp(my_prob, odds), model.edge_pp(my_raw, odds)
        k, sd, ln = c["kind"], c["side"], c["line"]
        sel = lambda p, k=k, sd=sd, ln=ln, o=odds: value_selector(p, p.grid, k, sd, ln, o)
        rob = model.robustness_check(nat_h, nat_a, nat_ctx, sel, odds, scale=1.0, today=DAY)
        side = sd if sd in ("home", "away") else None
        ctx_ok, ctx_reason = context_gate(side, inf[0].get("out_share"), inf[1].get("out_share"), p7)
        if not p7:
            ctx_reason = ("niet meetbaar — selectie te dun bij minstens één ploeg; poort 7 telt niet als "
                          "bescherming; rust niet meetbaar op interlands") if side else "geen kant om te benadelen"
        und = sides.check(side, avg, today=DAY) if avg else None
        und_ok, und_reason, wb = (und.passed, und.reason, und.would_block) if und else (True, "geen 1X2-gemiddelde", False)
        u9 = unders.check(c["market"], c["selection_label"], edge_pp_, "LIGHT", today=DAY)
        gates = {"odds": MIN_ODDS <= odds <= MAX_ODDS, "edge": edge_pp_ >= NEAR_LIGHT, "anticirc": True,
                 "tier": True, "tweede_methode": (p_xg > implied and p_split > implied) if p_split is not None else True,
                 "robuustheid": rob.min_edge > 0, "context": ctx_ok, "underdog": und_ok,
                 "doelpunten_onder": u9.passed}
        fg = next((g for g in GATE_ORDER if not gates[g]), None)
        out.append({"market": c["market"], "kind": k, "selection": c["selection_label"], "sel_key": c["sel_key"],
                    "line": ln, "odds": round(odds, 4), "odds_raw": c["price"],
                    "odds_source": (f"The Odds API (beste prijs, netto); {c['book']}" if rec_src == "oddsapi" else c["book"]),
                    "side": side, "my_prob": my_prob, "my_raw": my_raw, "implied": implied,
                    "p_xg": p_xg, "p_split": p_split, "edge_pp": edge_pp_, "edge_raw": edge_raw,
                    "edge_xg": model.edge_pp(p_xg, odds), "edge_split": model.edge_pp(p_split, odds) if p_split is not None else None,
                    "edge_robust_min": rob.min_edge, "edge_robust_max": rob.max_edge, "poorten": gates,
                    "context_reason": ctx_reason, "underdog_reason": und_reason, "would_block_underdog": wb,
                    "poort9_reason": u9.reason, "failed_gate": fg,
                    "score": model.selection_score(edge_pp_, my_prob, "LIGHT") if fg is None else None,
                    "score_ruw": model.selection_score(edge_raw, my_raw, "LIGHT"),
                    "poort5": "gemeten" if p_split is not None else "niet gemeten — selectiewaarde ontbreekt"})
    return out

def btts_cands(ev):
    best = {}
    for bm in (ev or {}).get("bookmakers", []):
        for mk in bm.get("markets", []):
            if mk["key"] != "btts": continue
            for oc in mk["outcomes"]:
                net = oddsapi.net_price(oc["price"], bm.get("title"))
                if oc["name"] not in best or net > best[oc["name"]][0]:
                    best[oc["name"]] = (net, oc["price"], bm.get("title"))
    out = []
    for name, side in (("Yes", "yes"), ("No", "no")):
        if name in best:
            net, price, book = best[name]
            out.append({"market": "BTTS", "kind": "btts", "side": side, "line": None, "sel_key": f"btts_{side}",
                        "price": price, "net": net, "book": book, "selection_label": f"BTTS {'Ja' if side=='yes' else 'Nee'}"})
    return out

results, btts_targets = {}, []
for comp, ms in runlist.items():
    res = []
    for m in ms:
        hid, aid = str(m["home_id"]), str(m["away_id"])
        rec = {k: m[k] for k in ("competition", "match_id", "home", "away", "kickoff_utc", "kickoff_nl", "source_day")}
        rec.update(match=f"{m['home']} – {m['away']}", home_id=int(hid), away_id=int(aid), group=m["group"])
        ok_h, nh = national.in_range(hid, nf); ok_a, na = national.in_range(aid, nf)
        if not (ok_h and ok_a):
            rec.update(tier="NONE", data_reason="; ".join(x for x, ok in ((nh, ok_h), (na, ok_a)) if not ok))
            res.append(rec); continue
        rec["tier"] = "LIGHT"
        ev = find_event(m) if "UEFA Nations League" in comp else None
        bxh = None if ev else find_bx(comp, m)
        if not ev and not bxh:
            rec["buiten_datadekking"] = True; res.append(rec); continue
        nat_h, nat_a, nat_ctx = national.team(hid, nf), national.team(aid, nf), national.context(nf)
        probs_nat = model.analyze_match(nat_h, nat_a, nat_ctx, scale=1.0, today=DAY)
        sq_ok_h, _ = squadform.usable(hid, squads); sq_ok_a, _ = squadform.usable(aid, squads)
        probs_sq = None
        if sq_ok_h and sq_ok_a:
            probs_sq = model.analyze_match(squadform.team(hid, sf, squads), squadform.team(aid, sf, squads),
                                           squadform.context(sf), scale=1.0, today=DAY)
        inf_h, inf_a = squadform.injuries(hid, squads), squadform.injuries(aid, squads)
        p7 = inf_h.get("out_share") is not None and inf_a.get("out_share") is not None
        if ev:
            src = "oddsapi"
            cands = nl_candidates(ev, ev["home_team"], ev["away_team"], m["home"], m["away"])
            avg = avg_h2h_nl(ev, ev["home_team"], ev["away_team"])
            if ev["id"] in btts_data: cands += btts_cands(btts_data[ev["id"]])
        else:
            src = "betexplorer"
            cands = bx_candidates(bxh[0], m["home"], m["away"], bxh[1]); avg = list(bxh[0])
        P = (nat_h, nat_a, nat_ctx, probs_nat, probs_sq, p7)
        scored = score_cands(cands, P, (inf_h, inf_a), avg, src)
        dv = sides.devig(avg) if avg else None
        rec.update(poort5_niet_gemeten=probs_sq is None, odds_source_kind=src,
                   odds_event_id=ev["id"] if ev else None, avg_odds_1x2=avg, all_candidates=scored,
                   lambdas=[probs_nat.lambda_home, probs_nat.lambda_away] if hasattr(probs_nat, "lambda_home") else None,
                   context={"poort7_bron": "squadform", "poort7_meetbaar": p7, "poort7_rust_meetbaar": False,
                            "home": {**inf_h, "name": m["home"], "out_names": inf_h.get("names", []), "squad_usable": sq_ok_h},
                            "away": {**inf_a, "name": m["away"], "out_names": inf_a.get("names", []), "squad_usable": sq_ok_a}},
                   landenrating={"home": f"{m['home']}: {nat_h.matches_played:.1f} gewogen duels",
                                 "away": f"{m['away']}: {nat_a.matches_played:.1f} gewogen duels"},
                   calibration={"market": list(dv) if dv else None,
                                "p_xg": [probs_nat.home, probs_nat.draw, probs_nat.away], "p_xg_label": "landenrating (national.py)",
                                "p_split": [probs_sq.home, probs_sq.draw, probs_sq.away] if probs_sq else None,
                                "p_split_label": "selectiewaarde (squadform.py)"})
        if ev:
            ce = max(s["edge_pp"] for s in scored) >= NEAR_LIGHT or max(s["edge_raw"] for s in scored) >= 16.0
            rec["kandidaat_edge_voor_btts"] = ce
            if ce: btts_targets.append(ev["id"])
        res.append(rec)
    results[comp] = res
json.dump(results, open("tmp-run/rc_nov12_pass.json", "w"), indent=1, ensure_ascii=False)
json.dump(btts_targets, open("tmp-run/rc_nov12_btts_targets.json", "w"))
for comp, rs in results.items():
    for r in rs:
        if r["tier"] == "NONE": print(f"{r['match']:38s} NONE  {r['data_reason']}"); continue
        if r.get("buiten_datadekking"): print(f"{r['match']:38s} BUITEN DATADEKKING"); continue
        c = r["calibration"]; best = max(r["all_candidates"], key=lambda x: x["edge_pp"])
        q = [x for x in r["all_candidates"] if all(v for k, v in x["poorten"].items() if k != "edge") and x["edge_pp"] >= NEAR_LIGHT]
        print(f"{r['match']:38s} p5={'-' if r['poort5_niet_gemeten'] else 'ok'} mod={[round(x*100,1) for x in c['p_xg']]} mkt={[round(x*100,1) for x in c['market']] if c['market'] else None} "
              f"best={best['selection']}@{best['odds']:.2f} {best['edge_pp']:+.2f} fg={best['failed_gate']} | pub-kand={len(q)}")
print("BTTS targets:", btts_targets)
