"""Stage 6 — vastleggen: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-10"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-10T04:05:00+02:00"

TOELICHTING = (
    "7 wedstrijden op de runlijst vandaag, in 2 van de 21 competities: de Champions League (6) "
    "en de Primeira Liga (1). De andere negentien hadden niets op de kalender - dat is GEEN "
    "WEDSTRIJD, geen storing. De cap van 40 (donderdag) is bij lange na niet geraakt: nul duels "
    "afgekapt. Zes duels kwamen door de datadekkingspoort (1 FULL, 5 LIGHT) en zijn over alle zes "
    "de markten doorgerekend: samen 96 selecties, nul bets. "
    "Wat deze run bijzonder maakt is hoe schoon de uitkomst is: van de 90 selecties binnen de "
    "koersband heeft er NUL een positieve herijkte edge. De hoogste staat op -0.80 pp (Como - RB "
    "Leipzig, BTTS nee @2.60), en dat is meteen ook de hoogste op de ruwe schaal (+9.93 pp). Er "
    "is dus geen enkele near_miss, geen enkele selectie die op poort 8 sneuvelde en geen enkele "
    "regel zonder_herijking - niet omdat er poorten dichtsloegen, maar omdat er domweg nergens "
    "een voordeel te vinden was. Alle 90 vielen af op poort 1 (edge), de overige 6 op poort 2 "
    "(odds buiten de band 1.30-6.00; Sabah FK @33.34 en het gelijkspel @11.50 bij Manchester "
    "United, en Lens +1 @1.25). "
    "Het patroon is precies wat par. 1g voorspelt. Ruw zou de routine vandaag naar de "
    "doelpuntenmarkten hebben gekeken - Como BTTS nee +9.93, Under 3.5 +9.52, PSV - Shakhtar "
    "Over 3.5 +9.11, Slavia - Lens 1X2 Lens +9.45 - en na de herijking blijft daar niets van "
    "over. Geen van die ruwe cijfers haalde overigens de LIGHT-drempel van 16.0 sowieso, dus "
    "zelfs zonder de correctie was dit een run met nul bets geweest. "
    "Het enige FULL-duel, Estrela da Amadora - Braga, blijft ver van de drempel van 8.0: de "
    "hoogste herijkte edge daar is -1.08 pp (1X2 Estrela @5.606), ruw +4.59 pp. "
    "De vroeg-seizoenscorrectie draait vandaag op EEN competitie (Primeira Liga, 5 speeldagen) "
    "en komt daardoor op x0.9985 uit - vrijwel neutraal. Dat is geen defect maar het gevolg van "
    "de kalender: de Champions League levert geen xG-waarneming voor de pooling, want die duels "
    "draaien op de omgerekende Europese schaal. Met een steekproef van een competitie is de "
    "correctie zwak onderbouwd; noteer dat, en verwacht hem terug zodra de nationale competities "
    "dit weekend weer spelen. "
    "De fit van par. 1g staat op 613 afgerekende gevallen (a=0.934, b=-0.444, trefkans 41.4% "
    "tegen een geclaimd gemiddelde van 51.8%) - hetzelfde getal als gisteren, want er is sinds "
    "de fit van 7 sep niets nieuws afgewikkeld dat de fit verschuift."
)

OMREKENINGEN = {
    "aanleiding": (
        "Alleen kruis-grens deze run. De zes Champions League-duels zijn stuk voor stuk door "
        "interleague.convert_team gehaald, dat de binnenlandse aanval- en verdedigingsverhouding "
        "van 2025/2026 omrekent naar de Europese schaal en de twee ploegen daarna in "
        "interleague.reference_league() tegen elkaar zet. Vijf duels lukten, een niet. Binnen een "
        "land was er niets om te rekenen: beide ploegen van Estrela da Amadora - Braga stonden "
        "gewoon in de Primeira Liga van vorig seizoen, dus geen promovendi- of "
        "degradantenomrekening. Een omgerekende ploeg is nooit FULL: die vijf duels staan op "
        "LIGHT, waar 16.0 pp edge nodig is in plaats van 8.0."),
    "naamkoppeling": (
        "Geen enkele ploeg liep vast op de naamkoppeling: ra_names.py koppelde alle zeven duels "
        "bij Fotmob en alle zes doorgerekende ook bij The Odds API en BetExplorer. Alle zes "
        "doorgerekende duels hebben dus een kalibratieblok (par. 6e)."),
    "toegepast_op": ["Fenerbahce", "AS Roma", "PSV Eindhoven", "Shakhtar Donetsk", "Como",
                     "RB Leipzig", "Manchester United", "Sabah FK", "Slavia Prague", "RC Lens"],
    "geweigerd": [
        "Bayern Munchen (Bayern Munchen - Bodo/Glimt): omgerekende aanval 2.742 buiten het "
        "waargenomen bereik 0.585-2.432 van interleague.in_range -> NONE, geen bet. Dit is de "
        "Coventry-val waar die poort voor bestaat: Bayern is binnenlands zo dominant (aanval "
        "2.218 tegen het Bundesliga-gemiddelde) dat de Duitse competitiefactor hem buiten alles "
        "tilt wat in de 2111 gemeten Europese duels is waargenomen. Buiten dat bereik is er geen "
        "meting, en dan is er ook geen kansinput op het niveau waarop gespeeld wordt.",
    ],
}

CREDITBRON = (
    "suggest_cap(19520, 21) = 464 - 19.520 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 480 gebruikt deze maand), 21 dagen tot de maandwissel, 2 runs per dag. Het "
    "plafond is ruim genoeg voor 3 credits per competitie, dus de bulk-aanroep (h2h + spreads + "
    "totals, par. 1a) is voor beide competities met een sportkey gedaan: dat levert vijf van de "
    "zes markten in een keer en zet 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Gemeten over de zes doorgerekende duels leverde dat gemiddeld +8.27% "
    "betere koers op dan het marktgemiddelde (mediaan +6.38%; de uitschieter is Manchester "
    "United - Sabah FK met +21.04%, waar de spreiding tussen boeken op een zware favoriet groot "
    "is). BTTS is voor alle 6 duels met dekking gekocht. De marktbalans-controle van par. 1a "
    "slaagt volledig: beide competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt, "
    "dus 2 op 2. Totaal 12 van 464 credits."
)

res = json.load(open("tmp-run/ra10_results.json"))
odds = json.load(open("tmp-run/ra10_odds.json"))
s3 = json.load(open("tmp-run/ra10_stage3.json"))
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
        for k in ("promovendi", "kruis_grens", "understat", "verplaatst", "poort8_geblokkeerd",
                  "afgekapt", "seizoensweging", "odds_1x2", "odds_1x2_best",
                  "beste_prijs_winst_pct", "zonder_herijking"):
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
          open("tmp-run/ra10_short.json", "w"), ensure_ascii=False)
