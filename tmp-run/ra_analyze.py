"""Stage 5 — analyse Run A 1 sep 2026. Beide methodes, alle zes markten, zeven poorten."""
import json, sys
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import fotmob, model, calibration, oddsapi, promotion, understat
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           edge_pp, asian_prob, dnb_prob, totals_prob, robustness_check,
                           selection_score, early_season_uplift, scale_level, splits_from_fotmob)
from ra_names import resolve, best_pair

DAY = date(2026, 9, 1)
NL = timezone(timedelta(hours=2))
THRESH = {"FULL": 8.0, "LIGHT": 16.0}   # verhoogd 31 aug 2026, zie _shared-rules.md §0
# Vanaf welke edge een afgewezen kandidaat nog een `near_miss` krijgt (en dus in shadow.jsonl
# belandt). Dit is met opzet de OUDE drempel: zonder deze ondergrens verdwijnt precies de groep
# die door de verhoging van vandaag wegvalt uit het schaduwlogboek, en is over een maand niet te
# meten of die verhoging geld bespaarde of alleen bets kostte.
NEAR = {"FULL": 3.0, "LIGHT": 6.0}
MIN_ODDS, MAX_ODDS = 1.30, 6.00

# Een bekercompetitie heeft zelf geen stand en dus geen divisie erboven of eronder. De ploegen
# komen wél uit een divisie: dit is de competitie waarvan de basis (niveau, splits) is genomen in
# ra_stage3.py, en dus ook de competitie waarop `promotion.TIER1/TIER2` moet worden opgezocht.
PROMO_COMP = {
    "Coppa Italia (ITA)": "Serie A (ITA)",
    "DFB Pokal (GER)":    "Bundesliga (GER)",
    "KNVB Beker (NED)":   "Eredivisie (NED)",
    "FA Cup (ENG)":       "Premier League (ENG)",
    "League Cup (ENG)":   "Premier League (ENG)",
}

cands = json.load(open("tmp-run/ra_ctx.json"))
s3 = json.load(open("tmp-run/ra_stage3.json"))
stats_meta, us_meta = s3["stats"], s3["understat"]
odds = json.load(open("tmp-run/ra_odds.json"))

# ---------- vroeg-seizoenscorrectie (§3 Stage 5) -------------------------------------------
obs, obs_comps = [], []
for comp, s in stats_meta.items():
    p, c = s["prev"], s["cur"]
    if p.get("has_xg") and c.get("has_xg") and p.get("avg_xg") and c.get("avg_xg") and c.get("played"):
        obs.append((p["avg_xg"], c["avg_xg"], c["played"])); obs_comps.append(comp)
FACTOR, POOLED, TOTAL_MD = early_season_uplift(obs)
print(f"vroeg seizoen: factor {FACTOR:.4f} (gepoold {POOLED:.4f} over {TOTAL_MD} speeldagen, "
      f"{len(obs)} competities)")

# ---------- competitiebasis ------------------------------------------------------------------
league_cache = {}
def league_ctx(comp, pid, season):
    if comp not in league_cache:
        st = fotmob.fetch_league_stats(pid, season)
        lg = LeagueContext(home_goals_per_match=st["home_goals_per_match"],
                           away_goals_per_match=st["away_goals_per_match"],
                           avg_xg_per_match=st["avg_xg_per_match"])
        league_cache[comp] = (scale_level(lg, FACTOR), st["teams"], st)
    return league_cache[comp]

