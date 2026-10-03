"""Run A 3 okt 2026 onder §5b: run-state, picks en logboeken.

De runlijst van Run A ligt stil op één competitie na: de FA Cup-kwalificatieronde, met 40 duels die
in geen enkele Fotmob-daglijst staan (bevinding van 2 okt 2026) en dus van BetExplorer komen.
Vier duels haalden de datadekkingspoort, één selectie haalde alle zeven de poorten, en onder §5b
bepaalt de rangorde de lijst omdat er minder dan MAX_SHORTLIST selecties boven de drempel staan.
"""
import json, re, sys, unicodedata
from datetime import date, timezone, timedelta
from scripts import toplist, sides
from scripts.ranking import max_shortlist

DAG = "2026-10-03"
DAY = date(2026, 10, 3)
CAPTURED = "2026-10-03T04:35:00+02:00"
BRON = ("BetExplorer (marktgemiddelde over 1 boek; de FA Cup heeft geen sportkey bij The Odds API, "
        "dus de beste prijs is niet op te halen en de bookmaker is niet herleidbaar — "
        "BetExplorer liet data-bookmaker op 8 aug 2026 vallen)")
PROB_SOURCES = [
    "Fotmob doelpunten National League North (ENG) — gf/ga per ploeg, vorig seizoen (46 speeldagen) "
    "gewogen met het lopende (10 speeldagen) via model.blend_seasons; geen xG beschikbaar, "
    "doelpunten zijn de sterktemaat (§4)",
    "Fotmob thuis/uit-splits National League North (ENG), seizoen 2025/2026 — tweede methode (§1d)",
]

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")

s3 = json.load(open("tmp-run/ra_oct03_stage3.json"))
an = json.load(open("tmp-run/ra_oct03_analyse.json"))
duels = s3["betexplorer"]["FA Cup (ENG)"]["duels_vandaag"]

MARKTEN_GEEN_PRIJS = {
    "DC":   "geen prijs: FA Cup heeft geen sportkey bij The Odds API; BetExplorer levert alleen 1X2",
    "DNB":  "geen prijs: idem — de 0.0-spreadlijn komt uit The Odds API en die dekt de FA Cup niet",
    "AH":   "geen prijs: idem — geen spreads beschikbaar voor deze competitie",
    "OU":   "geen prijs: idem — geen totals beschikbaar voor deze competitie",
    "BTTS": "geen prijs: idem — fetch_event_markets vereist een sportkey",
}
SEL_NAAM = {"1": "1 ({home} wint)", "X": "X (gelijkspel)", "2": "2 ({away} wint)"}

# kickoff: BetExplorer toont Britse tijd (nagerekend op PL 12:30/15:00, La Liga 20:00,
# Bundesliga 19:30 en Eredivisie 19:00 op 9/10 okt — alle drie de UK-slots, niet de CET-slots).
def kickoff(when):
    hhmm = when.split()[-1]
    h, m = (int(x) for x in hhmm.split(":"))
    return f"{DAG}T{h+1:02d}:{m:02d}:00+02:00", f"{h+1:02d}:{m:02d}"

