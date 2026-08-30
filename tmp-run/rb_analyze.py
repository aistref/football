"""Stage 5 — analyse. Beide methodes, alle beschikbare markten, zeven poorten."""
import json, sys, math
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import fotmob, model, context as ctxmod, calibration, oddsapi
from scripts.model import (TeamStats, LeagueContext, TeamSplits, analyze_match,
                           analyze_match_from_splits, edge_pp, asian_prob, dnb_prob,
                           totals_prob, robustness_check, selection_score, early_season_uplift,
                           scale_level, league_context_from_table, splits_from_fotmob)
from rb_names import resolve, norm, best_pair, side_of

DAY = date(2026, 8, 30)
NL = timezone(timedelta(hours=2))
THRESH = {"FULL": 3.0, "LIGHT": 6.0}
MIN_ODDS, MAX_ODDS = 1.30, 6.00
CURRENT_BASE = {"Eliteserien (NOR)", "Allsvenskan (SWE)"}

cands = json.load(open("tmp-run/rb_ctx.json"))
stats_meta = json.load(open("tmp-run/rb_stats.json"))
odds = json.load(open("tmp-run/rb_odds.json"))

# ---------- vroeg-seizoenscorrectie (§3 Stage 5) -------------------------------------------
obs, obs_comps = [], []
for comp, s in stats_meta.items():
    if comp in CURRENT_BASE:
        continue
    p, c = s.get("prev", {}), s.get("cur", {})
    if p.get("has_xg") and c.get("has_xg") and p.get("avg_xg") and c.get("avg_xg") and c.get("played"):
        obs.append((p["avg_xg"], c["avg_xg"], c["played"])); obs_comps.append(comp)
FACTOR, POOLED, TOTAL_MD = early_season_uplift(obs)
print(f"vroeg seizoen: factor {FACTOR:.4f} (gepoold {POOLED:.4f} over {TOTAL_MD} speeldagen, "
      f"{len(obs)} competities)")

# ---------- competitiebasis per competitie ---------------------------------------------------
league_cache = {}
def league_ctx(comp, pid, season, tier):
    if comp in league_cache:
        return league_cache[comp]
    st = fotmob.fetch_league_stats(pid, season)
    teams = st["teams"]
    if tier == "FULL":
        lg = LeagueContext(home_goals_per_match=st["home_goals_per_match"],
                           away_goals_per_match=st["away_goals_per_match"],
                           avg_xg_per_match=st["avg_xg_per_match"])
    else:   # geen xG bij Fotmob -> doelpunten als sterktemaat (LIGHT)
        played = sum(t.get("played", 0) for t in teams.values())
        goals = sum(t.get("gf", 0) for t in teams.values())
        lg = LeagueContext(home_goals_per_match=st["home_goals_per_match"],
                           away_goals_per_match=st["away_goals_per_match"],
                           avg_xg_per_match=goals / played if played else 1.35)
    if comp not in CURRENT_BASE:
        lg = scale_level(lg, FACTOR)
    league_cache[comp] = (lg, teams, st)
    return league_cache[comp]

def team_stats(row, tier):
    if tier == "FULL" and "xg" in row:
        return TeamStats(xg=row["xg"], xga=row["xga"], matches_played=row["mp"])
    return TeamStats(xg=row["gf"], xga=row["ga"], matches_played=row["played"])

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

# ---------- Stage 4: rangschikken en afkappen ---------------------------------------------------
from scripts.ranking import sort_key, max_deep_analyses
CAP = max_deep_analyses(DAY)

def markets_available(c):
    n = 0
    if find_1x2(c["competition"], c["home"], c["away"]):
        n += 1
    if c["competition"] in odds["bought"]["spreads"] and find_event(c["competition"], "spreads", c["home"], c["away"]):
        n += 3                                    # AH + DNB (0.0) + DC (±0.5), één credit
    if c["competition"] in odds["bought"]["totals"] and find_event(c["competition"], "totals", c["home"], c["away"]):
        n += 1
    return n

ranked = [c for c in cands if c["tier"] != "NONE"]
for c in ranked:
    c["markets"] = markets_available(c)