# ---------- Understat, tweede xG-model (§4) ---------------------------------------------------
us_cache = {}
def understat_pair(comp, code, season, home, away, lg_fotmob):
    """(TeamStats, TeamStats, LeagueContext) op Understat-schaal, of None."""
    if not code:
        return None
    if comp not in us_cache:
        try:
            d = understat.fetch_league(code, understat.season_code(season))
            t = understat.team_stats(d)
            c = understat.league_context(t)
            us_cache[comp] = (t, LeagueContext(home_goals_per_match=c["home_goals_per_match"],
                                               away_goals_per_match=c["away_goals_per_match"],
                                               avg_xg_per_match=c["avg_xg_per_match"]), d)
        except Exception as e:
            us_cache[comp] = None
            print(f"  understat {comp}: {type(e).__name__}: {e}")
    if not us_cache[comp]:
        return None
    teams, uctx, raw = us_cache[comp]
    rh, ra = resolve(home, teams), resolve(away, teams)
    if not (rh and ra):
        return None
    # normaliseren op het EIGEN competitiegemiddelde van Understat (§4), daarna op het niveau
    # dat de run gebruikt: alleen de sterkteverhouding komt van Understat, niet het niveau.
    uctx_scaled = scale_level(uctx, FACTOR)
    hs = TeamStats(xg=teams[rh]["xg"], xga=teams[rh]["xga"], matches_played=teams[rh]["mp"])
    as_ = TeamStats(xg=teams[ra]["xg"], xga=teams[ra]["xga"], matches_played=teams[ra]["mp"])
    roll = {"home": understat.rolling_xg(raw, rh, 8), "away": understat.rolling_xg(raw, ra, 8)}
    return hs, as_, uctx_scaled, rh, ra, roll

# ---------- prijzen terugvinden ---------------------------------------------------------------
def find_1x2(comp, home, away):
    rows = odds["fixtures"].get(comp) or []
    pool = [r for r in rows if r["is_today"]] or rows
    for r in pool:
        if resolve(home, {r["home"]: 1}) and resolve(away, {r["away"]: 1}):
            return r
    return best_pair(home, away, pool, lambda r: r["home"], lambda r: r["away"])

def find_event(comp, kind, home, away):
    evs = (odds["raw"].get(kind) or {}).get(comp) or []
    for e in evs:
        if resolve(home, {e["home_team"]: 1}) and resolve(away, {e["away_team"]: 1}):
            return e
    return best_pair(home, away, evs, lambda e: e["home_team"], lambda e: e["away_team"])

def side_of(outcome, home, away):
    if resolve(outcome, {home: 1}): return "home"
    if resolve(outcome, {away: 1}): return "away"
    return None

def best_btts(match_id):
    evs = odds["raw"]["btts"].get(str(match_id)) or []
    ev = evs if isinstance(evs, dict) else (evs[0] if evs else None)
    if not ev: return {}
    best = {}
    for b in ev.get("bookmakers", []):
        for m in b.get("markets", []):
            if m.get("key") != "btts": continue
            for o in m.get("outcomes", []):
                n = o["name"].lower()
                if n not in best or o["price"] > best[n][0]:
                    best[n] = (o["price"], b["title"])
    return best

# ---------- Stage 4: rangschikken en afkappen --------------------------------------------------
from scripts.ranking import sort_key, max_deep_analyses
CAP = max_deep_analyses(DAY)

def markets_available(c):
    n = 0
    if find_1x2(c["competition"], c["home"], c["away"]): n += 1
    if c["competition"] in odds["bought"]["spreads"] and find_event(c["competition"], "spreads", c["home"], c["away"]): n += 3
    if c["competition"] in odds["bought"]["totals"] and find_event(c["competition"], "totals", c["home"], c["away"]): n += 1
    if best_btts(c["match_id"]): n += 1
    return n

ranked = [c for c in cands if c["tier"] != "NONE"]
for c in ranked:
    c["markets"] = markets_available(c)
ranked.sort(key=lambda c: sort_key("FULL" if c["tier"] == "FULL" else "LIGHT",
                                   c["richness"], c["markets"], c["kickoff_utc"]))
keep = {id(c) for c in ranked[:CAP]}
trunc = ranked[CAP:]
TRUNC = {"cap": CAP, "afgekapt": len(trunc),
         "laagste_die_het_haalde": (None if len(ranked) < CAP else
             {"match": f"{ranked[CAP-1]['home']} – {ranked[CAP-1]['away']}",
              "richness": ranked[CAP-1]["richness"], "markets": ranked[CAP-1]["markets"]}),
         "hoogste_die_afviel": ({"match": f"{trunc[0]['home']} – {trunc[0]['away']}",
              "richness": trunc[0]["richness"], "markets": trunc[0]["markets"]} if trunc else None),
         "lijst": [f"{c['home']} – {c['away']}" for c in trunc],
         "laagste_richness_in_run": min(c["richness"] for c in ranked) if ranked else None,
         "hoogste_richness_in_run": max(c["richness"] for c in ranked) if ranked else None}
