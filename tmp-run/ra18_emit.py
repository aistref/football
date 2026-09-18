"""Stage 6 — vastleggen: picks.jsonl, run-state. Run A 18 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-18"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-18T04:20:00+02:00"

TOELICHTING = """Vrijdag 18 september: 12 wedstrijden op de runlijst, in 11 van de 21 competities - de eerste dag sinds lang waarop bijna de hele binnenlandse runlijst tegelijk speelt. Elf competities openden hun weekend met een vrijdagavondduel (Premier League, Serie A, La Liga, Bundesliga, Ligue 1, Championship, Eredivisie, de Belgische Pro League, de Super Lig, de Deense Superliga en de Ekstraklasa met twee duels), en de tien overige stonden leeg: Primeira Liga, Schotse Premiership, Champions League, Europa League, Conference League, FA Cup, League Cup, Coppa Italia, KNVB Beker en DFB Pokal. Dat is GEEN WEDSTRIJD, geen storing - de Europese speelweek was woensdag en donderdag afgelopen. De cap van 55 (vrijdag) kwam niet in de buurt: nul duels afgekapt. Alle twaalf duels kwamen door de datadekkingspoort - acht FULL en vier LIGHT, geen enkele NONE. Samen 171 doorgerekende selecties over alle zes de markten, en nul bets.

Vier ploegen zijn omgerekend uit de divisie eronder, en die vier bepalen welke duels LIGHT zijn: Monza (Serie B naar Serie A), Lyngby (1. Division naar de Deense Superliga), Wieczysta Krakow en het hele duel Wisla Krakow - Slask Wroclaw (allebei uit de I Liga naar de Ekstraklasa). Alle vier vielen binnen het gemeten bereik van conversion_in_range. Een omgerekende ploeg is nooit FULL, en LIGHT betekent een drempel van 16.0 procentpunt in plaats van 8.0 - met de herijking van par. 1g daar nog overheen.

Een correctie in de pipeline, en het is er een die een duel redde in plaats van er een te kosten. De regel van 15 september ("staan beide ploegen in dezelfde divisie onder de basis, reken het duel daar door") gold sinds die datum voor elke competitie. Vandaag sloeg hij aan op Wisla Krakow - Slask Wroclaw: twee ploegen die allebei uit de I Liga zijn gepromoveerd en dus allebei niet in de Ekstraklasa-stand van vorig seizoen staan. Het duel werd daardoor in de I Liga doorgerekend - op het doelpuntenniveau van de divisie eronder, terwijl ze vanavond in de Ekstraklasa spelen - en liep bovendien vast omdat de I Liga geen xG heeft. Par. 4 verantwoordt die regel expliciet met "een beker heeft zelf geen stand en dus geen competitiegemiddelde om ploegen op te normaliseren", en een competitie heeft dat wel. De regel is daarom teruggebracht tot waar hij voor bedoeld is: alleen bekers. Twee promovendi in een competitieduel gaan gewoon allebei door promotion.convert naar het niveau waarop ze spelen.

De inkoop kon vandaag geen scheve uitkomst veroorzaken. Alle elf competities hebben een sportkey en alle elf kregen de volle bulk-aanroep (h2h + spreads + totals), en de vijf duels met een kandidaat-edge kregen daarbovenop BTTS: 38 van 734 credits. De marktbalans-controle slaagt zo ruim als hij kan slagen, 11 op 11 met zowel een uitkomst- als een doelpuntenmarkt. De beste prijs leverde over de twaalf duels een mediaan van +5.80% op tegenover het BetExplorer-marktgemiddelde; het gemiddelde van +9.86% zegt vandaag niets, want daar zit Union Berlin bij Bayern in (+53.34%, een koers van 39.22 tegen een marktgemiddelde rond 25) en die selectie valt sowieso buiten de koersband.

Van de 171 selecties vielen er op de herijkte schaal 159 af op poort 1 (edge), 7 op poort 2 (koers buiten de band 1.30-6.00) en 5 alleen op de herijking. Op de ruwe schaal ziet dezelfde verdeling er anders uit: 149 op edge, 7 op de koers, 4 op poort 7 (context), 3 op poort 5 (tweede methode), 3 op poort 8 (underdog), en vijf selecties die alle acht poorten haalden. Die vijf komen uit drie duels en leveren drie rijen zonder_herijking op - een per wedstrijd, zoals par. 5a voorschrijft.

