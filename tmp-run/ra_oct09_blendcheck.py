"""Meting, geen wijziging: wat zou het lopende seizoen doen bij een OMGEREKENDE ploeg?

§4 ("Het lopende seizoen weegt mee") zegt "bouw de teamsterkte ALTIJD zo op" en noemt de
promovendi met zoveel woorden als de groep waar dat het hardst telt. De code doet het daar niet:
in `side_stats` gaat de blend-tak alleen op voor ploegen die WEL in de stand van vorig seizoen
staan; komt een ploeg uit `promotion.convert`, dan worden `conv.stats` ongeblend doorgegeven en
blijven de duels die de ploeg dit seizoen in de hogere divisie heeft gespeeld ongebruikt.

Dit script rekent uit wat dat vandaag waard is. Het verandert NIETS aan de gepubliceerde run.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from datetime import date
from scripts import fotmob, model, promotion, recalibrate, sides
from scripts.model import (TeamStats, analyze_match, analyze_match_from_splits, edge_pp,
                           combine_probs, robustness_check, blend_seasons, blend_weight,
                           splits_from_fotmob, selection_score)
from ra_names import resolve

DAY = date(2026, 10, 9)
FIT = recalibrate.load_fit()
res = json.load(open("tmp-run/ra_oct09_results.json"))
cands = {c["match_id"]: c for c in json.load(open("tmp-run/ra_oct09_cands.json"))}
NIVEAU = res["niveau"]
FACTOR = res["vroeg_seizoen"]["factor"]

PROMO_COMP = {"Segunda División (ESP)": "LaLiga2 (ESP)", "Super Lig (TUR)": "Süper Lig (TUR)"}

for m in res["matches"]:
    if not m.get("promovendi"):
        continue
    c = cands[m["match_id"]]
    comp = c["competition"]
    st_prev = fotmob.fetch_league_stats(c["primaryId"], c["season"])
    st_cur = fotmob.fetch_league_stats(c["primaryId"], c["season_cur"])
    keuze = model.league_level(st_prev, st_cur, uplift_factor=FACTOR)
    lg = keuze.league
    pcomp = PROMO_COMP.get(comp, comp)

    def zijde(naam, tabelsleutel):
        """(ongeblend, geblend) TeamStats + splits, zoals de run het doet en zoals §4 het vraagt."""
        if tabelsleutel:
            r = st_prev["teams"][tabelsleutel]
            prior = TeamStats(xg=r["xg"], xga=r["xga"], matches_played=r["mp"])
            sp = splits_from_fotmob(r)
        else:
            conv = None
            for fn, tier in ((promotion.convert, promotion.TIER2),
                             (promotion.convert_relegated, promotion.TIER1)):
                t = tier.get(pcomp)
                if not t:
                    continue
                try:
                    src = fotmob.fetch_league_stats(t.fotmob_id, c["season"])["teams"]
                    conv = fn(pcomp, resolve(naam, src) or naam, c["season"], lg)
                    break
                except Exception:
                    continue
            if conv is None:
                return None
            prior, sp = conv.stats, conv.splits
        ck = resolve(naam, st_cur["teams"])
        cur = None
        if ck:
            cr = st_cur["teams"][ck]
            if cr.get("mp") and cr.get("xg") is not None:
                cur = TeamStats(xg=cr["xg"], xga=cr["xga"], matches_played=cr["mp"])
        return prior, blend_seasons(prior, cur), sp, cur

    zh = zijde(c["home"], c["table_home"])
    za = zijde(c["away"], c["table_away"])
    if not (zh and za):
        print(f"{m['match']}: omrekening niet reproduceerbaar, overgeslagen")
        continue

    pick = m.get("pick") or (m.get("near_miss") and {"market": m["near_miss"]["market"],
                                                     "odds": m["near_miss"]["odds"]})
    print("=" * 78)
    print(f"{m['match']}  ({comp}, tier {m['tier']})")
    for naam, z in ((c["home"], zh), (c["away"], za)):
        prior, blended, _, cur = z
        if cur is None:
            print(f"  {naam}: geen lopend seizoen gevonden")
            continue
        w = blend_weight(cur.matches_played)
        print(f"  {naam}: vorig/omgerekend {prior.xg_per_match:.3f} xG / "
              f"{prior.xga_per_match:.3f} xGA  |  dit seizoen {cur.xg_per_match:.3f} / "
              f"{cur.xga_per_match:.3f} over {cur.matches_played} duels (gewicht {w:.3f})"
              f"  ->  geblend {blended.xg_per_match:.3f} / {blended.xga_per_math:.3f}"
              if False else
              f"  {naam}: vorig/omgerekend {prior.xg_per_match:.3f} xG / "
              f"{prior.xga_per_match:.3f} xGA  |  dit seizoen {cur.xg_per_match:.3f} / "
              f"{cur.xga_per_match:.3f} over {cur.matches_played} duels (gewicht {w:.3f})"
              f"  ->  geblend {blended.xg_per_match:.3f} / {blended.xga_per_match:.3f}")
    p_zonder = analyze_match(zh[0], za[0], lg)
    p_met = analyze_match(zh[1], za[1], lg)
    print(f"  lambdas ZONDER blend: {p_zonder.lambda_home:.3f} / {p_zonder.lambda_away:.3f}"
          f"   (dit is wat de run heeft gebruikt)")
    print(f"  lambdas MET blend:    {p_met.lambda_home:.3f} / {p_met.lambda_away:.3f}")
    print(f"  P(thuis) {p_zonder.home:.4f} -> {p_met.home:.4f}   "
          f"P(uit) {p_zonder.away:.4f} -> {p_met.away:.4f}")
