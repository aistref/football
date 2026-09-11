"""Stage 6 — vastleggen: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-11"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-11T04:10:00+02:00"

TOELICHTING = (
    "11 wedstrijden op de runlijst vandaag, in 10 van de 21 competities. De elf andere hadden "
    "niets op de kalender - de Premier League, de Primeira Liga, de Scottish Premiership, alle "
    "drie de Europese toernooien en alle vijf de nationale bekers. Dat is GEEN WEDSTRIJD, geen "
    "storing: het is de eerste speelronde na de interlandbreak van september, en die begint "
    "vrijdagavond met een duel per competitie. De cap van 55 (vrijdag) is bij lange na niet "
    "geraakt: nul duels afgekapt, de hele kalender is doorgerekend. "
    "Negen van de elf duels kwamen door de datadekkingspoort - 4 FULL en 5 LIGHT - en zijn over "
    "alle zes de markten doorgerekend: samen 161 selecties, nul bets. Twee duels vielen op NONE: "
    "Besiktas - Erzurumspor FK en FC Kobenhavn - AC Horsens, allebei omdat de promovendus buiten "
    "het gemeten bereik van de omrekening viel (zie omrekeningen). "
    "De inkoop was deze run maximaal breed. Alle tien competities hebben een sportkey, alle tien "
    "kregen de bulk-aanroep (h2h + spreads + totals) en alle elf duels kregen BTTS. Daarmee zijn "
    "alle zes de markten in alle tien competities meegenomen, en is de marktbalans-controle van "
    "par. 1a niet krap maar volledig geslaagd: 10 op 10 met zowel een uitkomst- als een "
    "doelpuntenmarkt. Een eenzijdige uitkomst kan vandaag dus niet uit de portemonnee komen. "
    "Van de 161 selecties vielen er 156 af op poort 1 (edge) en 5 op poort 2 (odds buiten de "
    "band 1.30-6.00). Poort 8 hield op de herijkte schaal niets tegen; poort 5 en 6 kwamen niet "
    "eens aan bod, want geen enkele selectie haalde de edge-drempel. "
    "Slechts 6 van de 161 selecties hebben uberhaupt een positieve herijkte edge, en vier daarvan "
    "liggen binnen de koersband. De hoogste binnen de band staat op +1.02 pp (Venezia - "
    "Fiorentina, 1X2 Venezia @3.205, LIGHT, drempel 16.0). De twee die er nog boven staan - "
    "Willem II winst @18.15 (+1.95) en het gelijkspel @9.75 (+1.28) bij AZ Alkmaar - zijn koersen "
    "ver buiten de band, precies het gebied waar par. 5a zegt dat de kansschatting te "
    "onnauwkeurig is om edge zinvol te noemen. "
    "Ruw zou de routine naar drie dingen hebben gekeken en er alsnog niets mee hebben gedaan: "
    "Willem II +2.25 @2.10 (+11.80), BTTS nee bij Union Berlin - Schalke 04 @2.62 (+11.07) en "
    "Under 3 in datzelfde duel @1.83 (+10.61). Alle drie zijn LIGHT, en 16.0 halen ze geen van "
    "drieen. Er is dus ook op de ruwe schaal geen bet, en geen enkele regel zonder_herijking. "
    "Vier FULL-selecties kwamen ruw wel boven de 8.0 uit en sneuvelden op een andere poort: "
    "Rennes - Marseille Over 3 (+8.59) en Rakow - Motor Lublin Over 3 (+8.10) op poort 5 (de twee "
    "methodes wijzen tegengesteld), en bij KV Mechelen - Anderlecht zowel 1X2 thuis (+8.11) als "
    "Double Chance 1X (+8.21) op poort 8 (KV Mechelen is de underdog onder de ondergrens van "
    "0.35). Herijkt staan die vier op -2.55 tot +0.80, dus de poorten en de correctie wijzen hier "
    "dezelfde kant op. Omdat geen van de vier de herijkte NEAR-drempel van 3.0 haalt, levert deze "
    "run geen enkele near_miss en dus geen nieuwe schaduwpick. "
    "De vroeg-seizoenscorrectie staat er vandaag veel beter voor dan gisteren: x1.0799, gepoold "
    "over 47 speeldagen in tien competities in plaats van over een enkele. Dat is de ruimste "
    "steekproef sinds de correctie bestaat, en hij dooft zichtbaar uit (ruwe verhouding 1.0935, "
    "afgevlakt naar 1.0799). "
    "De beste-prijs-inkoop leverde gemiddeld +6.83% betere koers op dan het BetExplorer-"
    "marktgemiddelde (mediaan +5.20%, bereik +4.28% tot +19.23%). Die uitschieter is AZ Alkmaar - "
    "Willem II, waar de boeken het ver oneens zijn over hoe groot het gat tussen Eredivisie en "
    "Eerste Divisie is. "
    "De fit van par. 1g staat na de twee afwikkelingen van vanochtend op 615 afgerekende gevallen "
    "(a=0.911, b=-0.438, trefkans 41.5% tegen een geclaimd gemiddelde van 51.8%). Die tien "
    "procentpunt scheefstand is precies wat vandaag het verschil maakt tussen ruwe edges rond de "
    "+10 en herijkte edges rond de nul."
)

OMREKENINGEN = {
    "aanleiding": (
        "Geen kruis-grens deze run - er staat geen Europees duel op de kalender. Wel zeven "
        "binnenlandse omrekeningen: zes promovendi en een degradant. Promovendi: Venezia (Serie B "
        "-> Serie A), Schalke 04 (2. Bundesliga -> Bundesliga), Willem II (Eerste Divisie -> "
        "Eredivisie), Erzurumspor FK (1. Lig -> Super Lig), AC Horsens (1. Division -> Superliga) "
        "en Wisla Krakow (I Liga -> Ekstraklasa). Degradant: West Ham United (Premier League -> "
        "Championship), omgerekend met convert_relegated. Vijf van de zeven vielen binnen het "
        "gemeten bereik en leveren een LIGHT-duel op; een omgerekende ploeg is nooit FULL, dus "
        "daar geldt 16.0 pp in plaats van 8.0."),
    "naamkoppeling": (
        "Geen enkele ploeg liep vast op de naamkoppeling: ra_names.py koppelde alle elf duels bij "
        "Fotmob, en alle negen doorgerekende ook bij The Odds API en BetExplorer. Alle negen "
        "hebben dus een kalibratieblok (par. 6e)."),
    "toegepast_op": ["Venezia", "Schalke 04", "West Ham United", "Willem II", "Wisla Krakow"],
    "geweigerd": [
        "Erzurumspor FK (Besiktas - Erzurumspor FK): omgerekende verdediging 0.483 buiten het "
        "gemeten bereik 0.497-1.124 van de Turkse conversie (eigen meting 31 aug 2026, n=27) -> "
        "NONE, geen bet. Erzurumspor kreeg in de 1. Lig zo weinig tegen dat de omrekening hem "
        "buiten alles tilt wat bij eerdere Turkse promovendi is waargenomen.",
        "AC Horsens (FC Kobenhavn - AC Horsens): omgerekende aanval 0.860 buiten het gemeten "
        "bereik 0.989-1.747 van de Deense conversie (eigen meting 31 aug 2026, n=18) -> NONE, "
        "geen bet. Horsens promoveerde met een aanval die zwakker is dan die van elke Deense "
        "promovendus in de meetreeks, en buiten dat bereik is er geen meting.",
    ],
}

CREDITBRON = (
    "suggest_cap(19500, 20) = 487 - 19.500 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 500 gebruikt deze maand), 20 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(487, 10) gaf 10 spreads / 10 totals, oftewel alle tien inkoopbare competities "
    "kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus de "
    "bulk-aanroep (h2h + spreads + totals, par. 1a) is voor alle tien gedaan: vijf van de zes "
    "markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde gemeten over de negen doorgerekende duels gemiddeld +6.83% "
    "betere koers op (mediaan +5.20%). BTTS is voor alle elf duels gekocht. De marktbalans-"
    "controle van par. 1a slaagt volledig en ruim: alle tien competities hebben zowel een "
    "uitkomstmarkt als een doelpuntenmarkt, dus 10 op 10 - geen enkele scheefheid in de uitkomst "
    "kan vandaag aan de inkoop liggen. Totaal 41 van 487 credits in 21 aanroepen; 19.459 over."
)

res = json.load(open("tmp-run/ra11_results.json"))
odds = json.load(open("tmp-run/ra11_odds.json"))
s3 = json.load(open("tmp-run/ra11_stage3.json"))
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
          open("tmp-run/ra11_short.json", "w"), ensure_ascii=False)
