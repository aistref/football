"""Stage 6 — vastleggen: picks.jsonl, run-state. Run A 19 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-19"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-19T04:05:00+02:00"

TOELICHTING = """Zaterdag 19 september, en dit is de drukste dag die deze routine tot nu toe heeft gedraaid: 57 wedstrijden in 13 van de 21 competities, van 13:30 tot 21:30. Dertien binnenlandse competities speelden allemaal (de Championship met negen duels, de Premier League, Bundesliga, Ligue 1 en de Schotse Premiership elk vijf, Serie A, La Liga, Eredivisie, Primeira Liga, de Belgische Pro League en de Super Lig elk vier, de Ekstraklasa drie en de Deense Superliga een), en de acht overige stonden leeg: de drie Europese toernooien plus alle vijf de bekers. Dat is GEEN WEDSTRIJD, geen storing - de Europese competitiefase begint pas volgende week en de bekerrondes liggen deze week stil.

Voor het eerst sinds de verhoging van 5 september knelt de cap. MAX_DEEP_ANALYSES staat op 55 voor zaterdag, er stonden er 57, dus twee duels zijn AFGEKAPT: St. Johnstone - Falkirk en Lommel - KV Mechelen. Beide vielen af op precies dezelfde datarijkdom als het duel dat het nog wel haalde (Lincoln City - Swansea City, score 5.0 tegen 5.0) - de tie-break was het aantal beschikbare markten en daarna de aftrap. Dat is exact wat de meting van 5 september voorspelt: de sortering scheidt niet, dus afkappen kost naar rato en niet de slechtste groep. Twee van de 57 is 3,5%, en beide waren LIGHT-duels met een omgerekende promovendus.

Van de 57 duels zijn er 40 FULL en 16 LIGHT, en precies een kwam op NONE uit: Newcastle United - Hull City. Twee LIGHT-duels vielen buiten de cap, dus binnen de cap staan er 40 FULL, 14 LIGHT en 1 NONE, en zijn er 54 werkelijk doorgerekend. Hull Citys omgerekende verdediging komt op 1.964 uit en dat ligt buiten het gemeten bereik van conversion_in_range (0.284-1.022 aan de invoerkant, waar Hull op 1.102 staat). Dat is de Coventry-val waar par. 4 voor waarschuwt, en de poort deed wat hij moet doen: geen meting op het niveau waarop gespeeld wordt, dus geen bet.

Zeventien duels hebben een omgerekende ploeg, en dat is meteen de grootste omrekenoperatie tot nu toe: achttien ploegen uit zes gemeten divisieparen plus vijf eigen metingen van 31 augustus. Twee ervan gaan naar beneden in plaats van naar boven - West Ham United en Burnley, allebei gedegradeerd uit de Premier League naar de Championship - en die tak gebruikt gap_for(E0,E1,down) met x1.830/0.634. Alle achttien op een na vielen binnen het gemeten bereik.

Samen 773 doorgerekende selecties over alle zes de markten, en nul bets. Op de herijkte schaal vielen er 735 af op poort 1 (edge), 24 op poort 2 (koers buiten de band 1.30-6.00) en 14 alleen op de herijking. Op de ruwe schaal ziet dezelfde verdeling er heel anders uit: 711 op edge, 24 op de koers, 18 op poort 7 (context), 6 op poort 8 (underdog), en veertien selecties die alle acht poorten haalden. Die veertien komen uit acht duels en leveren acht rijen zonder_herijking op, een per wedstrijd zoals par. 5a voorschrijft.

Het verschil tussen de twee schalen is vandaag groter dan ooit en het is de hele verklaring voor nul bets. Binnen de speelbare koersband staat de hoogste herijkte edge op +5.41 pp (Sevilla +2.5 bij Barcelona @1.71, FULL) tegen een drempel van 8.0; ruw stond diezelfde selectie op +19.11 pp. Dat is een verschil van bijna veertien procentpunt op een en dezelfde bet. De hoogste LIGHT-edge is +3.77 pp (Venezia wint van Lazio @4.04) tegen een drempel van 16.0 - daar is niet eens discussie over. In totaal zijn er 26 positieve herijkte edges tegen 304 positieve ruwe. Par. 1g beschrijft precies dit: het model zegt gemiddeld 51% waar het 41% gebeurt, en wie op de grootste geclaimde edge selecteert, selecteert op de grootste modelfout.

Een selectie haalde de drempel wel, maar niet de koersband: Sevilla wint van Barcelona op @14.23, herijkte edge +8.48 pp. MAX_ODDS staat op 6.00 omdat de kansschatting daarboven te onnauwkeurig is om edge zinvol te noemen, en dit is er een goede illustratie van - een herijkte kans van 15,5% op een thuisoverwinning tegen Barcelona is precies het gebied waar par. 0 zegt dat het model niets meer meet.

Poort 7 hield vandaag achttien selecties tegen op de ruwe schaal, poort 8 zes. Die zes staan verdeeld over drie duels (Tottenham - Aston Villa, Ajax - Excelsior en OH Leuven - RAAL La Louviere) en gaan als poort8_ruw het schaduwlogboek in. Op de herijkte schaal hield poort 8 niets tegen, want daar was de edge er toch al af - precies het patroon dat de notitie van 15 september beschrijft en de reden dat de reeks nooit groot genoeg is geworden. De poort vervalt over zes dagen, op 25 september, volgens het besluit van de gebruiker van 18 september.

