"""Run A, 6 okt 2026 — Stage 4/5: de vijf FA Cup-duels doorrekenen.

Waarom dit script korter is dan dat van Run B: er is één prijsbron (BetExplorer, marktgemiddelde
over 2 boeken) en één markt (1X2). De FA Cup heeft geen sportkey bij The Odds API, dus spreads,
totals en BTTS zijn niet te koop — dat is `niet opgevraagd` en geen gat (§6b-5b).

De datadekkingspoort (§4, "In een beker ligt de basis per WEDSTRIJD"): vier van de vijf duels
hebben hun twee ploegen in verschillende divisies van de Engelse piramide, of helemaal niet in een
divisie die Fotmob dekt -> NONE. Eén duel, Scarborough Athletic - Macclesfield FC, heeft beide
ploegen in dezelfde divisie (National League North) met 46 duels vorig seizoen en 10 dit seizoen.
Dat is precies het geval van 15 sep 2026: "spelen ze allebei in dezelfde divisie, dan is er niets
te overbruggen". Geen xG in die divisie, dus doelpunten als sterktemaat -> LIGHT (§4).
"""
import json
from datetime import date, datetime, timezone, timedelta
from scripts import fotmob, model, calibration, sides, recalibrate, ranking, context
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           edge_pp, robustness_check, selection_score, early_season_uplift,
                           splits_from_fotmob, blend_seasons, blend_weight, combine_probs)

DAY = date(2026, 10, 6)
NL = timezone(timedelta(hours=2))
THRESH = {"FULL": 8.0, "LIGHT": 16.0}
NEAR = {"FULL": 3.0, "LIGHT": 6.0}
MIN_ODDS, MAX_ODDS = 1.30, 6.00
ORDER = ("odds", "tweede_methode", "robuustheid", "context", "underdog", "edge")
KO_UTC = "2026-10-06T18:45:00.000Z"      # 19:45 UK = 20:45 NL

NLN = (8944, "National League North")
DUELS = [
    # (home_bx, away_bx, odds 1/X/2, boeken, divisie-oplossing)
    ("Atherton", "Trafford", (1.92, 4.00, 3.23), 2, None),
    ("Halesowen", "Stafford", (1.70, 4.22, 4.00), 2, None),
    ("Scarborough", "Macclesfield", (2.70, 3.63, 2.31), 2,
     {"league": NLN, "home": "Scarborough Athletic", "away": "Macclesfield FC"}),
    ("Spalding United", "Bury Town", (1.72, 4.10, 4.00), 2, None),
    ("Wingate & Finchley", "Bedford", (2.90, 3.68, 2.16), 2, None),
]
NONE_REDEN = {
    ("Atherton", "Trafford"):
        "geen van beide ploegen staat in een divisie die Fotmob met een stand dekt "
        "(National League, National League North/South, Northern/Southern/Isthmian Premier) — "
        "geen onafhankelijke kansinput, §2",
    ("Halesowen", "Stafford"):
        "Halesowen Town staat in Southern Premier Division Central, Stafford Rangers in geen "
        "enkele door Fotmob gedekte divisie — geen gedeelde divisie om op te normaliseren en "
        "geen gemeten niveauverschil (§4)",
    ("Spalding United", "Bury Town"):
        "Spalding United speelt dit seizoen in National League North, Bury Town in Southern "
        "Premier Division Central — twee divisies, en het niveauverschil daartussen is nergens "
        "gemeten (§4, conversion_in_range is een poort)",
    ("Wingate & Finchley", "Bedford"):
        "Wingate & Finchley staat in Isthmian Premier Division; 'Bedford' is bovendien niet "
        "eenduidig te herleiden (Bedford Town in National League North en Real Bedford in "
        "Southern Premier Division Central) — andere divisie en onzekere identificatie",
}

FIT = recalibrate.load_fit()
print("herijking:", FIT)

# ---- vroeg-seizoenscorrectie (§3 Stage 5) ----------------------------------------------------
seizoenen = {}
st_prev = fotmob.fetch_league_stats(NLN[0], "2025/2026", group=NLN[1])
st_cur = fotmob.fetch_league_stats(NLN[0], "2026/2027", group=NLN[1])
seizoenen["National League North (ENG)"] = (st_prev, st_cur)
obs, OVERGESLAGEN = model.uplift_observations(seizoenen)
FACTOR, POOLED, TOTAL_MD = early_season_uplift(obs)
print(f"vroeg seizoen: factor {FACTOR:.4f} (gepoold {POOLED:.4f}, {TOTAL_MD} speeldagen, "
      f"{len(obs)} competities)")
