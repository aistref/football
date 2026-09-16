"""Run B, 16 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/.

Zelfde opzet als `rb12_emit.py`. Nul bets, dus `picks.jsonl` krijgt geen regel; alles wat de
run heeft gemeten gaat naar `data/run-state/2026-09-16-run-b.json`, waar report.py, shadow.py,
calibration.py, ctxlog.py en toplist.py het uit lezen.
"""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-16"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-16T05:25:00+02:00"

TOELICHTING = (
 '"Drie duels, en geen ervan kwam in de buurt." Uit de runlijst van zeventien competities speelden '
 'er vandaag twee: de Allsvenskan met AIK - Mjällby en de Swiss Super League met Lugano - St. '
 'Gallen en Thun - Servette, alle drie om 19:00 Nederlandse tijd. De andere vijftien stonden leeg, '
 'en dat is geen storing: het is woensdag 16 september, midden in de Europese speelweek, en de '
 'binnenlandse competities uit deze runlijst spelen hun ronde in het weekend. Veertien van de '
 'vijftien staan simpelweg niet op de Fotmob-daglijst; de Kosovo Superleague komt daar nog altijd '
 'helemaal niet in voor - ongewijzigd sinds 13 aug 2026, dus opnieuw geen storing van vandaag. De '
 'cap stond op 40 (woensdag) tegen drie duels, dus MAX_DEEP_ANALYSES heeft deze run geen enkele '
 'analyse gekost.\n\n'
 'Alle drie zijn volledig doorgerekend op FULL: Fotmob heeft xG voor beide competities in zowel '
 'het vorige als het lopende seizoen, en alle zes ploegen staan in de stand. Vijf van de zes '
 'markten deden mee (BTTS is niet gekocht, zie hieronder), samen 51 selecties, en nul bets. De '
 'hoogste herijkte edge van de dag is -3.60 pp op 1X2 - Thun wint @ 2.86 bruto bij Betfair (2.823 '
 'na commissie), tegen een drempel van 8.0. Negatief, dus geen enkele selectie van deze run staat '
 'zelfs maar boven de marktkans; er is daarom ook geen enkele near_miss, want die begint bij +3.0 '
 'pp op de herijkte schaal. Vijftig van de 51 selecties vielen op dezelfde poort af - de edge - en '
 'de eenenvijftigste viel buiten de koersband van 1.30 tot 6.00.\n\n'
 'Ook op de RUWE schaal - het model zoals het tot 5 september rekende, zonder de herijking - haalt '
 'geen enkele selectie de drempel. De hoogste is diezelfde Thun-winst op +5.96 pp, ruim onder de '
 '8.0. Er gaat dus geen enkele rij met failed_gate = "herijking" naar het schaduwlogboek, en poort '
 '8 heeft op geen van beide schalen iets tegengehouden dat de edge-poort niet al had gesloten. Wat '
 'de dag wel laat zien is hoe ver de twee methodes uit elkaar liggen: bij Thun - Servette staat de '
 'splitsmethode op +30.47 pp en de xG-methode op -0.16 pp voor precies dezelfde selectie, en bij '
 'AIK - Mjällby is dat +23.87 tegen -0.05. De weging van 80/20 uit paragraaf 1f haalt dat grotendeels '
 'weg - en dat is precies waarvoor die weging is gemeten, want de splitsmethode is aantoonbaar de '
 'scheefste van de twee.\n\n'
 'Poort 7 zou twee van de drie thuisploegen sowieso hebben gesloten. AIK mist dertien spelers, '
 'samen 50% van zijn selectiewaarde, tegen 3% bij Mjällby; Lugano mist 52% tegen 41% bij St. '
 'Gallen. Bij Thun - Servette staat de poort aan beide kanten open, al speelde Servette drie dagen '
 'geleden nog (druk programma). Geen van de drie duels is verplaatst: alle drie worden gespeeld in '
 'het eigen stadion van de genoteerde thuisploeg.\n\n'
 'De fit van vanochtend staat op a=0.857, b=-0.464 over 671 afgerekende gevallen, met een '
 'gemiddelde geclaimde kans van 51.9% tegen een werkelijke trefkans van 40.8% - elf procentpunt te '
 'optimistisch. Dat is de scheefstand die van elke schatting af gaat, en ze kostte vandaag tussen '
 'de 4.5 en de 13.5 procentpunt edge per selectie - hoe hoger de geclaimde kans, hoe meer eraf.'
)

MARKTBALANS = (
 'GEHAALD, en ruimer dan gisteren: beide competities die vandaag speelden hebben een sportkey bij '
 'The Odds API (soccer_sweden_allsvenskan en soccer_switzerland_superleague) en kregen allebei de '
 'volle bulk-aanroep van 3 credits (h2h + spreads + totals). Twee van de twee, dus. Daaruit kwamen '
 'vijf van de zes markten voor elk van de drie duels: 1X2 op de beste prijs (3 selecties per duel), '
 'Asian Handicap (5 lijnen per duel), Draw No Bet uit de 0.0-lijn (2), Double Chance uit de '
 '+0.5-lijn (1) en Over/Under (4 tot 8 lijnen). Er is dus zowel een uitkomstmarkt als een '
 'doelpuntenmarkt in beide competities ingekocht en de controle van paragraaf 1a slaagt met marge.\n\n'
 'BTTS is de enige markt op nul, en dat is niet het geld maar het criterium: de tweede ronde koopt '
 'die markt alleen voor duels die al een kandidaat-edge tonen op de ruwe of de herijkte schaal '
 '(paragraaf 1a stap 2), en vandaag deed geen van de drie duels dat. Het plafond stond op 637 credits '
 'en er is 6 van uitgegeven; 631 bleef ongebruikt. De inkoop was deze run dus aantoonbaar niet de '
 'beperkende factor, en er is geen enkele competitie die vandaag om een ontbrekende sportkey '
 'buiten de boot viel - de Run B-competities zonder sportkey speelden geen van alle.'
)