ranked.sort(key=lambda c: sort_key(c["tier"], c["richness"], c["markets"], c["kickoff_utc"]))
keep = {id(c) for c in ranked[:CAP]}
truncated = ranked[CAP:]
TRUNC = {"cap": CAP, "afgekapt": len(truncated),
         "laagste_die_het_haalde": (None if len(ranked) < CAP else
             {"match": f"{ranked[CAP-1]['home']} – {ranked[CAP-1]['away']}", "tier": ranked[CAP-1]["tier"],
              "richness": ranked[CAP-1]["richness"], "markets": ranked[CAP-1]["markets"]}),
         "hoogste_die_afviel": ({"match": f"{truncated[0]['home']} – {truncated[0]['away']}",
              "tier": truncated[0]["tier"], "richness": truncated[0]["richness"],
              "markets": truncated[0]["markets"]} if truncated else None),
         "lijst": [f"{c['home']} – {c['away']} ({c['competition']}, {c['tier']}, "
                   f"datarijkdom {c['richness']}, {c['markets']} markten)" for c in truncated]}
print("afkapping:", json.dumps(TRUNC, ensure_ascii=False, indent=1))

# ---------- analyse ----------------------------------------------------------------------------
results = []
for c in cands:
    row = {"competition": c["competition"], "match": f"{c['home']} – {c['away']}",
           "match_id": c["match_id"], "home": c["home"], "away": c["away"],
           "tier": c["tier"], "kickoff_utc": c["kickoff_utc"],
           "kickoff_nl": datetime.fromisoformat(c["kickoff_utc"].replace("Z", "+00:00")).astimezone(NL).strftime("%H:%M"),
           "richness": c["richness"], "richness_parts": c.get("richness_parts"),
           "bet": False, "all_candidates": [], "markets_checked": {}}
    if c["tier"] == "NONE":
        row["reason"] = f"geen historie in deze divisie voor {', '.join(c['missing'])} (kruis-divisie) — data_tier NONE"
        results.append(row); continue
    if id(c) not in keep:
        row["afgekapt"] = True
        row["markets"] = c.get("markets")
        row["reason"] = (f"AFGEKAPT — buiten MAX_DEEP_ANALYSES ({CAP}); datarijkdom {c['richness']}/10 "
                         f"bij {c.get('markets')} beschikbare markten")
        results.append(row); continue

    lg, teams, st = league_ctx(c["competition"], c["primaryId"], c["season"], c["tier"])
    hrow, arow = teams[c["table_home"]], teams[c["table_away"]]
    hs, as_ = team_stats(hrow, c["tier"]), team_stats(arow, c["tier"])
    p_xg = analyze_match(hs, as_, lg)
    p_xg_ns = analyze_match(hs, as_, lg, shrink=1.0)
    sp_h, sp_a = splits_from_fotmob(hrow), splits_from_fotmob(arow)
    p_sp = analyze_match_from_splits(sp_h, sp_a, league=lg)
    row["lambdas"] = {"xg": [round(p_xg.lambda_home, 3), round(p_xg.lambda_away, 3)],
                      "split": [round(p_sp.lambda_home, 3), round(p_sp.lambda_away, 3)]}

    gate7 = (c.get("ctx") or {}).get("gate") or {}
    row["context"] = c.get("ctx")

    # --- markten verzamelen ---
    sel = []      # (markt, omschrijving, odds, bron, side, f_xg, f_split, f_probs_for_robustness)
    m1 = find_1x2(c["competition"], c["home"], c["away"])
    if m1:
        row["markets_checked"]["1X2"] = f"BetExplorer marktgemiddelde over {m1['books']} boeken (bookmaker niet herleidbaar)"
        o1, ox, o2 = m1["odds"]
        row["odds_1x2"] = [o1, ox, o2]
        sel += [("1X2", f"1 ({c['home']} wint)", o1, f"BetExplorer ({m1['books']} boeken, gemiddelde)", "home",
                 lambda p: p.home, lambda p: p.home),
                ("1X2", "X (gelijkspel)", ox, f"BetExplorer ({m1['books']} boeken, gemiddelde)", None,
                 lambda p: p.draw, lambda p: p.draw),
                ("1X2", f"2 ({c['away']} wint)", o2, f"BetExplorer ({m1['books']} boeken, gemiddelde)", "away",
                 lambda p: p.away, lambda p: p.away)]
    else:
        row["markets_checked"]["1X2"] = "niet gevonden in de BetExplorer-fixtureslijst van deze competitie"

    ev_sp = find_event(c["competition"], "spreads", c["home"], c["away"]) if c["competition"] in odds["bought"]["spreads"] else None
    if c["competition"] not in odds["bought"]["spreads"]:
        reden = ("niet opgevraagd — creditplafond van de run bereikt (§1a stap 0/1); "
                 "deze competitie kreeg de doelpuntenmarkt uit de rotatie"
                 if c["competition"] in odds["bought"]["totals"] else
                 ("geen sportkey bij The Odds API voor deze competitie" if not c["sportkey"]
                  else "niet opgevraagd — creditplafond van de run bereikt (§1a stap 0)"))
        for k in ("AH", "DNB", "DC"):
            row["markets_checked"][k] = reden
    elif ev_sp is None:
        for k in ("AH", "DNB", "DC"):
            row["markets_checked"][k] = "spreads opgehaald, maar deze wedstrijd stond niet in de respons"
    else:
        lines = oddsapi.best_by_line(ev_sp, "spreads")
        n_ah = n_dnb = n_dc = 0
        for (outcome, line), (o, book) in lines.items():
            side = side_of(outcome, c["home"], c["away"])
            if line is None or side is None:
                continue
            ln = float(line)
            if abs(ln) < 1e-9:
                sel.append(("Draw No Bet", f"DNB — {outcome}", o, f"The Odds API ({book})", side,
                            (lambda s: (lambda p: dnb_prob(p.grid, s, o)))(side),
                            (lambda s: (lambda p: dnb_prob(p.grid, s, o)))(side))); n_dnb += 1
            elif abs(ln - 0.5) < 1e-9:
                naam = c["home"] if side == "home" else c["away"]
                sel.append(("Double Chance", f"Double Chance — {naam} of gelijk (AH +0.5 @ {o})", o,
                            f"The Odds API ({book})", side,
                            (lambda s: (lambda p: asian_prob(p.grid, 0.5, s, o)))(side),
                            (lambda s: (lambda p: asian_prob(p.grid, 0.5, s, o)))(side))); n_dc += 1
            else:
                sel.append(("Asian Handicap", f"{outcome} {ln:+g}", o, f"The Odds API ({book})", side,
                            (lambda s, l: (lambda p: asian_prob(p.grid, l, s, o)))(side, ln),
                            (lambda s, l: (lambda p: asian_prob(p.grid, l, s, o)))(side, ln))); n_ah += 1
        row["markets_checked"]["AH"] = f"The Odds API spreads — {n_ah} handicaplijnen"
        row["markets_checked"]["DNB"] = (f"The Odds API spreads, 0.0-lijn — {n_dnb} selecties" if n_dnb
                                          else "geen 0.0-lijn in de spreads-respons voor deze wedstrijd")
        row["markets_checked"]["DC"] = (f"The Odds API spreads, ±0.5-lijn — {n_dc} selecties" if n_dc
                                         else "geen ±0.5-lijn in de spreads-respons voor deze wedstrijd")

    ev_to = find_event(c["competition"], "totals", c["home"], c["away"]) if c["competition"] in odds["bought"]["totals"] else None
    if c["competition"] not in odds["bought"]["totals"]:
        row["markets_checked"]["OU"] = ("geen sportkey bij The Odds API voor deze competitie" if not c["sportkey"]
                                        else "niet opgevraagd — deze competitie was vandaag niet aan de beurt in de rotatie (§1a stap 1)")
    elif ev_to is None:
        row["markets_checked"]["OU"] = "totals opgehaald, maar deze wedstrijd stond niet in de respons"
    else:
        lines = oddsapi.best_by_line(ev_to, "totals")
        n = 0
        for (outcome, line), (o, book) in lines.items():
            if line is None:
                continue
            ln, sd = float(line), outcome.lower()
            sel.append(("Over/Under", f"{outcome} {ln:g}", o, f"The Odds API ({book})", None,
                        (lambda l, s: (lambda p: totals_prob(p.grid, l, s, o)))(ln, sd),
                        (lambda l, s: (lambda p: totals_prob(p.grid, l, s, o)))(ln, sd))); n += 1
        row["markets_checked"]["OU"] = f"The Odds API totals — {n} lijnen"
    row["markets_checked"]["BTTS"] = "niet opgevraagd — creditplafond van de run bereikt (2 credits per wedstrijd, §1a stap 2)"
    row["markets_checked"]["context"] = "Fotmob blessures/schorsingen + vorm + rust + stadioncontrole"

    # --- poorten ---
    thresh = THRESH[c["tier"]]
    evaluated = []
    for markt, oms, o, bron, side, f_xg, f_sp in sel:
        try:
            px, ps = f_xg(p_xg), f_sp(p_sp)
        except Exception as e:
            continue
        if not (0 < px < 1 and 0 < ps < 1):
            continue
        my = (px + ps) / 2
        e_pp = edge_pp(my, o)
        e_xg, e_sp = edge_pp(px, o), edge_pp(ps, o)
        gates, fail = {}, None
        gates["odds"] = MIN_ODDS <= o <= MAX_ODDS
        gates["edge"] = e_pp >= thresh
        gates["tweede_methode"] = (px > 1 / o) and (ps > 1 / o)
        rb = None
        if gates["odds"] and gates["edge"] and gates["tweede_methode"]:
            rb = robustness_check(hs, as_, lg, f_xg, o)
            gates["robuustheid"] = rb.min_edge > 0
        else:
            gates["robuustheid"] = None
        g7 = gate7.get(side if side else "None") or {"passed": True, "reason": "geen kant om te benadelen"}
        gates["context"] = bool(g7["passed"])
        for k in ("odds", "edge", "tweede_methode", "robuustheid", "context"):
            if gates[k] is False:
                fail = k; break
        rec = {"market": markt, "selection": oms, "odds": o, "odds_source": bron, "side": side,
               "my_prob": round(my, 4), "implied": round(1 / o, 4),
               "edge_pp": round(e_pp, 2), "edge_xg": round(e_xg, 2), "edge_split": round(e_sp, 2),
               "edge_robust_min": (round(rb.min_edge, 2) if rb else None),
               "failed_gate": fail,
               "context_reason": g7.get("reason", ""),
               "score": round(selection_score(e_pp, my, c["tier"]), 3) if fail is None else None}
        evaluated.append(rec)
    row["candidates_evaluated"] = len(evaluated)
    row["all_candidates"] = sorted(evaluated, key=lambda r: -r["edge_pp"])[:12]

    passed = [r for r in evaluated if r["failed_gate"] is None]
    if passed:
        best = max(passed, key=lambda r: r["score"])
        second = sorted([r for r in passed if r is not best], key=lambda r: -r["score"])
        row["bet"] = True
        row["pick"] = best
        row["runner_up"] = ({"selection": second[0]["selection"], "score": second[0]["score"]} if second else None)
    else:
        near = [r for r in evaluated if r["edge_pp"] >= thresh and MIN_ODDS <= r["odds"] <= MAX_ODDS]
        if near:
            b = max(near, key=lambda r: r["edge_pp"])
            row["near_miss"] = {"market": f"{b['market']} — {b['selection']}", "odds": b["odds"],
                                "edge_xg": b["edge_xg"], "edge_split": b["edge_split"],
                                "edge_robust_min": b["edge_robust_min"],
                                "failed_gate": b["failed_gate"]}
            row["reason"] = {"edge": "edge onder drempel", "odds": "odds buiten band",
                             "tweede_methode": "data conflicterend",
                             "robuustheid": "edge niet robuust over het (shrink, rho)-grid",
                             "context": f"context spreekt de bet tegen — {b['context_reason']}"}[b["failed_gate"]]
        elif evaluated:
            row["reason"] = "edge onder drempel"
        else:
            row["reason"] = "geen prijzen gevonden voor deze wedstrijd"

    # --- kalibratie (§6e) ---
    if m1:
        row["calibration"] = {
            "market": [round(x, 4) for x in calibration.devig(list(m1["odds"]))],
            "p_xg": [round(p_xg.home, 4), round(p_xg.draw, 4), round(p_xg.away, 4)],
            "p_xg_noshrink": [round(p_xg_ns.home, 4), round(p_xg_ns.draw, 4), round(p_xg_ns.away, 4)],
            "p_split": [round(p_sp.home, 4), round(p_sp.draw, 4), round(p_sp.away, 4)],
        }
    results.append(row)

json.dump({"vroeg_seizoen": {"factor": FACTOR, "gepoold": POOLED, "speeldagen": TOTAL_MD,
                             "competities": obs_comps},
           "afkapping": TRUNC,
           "matches": results}, open("tmp-run/rb_results.json", "w"), ensure_ascii=False, indent=1)

for r in results:
    tag = "BET " if r["bet"] else "    "
    extra = (f"{r['pick']['market']} {r['pick']['selection']} @{r['pick']['odds']} "
             f"edge {r['pick']['edge_pp']:+.1f} score {r['pick']['score']}") if r["bet"] else r.get("reason", "")
    print(f"{tag}{r['tier']:5s} {r['match'][:40]:40s} n={r.get('candidates_evaluated',0):3d}  {extra}")
print("\nBETS:", sum(r["bet"] for r in results))
