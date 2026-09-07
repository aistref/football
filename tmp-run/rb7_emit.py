"""Run B, 7 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-07"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-07T05:15:00+02:00"

TOELICHTING = '11 wedstrijden op de runlijst vandaag, in 7 van de 17 competities. Tien hadden niets op de kalender, en dat is bij een maandag in de interlandperiode geen storing: van Tsjechie, Kroatie, Zwitserland, Oostenrijk, Albanie en Kosovo staat er geen enkele competitie in de Fotmob-daglijst, van Noorwegen alleen de 3. Divisjon (vier poules), van Hongarije alleen de NB II, van Duitsland alleen de Frauen-Bundesliga en van Engeland alleen League One - League Two speelde niet. De cap van 40 (maandag) is niet geraakt: nul duels afgekapt, alle 11 zijn beoordeeld. 8 van de 11 kwamen door de datadekkingspoort (3 FULL, 5 LIGHT), samen 89 selecties over alle zes de markten, en nul bets. De drie op NONE zijn alle drie hetzelfde geval en geen van drieen een storing: een ploeg die vorig seizoen niet in deze divisie speelde en waarvoor promotion.py geen gemeten divisiepaar heeft - Iraklis (Greek Super League) en FC Voluntari (Romanian SuperLiga) spelen in een competitie waarvoor helemaal geen paar bekend is, en Sabadell komt uit de DERDE divisie (Primera Federacion), waarvoor TIER2 onder LaLiga2 niets kent. Twee ploegen zijn wel omgerekend en kwamen daarmee op LIGHT: Kalmar FF (Superettan -> Allsvenskan) en Bromley (League Two -> League One). Dat er nul bets uitkomen ligt aan de herijking van 1g, net als bij Run A vanochtend en bij Run B gisteren. Ze staat op 610 afgerekende gevallen (a=0.921, b=-0.447) en haalt rond de tien procentpunt van elke kansschatting af. De hoogste herijkte edge van de hele run is +1.93 pp (AIK bij Malmo @4.63) bij een FULL-drempel van 8.0; dezelfde selectie stond ruw op +9.54 pp. Er is geen enkele near miss - de NEAR-ondergrens ligt op 3.0 pp voor FULL en 6.0 voor LIGHT, en geen enkele selectie komt daar herijkt boven. Een selectie haalde ruw wel alle acht poorten en herijkt niet (Malmo - AIK, Under 3.5 @1.69, ruw +8.73 pp tegen herijkt -3.12 pp); die gaat als schaduwpick mee met failed_gate herijking. Poort 8 hield vandaag niets tegen. Poort 7 wel, bij drie duels: Asteras Tripolis (22% van de selectiewaarde afwezig tegen 12%), Kalmar FF (14% tegen 0%) en AIK (56% tegen 23%) - dat laatste is de zwaarste blokkade die deze poort tot nu toe heeft gegeven.'

OMREKENINGEN = {'aanleiding': 'Vijf ploegen stonden vorig seizoen niet in de stand van de competitie van vandaag. Twee zijn omgerekend en kwamen daarmee op LIGHT - een omgerekende ploeg is nooit FULL, want RESIDUAL_SPREAD houdt na correctie nog onzekerheid over: Kalmar FF (Superettan -> Allsvenskan, gepoolde up-factor x0.605/1.513, aanval 1.213 en verdediging 0.490 allebei binnen het gemeten bereik) en Bromley (League Two -> League One, gemeten E2/E3-factor x0.782/1.375). Drie gingen naar NONE, en alle drie om dezelfde reden: er is geen gemeten divisiepaar om mee om te rekenen. Iraklis en FC Voluntari spelen in een competitie waarvoor promotion.py geen divisie boven of onder kent (Greek Super League respectievelijk Romanian SuperLiga); Sabadell komt uit de DERDE divisie, de Primera Federacion, en TIER2 kent onder LaLiga2 geen divisie - de omweg viel daar terug op TIER1 (La Liga) en Sabadell staat daar uiteraard niet in. NONE is in alle drie de gevallen de eerlijke uitkomst conform 4: buiten het gemeten bereik geen bet.', 'naamkoppeling': "Een reparatie aan tmp-run/ra_names.py, nodig voor de PRIJZEN en niet voor de tier: aliassen 'Universitatea Craiova' -> 'Univ. Craiova' en 'Universitatea Cluj' -> 'U. Cluj'. De Fotmob-stand van de Romanian SuperLiga schrijft de namen voluit, BetExplorer kort het eerste woord af. Na _DROP delen {universitatea, craiova} en {univ, craiova} wel een token, maar geen van beide is een deelverzameling van de ander, en dat is wat resolve eist. best_pair liep er net langs: 0.727 op Craiova en 0.500 op Cluj is 0.614 over het paar, tegen een vloer van 0.62. Universitatea Craiova - Universitatea Cluj kwam daardoor op nul doorgerekende selecties uit terwijl de rij met vijf boeken gewoon bij BetExplorer stond; Roemenie heeft geen sportkey, dus dat was de enige prijsbron die er was. Na de alias zijn het er drie.", 'toegepast_op': ['Kalmar FF', 'Bromley'], 'geweigerd': ['Iraklis (geen divisiepaar bekend voor de Greek Super League)', 'FC Voluntari (geen divisiepaar bekend voor de Romanian SuperLiga)', 'Sabadell (uit de Primera Federacion; TIER2 kent geen divisie onder LaLiga2)']}

CREDITBRON = 'suggest_cap(19597, 24) = 407 - 19.597 credits over volgens api_check.py van deze run (20K-plan, 403 gebruikt deze maand), 24 dagen tot de maandwissel, 2 runs per dag. Vijf van de zeven competities met wedstrijden hebben een sportkey bij The Odds API; voor de Romanian SuperLiga en de Keuken Kampioen Divisie bestaat er geen, en daar is BetExplorer de enige 1X2-bron (marktgemiddelde, bookmaker niet herleidbaar). split_budget(407, 5) geeft 5 spreads / 5 totals, en het plafond is ruim genoeg voor 3 credits per competitie, dus alle vijf kregen de bulk-aanroep met h2h EN spreads EN totals (1a, regel van 5 sep): vijf van de zes markten in een keer, met 1X2 op de beste prijs. Gemeten over de vijf duels waar beide bronnen een 1X2 gaven leverde dat gemiddeld +7.01% betere koers op dan het BetExplorer-marktgemiddelde (mediaan +7.02%, spreiding +5.84% tot +8.09%). BTTS is voor 7 duels gekocht a 1 credit. Totaal 22 van 407 credits in 12 aanroepen. Marktbalans-controle: 5 van de 7 competities hebben een doelpuntenmarkt en 7 van de 7 een uitkomstmarkt - ruim geslaagd, geen enkele markt viel weg door het plafond.'

res = json.load(open("tmp-run/rb7_results.json"))
odds = json.load(open("tmp-run/rb7_odds.json"))
s3 = json.load(open("tmp-run/rb7_stage3.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("ł", "l").replace("ß", "ss").replace("Ø", "o")
    return re.sub(r"[^a-z0-9]", "", s.lower())

def confidence(m):
    p = m["pick"]; rb = p["edge_robust_min"] or 0
    if m["tier"] == "FULL" and p["edge_pp"] >= 8 and rb >= 5: return "High"
    if p["edge_pp"] >= 5 and rb >= 3: return "Medium"
    return "Low"

def risk(m):
    p = m["pick"]
    if abs(p["edge_pp"]) >= 10 or p["odds"] >= 4.0: return "high"
    if p["edge_pp"] >= 5 or m["tier"] == "LIGHT": return "med"
    return "low"

bets = sorted([m for m in matches if m.get("bet")], key=lambda m: -m["pick"]["score"])
MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
short, n_light = set(), 0
for m in bets:
    if len(short) >= MAX_SHORT: break
    if m["tier"] == "LIGHT" and n_light >= MAX_LIGHT: continue
    short.add(m["match_id"]); n_light += m["tier"] == "LIGHT"

picks = []
for m in bets:
    p, c = m["pick"], m["competition"]
    b = stats[c]["prev"]
    ctx = m.get("context") or {}
    ho, aw = ctx.get("home", {}), ctx.get("away", {})
    prob_sources = [
        f"Fotmob {c} vorig seizoen xG — competitiegemiddelde {b['avg_xg']:.3f} xG per ploeg per duel "
        f"over {b['teams']} ploegen",
        f"Fotmob {c} thuis/uit-splits — thuis {b['home_gpm']:.3f} en uit {b['away_gpm']:.3f} doelpunten "
        f"per duel (tweede methode, multiplicatief op het competitiegemiddelde)",
        f"Fotmob wedstrijdcontext ({ctx.get('lineup_type') or 'geen opstelling'}): "
        f"thuis {ho.get('out_count', 0)} afwezig · vorm {ho.get('form') or 'onbekend'}; "
        f"uit {aw.get('out_count', 0)} afwezig · vorm {aw.get('form') or 'onbekend'} — poort 7: {p['context_reason']}",
        f"Vroeg-seizoenscorrectie x{vs['factor']:.4f} over {len(vs['competities'])} competities "
        f"({vs['speeldagen']} speeldagen, ruwe verhouding {vs['gepoold']:.4f}) — uitsluitend uit "
        f"xG-waarnemingen, geen enkele marktprijs (§2)",
    ]
    if m.get("understat"):
        u = m["understat"]; r = u["rolling_xg_8"]
        rl = " · ".join(f"{k} {v[0]}/{v[1]} xG over {v[2]} duels" for k, v in r.items() if v)
        prob_sources.append(f"Understat {c} — tweede, onafhankelijk xG-model (§4): rollende xG {rl}")
    if m.get("promovendi"):
        for k, note in m["promovendi"].items():
            prob_sources.append(f"Promovendi-omrekening ({k}) — {note}")
    ru = m.get("runner_up")
    notes = (f"xG-methode {p['edge_xg']:+.2f} pp, splitsmethode {p['edge_split']:+.2f} pp, gemiddelde "
             f"{p['edge_pp']:+.2f} pp. Zwakste stand van het (shrink, rho)-grid {p['edge_robust_min']:+.2f} pp. "
             f"selection_score {p['score']} uit {m['candidates_evaluated']} doorgerekende selecties. "
             + (f"Tweede werd {ru['selection']} met score {ru['score']}." if ru else
                "Geen tweede selectie haalde alle zeven poorten; sterkste afgewezen alternatief: "
                + (f"{rr['selection']} @ {rr['odds']} ({rr['edge_pp']:+.2f} pp, viel af op "
                   f"{rr['failed_gate']})." if (rr := m.get("runner_up_rejected")) else "geen.")))
    if p["market"] == "Double Chance":
        notes += " Gekocht als de +0.5-handicaplijn uit de spreads-respons (§1a)."
    picks.append({
        "id": f"{DAY}-{slug(c)}-{slug(m['home'])}-{slug(m['away'])}-{slug(p['market'])}-{slug(p['selection'])[:26]}",
        "run": "B", "run_date": DAY,
        "kickoff": datetime.fromisoformat(m["kickoff_utc"].replace("Z", "+00:00")).astimezone(NL).isoformat(),
        "competition": c, "home": m["home"], "away": m["away"],
        "market": p["market"], "selection": p["selection"],
        "odds": p["odds"], "odds_source": p["odds_source"], "odds_captured_at": CAPTURED,
        "implied_prob": p["implied"], "my_prob": p["my_prob"], "edge_pp": p["edge_pp"],
        "data_tier": m["tier"], "confidence": confidence(m),
        "prob_sources": prob_sources,
        "shortlisted": m["match_id"] in short,
        "result": "pending", "notes": notes, "settled_at": None,
    })
    m["_pick_id"] = picks[-1]["id"]; m["_risk"] = risk(m)
    m["_confidence"] = picks[-1]["confidence"]; m["_shortlisted"] = m["match_id"] in short

have = {json.loads(l)["id"] for l in open("data/picks.jsonl") if l.strip()}
nieuw = [p for p in picks if p["id"] not in have]
with open("data/picks.jsonl", "a") as fh:
    for p in nieuw:
        fh.write(json.dumps(p, ensure_ascii=False) + "\n")
print(f"picks toegevoegd: {len(nieuw)} van {len(picks)} ({len(picks) - len(nieuw)} stonden er al)")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00, "POORT_8_UNDERDOG": "licht sinds 5 sep 2026 — sides.UNDERDOG_FLOOR = 0.35",
    "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8, "HERIJKING": "recalibrate.apply, fit op uitslagen", "SETTLE_FALLBACK_HOURS": 2.0,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": TOELICHTING,
    "omrekeningen": OMREKENINGEN,
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = vs
state["credits"] = {
    "plafond": odds["cap"], "gebruikt": odds["guard"]["spent"] if isinstance(odds["guard"], dict) else None,
    "split_budget": odds["split"],
    "bron": CREDITBRON,
    "markten_gekocht": {"bulk_h2h_spreads_totals": odds["bought"]["spreads"],
                        "h2h": odds["bought"]["h2h"], "totals": odds["bought"]["totals"],
                        "btts": odds["bought"]["btts"]},
    "guard_report": odds["guard"],
}
by_comp = {}
for m in matches:
    by_comp.setdefault(m["competition"], []).append(m)
for comp, ms in by_comp.items():
    entry = {"status": "GEANALYSEERD", "matches": []}
    for m in ms:
        e = {"match": m["match"], "match_id": m["match_id"], "tier": m["tier"],
             "bet": bool(m.get("bet")), "kickoff_nl": m["kickoff_nl"], "kickoff_utc": m["kickoff_utc"],
             "markets_checked": m["markets_checked"], "lambdas": m.get("lambdas"),
             "per_market": m.get("per_market"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "understat", "verplaatst", "poort8_geblokkeerd", "afgekapt",
                  "seizoensweging", "odds_1x2", "odds_1x2_best", "beste_prijs_winst_pct", "ou25",
                  "zonder_herijking"):
            if m.get(k): e[k] = m[k]
        if m.get("reason"): e["reden"] = m["reason"]
        if m.get("near_miss"): e["near_miss"] = m["near_miss"]
        if m.get("calibration"): e["calibration"] = m["calibration"]
        if m.get("bet"):
            e["pick_id"] = m["_pick_id"]; e["pick"] = m["pick"]
            e["risico"] = m["_risk"]; e["shortlisted"] = m["_shortlisted"]
        entry["matches"].append(e)
    mark(state, comp, entry)
for comp, v in fx.items():
    if not v["matches"]:
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": [],
                           "reden": "niets op de kalender vandaag (Fotmob-daglijst)"})
save(state)
print("run-state weggeschreven")
json.dump({"short": sorted(short), "bets": [m["match"] for m in bets]},
          open("tmp-run/rb7_short.json", "w"), ensure_ascii=False)
