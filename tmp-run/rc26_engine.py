"""Kernfuncties voor Run C, 26 sep 2026 — hergebruikt uit tmp-run/c25_engine.py (25 sep)."""
import sys
sys.path.insert(0, '.')
from scripts import national, squadform, model, sides, oddsapi

WEIGHT_NAT = 0.70   # run-c.md: 0.70 landenrating / 0.30 selectiewaarde
NEAR_LIGHT = 6.0
EDGE_THRESHOLD_LIGHT_RAW = 16.0
MIN_ODDS, MAX_ODDS = 1.30, 6.00


def nat_stats_ctx(nf, home_id, away_id):
    h = national.team(home_id, nf)
    a = national.team(away_id, nf)
    ctx = national.context(nf)
    return h, a, ctx


def sq_stats_ctx(sf, squads, home_id, away_id):
    h = squadform.team(home_id, sf, squads)
    a = squadform.team(away_id, sf, squads)
    ctx = squadform.context(sf)
    return h, a, ctx


def value_1x2(probs, sel_key):
    return {"home": probs.home, "draw": probs.draw, "away": probs.away}[sel_key]


def value_selector(probs, grid, kind, side, line, odds):
    if kind == "1x2":
        return value_1x2(probs, side)
    if kind == "dnb":
        return model.dnb_prob(grid, side, odds)
    if kind == "ah":
        return model.asian_prob(grid, line, side, odds)
    if kind == "dc":
        return model.asian_prob(grid, 0.5, side, odds)
    if kind == "ou":
        return model.totals_prob(grid, line, side, odds)
    if kind == "btts":
        return probs.btts if side == "yes" else (1 - probs.btts)
    raise ValueError(kind)


def robustness_for(nat_h, nat_a, nat_ctx, kind, side, line, odds):
    def select(p):
        if kind == "1x2":
            return value_1x2(p, side)
        if kind in ("dnb", "ah", "dc", "ou"):
            g = p.grid
            if kind == "dnb":
                return model.dnb_prob(g, side, odds)
            if kind == "ah":
                return model.asian_prob(g, line, side, odds)
            if kind == "dc":
                return model.asian_prob(g, 0.5, side, odds)
            if kind == "ou":
                return model.totals_prob(g, line, side, odds)
        if kind == "btts":
            return p.btts if side == "yes" else (1 - p.btts)
        raise ValueError(kind)
    return model.robustness_check(nat_h, nat_a, nat_ctx, select, odds)


def nl_candidates(event, home_name, away_name, disp_home=None, disp_away=None):
    """Marktkandidaten uit één Odds-API event: 1X2, DNB, DC, AH, OU (geen BTTS).

    `home_name`/`away_name` = de namen ZOALS The Odds API ze teruggeeft — matchen gaat daarop,
    niet op Fotmob-namen (die wijken soms af: Czechia/Czech Republic, Turkiye/Turkey).
    `disp_home`/`disp_away` zijn de Fotmob-namen, voor het leesbare label.
    """
    disp_home = disp_home or home_name
    disp_away = disp_away or away_name
    out = []
    h2h = oddsapi.best_by_line(event, "h2h")
    for name, sel_key in ((home_name, "home"), ("Draw", "draw"), (away_name, "away")):
        hit = h2h.get((name, None))
        if hit:
            price, book = hit
            net = oddsapi.net_price(price, book)
            out.append({"market": "1X2", "kind": "1x2", "side": sel_key, "line": None,
                        "sel_key": sel_key, "price": price, "net": net, "book": book,
                        "selection_label": {"home": f"1 ({disp_home} wint)", "draw": "X (gelijkspel)",
                                            "away": f"2 ({disp_away} wint)"}[sel_key]})
    spreads = oddsapi.best_by_line(event, "spreads")
    for (name, pt), (price, book) in spreads.items():
        if pt is None:
            continue
        side = "home" if name == home_name else ("away" if name == away_name else None)
        if side is None:
            continue
        net = oddsapi.net_price(price, book)
        team = disp_home if side == "home" else disp_away
        if abs(pt) < 1e-9:
            market, kind = "Draw No Bet", "dnb"
            label = f"Draw No Bet +0 — {team}"
        elif abs(abs(pt) - 0.5) < 1e-9 and pt > 0:
            market, kind = "Double Chance", "dc"
            label = (f"Double Chance 1X ({disp_home} or Draw)" if side == "home"
                     else f"Double Chance X2 ({disp_away} or Draw)")
        else:
            market, kind = "Asian Handicap", "ah"
            sign = "+" if pt > 0 else ""
            label = f"Asian Handicap {sign}{pt:g} — {team}"
        out.append({"market": market, "kind": kind, "side": side, "line": pt,
                    "sel_key": f"ah_{side}_{pt}", "price": price, "net": net, "book": book,
                    "selection_label": label})
    totals = oddsapi.best_by_line(event, "totals")
    for (name, pt), (price, book) in totals.items():
        if pt is None or name not in ("Over", "Under"):
            continue
        side = "over" if name == "Over" else "under"
        net = oddsapi.net_price(price, book)
        out.append({"market": "Over/Under", "kind": "ou", "side": side, "line": pt,
                    "sel_key": f"ou_{side}_{pt}", "price": price, "net": net, "book": book,
                    "selection_label": f"{name} {pt:g}"})
    return out