for c, r in OVERGESLAGEN.items():
    print("  overgeslagen in de pool:", c, "—", r)

keuze = model.league_level(st_prev, st_cur, uplift_factor=FACTOR)
lg = keuze.league
NIVEAU = {"National League North (ENG)": keuze.as_dict()}
print(f"niveau NL North: route {keuze.source} — thuis {lg.home_goals_per_match:.3f} / "
      f"uit {lg.away_goals_per_match:.3f} / basis {lg.avg_xg_per_match:.3f}")

def side_stats(naam):
    r = st_prev["teams"][naam]
    prior = TeamStats(xg=float(r["gf"]), xga=float(r["ga"]), matches_played=r["played"])
    cr = st_cur["teams"].get(naam)
    cur = None
    if cr and cr.get("played") and cr.get("gf") is not None:
        cur = TeamStats(xg=float(cr["gf"]), xga=float(cr["ga"]), matches_played=cr["played"])
    merged = blend_seasons(prior, cur)
    note = None
    if cur is not None:
        note = {"eenheid": "doelpunten (geen xG bij Fotmob voor deze divisie)",
                "duels_dit_seizoen": cur.matches_played,
                "gewicht_dit_seizoen": round(blend_weight(cur.matches_played), 3),
                "xg_per_duel": {"vorig": round(prior.xg_per_match, 3),
                                "dit": round(cur.xg_per_match, 3),
                                "gewogen": round(merged.xg_per_match, 3)},
                "xga_per_duel": {"vorig": round(prior.xga_per_match, 3),
                                 "dit": round(cur.xga_per_match, 3),
                                 "gewogen": round(merged.xga_per_match, 3)}}
    return merged, splits_from_fotmob(r), note

