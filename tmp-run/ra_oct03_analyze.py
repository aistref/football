"""Run A, 3 okt 2026 — Stage 4/5 voor de vijf FA Cup-duels die de datadekkingspoort halen.

De FA Cup-kwalificatieronde staat in geen enkele Fotmob-daglijst (bevinding van 2 okt 2026); de
40 duels komen daarom van BetExplorer. Dat heeft drie gevolgen die dit script anders maken dan
`rb_oct02_analyze.py`:

1. **Geen xG.** Geen van de betrokken non-league-divisies levert xG bij Fotmob. De doelpunten zijn
   de sterktemaat, dus `data_tier = LIGHT` en de drempel is 16,0 pp (§0) — zelfde constructie als
   Keuken Kampioen Divisie bij Run B.
2. **Alleen 1X2 te koop.** De FA Cup heeft geen sportkey bij The Odds API, dus er is geen prijs
   voor Asian Handicap, Draw No Bet, Over/Under of BTTS. BetExplorer geeft het 1X2-gemiddelde.
   Double Chance is zonder eigen prijs niet af te zetten. Dat beperkt §5 tot één markt, en dat
   hoort in het rapport te staan in plaats van als "geen kandidaat" te verdwijnen.
3. **De competitiebasis komt per duel uit de divisie van de ploegen zelf**, niet uit de beker.
   §4 "In een beker ligt de basis per WEDSTRIJD, niet per toernooi".
"""
import json
from datetime import date
from scripts import fotmob, model, sides, recalibrate
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           edge_pp, robustness_check, selection_score, splits_from_fotmob,
                           blend_seasons, blend_weight, combine_probs, league_level)

DAY = date(2026, 10, 3)
THRESH = {"FULL": 8.0, "LIGHT": 16.0}
NEAR = {"FULL": 3.0, "LIGHT": 6.0}
MIN_ODDS, MAX_ODDS = 1.30, 6.00

# De vijf duels die Stage 3 overleefden, met per kant de divisie waaruit de basis komt.
# (betexplorer-naam, fotmob-tabelnaam, divisie-id)
NLN, SPC, NL1 = 8944, 8947, 117
DUELS = [
    ("Buxton", "Buxton", NLN, "South Shields", "South Shields", NLN, [3.00, 3.50, 2.15]),
    ("Kettering", "Kettering Town FC", SPC, "Worcester", "Worcester", SPC, [1.95, 3.65, 3.30]),
    ("Macclesfield", "Macclesfield FC", NLN, "Scarborough", "Scarborough Athletic", NLN, [1.73, 3.75, 4.00]),
    ("Morecambe", "Morecambe", NLN, "Darlington", "Darlington", NLN, [1.65, 3.85, 4.50]),
    ("Spennymoor", "Spennymoor Town FC", NLN, "Chester", "Chester FC", NLN, [2.75, 3.10, 2.45]),
]
DIVNAAM = {NLN: "National League North (ENG)", SPC: "Southern Premier Central (ENG)",
           NL1: "National League (ENG)"}

FIT = recalibrate.load_fit()
print("herijking:", FIT)

tables = {}
for lid in (NLN, SPC, NL1):
    tables[lid] = {s: fotmob.fetch_league_stats(lid, s) for s in ("2025/2026", "2026/2027")}
    for s, d in tables[lid].items():
        md = model.matchdays_played(d.get("teams") or {})
        print(f"  {DIVNAAM[lid]:34} {s}  {len(d['teams'])} ploegen, {md} speeldagen, "
              f"xG={any('xg' in t for t in d['teams'].values())}")

# --- competitiebasis per divisie (§3 Stage 5: league_level kiest de route) --------------------
niveau = {}
for lid in (NLN, SPC):
    keuze = league_level(tables[lid]["2025/2026"], tables[lid]["2026/2027"], uplift_factor=1.0)
    niveau[lid] = keuze
    print(f"\n{DIVNAAM[lid]}: route={keuze.as_dict().get('route')} "
          f"home_gpm={keuze.league.home_goals_per_match:.4f} "
          f"away_gpm={keuze.league.away_goals_per_match:.4f} "
          f"avg={keuze.league.avg_xg_per_match:.4f}")

def team_stats(lid, naam):
    """TeamStats uit doelpunten (geen xG beschikbaar), vorig + lopend geblend (§4)."""
    prev = (tables[lid]["2025/2026"]["teams"] or {}).get(naam)
    cur = (tables[lid]["2026/2027"]["teams"] or {}).get(naam)
    if prev is None and cur is None:
        return None, None, None
    def ts(row):
        if row is None:
            return None
        return TeamStats(xg=float(row["gf"]), xga=float(row["ga"]),
                         matches_played=int(row["played"]))
    t_prev, t_cur = ts(prev), ts(cur)
    if t_prev is None:
        return t_cur, 1.0, cur
    if t_cur is None:
        return t_prev, 0.0, prev
    w = blend_weight(t_cur.matches_played)
    return blend_seasons(t_prev, t_cur), w, cur