Poort 7 hield voor het eerst in dagen werkelijk iets tegen, en allebei de keren om een reden die een mens ook zou noemen. Bij Brentford - Chelsea heeft Brentford drie dagen rust tegen zes bij Chelsea, dus drie selecties op de thuisploeg gingen eruit. Bij Widzew Lodz - Wieczysta Krakow mist Widzew 28% van zijn selectiewaarde tegen 3% bij de tegenstander - Shehu, Cheng en Gazibegovic - en dat blokkeerde de selectie op de thuisploeg. Beide gevallen binden alleen op de ruwe schaal: op de herijkte schaal was de edge er toch al af.

Veertien selecties hebben een positieve herijkte edge. De hoogste staat op +4.50 pp (Widzew Lodz -1 @2.70) tegen een LIGHT-drempel van 16.0, en de hoogste op een FULL-duel is +3.71 pp (Lens wint bij Monaco @3.597, na 2% beurscommissie) tegen een drempel van 8.0. Ruw zijn er 79 positieve edges met +17.52 pp bovenaan (Over 3 bij Wisla Krakow - Slask Wroclaw). Dat verschil van veertien procentpunt tussen de twee schalen is precies wat par. 1g beschrijft en is vandaag opnieuw de hele verklaring voor nul bets.

Openstaand punt van deze run: de vroeg-seizoenscorrectie loopt achter op de kalender. Gemeten tegen de de-vigde marktkans op P(Over 2.5) over de acht duels met een 2.5-lijn aan beide kanten staat het model zonder correctie op -0.41 pp gemiddeld (absolute fout 3.47 pp) en met de correctie x1.0834 op +4.61 pp (absolute fout 4.89 pp). De correctie maakt de schatting vandaag dus aantoonbaar slechter. Dat is te begrijpen: de factor wordt gepoold over elf competities die tussen 3 en 8 speeldagen ver zijn, terwijl par. 3 Stage 5 hem juist bedoelt als uitdovende correctie voor de eerste speeldagen. Dit is een meting tegen de markt en dus uitsluitend een diagnose (par. 1d, par. 6e) - de correctie mag hier niet op worden afgeregeld. Maar drie dagen met hetzelfde teken zou wel betekenen dat de uitdoofcurve van early_season_uplift te traag is, en dat is een vraag die op uitkomsten te beantwoorden is."""

OMREKENINGEN = {
    "aanleiding": (
        "Vier promovendi-omrekeningen vandaag, geen enkele kruis-grens (de Europese toernooien "
        "speelden niet). Monza uit de Serie B naar de Serie A (x0.601/1.528, gemeten paar "
        "I1/I2), Lyngby uit de 1. Division naar de Deense Superliga (x0.624/1.807, eigen meting "
        "van 31 aug 2026), en drie Poolse ploegen uit de I Liga naar de Ekstraklasa "
        "(x0.680/1.743, eigen meting): Wieczysta Krakow, Wisla Krakow en Slask Wroclaw. Alle "
        "vier de duels vielen binnen het gemeten bereik van conversion_in_range - Wieczysta "
        "Krakow met een omgerekende verdediging van 0.929 precies op de bovengrens. Alle vier "
        "zijn LIGHT: een omgerekende ploeg is nooit FULL, want de omrekening haalt de "
        "systematische fout eruit en niet de onzekerheid. Wisla Krakow - Slask Wroclaw is het "
        "duel waarvoor de bekerregel van 15 september vandaag is teruggebracht tot bekers - zie "
        "de toelichting; zonder die correctie was het duel in de I Liga doorgerekend."),
    "toegepast_op": ["Monza", "Lyngby", "Wieczysta Kraków", "Wisła Kraków", "Śląsk Wrocław"],
    "geweigerd": [],
}

CREDITBRON = (
    "suggest_cap(19119, 13) = 734 - 19.119 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 881 gebruikt deze maand), 13 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(734, 11) gaf 11 spreads / 11 totals, oftewel alle elf inkoopbare competities "
    "kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus de "
    "bulk-aanroep (h2h + spreads + totals, par. 1a) is voor alle elf gedaan: vijf van de zes "
    "markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde over de twaalf duels een mediaan van +5.80% betere koers op "
    "(bereik +4.03% tot +53.34%; die bovenste is de outsiderkant bij Bayern en valt buiten de "
    "koersband). BTTS is daarna in een tweede ronde gekocht voor de vijf duels met een "
    "kandidaat-edge - zie par. 1a stap 2. Totaal 33 credits aan de bulk plus 5 aan BTTS = 38 "
    "van 734; 19.081 over."
)

res = json.load(open("tmp-run/ra18_results.json"))
odds = json.load(open("tmp-run/ra18_odds.json"))
s3 = json.load(open("tmp-run/ra18_stage3.json"))
uplift = json.load(open("tmp-run/ra18_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["duur"]["gestart"] = "2026-09-18T02:09:00+00:00"   # tijdstempel van de sessiemap
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