ko = datetime.fromisoformat(KO_UTC.replace("Z", "+00:00"))
results = []
for home, away, o1x2, boeken, opl in DUELS:
    rich = ranking.data_richness(None)
    row = {"competition": "FA Cup (ENG)", "match": f"{home} – {away}", "match_id": None,
           "home": home, "away": away, "kickoff_utc": KO_UTC,
           "kickoff_nl": ko.astimezone(NL).strftime("%H:%M"), "source_day": DAY.isoformat(),
           "richness": rich.total, "richness_parts": rich.parts, "markets": 1,
           "bet": False, "all_candidates": [], "candidates_evaluated": 0,
           "odds_1x2": list(o1x2),
           "odds_1x2_bron": f"BetExplorer, gemiddelde over {boeken} boeken",
           "context": None,
           "context_noot": ("niet op te halen — dit duel staat in geen enkele Fotmob-daglijst, "
                            "dus er is geen match_id om het contextblok mee op te vragen; "
                            "poort 7 staat daarmee open (§1c: een meting die er niet is, is geen "
                            "bewijs van een probleem)"),
           "markets_checked": {
               "1X2": (f"BetExplorer-marktgemiddelde over {boeken} boeken: 1 @{o1x2[0]}, "
                       f"X @{o1x2[1]}, 2 @{o1x2[2]}; bookmaker niet herleidbaar"),
               "DC":   "niet opgevraagd — geen sportkey bij The Odds API voor de FA Cup",
               "DNB":  "niet opgevraagd — geen sportkey bij The Odds API voor de FA Cup",
               "AH":   "niet opgevraagd — geen sportkey bij The Odds API voor de FA Cup",
               "OU":   "niet opgevraagd — geen sportkey bij The Odds API voor de FA Cup",
               "BTTS": "niet opgevraagd — geen sportkey bij The Odds API voor de FA Cup",
               "context": "niet op te halen — geen Fotmob-match_id voor dit duel"}}
    if opl is None:
        row["tier"] = "NONE"
        row["reason"] = NONE_REDEN[(home, away)]
        row["markets_checked"] = {k: ("niet doorgerekend — data_tier NONE "
                                      "(geen onafhankelijke kansinput)")
                                  for k in ("1X2", "DC", "DNB", "AH", "OU", "BTTS")}
        row["markets_checked"]["1X2"] += (f" · prijzen wel gezien: BetExplorer-marktgemiddelde "
                                          f"over {boeken} boeken, 1 @{o1x2[0]}, X @{o1x2[1]}, "
                                          f"2 @{o1x2[2]}")
        row["markets_checked"]["context"] = "niet op te halen — geen Fotmob-match_id voor dit duel"
        results.append(row); continue

    tier = "LIGHT"
    row["tier"] = tier
    row["basis_per_wedstrijd"] = {
        "competitie": "National League North (ENG)",
        "note": ("beide ploegen staan in dezelfde divisie onder de basisdivisie van de beker, dus "
                 "er is niets om te overbruggen (§4, 15 sep 2026). Fotmob-id 8944 met "
                 "group='National League North' — die id draagt óók National League South, dus "
                 "zonder group pakt fetch_league_stats er stil een van de twee."),
        "fotmob_id": NLN[0], "group": NLN[1]}
    hs, sp_h, nh = side_stats(opl["home"])
    as_, sp_a, na = side_stats(opl["away"])
    row["seizoensweging"] = {k: v for k, v in (("thuis", nh), ("uit", na)) if v}
    row["table_names"] = {"thuis": opl["home"], "uit": opl["away"]}

    p_xg = analyze_match(hs, as_, lg)
    p_xg_ns = analyze_match(hs, as_, lg, shrink=1.0)
    p_xg_s08 = analyze_match(hs, as_, lg, shrink=model.LEGACY_SHRINK)
    p_sp = analyze_match_from_splits(sp_h, sp_a, league=lg)
    row["lambdas"] = {"xg": [round(p_xg.lambda_home, 3), round(p_xg.lambda_away, 3)],
                      "split": [round(p_sp.lambda_home, 3), round(p_sp.lambda_away, 3)]}

    o1, ox, o2 = o1x2
    src = f"BetExplorer ({boeken} boeken, marktgemiddelde; bookmaker niet herleidbaar)"
    sel = [("1X2", f"1 ({home} wint)", o1, src, "home", lambda p: p.home),
           ("1X2", "X (gelijkspel)", ox, src, None, lambda p: p.draw),
           ("1X2", f"2 ({away} wint)", o2, src, "away", lambda p: p.away)]

    thresh, near_t = THRESH[tier], NEAR[tier]
    evaluated = []
    for markt, oms, o, bron, side, f in sel:
        px, ps = f(p_xg), f(p_sp)
        if not (0 < px < 1 and 0 < ps < 1):
            continue
        my_raw = combine_probs(px, ps)
        my = recalibrate.apply(my_raw, FIT)
        e_pp, e_raw = edge_pp(my, o), edge_pp(my_raw, o)
        e_xg, e_sp = edge_pp(px, o), edge_pp(ps, o)
        g8 = sides.check(side, row["odds_1x2"], today=DAY)
        base = {"odds": MIN_ODDS <= o <= MAX_ODDS,
                "tweede_methode": (px > 1 / o) and (ps > 1 / o),
                "context": True, "underdog": g8.passed}
        rb = None
        if all(base.values()) and (e_pp >= near_t or e_raw >= thresh):
            rb = robustness_check(hs, as_, lg, f, o)
        poorten = dict(base)
        poorten["robuustheid"] = (rb.min_edge > 0) if rb is not None else None

        def _fail(ev, _base=base, _rb=rb):
            g = dict(_base)
            g["edge"] = ev >= thresh
            g["robuustheid"] = (_rb.min_edge > 0) if _rb is not None else None
            return next((k for k in ORDER if g.get(k) is False), None)

        fail, fail_raw = _fail(e_pp), _fail(e_raw)
        if fail == "edge" and fail_raw is None:
            fail = "herijking"
        evaluated.append({"market": markt, "selection": oms, "odds": o, "odds_source": bron,
                          "side": side, "my_prob": round(my, 4), "my_raw": round(my_raw, 4),
                          "implied": round(1 / o, 4),
                          "p_xg": round(px, 4), "p_split": round(ps, 4),
                          "edge_pp": round(e_pp, 2), "edge_raw": round(e_raw, 2),
                          "edge_xg": round(e_xg, 2), "edge_split": round(e_sp, 2),
                          "edge_robust_min": (round(rb.min_edge, 2) if rb else None),
                          "failed_gate": fail, "failed_gate_ruw": fail_raw, "poorten": poorten,
                          "bet_ruw": fail_raw is None, "bet_beide": fail is None and fail_raw is None,
                          "context_reason": "geen contextdata op te halen — poort open",
                          "underdog_reason": g8.reason,
                          "poort8_vervallen": bool(getattr(g8, "would_block", False)),
                          "score": round(selection_score(e_pp, my, tier), 3) if fail is None else None,
                          "score_ruw": round(selection_score(e_raw, my_raw, tier), 3)})
    row["candidates_evaluated"] = len(evaluated)
    row["per_market"] = {"1X2": {"n": len(evaluated), "bets": 0}}

    def _rmin(b):
        if b["edge_robust_min"] is not None:
            return b["edge_robust_min"]
        fn = next((f for m, oms, o, br, sd, f in sel
                   if m == b["market"] and oms == b["selection"]), None)
        if fn is None:
            return None
        try:
            return round(robustness_check(hs, as_, lg, fn, b["odds"]).min_edge, 2)
        except Exception:
            return None

    _p8 = [r for r in evaluated if r["failed_gate"] == "underdog"]
    row["poort8_geblokkeerd"] = []
    if _p8:
        b8 = max(_p8, key=lambda r: selection_score(r["edge_pp"], r["my_prob"], tier))
        b8["edge_robust_min"] = _rmin(b8)
        row["poort8_geblokkeerd"] = [{
            "market": f"{b8['market']} — {b8['selection']}", "odds": b8["odds"],
            "edge_pp": b8["edge_pp"], "my_prob": b8["my_prob"], "my_raw": b8["my_raw"],
            "edge_xg": b8["edge_xg"], "edge_split": b8["edge_split"],
            "edge_robust_min": b8["edge_robust_min"], "failed_gate": "underdog",
            "score": round(selection_score(b8["edge_pp"], b8["my_prob"], tier), 3),
            "ook_geblokkeerd": len(_p8) - 1, "reden": b8["underdog_reason"]}]

    _p8r = [r for r in evaluated if r["failed_gate_ruw"] == "underdog"
            and not any(q["market"] == r["market"] and q["selection"] == r["selection"] for q in _p8)]
    row["poort8_ruw"] = []
    if _p8r:
        b = max(_p8r, key=lambda r: selection_score(r["edge_raw"], r["my_raw"], tier))
        b["edge_robust_min"] = _rmin(b)
        row["poort8_ruw"] = [{
            "market": f"{b['market']} — {b['selection']}", "odds": b["odds"],
            "my_prob": b["my_raw"], "edge_pp": b["edge_raw"],
            "my_prob_herijkt": b["my_prob"], "edge_pp_herijkt": b["edge_pp"],
            "edge_xg": b["edge_xg"], "edge_split": b["edge_split"],
            "edge_robust_min": b["edge_robust_min"], "failed_gate": "underdog_ruw",
            "score_ruw": b["score_ruw"], "ook_geblokkeerd": len(_p8r) - 1,
            "reden": (f"ruw {b['edge_raw']:+.2f} pp (drempel {thresh:.1f}), alle andere poorten "
                      f"open — {b['underdog_reason']}")}]

    _wb = [r for r in evaluated if r.get("poort8_vervallen")]
    row["poort8_vervallen"] = None
    if _wb:
        bw = max(_wb, key=lambda r: r["score_ruw"])
        row["poort8_vervallen"] = {"n_selecties": len(_wb), "gepubliceerd": False,
            "sterkste": {"market": f"{bw['market']} — {bw['selection']}", "odds": bw["odds"],
                         "side": bw["side"], "my_prob": bw["my_prob"], "my_raw": bw["my_raw"],
                         "edge_pp": bw["edge_pp"], "edge_raw": bw["edge_raw"],
                         "score_ruw": bw["score_ruw"], "reden": bw["underdog_reason"]}}

    row["all_candidates"] = sorted(evaluated, key=lambda r: -r["edge_pp"])
    row["kandidaat_edge"] = any(MIN_ODDS <= r["odds"] <= MAX_ODDS
                                and (r["edge_pp"] >= near_t or r["edge_raw"] >= thresh)
                                for r in evaluated)

    passed = [r for r in evaluated if r["bet_beide"]]
    if passed:
        best = max(passed, key=lambda r: r["score"])
        rest = sorted([r for r in evaluated if r is not best and r["failed_gate"] is None],
                      key=lambda r: -r["score"])
        row["bet"] = True; row["pick"] = best
        if best.get("poort8_vervallen") and row.get("poort8_vervallen"):
            row["poort8_vervallen"]["gepubliceerd"] = True
        row["runner_up"] = ({"selection": f"{rest[0]['market']} — {rest[0]['selection']}",
                             "score": rest[0]["score"]} if rest else None)
        if not rest:
            others = sorted([r for r in evaluated if r is not best], key=lambda r: -r["edge_pp"])
            if others:
                o0 = others[0]
                row["runner_up_rejected"] = {
                    "selection": f"{o0['market']} — {o0['selection']}", "odds": o0["odds"],
                    "edge_pp": o0["edge_pp"], "failed_gate": o0["failed_gate"] or "edge"}
    else:
        near = [r for r in evaluated if r["edge_pp"] >= near_t
                and MIN_ODDS <= r["odds"] <= MAX_ODDS and r["failed_gate"] != "underdog"]
        if near:
            b = max(near, key=lambda r: r["edge_pp"])
            gate = b["failed_gate"] or ("edge" if b["edge_pp"] < thresh else "herijking_omgekeerd")
            row["near_miss"] = {"market": f"{b['market']} — {b['selection']}", "odds": b["odds"],
                                "edge_pp": b["edge_pp"], "my_prob": b["my_prob"],
                                "my_raw": b["my_raw"], "edge_xg": b["edge_xg"],
                                "edge_split": b["edge_split"], "edge_robust_min": _rmin(b),
                                "failed_gate": gate}
            row["reason"] = {
                "edge": f"edge onder drempel ({b['edge_pp']:+.2f} pp, nodig {thresh:.1f})",
                "herijking": (f"alleen de herijking hield hem tegen: ruw {b['edge_raw']:+.2f} pp, "
                              f"herijkt {b['edge_pp']:+.2f} pp, nodig {thresh:.1f}"),
                "herijking_omgekeerd": (f"alleen de ruwe schaal hield hem tegen: ruw "
                                        f"{b['edge_raw']:+.2f} pp, herijkt {b['edge_pp']:+.2f} pp"),
                "odds": "odds buiten band", "tweede_methode": "data conflicterend",
                "robuustheid": "edge niet robuust over het (shrink, rho)-grid",
                "context": "context spreekt de bet tegen",
                "underdog": f"poort 8 — {b['underdog_reason']}"}[gate]
        elif evaluated:
            row["reason"] = "edge onder drempel"
        else:
            row["reason"] = "geen prijzen gevonden voor deze wedstrijd"

    row["calibration"] = {
        "market": [round(x, 4) for x in calibration.devig(list(o1x2))],
        "p_xg": [round(p_xg.home, 4), round(p_xg.draw, 4), round(p_xg.away, 4)],
        "p_xg_noshrink": [round(p_xg_ns.home, 4), round(p_xg_ns.draw, 4), round(p_xg_ns.away, 4)],
        "p_xg_shrink08": [round(p_xg_s08.home, 4), round(p_xg_s08.draw, 4), round(p_xg_s08.away, 4)],
        "p_split": [round(p_sp.home, 4), round(p_sp.draw, 4), round(p_sp.away, 4)]}
    results.append(row)

