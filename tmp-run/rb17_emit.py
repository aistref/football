"""Stage 6 — vastleggen: picks.jsonl, run-state. Run B 17 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-17"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-17T05:05:00+02:00"

TOELICHTING = """Donderdag 17 september: een wedstrijd op de hele runlijst. Van de zeventien competities uit prompts/run-b.md had er precies een iets op de kalender - English League One, met AFC Wimbledon - Milton Keynes Dons om 21:00 Nederlandse tijd. De andere zestien stonden leeg. Dat is geen storing maar de kalender: het is donderdag in een Europese speelweek, en de binnenlandse competities en lagere divisies uit deze runlijst spelen hun ronde in het weekend. De Kosovo Superleague komt nog altijd helemaal niet op de Fotmob-daglijst voor - ongewijzigd sinds 13 aug 2026, dus opnieuw geen storing van vandaag. De cap stond op 40 (donderdag) tegen een duel, dus MAX_DEEP_ANALYSES heeft deze run geen enkele analyse gekost.

Dat ene duel is volledig doorgerekend, op LIGHT, en leverde nul bets uit elf selecties. LIGHT en niet FULL omdat Milton Keynes Dons vorig seizoen in League Two speelde: de ploeg is met scripts/promotion.py omgerekend van League Two naar League One, en een omgerekende ploeg is nooit FULL (par. 4). De omrekening zelf is gemeten en valt binnen het bereik - relatieve aanval 1.450 en verdediging 0.759 over 46 League Two-duels, omgerekend met het gemeten paar E2/E3 (x0.782 aanval, x1.375 verdediging) naar 1.134 en 1.044. LIGHT betekent een drempel van 16.0 procentpunt in plaats van 8.0, en daar gaat de herijking van par. 1g nog overheen.

Er was vandaag geen enkele selectie die ook maar boven de marktkans uitkwam. De hoogste herijkte edge van de dag staat op -6.09 procentpunt (Asian Handicap, MK Dons -1 @3.55), en dat is de best scorende van elf. Alle elf vielen af: tien op de edge-poort en een op de koersband, want Wimbledon +1 stond op 1.25 en de ondergrens is 1.30. Omdat geen enkele kandidaat positief uitkomt is er ook geen enkele near_miss - die begint bij +6.0 pp op de herijkte schaal voor LIGHT - en dus geen rij in het schaduwlogboek, geen poort-8-rij en geen rij zonder_herijking. Poort 5 (tweede methode), 6 (robuustheid), 7 (context) en 8 (underdog) hebben deze run niets tegengehouden; de edge-poort deed al het werk.

Ook op de ruwe schaal, zonder de herijking, verandert het beeld niet wezenlijk. Daar staan vier van de elf selecties positief, met +3.12 pp op Over 2.5 als hoogste - nog altijd ver onder de 16.0 die voor LIGHT geldt. Dit is dus niet een dag waarop de correctie van par. 1g een bet tegenhield, maar een dag waarop het model en de markt het gewoon met elkaar eens waren.

De inkoop kon vandaag geen scheve uitkomst veroorzaken, maar de marktbalans-controle slaagt wel met de kleinst mogelijke marge: er is maar een competitie, en die kreeg de volle bulk-aanroep (h2h + spreads + totals, 3 credits), dus er zit zowel een uitkomst- als een doelpuntenmarkt in de run - 1 op 1 voor allebei. Vijf van de zes markten deden mee: 1X2 op de beste prijs, Asian Handicap op vier lijnen, Draw No Bet op de 0.0-lijn en Over/Under op twee lijnen. Double Chance viel weg omdat er geen enkele plus-0.5-lijn in de spreads-respons zat, en BTTS is niet gekocht omdat dit duel geen kandidaat-edge toonde (par. 1a stap 2) - dat staat zo in markets_checked en niet als "opgevraagd maar niet genoteerd".

De beste prijs stond bij alle drie de 1X2-uitkomsten bij Betfair, en dat is een beurs: de gepubliceerde koersen zijn daarom doorgerekend met oddsapi.net_price (2% commissie over de nettowinst). Tegenover het BetExplorer-marktgemiddelde over drie boeken leverde dat +5.99% betere koers op - de winst die par. 1a beschrijft, ook op een dag dat er niets uit komt.