def bx_candidates(row_odds, home_name, away_name, n_books):
    o1, ox, o2 = row_odds
    src = f"BetExplorer marktgemiddelde ({n_books} boeken)"
    return [
        {"market": "1X2", "kind": "1x2", "side": "home", "line": None, "sel_key": "home",
         "price": o1, "net": o1, "book": src,
         "selection_label": f"1 ({home_name} wint)"},
        {"market": "1X2", "kind": "1x2", "side": "draw", "line": None, "sel_key": "draw",
         "price": ox, "net": ox, "book": src,
         "selection_label": "X (gelijkspel)"},
        {"market": "1X2", "kind": "1x2", "side": "away", "line": None, "sel_key": "away",
         "price": o2, "net": o2, "book": src,
         "selection_label": f"2 ({away_name} wint)"},
    ]


def avg_h2h_nl(event, home_name, away_name):
    """Ongewogen marktgemiddelde 1X2 over alle boeken (voor poort 8 en het kalibratieblok)."""
    sums = {"home": 0.0, "draw": 0.0, "away": 0.0}
    n = {"home": 0, "draw": 0, "away": 0}
    for bm in event.get("bookmakers", []):
        for mk in bm.get("markets", []):
            if mk["key"] != "h2h":
                continue
            for oc in mk["outcomes"]:
                if oc["name"] == home_name:
                    k = "home"
                elif oc["name"] == away_name:
                    k = "away"
                elif oc["name"] == "Draw":
                    k = "draw"
                else:
                    continue
                sums[k] += oc["price"]
                n[k] += 1
    if not all(n.values()):
        return None
    return [sums["home"] / n["home"], sums["draw"] / n["draw"], sums["away"] / n["away"]]


def context_gate(side, out_share_home, out_share_away, meetbaar):
    if side not in ("home", "away"):
        return True, "geen kant om te benadelen"
    if not meetbaar or out_share_home is None or out_share_away is None:
        return True, "niet meetbaar (selectie te dun) — poort open"
    diff = (out_share_home - out_share_away) if side == "home" else (out_share_away - out_share_home)
    mine = out_share_home if side == "home" else out_share_away
    theirs = out_share_away if side == "home" else out_share_home
    label = "geen materieel nadeel"
    passed = True
    if diff >= 0.10:
        passed = False
        label = "dicht — mist ≥10 pp meer selectiewaarde dan de tegenstander"
    reason = (f"gemeten (poort7_bron=squadform): {mine:.1%} vs {theirs:.1%} - {label}; "
              f"rust niet meetbaar op interlands")
    return passed, reason
