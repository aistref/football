"""Run B 24 sep 2026 — Stage 4/5 voor het enige duel van de runlijst.

Seattle Sounders FC – Real Salt Lake (MLS, id 130). Bijzonderheid van deze run: het duel trapte
af om 01:40Z / 03:40 NL en stond bij het draaien van de run op 89' (2-0, `finished` false). Er is
dus geen bet te publiceren — de gebruiker zet tussen 07:00 en 08:00 in (§0). Wat er wél kan, en
wat deze analyse doet, is de wedstrijd op **pre-match** input doorrekenen voor het kalibratie- en
contextlogboek: de stand van 2026 telt dit duel nog niet mee (25 resp. 26 duels van 27 speeldagen)
en het BetExplorer-marktgemiddelde is de slotkoers van vóór de aftrap.

Competitieniveau: rechtstreeks uit het LOPENDE seizoen. MLS loopt op kalenderjaar en staat op 27
speeldagen — dat is openstaand punt 3 uit runs/2026-09-20-run-b.md, waar `early_season_uplift`
voor een halverwege lopend seizoen een echt niveauverschil als vroeg-seizoenseffect leest.
"""
import json
from datetime import date, datetime, timezone, timedelta
from scripts import fotmob, model, context, squad, ranking, recalibrate, sides
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           edge_pp, asian_prob, dnb_prob, totals_prob, robustness_check,
                           selection_score, splits_from_fotmob, blend_seasons, blend_weight,
                           combine_probs)

DAY = date(2026, 9, 24)
NL = timezone(timedelta(hours=2))
MATCH_ID = 5071094
HOME, AWAY = "Seattle Sounders FC", "Real Salt Lake"
HOME_ID, AWAY_ID = 130394, 6606
KICKOFF = "2026-09-24T01:40:00.000Z"
# BetExplorer, marktgemiddelde over 4 boeken, uitgelezen 05:25 CEST. Dit is de pre-match
# slotkoers: de rij stond nog in de fixturetabel met het label "Today 02:30" (UK-tijd).
BX_1X2 = (1.76, 3.90, 4.13)
BX_BOOKS = 4

s3 = json.load(open("tmp-run/rb24_stage3.json"))
prev, cur = s3["prev"], s3["cur"]

FIT = recalibrate.load_fit()
print("herijking:", FIT)

# --- competitiebasis: lopend seizoen, geen uplift (zie docstring) ---------------------------
lg = LeagueContext(home_goals_per_match=cur["home_goals_per_match"],
                   away_goals_per_match=cur["away_goals_per_match"],
                   avg_xg_per_match=cur["avg_xg_per_match"])
print(f"niveau (2026, {cur['played']} speeldagen): thuis {lg.home_goals_per_match:.3f} / uit "
      f"{lg.away_goals_per_match:.3f} / xG {lg.avg_xg_per_match:.3f}")
lg_prev = LeagueContext(home_goals_per_match=prev["home_goals_per_match"],
                        away_goals_per_match=prev["away_goals_per_match"],
                        avg_xg_per_match=prev["avg_xg_per_match"])
print(f"niveau (2025, ter vergelijking): thuis {lg_prev.home_goals_per_match:.3f} / uit "
      f"{lg_prev.away_goals_per_match:.3f} / xG {lg_prev.avg_xg_per_match:.3f} "
      f"-> verhouding lopend/vorig = {cur['avg_xg_per_match']/prev['avg_xg_per_match']:.4f}")

def ts(d):
    return TeamStats(xg=d["xg"], xga=d["xga"], matches_played=d["mp"])

teams = {}
for label, name in (("home", HOME), ("away", AWAY)):
    p, c = prev["teams"][name], cur["teams"][name]
    blended = blend_seasons(ts(p), ts(c), k=model.CREDIBILITY_K)
    w = blend_weight(c["mp"], k=model.CREDIBILITY_K)
    teams[label] = blended
    print(f"{name}: vorig {p['xg']}/{p['xga']} over {p['mp']} | lopend {c['xg']}/{c['xga']} over "
          f"{c['mp']} | blend-gewicht lopend {w:.3f} -> xG/duel {blended.xg_per_match:.3f}, "
          f"xGA/duel {blended.xga_per_match:.3f}")