Een bevinding uit de code, en het is er een die een duel had kunnen kosten. De runlijst van Run B schrijft "English League One (ENG)"; promotion.TIER1 en TIER2 kennen die divisie onder haar eigen naam "League One (ENG)". Het analyseskelet van Run A zoekt die tabellen op met een rauwe TIER2.get(naam), en dan vindt hij voor deze runlijstnaam niets - met als gevolg dat MK Dons ten onrechte op NONE was uitgekomen terwijl E2/E3 gewoon gemeten in footballdata.MEASURED_GAPS staat. promotion.COMPETITION_ALIASES bestaat precies hiervoor en de docstring daar zegt het met zoveel woorden: vertaal altijd via _resolve en niet met een rauwe TIER2.get. Dat is nu ook gedaan in tmp-run/rb17_analyze.py. Het is dezelfde soort fout als die van 5 sep 2026, toen zestien duels op NONE kwamen door een ontbrekende sleutel in plaats van een ontbrekende meting - alleen deze keer een laag hoger, in het script dat de tabel opzoekt in plaats van in de tabel zelf.

De vroeg-seizoenscorrectie staat deze run op x1.0477, maar hij leunt op een enkele waarneming: League One is de enige competitie in de run en staat op 6 speeldagen (gepoold 1.1112). De controle tegen de markt die par. 3 Stage 5 vraagt, kon vandaag niet worden uitgevoerd: die eist twee ploegen die allebei een eigen rij in de stand van vorig seizoen hebben, en MK Dons heeft die niet - hun cijfers komen uit de omrekening. Dat staat zo in de run-state genoteerd; het is geen overgeslagen stap maar een meting met nul waarnemingen."""

OMREKENINGEN = {
    "aanleiding": (
        "Een omrekening vandaag, binnenlands (par. 4, promovendi). Milton Keynes Dons promoveerde "
        "uit League Two en staat daarom niet in de League One-stand van 2025/2026. "
        "promotion.convert rekent de ploeg om op het gemeten divisiepaar E2/E3 uit "
        "footballdata.MEASURED_GAPS: relatieve aanval 1.450 en verdediging 0.759 over 46 "
        "League Two-duels worden x0.782 respectievelijk x1.375 naar League One-niveau gebracht, "
        "wat uitkomt op 1.134 en 1.044. Beide vallen binnen het gemeten bereik (aanval "
        "0.976-1.547, verdediging 0.565-1.068 over n=43), dus conversion_in_range staat open en "
        "het duel is doorgerekend - op LIGHT, want een omgerekende ploeg is nooit FULL. "
        "AFC Wimbledon staat wel gewoon in de stand en is niet omgerekend."),
    "toegepast_op": ["Milton Keynes Dons"],
    "geweigerd": [],
    "sleutelfout_verholpen": (
        "De opzoeking van TIER1/TIER2 gebeurde in het analyseskelet met een rauwe "
        "TIER2.get(naam). De runlijstnaam 'English League One (ENG)' staat daar niet in - de "
        "tabellen kennen 'League One (ENG)' - dus zonder vertaling was MK Dons ten onrechte op "
        "NONE uitgekomen. Opgelost met promotion._resolve, precies zoals de docstring bij "
        "COMPETITION_ALIASES voorschrijft."),
}

CREDITBRON = (
    "suggest_cap(19122, 14) = 682 - 19.122 credits over volgens api_check.py van deze run "
    "(20K-plan, 878 gebruikt deze maand), 14 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(682, 1) gaf 1 spreads / 1 totals: er is maar een inkoopbare competitie in de "
    "run. Het plafond laat 3 credits per competitie ruimschoots toe, dus de bulk-aanroep "
    "(h2h + spreads + totals, par. 1a) is gedaan: vijf van de zes markten in een keer, en 1X2 op "
    "de beste prijs in plaats van op het BetExplorer-marktgemiddelde. Dat leverde +5.99% betere "
    "koers op over de drie uitkomsten, alle drie bij Betfair en dus na 2% beurscommissie "
    "gerekend. BTTS is niet gekocht: het enige duel toonde geen kandidaat-edge (par. 1a stap 2), "
    "niet op de herijkte en niet op de ruwe schaal. Totaal 3 van 682 credits; 19.119 over. "
    "Marktbalans-controle: 1 van 1 competitie heeft een uitkomstmarkt en 1 van 1 een "
    "doelpuntenmarkt - hij slaagt, maar met de kleinst mogelijke marge, omdat er maar een "
    "competitie speelt."
)

res = json.load(open("tmp-run/rb17_results.json"))
odds = json.load(open("tmp-run/rb17_odds.json"))
s3 = json.load(open("tmp-run/rb17_stage3.json"))
uplift = json.load(open("tmp-run/rb17_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
state["duur"]["start"] = "2026-09-17T02:55:00+00:00"   # tijdstempel van de sessiemap
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