VROEG_SEIZOEN_NOOT = (
 'Factor 1.0377, gepoold 1.0481 over 29 speeldagen in twee competities, gemeten in xG. De '
 'Allsvenskan scoorde vorig seizoen 1.440 xG per ploeg per duel en staat dit seizoen na 21 '
 'speeldagen op 1.491; de Swiss Super League 1.604 tegen 1.734 na 8 speeldagen. De prior trekt de '
 'gepoolde verhouding van 1.0481 terug naar 1.0377. Alles komt uit de stand bij Fotmob; er komt '
 'geen enkele bookmakerprijs aan te pas, dus paragraaf 2 en de waarschuwing bij early_season_uplift '
 'blijven gerespecteerd. Een kanttekening die erbij hoort: twee observaties is nog steeds een '
 'smalle basis, en de Allsvenskan is met 21 van de 30 speeldagen niet eens meer vroeg in het '
 'seizoen - daar hoort de correctie al bijna uitgedoofd te zijn, en met 1.035 op de eigen '
 'waarneming is ze dat ook zo ongeveer.'
)

CREDITBRON = (
 'suggest_cap(19140, 15) = 637 - 19.140 credits over volgens api_check.py van deze run (20K-plan, '
 '860 gebruikt deze maand), 15 dagen tot de maandwissel, 2 runs per dag. split_budget(637, 2) '
 'geeft 2 spreads / 2 totals bij twee inkoopbare competities, en omdat 3 x 2 = 6 ruim onder 637 '
 'ligt gaat de volle bulk door: h2h + spreads + totals in een aanroep per competitie. Uitgegeven: '
 '6 credits in 2 bulk-aanroepen; de tweede ronde kocht geen BTTS, want geen enkel duel toonde een '
 'kandidaat-edge. Totaal 6 van 637, nog 19.134 credits over.'
)

res = json.load(open("tmp-run/rb16_results.json"))
odds = json.load(open("tmp-run/rb16_odds.json"))
s3 = json.load(open("tmp-run/rb16_stage3.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("ł", "l").replace("ß", "ss").replace("Ø", "o")
    return re.sub(r"[^a-z0-9]", "", s.lower())

bets = sorted([m for m in matches if m.get("bet")], key=lambda m: -m["pick"]["score"])
MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
print(f"bets: {len(bets)} — MAX_SHORTLIST {MAX_SHORT}")
assert not bets, "deze run verwacht nul bets; pas rb16_emit.py aan als dat verandert"

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
    "POORT_8_UNDERDOG": "licht sinds 5 sep 2026 — sides.UNDERDOG_FLOOR = 0.35",
    "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
    "HERIJKING": "recalibrate.apply, fit op uitslagen", "SETTLE_FALLBACK_HOURS": 2.0,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": TOELICHTING,
    "marktbalans": MARKTBALANS,
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = {**vs, "noot": VROEG_SEIZOEN_NOOT}
state["credits"] = {
    "plafond": odds["cap"],
    # odds["spent"] is alleen de bulk-ronde; de BTTS-ronde van rb16_btts.py telt erbij op,
    # en `guard_totaal` is de enige plek waar die twee al bij elkaar staan.
    "gebruikt": odds["spent"] + len(odds["bought"]["btts"]),
    "guard_totaal": odds.get("guard_totaal"),
    "split_budget": odds["split"],
    "bron": CREDITBRON,
    "markten_gekocht": {"bulk_h2h_spreads_totals": odds["bought"]["spreads"],
                        "h2h": odds["bought"]["h2h"], "totals": odds["bought"]["totals"],
                        "btts": odds["bought"]["btts"]},
    "marktbalans": MARKTBALANS,
    "geen_sportkey": odds.get("geen_sportkey", []),
    "guard_report": odds["guard"],
}
by_comp = {}
for m in matches:
    by_comp.setdefault(m["competition"], []).append(m)
for comp, ms in by_comp.items():
    entry = {"status": "GEANALYSEERD", "matches": []}
    for m in ms:
        e = {"match": m["match"], "match_id": m["match_id"], "tier": m["tier"],
             "bet": bool(m.get("bet")), "kickoff_nl": m["kickoff_nl"], "kickoff_utc": m["kickoff_utc"],
             "markets_checked": m["markets_checked"], "lambdas": m.get("lambdas"),
             "per_market": m.get("per_market"), "eenheid": m.get("eenheid"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "understat", "verplaatst", "poort8_geblokkeerd", "poort8_ruw",
                  "basis_per_wedstrijd", "afgekapt",
                  "seizoensweging", "odds_1x2", "odds_1x2_best", "beste_prijs_winst_pct", "ou25",
                  "zonder_herijking"):
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
print("run-state weggeschreven")
