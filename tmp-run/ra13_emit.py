"""Stage 6 — vastleggen: picks.jsonl, run-state. Run A 13 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-13"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-13T04:18:00+02:00"

TOELICHTING = (
    "Zondag 13 september: 36 wedstrijden op de runlijst, in 12 van de 21 competities. De negen "
    "andere hadden niets op de kalender - de Scottish Premiership, alle drie de Europese "
    "toernooien en alle vijf de nationale bekers. Dat is GEEN WEDSTRIJD, geen storing. De cap van "
    "55 (zondag) is niet geraakt: nul duels afgekapt, de hele kalender is doorgerekend. "
    "Voor het eerst sinds deze routine bestaat kwamen ALLE wedstrijden door de datadekkingspoort: "
    "24 FULL en 12 LIGHT, nul op NONE. Dat is geen toeval maar het gevolg van de twaalf "
    "omrekeningen - elf promovendi en een degradant - die deze run alle twaalf binnen het gemeten "
    "bereik vielen. Samen leverde dat 507 doorgerekende selecties op over alle zes de markten, en "
    "nul bets. "
    "De inkoop kon vandaag geen scheve uitkomst veroorzaken. Alle twaalf competities hebben een "
    "sportkey, alle twaalf kregen de volle bulk-aanroep (h2h + spreads + totals), en de dertien "
    "duels met een kandidaat-edge kregen daarbovenop BTTS: 49 van 535 credits. De marktbalans-"
    "controle slaagt daarmee volledig, 12 op 12 met zowel een uitkomst- als een doelpuntenmarkt. "
    "Van de 507 selecties vielen er 456 af op poort 1 (edge), 32 op poort 2 (koers buiten de band "
    "1.30-6.00), 6 op poort 7 (context), 3 op poort 8 (underdog) en 10 alleen op de herijking. "
    "Poort 5 en 6 hielden deze run niets tegen. "
    "Drieenvijftig selecties hebben een positieve herijkte edge, 40 daarvan binnen de koersband. "
    "De hoogste staat op +14.05 pp: Brest +1.5 tegen Paris Saint-Germain @2.25 - en die is door "
    "poort 8 tegengehouden, want de markt geeft Brest 9.2% tegen 76.2% voor PSG, ver onder de "
    "ondergrens van 35%. Daarna komen Gil Vicente +2.25 @1.88 (+12.37) en Levante +2.5 @1.89 "
    "(+10.14), allebei tegengehouden door poort 7: bij Gil Vicente en bij Levante mist juist de "
    "gespeelde kant de meeste selectiewaarde. De hoogste die op niets anders dan de edge zelf "
    "sneuvelde is SonderjyskE winst bij Lyngby @5.41 met +9.48 pp tegen een LIGHT-drempel van "
    "16.0. "
    "Op de ruwe schaal zijn er 212 positieve edges, en vier duels zouden zonder de herijking wel "
    "een bet hebben opgeleverd: Levante - Barcelona (BTTS ja @1.91, ruw +16.13), Pogon Szczecin - "
    "Wieczysta Krakow (Over 2.5 @1.70, ruw +19.44), Benfica - Gil Vicente (Under 3.5 @1.65, ruw "
    "+11.57) en Club Brugge - Royal Antwerp (Under 3.5 @1.87, ruw +9.09). Die vier staan als "
    "schaduwpick met failed_gate = herijking in het logboek; herijkt staan ze op +3.39, +7.43, "
    "-1.06 en -3.48. "
    "Twee dingen uit deze run verdienen aandacht en staan onderaan bij Bevindingen. Ten eerste een "
    "naamkoppelingsfout die is opgespoord en gerepareerd: de ligatuur ae werd door norm() "
    "weggegooid in plaats van uitgeschreven, waardoor Nordsjaelland - AGF bij geen enkele "
    "prijsbron terug te vinden was. Ten tweede: de vroeg-seizoenscorrectie doet vandaag precies "
    "wat ze moet doen, terwijl ze gisteren nog overschoot - dezelfde controle, tegengesteld teken, "
    "en dat zegt iets over de meting en niet over de correctie."
)

OMREKENINGEN = {
    "aanleiding": (
        "Geen kruis-grens deze run - er staat geen Europees duel op de kalender. Wel twaalf "
        "binnenlandse omrekeningen, het hoogste aantal in een Run A tot nu toe: elf promovendi "
        "(Coventry City, Monza, Malaga, Deportivo A Coruna, Elversberg, Troyes, Le Mans, Kortrijk, "
        "Amed Sportif, Lyngby en Wieczysta Krakow) en een degradant (Wolverhampton Wanderers, "
        "omgerekend met convert_relegated). Alle twaalf vielen binnen het gemeten bereik van hun "
        "divisiepaar, dus alle twaalf leveren een LIGHT-duel op; een omgerekende ploeg is nooit "
        "FULL, dus daar geldt 16.0 pp in plaats van 8.0. Nul afwijzingen betekent ook nul duels op "
        "NONE - voor het eerst."),
    "naamkoppeling": (
        "Een ploeg liep wel vast, en dat is Bevinding 1: Nordsjaelland - AGF. Fotmob schrijft "
        "Nordsjaelland met de ligatuur ae, en norm() in ra_names.py gooide die weg in plaats van "
        "hem uit te schrijven, zodat nordsjlland tegenover nordsjaelland stond bij The Odds API en "
        "BetExplorer. Samen met AGF tegenover Aarhus zakte het paar onder de vloer van best_pair. "
        "Beide oorzaken zijn gerepareerd en de analyse is daarna opnieuw gedraaid; alle 36 duels "
        "hebben nu een kalibratieblok (par. 6e) en een 1X2-marktgemiddelde."),
    "toegepast_op": ["Coventry City", "Monza", "Málaga", "Deportivo A Coruña", "Elversberg",
                     "Troyes", "Le Mans", "Wolverhampton Wanderers", "Kortrijk", "Amed Sportif",
                     "Lyngby", "Wieczysta Kraków"],
    "geweigerd": [],
}

CREDITBRON = (
    "suggest_cap(19310, 18) = 535 - 19.310 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 690 gebruikt deze maand), 18 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(535, 12) gaf 12 spreads / 12 totals, oftewel alle twaalf inkoopbare competities "
    "kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus de bulk-"
    "aanroep (h2h + spreads + totals, par. 1a) is voor alle twaalf gedaan: vijf van de zes "
    "markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde over de 36 duels gemiddeld +7.73% betere koers op (mediaan "
    "+5.94%, bereik +3.70% tot +24.19%); in 49 van de 102 gevallen stond die beste prijs bij een "
    "beurs en is er met net_price gerekend. BTTS is daarna in een tweede ronde gekocht voor de "
    "dertien duels met een kandidaat-edge - zie par. 1a stap 2 en Bevinding 3. Totaal 36 credits "
    "aan de bulk plus 13 aan BTTS = 49 van 535; 19.261 over."
)

res = json.load(open("tmp-run/ra13_results.json"))
odds = json.load(open("tmp-run/ra13_odds.json"))
s3 = json.load(open("tmp-run/ra13_stage3.json"))
uplift = json.load(open("tmp-run/ra13_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["duur"]["gestart"] = "2026-09-13T02:09:30+00:00"   # tijdstempel van de sessiemap
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
    "POORT_8_UNDERDOG": "licht sinds 5 sep 2026 — sides.UNDERDOG_FLOOR = 0.35",
    "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
    "HERIJKING": "recalibrate.apply, fit op uitslagen", "SETTLE_FALLBACK_HOURS": 2.0,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": TOELICHTING,
    "omrekeningen": OMREKENINGEN,
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = {**vs, "controle_tegen_de_markt": uplift}
state["credits"] = {
    "plafond": odds["cap"], "gebruikt": odds.get("guard_totaal"),
    "split_budget": odds["split"],
    "bron": CREDITBRON,
    "markten_gekocht": {"bulk_h2h_spreads_totals": odds["bought"]["spreads"],
                        "h2h": odds["bought"]["h2h"], "totals": odds["bought"]["totals"],
                        "btts": odds["bought"]["btts"]},
    "btts_kandidaat_edge": odds.get("btts_kandidaat_edge"),
    "guard_report": odds["guard"], "guard_report_btts": odds.get("guard_btts"),
}
by_comp = {}
for m in matches:
    by_comp.setdefault(m["competition"], []).append(m)
for comp, ms in by_comp.items():
    doorgerekend = [m for m in ms if m["tier"] != "NONE"]
    entry = {"status": "GEANALYSEERD" if doorgerekend else "BUITEN DATADEKKING", "matches": []}
    if not doorgerekend:
        entry["reden"] = (f"{len(ms)} wedstrijd(en) vandaag, geen enkele met een bruikbare "
                          f"onafhankelijke kansinput op het niveau waarop gespeeld wordt")
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
                  "beste_prijs_winst_pct", "zonder_herijking", "kandidaat_edge"):
            if m.get(k): e[k] = m[k]
        if m.get("reason"): e["reden"] = m["reason"]
        if m.get("near_miss"): e["near_miss"] = m["near_miss"]
        if m.get("calibration"): e["calibration"] = m["calibration"]
        entry["matches"].append(e)
    mark(state, comp, entry)
for comp, v in fx.items():
    if not v["matches"]:
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": [],
                           "reden": "niets op de kalender vandaag (Fotmob-daglijst)"})
save(state)
print("run-state weggeschreven:", len(state["competitions"]), "competities")
