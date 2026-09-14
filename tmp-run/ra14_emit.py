"""Stage 6 — vastleggen: picks.jsonl, run-state. Run A 14 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-14"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-14T04:12:00+02:00"

TOELICHTING = """Maandag 14 september: 11 wedstrijden op de runlijst, in 7 van de 21 competities. De veertien andere hadden niets op de kalender - Bundesliga, Ligue 1, Championship, Eredivisie, de Belgische Pro League, de Scottish Premiership, alle drie de Europese toernooien en alle vijf de nationale bekers. Dat is GEEN WEDSTRIJD, geen storing. De cap van 40 (maandag) is niet in de buurt gekomen: nul duels afgekapt, de hele kalender is doorgerekend. Alle elf duels kwamen door de datadekkingspoort - tien FULL en een LIGHT, nul op NONE. Samen leverde dat 155 doorgerekende selecties op over alle zes de markten, en nul bets.

De inkoop kon vandaag geen scheve uitkomst veroorzaken. Alle zeven competities hebben een sportkey, alle zeven kregen de volle bulk-aanroep (h2h + spreads + totals), en de vier duels met een kandidaat-edge kregen daarbovenop BTTS: 25 van 565 credits. De marktbalans-controle slaagt daarmee volledig, 7 op 7 met zowel een uitkomst- als een doelpuntenmarkt.

Van de 155 selecties vielen er op de herijkte schaal 140 af op poort 1 (edge), 10 op poort 2 (koers buiten de band 1.30-6.00) en 5 alleen op de herijking. Op de ruwe schaal ziet dezelfde verdeling er anders uit, en dat is de informatieve versie: 132 op edge, 10 op de koers, 6 op poort 7 (context), 2 op poort 8 (underdog) en 5 die alle acht poorten haalden. Poort 5 en 6 hielden deze run niets tegen.

Negen selecties hebben een positieve herijkte edge, vijf daarvan binnen de koersband. De hoogste staat op +4.82 pp: Parma winst bij Como @17.66 - en die valt af op poort 2, want de koers ligt ver boven MAX_ODDS. De hoogste binnen de band is Parma +1.5 @2.25 met +4.60 pp tegen een drempel van 8.0.

Op de ruwe schaal zijn er 63 positieve edges, en twee duels zouden zonder de herijking wel een bet hebben opgeleverd: Como - Parma (Under 3 @1.79, ruw +11.19) en Gaziantep FK - Fenerbahce (Over 2.5 @1.77, ruw +9.20). Herijkt staan die twee op -1.80 en -3.75. Ze staan als schaduwpick met failed_gate = herijking in het logboek.

Wat deze run apart zet staat onderaan bij Bevindingen. Twee duels waren op de ruwe schaal een bet geweest en werden niet door de herijking maar door poort 7 tegengehouden - Villarreal - Real Betis en Radomiak Radom - Piast Gliwice - en in beide gevallen mist juist de thuisploeg, de kant waar het model op wilde spelen, de meeste selectiewaarde. Die twee verdwijnen uit elke reeks: ze halen de NEAR-drempel op de herijkte schaal niet en komen dus niet in het schaduwlogboek. En de vroeg-seizoenscorrectie schiet vandaag over, tegengesteld aan gisteren."""

OMREKENINGEN = {
    "aanleiding": (
        "Geen kruis-grens deze run - er staat geen Europees duel op de kalender. Wel een "
        "binnenlandse omrekening: Maritimo staat niet in de Primeira Liga-stand van 2025/2026 "
        "maar in die van Liga Portugal 2, en promotion.convert rekent hem om met de eigen meting "
        "van 31 aug 2026 voor het paar Primeira Liga / Liga Portugal 2 (x0.615 aanval, x1.504 "
        "verdediging). Relatieve aanval 1.203 en verdediging 0.698 over 34 duels worden daarmee "
        "0.740 en 1.050, allebei binnen het gemeten bereik. Een omgerekende ploeg is nooit FULL, "
        "dus Moreirense - Maritimo is het enige LIGHT-duel van de run en heeft een drempel van "
        "16.0 pp in plaats van 8.0."),
    "toegepast_op": ["Marítimo"],
    "geweigerd": [],
}

CREDITBRON = (
    "suggest_cap(19232, 17) = 565 - 19.232 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 768 gebruikt deze maand), 17 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(565, 7) gaf 7 spreads / 7 totals, oftewel alle zeven inkoopbare competities "
    "kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus de bulk-"
    "aanroep (h2h + spreads + totals, par. 1a) is voor alle zeven gedaan: vijf van de zes "
    "markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde over de elf duels gemiddeld +6.79% betere koers op (mediaan "
    "+5.90%, bereik +3.76% tot +13.12%); in 52 van de 155 doorgerekende selecties stond de beste "
    "prijs bij een beurs en is er met net_price gerekend. BTTS is daarna in een tweede ronde "
    "gekocht voor de vier duels met een kandidaat-edge - zie par. 1a stap 2. Totaal 21 credits "
    "aan de bulk plus 4 aan BTTS = 25 van 565; 19.207 over."
)

res = json.load(open("tmp-run/ra14_results.json"))
odds = json.load(open("tmp-run/ra14_odds.json"))
s3 = json.load(open("tmp-run/ra14_stage3.json"))
uplift = json.load(open("tmp-run/ra14_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["duur"]["gestart"] = "2026-09-14T02:10:15+00:00"   # tijdstempel van de sessiemap
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