TRUNC = {"cap": ranking.max_deep_analyses(DAY), "afgekapt": 0,
         "laagste_die_het_haalde": None, "hoogste_die_afviel": None, "lijst": [],
         "noot": ("vijf duels op een cap van 40 — de afkapping bindt niet, dus de datarijkdom "
                  "bepaalt vandaag alleen de volgorde en niet wie er afvalt")}

json.dump({"vroeg_seizoen": {"factor": FACTOR, "gepoold": POOLED, "speeldagen": TOTAL_MD,
                             "competities": [c for c in seizoenen if c not in OVERGESLAGEN],
                             "overgeslagen": OVERGESLAGEN},
           "niveau": NIVEAU, "afkapping": TRUNC, "matches": results},
          open("tmp-run/ra_oct06_results.json", "w"), ensure_ascii=False, indent=1)

for r in results:
    tag = "BET " if r["bet"] else "    "
    extra = (f"{r['pick']['market']} {r['pick']['selection']} @{r['pick']['odds']} "
             f"edge {r['pick']['edge_pp']:+.1f}") if r["bet"] else r.get("reason", "")
    print(f"{tag}{r['tier']:5s} {r['match'][:34]:34s} n={r['candidates_evaluated']:2d}  {extra[:110]}")
print("\nBETS:", sum(r["bet"] for r in results))
