"""Wat de zes Champions League-duels van 8 sep 2026 doen door alle acht poorten van §1.

Zelfde keten als ra8_analyze.py, maar met `interleague.convert_team` in plaats van de
kruis-grens-uitzondering. Tier is LIGHT (een omgerekende ploeg is nooit FULL), dus de drempel is
EDGE_THRESHOLD_LIGHT = 16.0 procentpunt op de HERIJKTE kans.
"""
import json, sys
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts import interleague as il, oddsapi, recalibrate, sides
from scripts.model import (analyze_match, analyze_match_from_splits, asian_prob, combine_probs,
                           dnb_prob, edge_pp, robustness_check, selection_score, totals_prob)

THRESH, MIN_ODDS, MAX_ODDS = 16.0, 1.30, 6.00
FIT = recalibrate.load_fit()
LG = il.reference_league()
odds = json.load(open("tmp-run/ra8_odds.json"))["raw"]
UCL = [m for m in json.load(open("tmp-run/ra8_cands.json"))
       if m["competition"] == "UEFA Champions League"]
print(f"herijking: {FIT}\ndrempel LIGHT: {THRESH} pp\n")


def event(kind, home, away):
    for ev in (odds.get(kind) or {}).get("UEFA Champions League") or []:
        h = home.split()[0].lower() in ev["home_team"].lower() or ev["home_team"].split()[0].lower() in home.lower()
        a = away.split()[0].lower() in ev["away_team"].lower() or ev["away_team"].split()[0].lower() in away.lower()
        if h and a:
            return ev
    return None


def side_of(outcome, home, away, ev):
    if outcome.lower() in ev["home_team"].lower():
        return "home"
    if outcome.lower() in ev["away_team"].lower():
        return "away"
    return None


rows = []
for m in UCL:
    name = f"{m['home']} – {m['away']}"
    try:
        ch = il.convert_team(m["home_id"], m["home"], "2025/2026")
        ca = il.convert_team(m["away_id"], m["away"], "2025/2026")
    except il.InterLeagueError as exc:
        print(f"{name:34s} NONE — {exc}")
        continue
    if not (ch.in_range and ca.in_range):
        print(f"{name:34s} NONE — omrekening buiten het gemeten bereik")
        continue

    p_xg = analyze_match(ch.stats, ca.stats, LG)
    p_sp = analyze_match_from_splits(ch.splits, ca.splits, league=LG)

    sel = []
    ev = event("h2h", m["home"], m["away"])
    odds_1x2 = None
    if ev:
        best = oddsapi.best_by_line(ev, "h2h")
        trio = {}
        for (outcome, _), (price, book) in best.items():
            net = oddsapi.net_price(price, book)
            if outcome.lower() in ("draw", "gelijkspel"):
                trio["X"] = price
                sel.append(("1X2", "X (gelijkspel)", net, book, None, lambda p: p.draw))
            else:
                s = side_of(outcome, m["home"], m["away"], ev)
                if not s:
                    continue
                trio["1" if s == "home" else "2"] = price
                sel.append(("1X2", f"{'1' if s=='home' else '2'} ({outcome} wint)", net, book, s,
                            (lambda ss: (lambda p: p.home if ss == "home" else p.away))(s)))
        if len(trio) == 3:
            odds_1x2 = [trio["1"], trio["X"], trio["2"]]
    ev_sp = event("spreads", m["home"], m["away"])
    if ev_sp:
        for (outcome, line), (price, book) in oddsapi.best_by_line(ev_sp, "spreads").items():
            s = side_of(outcome, m["home"], m["away"], ev_sp)
            if line is None or s is None:
                continue
            ln = float(line)
            sel.append(("Asian Handicap" if abs(ln) > 1e-9 else "Draw No Bet",
                        f"{outcome} {ln:+g}", price, book, s,
                        (lambda ss, ll, oo: (lambda p: asian_prob(p.grid, ll, ss, oo)))(s, ln, price)))
    ev_to = event("totals", m["home"], m["away"])
    if ev_to:
        for (outcome, line), (price, book) in oddsapi.best_by_line(ev_to, "totals").items():
            if line is None:
                continue
            sel.append(("Over/Under", f"{outcome} {float(line):g}", price, book, None,
                        (lambda ll, oo, pr: (lambda p: totals_prob(p.grid, ll, oo, pr)))(
                            float(line), outcome.lower(), price)))

    best_row = None
    for markt, oms, o, book, s, fn in sel:
        try:
            px, ps = fn(p_xg), fn(p_sp)
        except Exception:
            continue
        if not (0 < px < 1 and 0 < ps < 1):
            continue
        my_raw = combine_probs(px, ps)
        my = recalibrate.apply(my_raw, FIT)
        e = edge_pp(my, o)
        gates = {"odds": MIN_ODDS <= o <= MAX_ODDS,
                 "edge": e >= THRESH,
                 "tweede_methode": px > 1 / o and ps > 1 / o,
                 "underdog": sides.check(s, odds_1x2).passed}
        rb = None
        if all(gates.values()):
            rb = robustness_check(ch.stats, ca.stats, LG, fn, o)
            gates["robuustheid"] = rb.min_edge > 0
        failed = next((k for k in ("odds", "edge", "tweede_methode", "robuustheid", "underdog")
                       if gates.get(k) is False), None)
        cand = {"markt": markt, "sel": oms, "odds": o, "book": book, "my": my, "raw": my_raw,
                "edge": e, "edge_raw": edge_pp(my_raw, o), "failed": failed,
                "score": selection_score(e, my, "LIGHT")}
        if best_row is None or cand["edge"] > best_row["edge"]:
            best_row = cand
        rows.append({**cand, "match": name})
    if best_row:
        print(f"{name:34s} LIGHT  beste: {best_row['markt']} {best_row['sel'][:26]:26s} "
              f"@{best_row['odds']:5.2f}  edge {best_row['edge']:+6.2f} (ruw {best_row['edge_raw']:+6.2f})"
              f"  valt af op {best_row['failed']}")

qual = [r for r in rows if r["failed"] is None]
print(f"\ndoorgerekende selecties: {len(rows)}")
print(f"selecties die ALLE poorten halen op de herijkte kans: {len(qual)}")
for r in sorted(qual, key=lambda r: -r["score"]):
    print(f"   BET {r['match']}: {r['markt']} {r['sel']} @{r['odds']} edge {r['edge']:+.2f} score {r['score']:.3f}")
raw_only = [r for r in rows if r["failed"] == "edge" and r["edge_raw"] >= THRESH]
print(f"selecties die het ZONDER de herijking wel zouden halen: {len(raw_only)}")
for r in sorted(raw_only, key=lambda r: -r["edge_raw"])[:5]:
    print(f"   {r['match']}: {r['markt']} {r['sel']} @{r['odds']} ruw {r['edge_raw']:+.2f} herijkt {r['edge']:+.2f}")
