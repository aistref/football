"""Run B, 15 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/.

Zelfde opzet als `rb12_emit.py`. Nul bets, dus `picks.jsonl` krijgt geen regel; alles wat de
run heeft gemeten gaat naar `data/run-state/2026-09-15-run-b.json`, waar report.py, shadow.py,
calibration.py, ctxlog.py en toplist.py het uit lezen.
"""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-15"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-15T05:13:00+02:00"

TOELICHTING = (
 '"Een duel." Uit de hele runlijst van zeventien competities speelt er vandaag precies een: '
 'Grasshopper - Sion in de Swiss Super League, om 19:00 Nederlandse tijd in het Letzigrund. De '
 'andere zestien stonden leeg, en dat is geen storing: het is dinsdag 15 september, de Europese '
 'speelweek, en de binnenlandse competities uit deze runlijst spelen hun ronde in het weekend. '
 'Vijftien van de zestien staan simpelweg niet op de Fotmob-daglijst; de Kosovo Superleague komt '
 'daar nog altijd helemaal niet in voor - ongewijzigd sinds 13 aug 2026, dus opnieuw geen storing '
 'van vandaag. De cap stond op 40 (dinsdag) tegen een duel, dus MAX_DEEP_ANALYSES heeft deze run '
 'geen enkele analyse gekost.\n\n'
 'Dat ene duel is volledig doorgerekend op FULL: Fotmob heeft xG voor de Swiss Super League in '
 'zowel 2025/2026 als het lopende seizoen, en beide ploegen staan in de stand. Alle zes markten '
 'deden mee, samen 17 selecties, en nul bets. De hoogste herijkte edge van de dag is +2.03 pp op '
 '1X2 - Grasshopper wint @ 4.35 (Pinnacle), tegen een drempel van 8.0. Dat is niet net-aan maar '
 'ruim eronder, en er is dus ook geen enkele near_miss: die begint bij 3.0 pp.\n\n'
 'Wat deze dag wel laat zien is hoe ver de twee methodes uit elkaar kunnen liggen. Op de RUWE '
 'schaal staat diezelfde Grasshopper-winst op +9.25 pp en dus boven de drempel, maar die edge komt '
 'volledig van de xG-methode (+12.13 pp) terwijl de splitsmethode er met -2.27 pp precies de '
 'andere kant op wijst. Poort 5 sluit dan: twee methodes die tegengesteld wijzen, geen bet. Dat is '
 'ook de reden dat er deze run geen schaduwrij met failed_gate = "herijking" meegaat - er is geen '
 'selectie die op de ruwe kans alle acht poorten haalt. De poorten 7 en 8 zouden diezelfde kant '
 'trouwens sowieso hebben gesloten: Grasshopper mist 40% van zijn selectiewaarde tegen 10% bij '
 'Sion (Mikulic, Von Moos en Meyer), en de markt zet Grasshopper op 22.5% - onder de 35% waar '
 'poort 8 dichtgaat. Drie onafhankelijke remmen op dezelfde selectie; op de herijkte schaal kwam '
 'het niet eens zo ver, want daar viel hij al op de edge af.\n\n'
 'De fit van vanochtend staat op a=0.865, b=-0.455 over 662 afgerekende gevallen, met een '
 'gemiddelde geclaimde kans van 51.8% tegen een werkelijke trefkans van 40.9% - bijna elf '
 'procentpunt te optimistisch. Dat is de scheefstand die van elke schatting af gaat, en op dit '
 'duel kostte ze 7.2 procentpunt edge.'
)

MARKTBALANS = (
 'GEHAALD, maar zo krap als het maar kan: er speelde een competitie, dus alles hangt aan die ene '
 'inkoop. De Swiss Super League heeft een sportkey bij The Odds API '
 '(soccer_switzerland_superleague) en kreeg de volle bulk-aanroep van 3 credits (h2h + spreads + '
 'totals). Daaruit kwamen vier van de zes markten - 1X2 op de beste prijs (3 selecties), Asian '
 'Handicap (5), Double Chance uit de +0.5-lijn (1) en Over/Under (6) - en de tweede ronde kocht er '
 'BTTS bij (2 selecties, 1 credit). Er is dus zowel een uitkomstmarkt als een doelpuntenmarkt '
 'ingekocht en de controle van §1a slaagt, maar met een competitie is "hoe ruim" hier niet meer '
 'dan: een van een.\n\n'
 'Draw No Bet is de enige markt die op nul staat, en dat is niet het geld: er zat geen 0.0-lijn in '
 'de spreads-respons, dus er viel niets af te leiden. Het plafond stond op 598 credits en er is 4 '
 'van uitgegeven; 594 bleef ongebruikt. De inkoop was deze run dus aantoonbaar niet de beperkende '
 'factor, en er is geen enkele competitie die vandaag om een ontbrekende sportkey buiten de boot '
 'viel - de drie Run B-competities zonder sportkey speelden geen van alle.'
)

VROEG_SEIZOEN_NOOT = (
 'Factor 1.0374, gepoold 1.0747 over 8 speeldagen in een competitie, gemeten in xG. De Swiss '
 'Super League scoorde vorig seizoen 1.604 xG per ploeg per duel en staat dit seizoen na acht '
 'speeldagen op 1.723; de prior van 8 speeldagen trekt die verhouding terug van 1.0747 naar '
 '1.0374. Alles komt uit de stand bij Fotmob; er komt geen enkele bookmakerprijs aan te pas, dus '
 '§2 en de waarschuwing bij early_season_uplift blijven gerespecteerd. Een kanttekening die erbij '
 'hoort: met een enkele observatie is dit geen gepoolde meting meer maar de waarneming van deze '
 'ene competitie, half teruggetrokken naar 1.0. Dat is precies wat de prior hoort te doen bij '
 'weinig data, maar het is iets anders dan de 69 speeldagen over zes competities van gisteren.'
)

CREDITBRON = (
 'suggest_cap(19167, 16) = 598 - 19.167 credits over volgens api_check.py van deze run (20K-plan, '
 '833 gebruikt deze maand), 16 dagen tot de maandwissel, 2 runs per dag. split_budget(598, 1) '
 'geeft 1 spreads / 1 totals bij een inkoopbare competitie, en omdat 3 x 1 = 3 ruim onder 598 ligt '
 'gaat de volle bulk door: h2h + spreads + totals in een aanroep. Uitgegeven: 3 credits in 1 '
 'bulk-aanroep, plus 1 credit voor de enige BTTS-aanroep van de tweede ronde = 4 van 598. Dat BTTS '
 '1 credit kost in plaats van de 2 uit §1a is sinds begin september elke run zo - het maakt BTTS '
 'goedkoper dan begroot, nooit duurder. Nog 19.163 credits over.'
)

res = json.load(open("tmp-run/rb15_results.json"))
odds = json.load(open("tmp-run/rb15_odds.json"))
s3 = json.load(open("tmp-run/rb15_stage3.json"))
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
assert not bets, "deze run verwacht nul bets; pas rb15_emit.py aan als dat verandert"

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
    # odds["spent"] is alleen de bulk-ronde; de BTTS-ronde van rb15_btts.py telt erbij op,
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
        for k in ("promovendi", "understat", "verplaatst", "poort8_geblokkeerd", "afgekapt",
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