# splitsmethode: thuis/uit-doelpunten, ook geblend over de twee seizoenen
def splits(name):
    p, c = prev["teams"][name], cur["teams"][name]
    merged = {"home": {k: p["home"][k] + c["home"][k] for k in ("played", "gf", "ga")},
              "away": {k: p["away"][k] + c["away"][k] for k in ("played", "gf", "ga")}}
    return splits_from_fotmob(merged)

sp_home, sp_away = splits(HOME), splits(AWAY)

probs_xg = analyze_match(teams["home"], teams["away"], lg, shrink=model.DEFAULT_SHRINK)
probs_sp = analyze_match_from_splits(sp_home, sp_away, league=lg)
print(f"\nxG-methode   : 1 {probs_xg.home:.4f} X {probs_xg.draw:.4f} 2 {probs_xg.away:.4f}"
      f"  lambda {probs_xg.lambda_home:.3f}/{probs_xg.lambda_away:.3f}")
print(f"splitsmethode: 1 {probs_sp.home:.4f} X {probs_sp.draw:.4f} 2 {probs_sp.away:.4f}"
      f"  lambda {probs_sp.lambda_home:.3f}/{probs_sp.lambda_away:.3f}")

# --- context (poort 7) + datarijkdom --------------------------------------------------------
ctx = context.fetch_match_context(MATCH_ID, KICKOFF)
tv_home = squad.turnover(HOME_ID, ctx.home.squad_value if ctx.home else 0.0)
tv_away = squad.turnover(AWAY_ID, ctx.away.squad_value if ctx.away else 0.0)
rich = ranking.data_richness(ctx, tv_home, tv_away,
                            matches_home=cur["teams"][HOME]["played"],
                            matches_away=cur["teams"][AWAY]["played"])
m = json.load(open("tmp-run/rb24_match.json"))
_gen = m.get("general", {}) or {}
_st = (_gen.get("matchTimeUTCDate") and _gen) or _gen
_v = (m.get("content", {}) or {}).get("matchFacts", {}).get("infoBox", {}).get("Stadium", {}) or {}
stadium = _v.get("name") or ((ctx.venue or {}) if isinstance(ctx.venue, dict) else {}).get("name") or str(ctx.venue or "")
city = _v.get("city") or ""
venue = context.check_venue(stadium, city, HOME_ID, AWAY_ID)
print(f"\ndatarijkdom {rich.total}: {rich.parts} | {rich.notes}")
print("stadion:", venue)

# --- kandidaten over de markten waarvoor een PRE-MATCH prijs bestaat ------------------------
# Alleen 1X2: The Odds API gaf voor dit duel live prijzen (Seattle 1.01, RSL 1000.0) omdat het al
# 89 minuten onderweg was, en een live prijs is geen marktoordeel over de wedstrijd vooraf.
imp = [1 / o for o in BX_1X2]
overround = sum(imp)
devig = [i / overround for i in imp]
print(f"\nBetExplorer 1X2 {BX_1X2} over {BX_BOOKS} boeken; marge {overround - 1:.4f}; "
      f"de-vigd {[round(d, 4) for d in devig]}")

SEL = [("1X2", f"1 ({HOME} wint)", BX_1X2[0], "home", probs_xg.home, probs_sp.home,
        lambda p: p.home),
       ("1X2", "X (gelijkspel)", BX_1X2[1], None, probs_xg.draw, probs_sp.draw, lambda p: p.draw),
       ("1X2", f"2 ({AWAY} wint)", BX_1X2[2], "away", probs_xg.away, probs_sp.away,
        lambda p: p.away)]