ana = {r["match"]: r for r in an["rows"]}
matches = []
for d in duels:
    naam = f"{d['home']} - {d['away']}"
    k_utc, k_nl = kickoff(d["when"])
    r = ana.get(naam)
    o = list(d["odds"])
    base = {"competition": "FA Cup (ENG)", "match": f"{d['home']} – {d['away']}",
            "home": d["home"], "away": d["away"],
            "kickoff_utc": k_utc.replace("+02:00", "+02:00"), "kickoff_nl": k_nl,
            "source_day": DAG, "fixture_source": "BetExplorer (niet in de Fotmob-daglijst)",
            "odds_1x2": o, "odds_source": BRON, "bookmakers": 1, "bet": False}
    if r is None:
        base.update({"tier": "NONE", "status": "BUITEN DATADEKKING",
                     "reden": "geen van beide ploegen staat in een bereikbare Fotmob-competitietabel "
                              "(8947 Southern Premier Central, 8944 National League North, 117 "
                              "National League, 108/109 League One/Two); Understat dekt vijf "
                              "topcompetities, fbref/Forebet/FootyStats/PredictZ staan achter "
                              "Cloudflare. Geen onafhankelijke kansinput -> §2 -> geen bet.",
                     "all_candidates": [], "markets_checked": {}})
        matches.append(base); continue
    if not r.get("selecties"):
        base.update({"tier": "NONE", "status": "BUITEN DATADEKKING",
                     "reden": r.get("status"), "all_candidates": [], "markets_checked": {}})
        matches.append(base); continue
    cands = []
    for s in r["selecties"]:
        gates = dict(s["poorten"])
        failed = None
        for g in ("odds", "anticirc", "tier", "tweede_methode", "robuust", "context", "underdog"):
            if not gates[g]:
                failed = {"tweede_methode": "tweede_methode", "robuust": "robuustheid",
                          "context": "context", "underdog": "underdog",
                          "odds": "odds", "anticirc": "anticirc", "tier": "tier"}[g]
                break
        if failed is None and s["edge_pp"] < 16.0:
            failed = "edge"
        cands.append({
            "market": "1X2", "selection": SEL_NAAM[s["selection"]].format(**base),
            "odds": s["odds"], "odds_source": BRON, "side": s["side"],
            "my_prob": s["my_prob"], "my_raw": s["my_raw"], "implied": s["implied"],
            "p_xg": s["p_xg"], "p_split": s["p_split"],
            "edge_pp": s["edge_pp"],
            "edge_raw": round((s["my_raw"] - s["implied"]) * 100, 2),
            "edge_xg": round((s["p_xg"] - s["implied"]) * 100, 2),
            "edge_split": round((s["p_split"] - s["implied"]) * 100, 2),
            "edge_robust_min": s["edge_robust_min"], "edge_robust_max": s["edge_robust_max"],
            "poorten": {k: bool(v) for k, v in gates.items()},
            "failed_gate": failed,
            "poort8_vervallen": bool(s["would_block_underdog"]),
            "prob_sources": PROB_SOURCES,
        })
    mk = {"1X2": True, **MARKTEN_GEEN_PRIJS}
    base.update({
        "tier": r["tier"], "status": "GEANALYSEERD", "divisie": r["divisie"],
        "lambdas": {"xg": r["lambda"]}, "blend_gewicht_lopend_seizoen": r["blend_w"],
        "prob_sources": PROB_SOURCES, "all_candidates": cands, "markets_checked": mk,
        "context": {"opgehaald": False,
                    "reden": "de FA Cup-kwalificatieronde staat in geen Fotmob-daglijst, dus er is "
                             "geen match_id en context.fetch_match_context kan niet draaien. "
                             "Poort 7 staat daarmee open op de regel 'een meting die er niet is, is "
                             "geen bewijs van een probleem' (§1c). check_venue is om dezelfde reden "
                             "niet uitgevoerd: geen stadionveld beschikbaar."},
        "datarijkdom": {"score": None,
                        "reden": "ranking.data_richness leunt volledig op het Fotmob-wedstrijdblok "
                                 "(opstelling, uitvallers, teamForm, squad.turnover); dat blok "
                                 "bestaat niet voor deze duels. De cap (55) bond nergens, dus er is "
                                 "niets gerangschikt en niets afgekapt."},
        "calibration": {
            "market": [round(1 / x / sum(1 / y for y in o), 6) for x in o],
            "p_xg": [s["p_xg"] for s in r["selecties"]],
            "p_xg_label": "doelpunten + blend_seasons (model.analyze_match, geen xG beschikbaar)",
            "p_split": [s["p_split"] for s in r["selecties"]],
            "p_split_label": "thuis/uit-splits 2025/2026 (model.analyze_match_from_splits)"},
    })
    base["bet"] = any(c["failed_gate"] is None for c in cands)
    matches.append(base)

state = {"run": "a", "date": DAG, "resumed_count": 0,
         "competitions": {}, "completed": False}
for name, v in s3["fixtures"].items():
    if name == "FA Cup (ENG)":
        continue
    state["competitions"][name] = {
        "status": "GEEN WEDSTRIJD", "matches": [], "fotmob_id": v.get("fotmob_id"),
        "toelichting": "interlandvenster; geen duel in het inzetvenster bij Fotmob én BetExplorer"}
state["competitions"]["FA Cup (ENG)"] = {
    "status": "GEANALYSEERD", "matches": matches, "fotmob_id": None,
    "toelichting": "40 kwalificatieduels, alleen bij BetExplorer; 4 door de datadekkingspoort"}

