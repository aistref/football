"""Stage 6 — vastleggen: picks.jsonl, run-state. Run A 15 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-15"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-15T04:20:00+02:00"

TOELICHTING = """Dinsdag 15 september: 18 wedstrijden op de runlijst, in 7 van de 21 competities. De veertien andere hadden niets op de kalender - Premier League, Serie A, Bundesliga, Ligue 1, Primeira Liga, de Belgische Pro League, de Super Lig, de Deense Superliga, alle drie de Europese toernooien en de FA Cup, de KNVB Beker en de DFB Pokal. Dat is GEEN WEDSTRIJD, geen storing. De cap van 40 (dinsdag) is niet in de buurt gekomen: nul duels afgekapt, de hele kalender is doorgerekend. Vijftien duels kwamen door de datadekkingspoort - twaalf FULL en drie LIGHT - en drie kwamen op NONE uit. Samen leverde dat 197 doorgerekende selecties op over alle zes de markten, en nul bets.

De drie NONE-duels zitten alle drie in een beker, en alle drie op hetzelfde soort gat: een ploeg die te ver onder de basisdivisie speelt. De League Cup gebruikt de Premier League 2025/2026 als basis, dus een Championship-ploeg is een omrekening en een League One-ploeg twee divisies - en over twee divisies is er geen gemeten factor. Peterborough United, Barnsley en Reading komen alle drie uit League One, en dat maakt Peterborough - Barnsley en Reading - Brentford onrekenbaar. Bij Genoa - Sudtirol ligt het anders: de omrekening bestaat wel (Serie A / Serie B, x0.601/1.528) maar Sudtirol komt met een relatieve aanval van 0.781 onder de gemeten ondergrens van 1.004 uit. Dat is conversion_in_range als poort en niet als aantekening - de Coventry-val.

De inkoop kon vandaag geen scheve uitkomst veroorzaken. Alle zeven competities hebben een sportkey, alle zeven kregen de volle bulk-aanroep (h2h + spreads + totals), en de negen duels met een kandidaat-edge kregen daarbovenop BTTS: 30 van 599 credits. De marktbalans-controle slaagt daarmee volledig, 7 op 7 met zowel een uitkomst- als een doelpuntenmarkt.

Van de 197 selecties vielen er op de herijkte schaal 177 af op poort 1 (edge), 12 op poort 2 (koers buiten de band 1.30-6.00) en 8 alleen op de herijking. Op de ruwe schaal ziet dezelfde verdeling er anders uit, en dat is de informatieve versie: 166 op edge, 12 op de koers, 10 op poort 8 (underdog), 1 op poort 7 (context) en 8 die alle acht poorten haalden. Poort 5 en 6 hielden deze run niets tegen.

Veertien selecties hebben een positieve herijkte edge, acht daarvan binnen de koersband. De hoogste staat op +8.73 pp: Elche wint van Real Madrid @15.21 - en die valt af op poort 2, want de koers ligt ver boven MAX_ODDS. De hoogste binnen de band is Elche +1.75 @2.20 met +6.38 pp tegen een drempel van 8.0, en dat is meteen de enige near_miss van de run.

Op de ruwe schaal zijn er 87 positieve edges, en drie duels zouden zonder de herijking wel een bet hebben opgeleverd: Deportivo Alaves - Valencia (Over 2.5 @2.28, ruw +8.37), Hibernian - Kilmarnock (Hibernian -1.25 @2.06, ruw +10.33) en Motherwell - Aberdeen (Motherwell wint @1.85, ruw +10.69). Herijkt staan die drie op -3.20, -2.16 en -2.29. Ze staan als schaduwpick met failed_gate = herijking in het logboek.

Wat deze run apart zet staat onderaan bij Bevindingen. De vier grootste ruwe edges van de dag - drie handicaps op Elche tegen Real Madrid en een op Willem II bij Ajax, alle vier tussen +17.8 en +19.4 pp - zijn niet door de herijking maar door poort 8 tegengehouden. Dat is precies het geval waar par. 1e voor gemaakt is, en het laat zien dat de twee remmen elkaar hier niet dubbelop tegenhouden maar om beurten. En Rayo Vallecano - Espanyol werd niet in Vallecas gespeeld maar in Leganes; check_venue zag dat en zette relocated."""

OMREKENINGEN = {
    "aanleiding": (
        "Geen kruis-grens deze run - er staat geen Europees duel op de kalender. Wel vier "
        "binnenlandse omrekeningen, waarvan drie geslaagd en een geweigerd. Geslaagd: Lincoln "
        "City uit League One naar de Championship (x0.673/1.638, gemeten paar E1/E2), Willem II "
        "uit de Eerste Divisie naar de Eredivisie (x0.614/1.564, eigen meting van 31 aug 2026) en "
        "Ipswich Town uit de Championship naar de Premier League-basis van de League Cup "
        "(x0.541/1.783, gemeten paar E0/E1). Alle drie vielen binnen het gemeten bereik, en alle "
        "drie leveren daarmee LIGHT op met een drempel van 16.0 pp in plaats van 8.0 - een "
        "omgerekende ploeg is nooit FULL. Geweigerd: Sudtirol komt uit Serie B met een relatieve "
        "aanval van 0.781 en het gemeten bereik voor I1/I2 begint pas bij 1.004, dus "
        "conversion_in_range gaat dicht en Genoa - Sudtirol wordt NONE. Daarnaast drie ploegen "
        "waarvoor de omrekening niet eens bestaat: Peterborough United, Barnsley en Reading "
        "spelen in League One, twee divisies onder de Premier League-basis van de League Cup, en "
        "over twee divisies is er geen gemeten factor."),
    "toegepast_op": ["Lincoln City", "Willem II", "Ipswich Town"],
    "geweigerd": ["Südtirol (buiten bereik)", "Peterborough United (twee divisies)",
                  "Barnsley (twee divisies)", "Reading (twee divisies)"],
}

CREDITBRON = (
    "suggest_cap(19197, 16) = 599 - 19.197 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 803 gebruikt deze maand), 16 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(599, 7) gaf 7 spreads / 7 totals, oftewel alle zeven inkoopbare competities "
    "kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus de bulk-"
    "aanroep (h2h + spreads + totals, par. 1a) is voor alle zeven gedaan: vijf van de zes "
    "markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde over de veertien duels met beide prijzen gemiddeld +7.13% "
    "betere koers op (bereik +3.30% tot +16.97%); in 30 van de 197 doorgerekende selecties "
    "stond de beste prijs bij een beurs en is er met net_price gerekend. BTTS is daarna in een "
    "tweede ronde gekocht voor de negen duels met een kandidaat-edge - zie par. 1a stap 2. "
    "Totaal 21 credits aan de bulk plus 9 aan BTTS = 30 van 599; 19.167 over."
)

res = json.load(open("tmp-run/ra15_results.json"))
odds = json.load(open("tmp-run/ra15_odds.json"))
s3 = json.load(open("tmp-run/ra15_stage3.json"))
uplift = json.load(open("tmp-run/ra15_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["duur"]["gestart"] = "2026-09-15T02:08:30+00:00"   # tijdstempel van de sessiemap
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