print("afkapping:", json.dumps(TRUNC, ensure_ascii=False))

# ---------- analyse ----------------------------------------------------------------------------
results = []
for c in cands:
    ko = datetime.fromisoformat(c["kickoff_utc"].replace("Z", "+00:00"))
    row = {"competition": c["competition"], "match": f"{c['home']} – {c['away']}",
           "match_id": c["match_id"], "home": c["home"], "away": c["away"],
           "kickoff_utc": c["kickoff_utc"], "kickoff_nl": ko.astimezone(NL).strftime("%H:%M"),
           "richness": c["richness"], "richness_parts": c.get("richness_parts"),
           "markets": c.get("markets"), "bet": False, "all_candidates": [], "markets_checked": {}}

    lg, teams, st = league_ctx(c["competition"], c["primaryId"], c["season"])

    # --- teamsterktes: uit de stand, of omgerekend uit de divisie eronder (promovendi) dan wel
    #     erboven (degradanten). Beide richtingen zijn §4; de tweede kan sinds 1 sep 2026. ---
    promo_notes, tier_box = {}, [c["tier"]]

    def _source_name(name, fotmob_id, season):
        """De naam zoals de brontabel hem schrijft, of de originele als hij er niet in staat."""
        try:
            tbl = fotmob.fetch_league_stats(fotmob_id, season)["teams"]
        except Exception:
            return name
        return resolve(name, tbl) or name

    def side_stats(name, table_key):
        if table_key:
            r = teams[table_key]
            return TeamStats(xg=r["xg"], xga=r["xga"], matches_played=r["mp"]), splits_from_fotmob(r), None
        errors = []
        pcomp = PROMO_COMP.get(c["competition"], c["competition"])
        t2 = promotion.TIER2.get(pcomp)
        if t2:
            try:
                conv = promotion.convert(pcomp, _source_name(name, t2.fotmob_id, c["season"]),
                                         c["season"], lg)
                tier_box[0] = "NONE" if not conv.in_range else "LIGHT"
                return conv.stats, conv.splits, conv.note
            except promotion.PromotionError as e:
                errors.append(f"promovendus: {e}")
        t1 = promotion.TIER1.get(pcomp)
        if t1:
            try:
                conv = promotion.convert_relegated(pcomp,
                                                   _source_name(name, t1.fotmob_id, c["season"]),
                                                   c["season"], lg)
                tier_box[0] = "NONE" if not conv.in_range else "LIGHT"
                return conv.stats, conv.splits, conv.note
            except promotion.PromotionError as e:
                errors.append(f"degradant: {e}")
        raise promotion.PromotionError("; ".join(errors) or
                                       f"geen divisie boven of onder {pcomp!r} bekend")
    try:
        hs, sp_h, nh = side_stats(c["home"], c["table_home"])
        as_, sp_a, na = side_stats(c["away"], c["table_away"])
        tier = tier_box[0]
    except promotion.PromotionError as e:
        row["tier"] = "NONE"; row["reason"] = f"geen historie in deze divisie: {e}"
        results.append(row); continue
    if nh: promo_notes["thuis"] = nh
    if na: promo_notes["uit"] = na
    row["tier"] = tier
    if promo_notes: row["promovendi"] = promo_notes
    if tier == "NONE":
        row["reason"] = "omrekening buiten het gemeten bereik (conversion_in_range) — data_tier NONE"
        results.append(row); continue
    if id(c) not in keep:
        row["afgekapt"] = True
        row["reason"] = f"AFGEKAPT — buiten MAX_DEEP_ANALYSES ({CAP})"
        results.append(row); continue

    p_xg = analyze_match(hs, as_, lg)
    p_xg_ns = analyze_match(hs, as_, lg, shrink=1.0)
    p_sp = analyze_match_from_splits(sp_h, sp_a, league=lg)
    row["lambdas"] = {"xg": [round(p_xg.lambda_home, 3), round(p_xg.lambda_away, 3)],
                      "split": [round(p_sp.lambda_home, 3), round(p_sp.lambda_away, 3)]}

    # Understat als tweede, onafhankelijke xG-bron — meting voor §6e, niet voor my_prob
    up = understat_pair(c["competition"], c.get("understat"), c["season"], c["home"], c["away"], lg)
    p_us = None
    if up:
        uh, ua, uctx, urh, ura, roll = up
        p_us = analyze_match(uh, ua, uctx)
        row["understat"] = {"home": urh, "away": ura,
                            "lambdas": [round(p_us.lambda_home, 3), round(p_us.lambda_away, 3)],
                            "rolling_xg_8": {k: (None if v is None else [round(v[0], 2), round(v[1], 2), v[2]])
                                             for k, v in roll.items()}}

    gate7 = (c.get("ctx") or {}).get("gate") or {}
    row["context"] = c.get("ctx")
    ven = ((c.get("ctx") or {}).get("venue") or {})
    if ven.get("relocated"):
        row["verplaatst"] = ven

    # --- markten verzamelen ---
    sel = []
    m1 = find_1x2(c["competition"], c["home"], c["away"])
    if m1:
        o1, ox, o2 = m1["odds"]
        row["odds_1x2"] = [o1, ox, o2]
        src = f"BetExplorer ({m1['books']} boeken, marktgemiddelde; bookmaker niet herleidbaar)"
        row["markets_checked"]["1X2"] = (f"BetExplorer marktgemiddelde over {m1['books']} boeken: "
                                         f"1 @{o1}, X @{ox}, 2 @{o2}")
        sel += [("1X2", f"1 ({c['home']} wint)", o1, src, "home", lambda p: p.home),
                ("1X2", "X (gelijkspel)", ox, src, None, lambda p: p.draw),
                ("1X2", f"2 ({c['away']} wint)", o2, src, "away", lambda p: p.away)]
    else:
        row["markets_checked"]["1X2"] = "niet gevonden in de BetExplorer-fixtureslijst"

    ev_sp = find_event(c["competition"], "spreads", c["home"], c["away"])
    if ev_sp is None:
        for k in ("AH", "DNB", "DC"):
            row["markets_checked"][k] = "spreads opgehaald, maar deze wedstrijd stond niet in de respons"
    else:
        lines = oddsapi.best_by_line(ev_sp, "spreads")
        n_ah = n_dnb = n_dc = 0
        for (outcome, line), (o, book) in lines.items():
            side = side_of(outcome, c["home"], c["away"])
            if line is None or side is None: continue
            ln = float(line)
            if abs(ln) < 1e-9:
                sel.append(("Draw No Bet", f"DNB — {outcome}", o, f"The Odds API ({book})", side,
                            (lambda s, oo: (lambda p: dnb_prob(p.grid, s, oo)))(side, o))); n_dnb += 1
            elif abs(abs(ln) - 0.5) < 1e-9:
                naam = c["home"] if side == "home" else c["away"]
                if ln > 0:
                    sel.append(("Double Chance", f"Double Chance — {naam} of gelijk (AH +0.5 @ {o})", o,
                                f"The Odds API ({book})", side,
                                (lambda s, oo: (lambda p: asian_prob(p.grid, 0.5, s, oo)))(side, o))); n_dc += 1
                else:
                    sel.append(("Asian Handicap", f"{outcome} {ln:+g}", o, f"The Odds API ({book})", side,
                                (lambda s, l, oo: (lambda p: asian_prob(p.grid, l, s, oo)))(side, ln, o))); n_ah += 1
            else:
                sel.append(("Asian Handicap", f"{outcome} {ln:+g}", o, f"The Odds API ({book})", side,
                            (lambda s, l, oo: (lambda p: asian_prob(p.grid, l, s, oo)))(side, ln, o))); n_ah += 1
        row["markets_checked"]["AH"] = f"The Odds API spreads, beste prijs per lijn — {n_ah} handicaplijnen"
        row["markets_checked"]["DNB"] = (f"The Odds API spreads, 0.0-lijn — {n_dnb} selecties" if n_dnb
                                         else "geen 0.0-lijn in de spreads-respons")
        row["markets_checked"]["DC"] = (f"The Odds API spreads, +0.5-lijn — {n_dc} selecties" if n_dc
                                        else "geen +0.5-lijn in de spreads-respons")

    ev_to = find_event(c["competition"], "totals", c["home"], c["away"])
    if ev_to is None:
        row["markets_checked"]["OU"] = "totals opgehaald, maar deze wedstrijd stond niet in de respons"
    else:
        lines = oddsapi.best_by_line(ev_to, "totals")
        n = 0
        for (outcome, line), (o, book) in lines.items():
            if line is None: continue
            ln, sd = float(line), outcome.lower()
            sel.append(("Over/Under", f"{outcome} {ln:g}", o, f"The Odds API ({book})", None,
                        (lambda l, s, oo: (lambda p: totals_prob(p.grid, l, s, oo)))(ln, sd, o))); n += 1
        row["markets_checked"]["OU"] = f"The Odds API totals, beste prijs per lijn — {n} lijnen"

    bt = best_btts(c["match_id"])
    if bt:
        for naam, (o, book) in bt.items():
            ja = naam.startswith("y")
            sel.append(("BTTS", f"Beide ploegen scoren — {'ja' if ja else 'nee'}", o,
                        f"The Odds API ({book})", None,
                        (lambda j: (lambda p: p.btts if j else 1 - p.btts))(ja)))
        row["markets_checked"]["BTTS"] = f"The Odds API event-markt btts — {len(bt)} selecties"
    else:
        row["markets_checked"]["BTTS"] = "btts opgevraagd, maar geen boek noteerde deze markt"
    row["markets_checked"]["context"] = "Fotmob blessures/schorsingen + vorm + rust + stadioncontrole"

    # --- poorten ---
    thresh = THRESH[tier]
    evaluated = []
    for markt, oms, o, bron, side, f in sel:
        try:
            px, ps = f(p_xg), f(p_sp)
        except Exception:
            continue
        if not (0 < px < 1 and 0 < ps < 1):
            continue
        my = (px + ps) / 2
        e_pp, e_xg, e_sp = edge_pp(my, o), edge_pp(px, o), edge_pp(ps, o)
        gates = {"odds": MIN_ODDS <= o <= MAX_ODDS, "edge": e_pp >= thresh,
                 "tweede_methode": (px > 1 / o) and (ps > 1 / o)}
        rb = None
        if all(gates.values()):
            rb = robustness_check(hs, as_, lg, f, o)
            gates["robuustheid"] = rb.min_edge > 0
        else:
            gates["robuustheid"] = None
        g7 = gate7.get(side if side else "None") or {"passed": True, "reason": "geen kant om te benadelen"}
        gates["context"] = bool(g7["passed"])
        fail = next((k for k in ("odds", "edge", "tweede_methode", "robuustheid", "context")
                     if gates[k] is False), None)
        evaluated.append({"market": markt, "selection": oms, "odds": o, "odds_source": bron,
                          "side": side, "my_prob": round(my, 4), "implied": round(1 / o, 4),
                          "p_xg": round(px, 4), "p_split": round(ps, 4),
                          "edge_pp": round(e_pp, 2), "edge_xg": round(e_xg, 2),
                          "edge_split": round(e_sp, 2),
                          "edge_robust_min": (round(rb.min_edge, 2) if rb else None),
                          "failed_gate": fail, "context_reason": g7.get("reason", ""),
                          "score": round(selection_score(e_pp, my, tier), 3) if fail is None else None})
    row["candidates_evaluated"] = len(evaluated)
    row["all_candidates"] = sorted(evaluated, key=lambda r: -r["edge_pp"])[:14]

    passed = [r for r in evaluated if r["failed_gate"] is None]
    if passed:
        best = max(passed, key=lambda r: r["score"])
        rest = sorted([r for r in evaluated if r is not best and r["failed_gate"] is None],
                      key=lambda r: -r["score"])
        row["bet"] = True; row["pick"] = best
        row["runner_up"] = ({"selection": f"{rest[0]['market']} — {rest[0]['selection']}",
                             "score": rest[0]["score"]} if rest else None)
        # Haalde maar één selectie alle poorten, dan is "de tweede" niet leeg maar de sterkste
        # die wél afviel — met de poort erbij. Zonder dat staat er in het runrapport 'geen
        # tweede' terwijl er zes selecties waren doorgerekend (§1, laatste alinea).
        if not rest:
            others = sorted([r for r in evaluated if r is not best],
                            key=lambda r: -r["edge_pp"])
            if others:
                o0 = others[0]
                row["runner_up_rejected"] = {
                    "selection": f"{o0['market']} — {o0['selection']}",
                    "odds": o0["odds"], "edge_pp": o0["edge_pp"],
                    "failed_gate": o0["failed_gate"] or "edge"}
    else:
        near = [r for r in evaluated if r["edge_pp"] >= NEAR[tier] and MIN_ODDS <= r["odds"] <= MAX_ODDS]
        if near:
            b = max(near, key=lambda r: r["edge_pp"])
            gate = b["failed_gate"] or ("edge" if b["edge_pp"] < thresh else None)
            # §5 eist alle drie de getallen in de "Net niet"-tabel, niet alleen de poort die hem
            # afwees. `robustness_check` draait hierboven alleen voor selecties die de edge-poort
            # halen, dus voor een net-nietter is `edge_robust_min` daar per definitie leeg — en
            # dan valt precies niet te zien of het één poort was of een breed tekort. Eén extra
            # aanroep per wedstrijd, alleen voor de kandidaat die in het rapport komt.
            rmin = b["edge_robust_min"]
            if rmin is None:
                fn = next((f for markt, oms, o, bron, side, f in sel
                           if markt == b["market"] and oms == b["selection"]), None)
                if fn is not None:
                    try:
                        rmin = round(robustness_check(hs, as_, lg, fn, b["odds"]).min_edge, 2)
                    except Exception:
                        rmin = None
            row["near_miss"] = {"market": f"{b['market']} — {b['selection']}", "odds": b["odds"],
                                "edge_pp": b["edge_pp"],
                                "edge_xg": b["edge_xg"], "edge_split": b["edge_split"],
                                "edge_robust_min": rmin,
                                "failed_gate": gate}
            row["reason"] = {"edge": f"edge onder drempel ({b['edge_pp']:+.2f} pp, nodig {thresh:.1f})",
                             "odds": "odds buiten band",
                             "tweede_methode": "data conflicterend",
                             "robuustheid": "edge niet robuust over het (shrink, rho)-grid",
                             "context": f"context spreekt de bet tegen — {b['context_reason']}"}[gate]
        elif evaluated:
            row["reason"] = "edge onder drempel"
        else:
            row["reason"] = "geen prijzen gevonden voor deze wedstrijd"

    # --- kalibratie (§6e) ---
    if m1:
        cal = {"market": [round(x, 4) for x in calibration.devig(list(m1["odds"]))],
               "p_xg": [round(p_xg.home, 4), round(p_xg.draw, 4), round(p_xg.away, 4)],
               "p_xg_noshrink": [round(p_xg_ns.home, 4), round(p_xg_ns.draw, 4), round(p_xg_ns.away, 4)],
               "p_split": [round(p_sp.home, 4), round(p_sp.draw, 4), round(p_sp.away, 4)]}
        if p_us:
            cal["p_xg_understat"] = [round(p_us.home, 4), round(p_us.draw, 4), round(p_us.away, 4)]
        row["calibration"] = cal
    results.append(row)

json.dump({"vroeg_seizoen": {"factor": FACTOR, "gepoold": POOLED, "speeldagen": TOTAL_MD,
                             "competities": obs_comps},
           "afkapping": TRUNC, "matches": results},
          open("tmp-run/ra_results_v2.json", "w"), ensure_ascii=False, indent=1)

for r in results:
    tag = "BET " if r["bet"] else "    "
    extra = (f"{r['pick']['market']} {r['pick']['selection']} @{r['pick']['odds']} "
             f"edge {r['pick']['edge_pp']:+.1f} score {r['pick']['score']}") if r["bet"] else r.get("reason", "")
    print(f"{tag}{r['tier']:5s} {r['match'][:38]:38s} n={r.get('candidates_evaluated', 0):3d}  {extra}")
print("\nBETS:", sum(r["bet"] for r in results))