rows = []
for bh, fh, lid_h, ba, fa, lid_a, o in DUELS:
    lid = lid_h if lid_h == lid_a else None
    if lid is None:
        rows.append({"match": f"{bh} - {ba}", "status": "KRUIS-DIVISIE, niet doorgerekend"})
        continue
    league = niveau[lid].league
    sh, wh, row_h = team_stats(lid, fh)
    sa, wa, row_a = team_stats(lid, fa)
    if sh is None or sa is None:
        rows.append({"match": f"{bh} - {ba}", "status": "geen tabelrij"})
        continue
    # De splits komen van VORIG seizoen: Fotmob geeft de thuis/uit-doelpunten van het lopende
    # seizoen pas laat betrouwbaar, en op 9 a 10 speeldagen staan ze extreem (Run B houdt het om
    # dezelfde reden op het vorige seizoen). Staat een ploeg niet in de tabel van vorig seizoen,
    # dan kwam ze uit een ANDERE divisie en is er geen omrekening voor deze niveaus in
    # scripts/promotion.py -> data_tier = NONE, geen bet (SS4 "Kruis-divisie").
    prev_teams = tables[lid]["2025/2026"]["teams"] or {}
    if fh not in prev_teams or fa not in prev_teams:
        ontbreekt = [n for n in (fh, fa) if n not in prev_teams]
        rows.append({"match": f"{bh} - {ba}", "divisie": DIVNAAM[lid], "tier": "NONE",
                     "status": "KRUIS-DIVISIE zonder omrekening: "
                               + ", ".join(ontbreekt)
                               + " stond vorig seizoen niet in deze divisie en "
                                 "scripts/promotion.py kent geen TIER-keten voor dit niveau",
                     "selecties": []})
        print(f"\n=== {bh} - {ba}: NONE — {', '.join(ontbreekt)} kruist een divisiegrens "
              f"zonder omrekening ===")
        continue
    p_xg = analyze_match(sh, sa, league)
    spl_h = splits_from_fotmob(prev_teams[fh])
    spl_a = splits_from_fotmob(prev_teams[fa])
    p_split = analyze_match_from_splits(spl_h, spl_a, league=league)
    probs = {"1": (p_xg.home, p_split.home, o[0], "home"),
             "X": (p_xg.draw, p_split.draw, o[1], None),
             "2": (p_xg.away, p_split.away, o[2], "away")}
    out = {"match": f"{bh} - {ba}", "divisie": DIVNAAM[lid], "tier": "LIGHT",
           "lambda": [round(p_xg.lambda_home, 3), round(p_xg.lambda_away, 3)],
           "blend_w": [round(wh, 3), round(wa, 3)], "odds_1x2": o, "selecties": []}
    for sel, (pxg, psp, odd, side) in probs.items():
        raw = combine_probs(pxg, psp)
        mp = recalibrate.apply(raw, FIT)
        imp = 1.0 / odd
        e = (mp - imp) * 100
        getter = {"1": (lambda r: r.home), "X": (lambda r: r.draw), "2": (lambda r: r.away)}[sel]
        rb = robustness_check(sh, sa, league, getter, odd)
        gates = {
            "odds": MIN_ODDS <= odd <= MAX_ODDS,
            "anticirc": True,                      # doelpunten/splits, geen marktinput
            "tier": True,                          # LIGHT != NONE
            "tweede_methode": (pxg > imp) and (psp > imp),
            "robuust": rb.min_edge > 0,
            "context": True,                       # geen Fotmob-contextblok voor deze divisies
            "underdog": sides.check(side, o, today=DAY).passed,
        }
        out["selecties"].append({
            "selection": sel, "odds": odd, "implied": round(imp, 4),
            "p_xg": round(pxg, 4), "p_split": round(psp, 4),
            "my_raw": round(raw, 4), "my_prob": round(mp, 4), "edge_pp": round(e, 2),
            "edge_robust_min": round(rb.min_edge, 2), "edge_robust_max": round(rb.max_edge, 2),
            "side": side, "poorten": gates,
            "alle_poorten_open": all(gates.values()),
            "drempel_gehaald": e >= THRESH["LIGHT"],
            "near_miss": e >= NEAR["LIGHT"],
            "selection_score": round(selection_score(e, mp, "LIGHT"), 4),
            "would_block_underdog": sides.check(side, o, today=DAY).would_block,
        })
    rows.append(out)

for r in rows:
    print(f"\n=== {r['match']}  ({r.get('divisie','?')}) lambda={r.get('lambda')} ===")
    for s in r.get("selecties", []):
        flag = "BET-KANDIDAAT" if s["alle_poorten_open"] and s["drempel_gehaald"] else ""
        dicht = [k for k, v in s["poorten"].items() if not v]
        print(f"  {s['selection']} @ {s['odds']:.2f}  impl={s['implied']*100:5.2f}%  "
              f"p_xg={s['p_xg']*100:5.2f}  p_split={s['p_split']*100:5.2f}  "
              f"my={s['my_prob']*100:5.2f}  edge={s['edge_pp']:+6.2f}pp  "
              f"robuust[{s['edge_robust_min']:+.2f},{s['edge_robust_max']:+.2f}]  "
              f"dicht={dicht or '-'} {flag}")

json.dump({"day": DAY.isoformat(), "fit": str(FIT), "rows": rows,
           "niveau": {str(k): v.as_dict() for k, v in niveau.items()}},
          open("tmp-run/ra_oct03_analyse.json", "w"), ensure_ascii=False, indent=1)

best = [s for r in rows for s in r.get("selecties", [])
        if s["alle_poorten_open"] and s["drempel_gehaald"]]
print(f"\nselecties met alle poorten open EN drempel 16,0 pp gehaald: {len(best)}")
nm = [s for r in rows for s in r.get("selecties", []) if s["near_miss"]]
print(f"near_miss (>= 6,0 pp): {len(nm)}")