De inkoop kan de uitkomst niet hebben veroorzaakt. Alle dertien competities hebben een sportkey, alle dertien kregen de volle bulk-aanroep (h2h + spreads + totals), en de vijftien duels met een kandidaat-edge kregen daarbovenop BTTS: 54 van 793 credits. De marktbalans-controle slaagt zo ruim als hij kan slagen, 13 op 13 met zowel een uitkomst- als een doelpuntenmarkt. De beste prijs leverde over 51 duels een mediaan van +4.96% op tegenover het BetExplorer-marktgemiddelde (gemiddeld +5.68%, hoogste +16.37% bij Sporting CP - Arouca).

Het openstaande punt van gisteren is vandaag gemeten en wijst de andere kant op. De vroeg-seizoenscorrectie staat op x1.0861 (gepoold 1.0943 over 84 speeldagen in 13 competities). Tegen de de-vigde marktkans op P(Over 2.5), over 40 duels met een 2.5-lijn aan beide kanten: zonder correctie -2.71 pp gemiddeld met een absolute fout van 4.42 pp, met correctie +2.66 pp met een absolute fout van 4.21 pp. De correctie maakt de schatting vandaag dus iets beter in plaats van slechter, terwijl ze gisteren op acht duels aantoonbaar slechter uitviel. Wat in beide gevallen hetzelfde is: het teken klapt van onder de markt naar boven de markt, dus de correctie schiet door. Met 40 duels in plaats van acht is dit de betrouwbaardere van de twee metingen. Dit blijft een meting tegen de markt en dus uitsluitend een diagnose (par. 1d, par. 6e) - er mag niet op worden afgeregeld."""

OMREKENINGEN = {
    "aanleiding": (
        "Zeventien duels met een omgerekende ploeg, achttien ploegen in totaal, geen enkele "
        "kruis-grens (de Europese toernooien speelden niet). Zes gemeten divisieparen bij "
        "football-data.co.uk: E0/E1 omhoog voor Ipswich Town, Hull City en Coventry City en "
        "omlaag voor West Ham United en Burnley (x1.830/0.634), E1/E2 voor Cardiff City en "
        "Lincoln City, I1/I2 voor Venezia, SP1/SP2 voor Racing Santander, F1/F2 voor Troyes en "
        "Le Mans, en SC0/SC1 voor St. Johnstone. Daarnaast vijf eigen metingen van 31 aug 2026 "
        "op Fotmob: ADO Den Haag en Cambuur plus Willem II (NED x0.614/1.564), Maritimo "
        "(POR x0.615/1.504), Lommel (BEL x0.696/1.604) en Corum FK (TUR x0.708/1.497). "
        "Zeventien van de achttien vielen binnen het gemeten bereik van conversion_in_range. "
        "De uitzondering is Hull City: een relatieve verdediging van 1.102 ligt boven de "
        "bovengrens 1.022 van E0/E1 omhoog, dus Newcastle United - Hull City is NONE geworden "
        "en niet doorgerekend. Alle omgerekende duels zijn LIGHT: een omgerekende ploeg is "
        "nooit FULL, want de omrekening haalt de systematische fout eruit en niet de "
        "onzekerheid. Twee ploegen gaan naar BENEDEN in plaats van omhoog - West Ham United en "
        "Burnley, gedegradeerd uit de Premier League - en dat is de tak die op 30 aug is "
        "toegevoegd en vandaag voor het eerst twee duels tegelijk raakt."),
    "toegepast_op": ["Ipswich Town", "Hull City", "Coventry City", "Venezia",
                     "Racing Santander", "Troyes", "Le Mans", "Cardiff City",
                     "West Ham United", "Burnley", "Lincoln City", "ADO Den Haag", "Cambuur",
                     "Willem II", "Mar\u00edtimo", "Lommel", "\u00c7orum FK", "St. Johnstone"],
    "geweigerd": [
        "Hull City - omgerekende verdediging buiten het gemeten bereik van E0/E1 omhoog "
        "(1.102 tegen een bovengrens van 1.022); Newcastle United - Hull City daarmee NONE."],
}

CREDITBRON = (
    "suggest_cap(19066, 12) = 793 - 19.066 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 934 gebruikt deze maand), 12 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(793, 13) gaf 13 spreads / 13 totals, oftewel alle dertien inkoopbare "
    "competities kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus "
    "de bulk-aanroep (h2h + spreads + totals, par. 1a) is voor alle dertien gedaan: vijf van de "
    "zes markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde over 51 duels een mediaan van +4.96% betere koers op "
    "(gemiddeld +5.68%, hoogste +16.37% bij Sporting CP - Arouca). BTTS is daarna in een tweede "
    "ronde gekocht voor de vijftien duels met een kandidaat-edge - zie par. 1a stap 2. Totaal "
    "39 credits aan de bulk plus 15 aan BTTS = 54 van 793; 19.012 over."
)

res = json.load(open("tmp-run/ra19_results.json"))
odds = json.load(open("tmp-run/ra19_odds.json"))
s3 = json.load(open("tmp-run/ra19_stage3.json"))
uplift = json.load(open("tmp-run/ra19_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["duur"]["gestart"] = "2026-09-19T02:09:00+00:00"   # tijdstempel van de sessiemap
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
