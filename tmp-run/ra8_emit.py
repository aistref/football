"""Stage 6 — vastleggen: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-08"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-08T04:14:00+02:00"

TOELICHTING = (
    "19 wedstrijden op de runlijst vandaag, in 4 van de 21 competities: de Championship (6), "
    "de Eredivisie (2), de League Cup (5) en de Champions League (6). De andere zeventien "
    "hadden niets op de kalender - dat is GEEN WEDSTRIJD, geen storing. De cap van 40 "
    "(maandag) is niet geraakt: nul duels afgekapt, alle negentien zijn tot en met de "
    "datadekkingspoort behandeld. "
    "Tien kwamen daar doorheen (5 FULL, 5 LIGHT) en zijn volledig doorgerekend: samen 141 "
    "selecties over alle zes de markten, en nul bets. Negen vielen af op data_tier NONE, en "
    "die negen verdienen uitleg omdat het er ongewoon veel zijn. Zes ervan zijn de "
    "Champions League-duels: daar staan ploegen uit verschillende LANDEN tegenover elkaar, en "
    "het model kent het krachtsverschil tussen twee nationale competities niet - "
    "promotion.MEASURED_TIER2_GAP meet divisies binnen een land, tussen landen bestaat zo'n "
    "gemeten factor niet. Doorrekenen geeft dan geen kansschatting terug maar de ontbrekende "
    "competitiesterkte; op 19 aug 2026 was dat zeventien procentpunt op een uitwinst. De drie "
    "andere zijn League Cup-duels waarin een ploeg twee divisies lager speelt (Lincoln, Leyton "
    "Orient, Bradford) of waar de omrekening buiten het gemeten bereik viel (Hull, "
    "verdediging 1.102 tegen een bovengrens van 1.022). "
    "Nul bets is vandaag niet het werk van de herijking. De hoogste edge NA herijking is "
    "+5.88 pp (Wrexham - Burnley, 1X2 Burnley @ 3.695) en dat is een LIGHT-duel, waar 16.0 pp "
    "nodig is; de hoogste FULL-edge is -1.88 pp. Maar ook ZONDER de herijking haalde niets de "
    "drempel: het beste FULL-cijfer is dan +5.89 pp (Watford - Preston, 1X2 Preston, nodig "
    "8.0) en het beste LIGHT-cijfer +15.84 pp (Wrexham - Burnley, nodig 16.0) - dat laatste "
    "mist met 0.16 pp. Er gaat dus vandaag geen enkele regel als failed_gate herijking naar "
    "het schaduwlogboek, want er is geen selectie die op de ruwe schaal wel en op de herijkte "
    "niet door de poorten kwam. De fit staat op 613 afgerekende gevallen (a=0.934, b=-0.444, "
    "trefkans 41.4% tegen een geclaimd gemiddelde van 51.8%)."
)

OMREKENINGEN = {
    "aanleiding": (
        "Zes ploegen stonden vorig seizoen niet in de stand van de competitie waarvan de basis "
        "wordt gebruikt, en zijn omgerekend. Twee richtingen. Omhoog uit de divisie eronder: "
        "Cardiff City (League One -> Championship), Bolton Wanderers (League One -> de "
        "Premier League-basis van de League Cup), en Middlesbrough, Millwall en Hull City "
        "(Championship -> diezelfde Premier League-basis). Omlaag uit de divisie erboven: "
        "Burnley en West Ham United (Premier League -> Championship-basis). Een omgerekende "
        "ploeg is nooit FULL - RESIDUAL_SPREAD houdt na correctie nog onzekerheid over - dus "
        "die vijf duels staan op LIGHT, waar 16.0 pp edge nodig is in plaats van 8.0."),
    "naamkoppeling": (
        "Geen enkele ploeg liep vast op de naamkoppeling: ra_names.py koppelde alle negentien "
        "duels bij Fotmob, en de tien doorgerekende ook bij The Odds API. FC Utrecht - Go "
        "Ahead Eagles stond niet in de BetExplorer-fixturelijst van de Eredivisie; dat is geen "
        "naamprobleem maar een ontbrekende rij, en het gevolg is dat dat duel geen "
        "marktgemiddelde heeft (dus geen kalibratieblok, en poort 8 staat er open)."),
    "toegepast_op": ["Cardiff City", "Burnley", "Bolton Wanderers", "West Ham United",
                     "Middlesbrough", "Millwall"],
    "geweigerd": [
        "Hull City (Sunderland - Hull): verdediging 1.102 buiten het gemeten bereik "
        "0.284-1.022 van conversion_in_range -> NONE, geen bet",
        "Lincoln City (Bournemouth - Lincoln): League One, twee divisies onder de "
        "Premier League-basis - er is geen gemeten factor over twee divisies -> NONE",
        "Leyton Orient en Bradford City (Leyton Orient - Bradford): idem, beide League One "
        "-> NONE",
    ],
}

CREDITBRON = (
    "suggest_cap(19575, 23) = 425 - 19.575 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 425 gebruikt deze maand), 23 dagen tot de maandwissel, 2 runs per dag. Het "
    "plafond is ruim genoeg voor 3 credits per competitie, dus de bulk-aanroep is voor alle 4 "
    "competities met een sportkey gedaan met h2h EN spreads EN totals (1a, regel van 5 sep): "
    "dat levert vijf van de zes markten in een keer en zet 1X2 op de beste prijs in plaats van "
    "op het BetExplorer-marktgemiddelde. Gemeten over de negen duels met beide bronnen leverde "
    "dat +5.38% betere koers op dan het marktgemiddelde. BTTS is voor alle 13 duels met dekking "
    "gekocht (2 credits per wedstrijd). De Champions League is wel ingekocht hoewel die duels "
    "op NONE eindigen: 3 credits op een plafond van 425 is verwaarloosbaar, en zonder die "
    "aanroep zou van tevoren niet vaststaan dat de prijzen er waren - nu is zichtbaar dat de "
    "beperking bij de kansinput zit en niet bij de markt. Totaal 25 van 425 credits."
)

res = json.load(open("tmp-run/ra8_results.json"))
odds = json.load(open("tmp-run/ra8_odds.json"))
s3 = json.load(open("tmp-run/ra8_stage3.json"))
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
        "run": "A", "run_date": DAY,
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
state = load_or_start("a", date.fromisoformat(DAY))
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
    # Een competitie waarin GEEN enkel duel de datadekkingspoort haalde, is niet geanalyseerd
    # maar buiten datadekking gevallen (§5). Dat geldt vandaag voor de Champions League: zes
    # duels, alle zes kruis-grens, nul doorgerekend.
    doorgerekend = [m for m in ms if m["tier"] != "NONE"]
    entry = {"status": "GEANALYSEERD" if doorgerekend else "BUITEN DATADEKKING", "matches": []}
    if not doorgerekend:
        entry["reden"] = (f"{len(ms)} wedstrijd(en) vandaag, geen enkele met een bruikbare "
                          f"onafhankelijke kansinput op het niveau waarop gespeeld wordt — "
                          f"zie 'reden' per duel")
    for m in ms:
        e = {"match": m["match"], "match_id": m["match_id"], "tier": m["tier"],
             "bet": bool(m.get("bet")), "kickoff_nl": m["kickoff_nl"], "kickoff_utc": m["kickoff_utc"],
             "markets_checked": m["markets_checked"], "lambdas": m.get("lambdas"),
             "per_market": m.get("per_market"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "understat", "verplaatst", "poort8_geblokkeerd", "afgekapt",
                  "seizoensweging", "odds_1x2", "odds_1x2_best", "beste_prijs_winst_pct",
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
          open("tmp-run/ra8_short.json", "w"), ensure_ascii=False)