cands = []
for market, selection, odds, side, p_xg, p_split, pick in SEL:
    my_raw = combine_probs(p_xg, p_split)
    my_prob = recalibrate.apply(my_raw, FIT)
    e_raw, e_her = edge_pp(my_raw, odds), edge_pp(my_prob, odds)
    gate_odds = model.MIN_ODDS <= odds <= model.MAX_ODDS if hasattr(model, "MIN_ODDS") else 1.30 <= odds <= 6.00
    gate_2m = p_xg > 1 / odds and p_split > 1 / odds
    gate_ctx = context.check(ctx, side)
    gate_side = sides.check(side, list(BX_1X2), today=DAY)
    rob = robustness_check(teams["home"], teams["away"], lg, pick, odds)
    c = {"market": market, "selection": selection, "odds": odds,
         "odds_source": f"BetExplorer ({BX_BOOKS} boeken, pre-match marktgemiddelde; "
                        f"bookmaker niet herleidbaar)",
         "side": side, "p_xg": round(p_xg, 4), "p_split": round(p_split, 4),
         "my_raw": round(my_raw, 4), "my_prob": round(my_prob, 4), "implied": round(1 / odds, 4),
         "edge_pp": round(e_her, 2), "edge_raw": round(e_raw, 2),
         "edge_xg": round(edge_pp(p_xg, odds), 2), "edge_split": round(edge_pp(p_split, odds), 2),
         "edge_robust_min": round(rob.min_edge, 2),
         "poorten": {"odds": gate_odds, "tweede_methode": gate_2m, "context": gate_ctx.passed,
                     "underdog": gate_side.passed, "robuustheid": rob.min_edge > 0},
         "context_reason": gate_ctx.reason, "underdog_reason": gate_side.reason,
         "poort8_vervallen": bool(getattr(gate_side, "would_block", False)),
         "score": round(selection_score(e_her, my_prob, "FULL"), 3),
         "score_ruw": round(selection_score(e_raw, my_raw, "FULL"), 3)}
    cands.append(c)
    print(f"  {selection:32s} @{odds:5.2f} imp {1/odds:6.2%} ruw {my_raw:6.2%} herijkt {my_prob:6.2%} "
          f"edge {e_her:+6.2f} (ruw {e_raw:+6.2f}) | 2e-methode {gate_2m} robuust {rob.min_edge:+.2f} "
          f"ctx {gate_ctx.passed} underdog {gate_side.passed}")

json.dump({"candidates": cands, "richness": rich.total, "richness_notes": rich.notes, "richness_parts": rich.parts,
           "venue": {k: v for k, v in venue.__dict__.items()},
           "stadion": {"naam": stadium, "stad": city},
           "probs_xg": {"1": probs_xg.home, "X": probs_xg.draw, "2": probs_xg.away,
                        "lh": probs_xg.lambda_home, "la": probs_xg.lambda_away},
           "probs_split": {"1": probs_sp.home, "X": probs_sp.draw, "2": probs_sp.away,
                           "lh": probs_sp.lambda_home, "la": probs_sp.lambda_away},
           "devig": devig, "overround": overround, "fit": {"a": FIT.a, "b": FIT.b, "n": FIT.n},
           "context": {"home": ctx.home.__dict__ if ctx.home else None,
                       "away": ctx.away.__dict__ if ctx.away else None,
                       "rest_home": ctx.home.rest_days if ctx.home else None,
                       "rest_away": ctx.away.rest_days if ctx.away else None,
                       "lineup_type": ctx.lineup_type},
           "turnover": {"home": tv_home.__dict__, "away": tv_away.__dict__},
           "league": {"home_gpm": lg.home_goals_per_match, "away_gpm": lg.away_goals_per_match,
                      "avg_xg": lg.avg_xg_per_match, "bron": "lopend seizoen 2026, 27 speeldagen"}},
          open("tmp-run/rb24_analysis.json", "w"), ensure_ascii=False, indent=1, default=str)
print("\ngeschreven: tmp-run/rb24_analysis.json")