top = toplist.build(state)
print("MAX_SHORTLIST:", max_shortlist(DAY))
print("\n--- TOP herijkt ---")
for i, r in enumerate(top["herijkt"], 1):
    print(f" {i}. {r['match']:34} {r['market']} {r['selection']:22} @ {r['odds']:.2f} "
          f"edge {r['edge_pp']:+.2f}pp score {r['score']} [{r['tier']}] {r['status']}")
if not top["herijkt"]:
    print(" (leeg)")
print("--- TOP ruw ---")
for i, r in enumerate(top["ruw"], 1):
    print(f" {i}. {r['match']:34} {r['market']} {r['selection']:22} @ {r['odds']:.2f} "
          f"edge {r['edge_pp']:+.2f}pp score {r['score']} [{r['tier']}] {r['status']}")

idx = {m["match"]: m for m in matches}
picks = []
for n, r in enumerate(top["herijkt"], 1):
    m = idx[r["match"]]
    cand = next(c for c in m["all_candidates"]
                if c["market"] == r["market"] and c["selection"] == r["selection"])
    g = sides.check(cand["side"], m["odds_1x2"], today=DAY)
    picks.append({
        "id": f"{DAG}-{slug(m['competition'])}-{slug(m['home'])}-{slug(m['away'])}-"
              f"{slug(r['market'])}-{slug(r['selection'])}",
        "run": "A", "run_date": DAG, "kickoff": m["kickoff_utc"],
        "competition": m["competition"], "home": m["home"], "away": m["away"],
        "market": r["market"], "selection": r["selection"], "odds": r["odds"],
        "odds_source": BRON, "odds_captured_at": CAPTURED,
        "implied_prob": round(1 / r["odds"], 4), "my_prob": r["prob"],
        "my_raw": cand["my_raw"], "edge_pp": r["edge_pp"], "data_tier": r["tier"],
        "confidence": "Low",
        "prob_sources": PROB_SOURCES, "shortlisted": True, "result": "pending",
        "notes": (
            f"Gepubliceerd op rangorde (§5b): plek {n} van {len(top['herijkt'])} over "
            f"{sum(1 for m2 in matches if m2['tier'] in ('FULL','LIGHT'))} doorgerekende "
            f"wedstrijden; {r['status']}. selection_score {r['score']}. "
            f"Edge onder de LIGHT-lat van 16,0 pp — die lat snijdt onder §5b alleen als er méér "
            f"dan MAX_SHORTLIST ({max_shortlist(DAY)}) selecties boven staan, en er staat er nul. "
            f"Ruwe kans {cand['my_raw']}, ruwe edge {cand['edge_raw']} pp; xG-methode "
            f"(op doelpunten) {cand['edge_xg']} pp, splitsmethode {cand['edge_split']} pp, "
            f"zwakste stand van het (shrink, rho)-grid {cand['edge_robust_min']} pp, sterkste "
            f"{cand['edge_robust_max']} pp. shrink staat sinds 19 sep op 1.00 (§6e). "
            f"Poort 8: {g.reason}. "
            f"LET OP — drie beperkingen die bij deze pick horen: (1) data_tier LIGHT omdat National "
            f"League North geen xG bij Fotmob heeft, doelpunten zijn de sterktemaat; (2) de koers "
            f"is een 'marktgemiddelde' over één boek, niet de beste prijs en geen consensus — §1a "
            f"meet dat de beste prijs gemiddeld 1,84 pp edge toevoegt, dus deze edge is eerder te "
            f"laag dan te hoog, maar met één boek is er ook geen marktoordeel om poort 8 en §6e "
            f"stevig op te zetten; (3) er is geen contextblok (poort 7 stond open bij gebrek aan "
            f"meting, niet bij gebrek aan risico) en geen stadioncontrole."),
    })

json.dump({"day": DAG, "matches": matches}, open("tmp-run/ra_oct03_results.json", "w"),
          ensure_ascii=False, indent=1)
json.dump(state, open(f"data/run-state/{DAG}-run-a.json", "w"), ensure_ascii=False, indent=1)
json.dump({"top": top, "picks": picks}, open("tmp-run/ra_oct03_top.json", "w"),
          ensure_ascii=False, indent=1)
print(f"\npicks: {len(picks)}")
for p in picks:
    print(" ", p["id"], p["odds"], p["my_prob"], p["edge_pp"])
