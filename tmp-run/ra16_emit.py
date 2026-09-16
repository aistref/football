"""Stage 6 — vastleggen: picks.jsonl, run-state. Run A 16 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-16"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-16T04:25:00+02:00"

TOELICHTING = """Woensdag 16 september: 17 wedstrijden op de runlijst, in 3 van de 21 competities. La Liga speelde een midweekse speelronde (4 duels), de Europa League opende zijn competitiefase (9 duels) en de League Cup had de derde ronde (4 duels). De achttien andere competities hadden niets op de kalender - Premier League, Serie A, Bundesliga, Ligue 1, Championship, Eredivisie, Primeira Liga, de Belgische Pro League, de Super Lig, de Schotse Premiership, de Deense Superliga, de Ekstraklasa, de Champions League, de Conference League, de FA Cup, de Coppa Italia, de KNVB Beker en de DFB Pokal. Dat is GEEN WEDSTRIJD, geen storing. De cap van 40 (woensdag) kwam niet in de buurt: nul duels afgekapt, de hele kalender is doorgerekend. Veertien duels kwamen door de datadekkingspoort - vier FULL en tien LIGHT - en drie kwamen op NONE uit. Samen 188 doorgerekende selecties over alle zes de markten, en nul bets.

Die tien LIGHT-duels zijn bijna allemaal Europees, en dat drukt het hele beeld van vandaag. Zeven van de negen Europa League-duels zijn met scripts/interleague.py naar de Europese schaal omgerekend, en een omgerekende ploeg is nooit FULL. LIGHT betekent een drempel van 16.0 procentpunt in plaats van 8.0, en daar gaat de herijking van par. 1g nog overheen. Twee Europese duels haalden de omrekening niet: Ararat Armenia - Sparta Prague en Bayer Leverkusen - NK Celje. Voor Armenie en Slovenie is geen competitiefactor gemeten - onder de 40 Europese duels is die factor vrijwel volledig door de regularisatie bepaald en dus een aanname in plaats van een meting. Dat is de poort van par. 4, niet een storing, en het is ook precies waar het model het minst weet.

Het derde NONE-duel zit in de beker: Fleetwood Town - Sheffield United. De League Cup gebruikt de Premier League 2025/2026 als basis. Sheffield United komt uit de Championship en is een omrekening, maar Fleetwood Town speelt twee divisies lager en over twee divisies is er geen gemeten factor. De regel van 15 september die Peterborough - Barnsley redde helpt hier niet: die geldt alleen als beide ploegen in dezelfde divisie onder de basis spelen, en dat is hier juist niet zo.

De inkoop kon vandaag geen scheve uitkomst veroorzaken. Alle drie de competities hebben een sportkey, alle drie kregen de volle bulk-aanroep (h2h + spreads + totals), en de vier duels met een kandidaat-edge kregen daarbovenop BTTS: 13 van 637 credits. De marktbalans-controle slaagt volledig, 3 op 3 met zowel een uitkomst- als een doelpuntenmarkt.

Van de 188 selecties vielen er op de herijkte schaal 172 af op poort 1 (edge), 10 op poort 2 (koers buiten de band 1.30-6.00) en 6 alleen op de herijking. Op de ruwe schaal ziet dezelfde verdeling er anders uit: 165 op edge, 10 op de koers, 4 op poort 7 (context), 2 op poort 8 (underdog), 1 op poort 5 (tweede methode) en 6 die alle acht poorten haalden. Poort 6 (robuustheid) hield deze run niets tegen.

Zeventien selecties hebben een positieve herijkte edge, dertien daarvan binnen de koersband. De hoogste van allemaal staat op +8.44 pp - Osasuna wint bij Atletico Madrid @9.43 - en die valt af op poort 2, want de koers ligt ver boven MAX_ODDS. De hoogste binnen de band is Under 2.5 bij Olympiacos - Jagiellonia @2.32 met +7.10 pp, tegen een LIGHT-drempel van 16.0.

Op de ruwe schaal zijn er 83 positieve edges, en drie duels zouden zonder de herijking wel een bet hebben opgeleverd: Atletico Madrid - Osasuna (Under 2.5 @2.28, ruw +9.52), Olympiacos - Jagiellonia Bialystok (Under 3 @1.76, ruw +17.57) en Everton - Wolverhampton (Under 2.75 @1.93, ruw +8.97). Herijkt staan die drie op -2.47, +4.24 en -4.02. Ze staan als schaduwpick met failed_gate = herijking in het logboek. Wat opvalt: alle drie zijn een doelpuntenmarkt en alle drie een Under. Dat is dezelfde richting als de uplift-controle hieronder, die het model 4.89 pp onder de markt zet op P(Over 2.5) - het model verwacht vandaag stelselmatig minder doelpunten dan de bookmakers.

En Hapoel Beer Sheva - Dinamo Zagreb werd niet in Beer Sheva gespeeld maar in de Arena Giulesti in Boekarest. check_venue zag dat en zette relocated. Thuisvoordeel is de aanname waar het model het zwaarst op leunt, dus dat hoort in het rapport te staan - ook al gaat de poort gewoon open."""

OMREKENINGEN = {
    "aanleiding": (
        "Twee soorten omrekening vandaag, en allebei in bulk. Kruis-grens (par. 4, 8 sep 2026): "
        "negen Europa League-duels, waarvan er zeven zijn omgerekend naar de Europese schaal met "
        "scripts/interleague.py en twee niet. Geslaagd zijn Omonia - Celta Vigo, Milan - Benfica, "
        "Anderlecht - Lyon, Hapoel Beer Sheva - Dinamo Zagreb, Olympiacos - Jagiellonia, Sturm "
        "Graz - Rennes en Sunderland - AZ Alkmaar; alle veertien ploegen vielen binnen het "
        "gemeten bereik van de omgerekende aanval en verdediging. Geweigerd zijn Ararat Armenia "
        "(ARM) en NK Celje (SVN): voor die twee landen is geen competitiefactor gemeten, want "
        "onder interleague.MIN_MATCHES = 40 Europese duels is de factor vrijwel volledig door de "
        "regularisatie bepaald. Ararat Armenia - Sparta Prague en Bayer Leverkusen - NK Celje "
        "komen daarmee op NONE. Binnenlands (par. 4, promovendi): drie geslaagde omrekeningen - "
        "Deportivo A Coruna en Racing Santander uit LaLiga2 naar La Liga (x0.661/1.498, gemeten "
        "paar SP1/SP2) en Coventry City uit de Championship naar de Premier League-basis van de "
        "League Cup (x0.541/1.783, gemeten paar E0/E1). Alle drie binnen het gemeten bereik, en "
        "alle drie LIGHT: een omgerekende ploeg is nooit FULL. Geweigerd: Fleetwood Town speelt "
        "twee divisies onder de Premier League-basis van de League Cup, en over twee divisies is "
        "er geen gemeten factor - Fleetwood Town - Sheffield United wordt NONE."),
    "toegepast_op": ["Deportivo A Coruña", "Racing Santander", "Coventry City",
                     "Omonia Nicosia", "Celta Vigo", "Milan", "Benfica", "Anderlecht", "Lyon",
                     "Hapoel Beer Sheva", "Dinamo Zagreb", "Olympiacos", "Jagiellonia Białystok",
                     "Sturm Graz", "Rennes", "Sunderland", "AZ Alkmaar"],
    "geweigerd": ["Ararat Armenia (ARM, geen gemeten competitiefactor)",
                  "NK Celje (SVN, geen gemeten competitiefactor)",
                  "Fleetwood Town (twee divisies onder de bekerbasis)"],
}

CREDITBRON = (
    "suggest_cap(19153, 15) = 637 - 19.153 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 847 gebruikt deze maand), 15 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(637, 3) gaf 3 spreads / 3 totals, oftewel alle drie de inkoopbare competities "
    "kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus de "
    "bulk-aanroep (h2h + spreads + totals, par. 1a) is voor alle drie gedaan: vijf van de zes "
    "markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde over de veertien duels met beide prijzen gemiddeld +7.01% "
    "betere koers op (bereik +3.56% tot +22.09%). BTTS is daarna in een tweede ronde gekocht "
    "voor de vier duels met een kandidaat-edge - zie par. 1a stap 2. Totaal 9 credits aan de "
    "bulk plus 4 aan BTTS = 13 van 637; 19.140 over."
)

res = json.load(open("tmp-run/ra16_results.json"))
odds = json.load(open("tmp-run/ra16_odds.json"))
s3 = json.load(open("tmp-run/ra16_stage3.json"))
uplift = json.load(open("tmp-run/ra16_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["duur"]["gestart"] = "2026-09-16T02:08:44+00:00"   # tijdstempel van de sessiemap
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
                  "poort8_ruw", "basis_per_wedstrijd",
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
