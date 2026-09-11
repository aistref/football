"""Run B, 11 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/.

Zelfde opzet als `rb9_emit.py`. Nul bets, dus `picks.jsonl` krijgt geen regel; alles wat de
run heeft gemeten gaat naar `data/run-state/2026-09-11-run-b.json`, waar report.py, shadow.py,
calibration.py, ctxlog.py en toplist.py het uit lezen.
"""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-11"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-11T05:05:00+02:00"

TOELICHTING = (
 'De eerste volle Run B-dag sinds de interlandbreak, en meteen de grootste van deze maand: '
 'negentien duels in acht van de zeventien competities. De cap staat op 55 (vrijdag) en is niet '
 'in de buurt gekomen - nul duels afgekapt, alle negentien gerangschikt en zestien volledig '
 'doorgerekend. Van die zestien staan er zes op FULL en tien op LIGHT, samen 128 selecties, '
 'nul bets. Drie duels vielen op NONE, alle drie op hetzelfde punt: een ploeg zonder historie in '
 'deze divisie en geen gemeten omrekening voor de divisie waar hij vandaan komt. Twee daarvan '
 'zitten in de Serie B (Arezzo en Benevento, allebei gepromoveerd uit de Serie C - promotion.TIER2 '
 'heeft geen regel voor Serie B omdat er geen gemeten Italiaans derde-divisiepaar is) en een in de '
 'Kategoria Superiore (Skenderbeu, gepromoveerd uit de Kategoria e Pare - voor Albanie is er in '
 'geen van beide richtingen een gemeten factor). Hellas Verona en Pisa, allebei gedegradeerd uit '
 'de Serie A, konden wel worden omgerekend; bij Benevento - Hellas Verona sneuvelt het duel dus op '
 'de andere ploeg.\n\n'
 'Wat deze run wel heeft opgeleverd is een gerepareerde omrekening in de andere richting. Heracles '
 'en NAC Breda zijn deze zomer uit de Eredivisie gezakt en kwamen vanochtend allebei op NONE uit '
 'met de melding "geen divisie boven of onder Keuken Kampioen Divisie (NED) bekend". Dat was geen '
 'ontbrekende meting maar een ontbrekende aanroep: de Eredivisie staat sinds de eerste versie in '
 'promotion.TIER2 met de Eerste Divisie eronder (Fotmob 111), alleen stond het spiegelbeeld niet '
 'in TIER1. Die regel is toegevoegd (Tier1(57, "Eredivisie (NED)")), precies zoals op 1 sep voor '
 'League One en League Two is gedaan, en beide duels staan nu op LIGHT. Let op de beperking die '
 'erbij hoort: voor dit paar bestaat geen football-data-koppel en MEASURED_TIER2_GAP meet alleen '
 'de richting omhoog, dus de omrekening loopt op de GEPOOLDE factor (x1.654 aanval, x0.647 '
 'verdediging, n=240) en niet op een eigen meting. Beide ploegen vallen binnen het gemeten bereik.\n\n'
 'De opvallendste meting van de dag staat bij Hacken - Mjallby, en ze is een waarschuwing en geen '
 'kans. De twee methodes liggen daar 63 procentpunt uit elkaar op dezelfde selectie: de xG-methode '
 'geeft Mjallby 21.0% kans op de uitwinst, de splitsmethode 84.4%. De oorzaak is aanwijsbaar en '
 'structureel. De Allsvenskan is een kalenderjaarcompetitie en staat op speeldag 20, dus '
 'blend_seasons weegt het lopende seizoen voor 0.70 mee in de xG-methode - die ziet een Mjallby '
 'dat dit jaar 20 punten uit 19 duels haalt (xG 1.23, xGA 1.93 per duel). De splitsmethode moet '
 'volgens 4 op vorig seizoen blijven staan omdat ze thuis/uit-doelpunten nodig heeft, en ziet dus '
 'nog steeds de kampioen van 2025: 75 punten, uit 32-10. Dat zijn twee verschillende ploegen. '
 'Poort 5 vangt dit niet - beide methodes verslaan de markt aan dezelfde kant - maar poort 7 en '
 'poort 8 deden het allebei wel: Mjallby had vier dagen rust tegen zes bij Hacken, en met een '
 'marktkans van 18.7% staat de selectie ver onder de UNDERDOG_FLOOR van 0.35. Dat is de enige '
 'near_miss van de run (herijkt +8.41 pp, boven de FULL-drempel van 8.0) en hij gaat als '
 'failed_gate = "context" het schaduwlogboek in.\n\n'
 'Verder zijn er geen verrassingen. De hoogste herijkte edge daarna is +7.35 pp op Jong AZ Alkmaar '
 'bij Heracles, en die sneuvelt op de koersband: 6.37 ligt boven MAX_ODDS van 6.00. Daarna valt '
 'het meteen weg - de nummer drie staat op +1.11 pp en de nummer vier op +0.13 pp. Er is geen '
 'enkele selectie die zonder de herijking wel een bet was geweest; het blok zonder_herijking is '
 'leeg. De 128 selecties vielen af op de edge (121), op de koersband (6) en op de context (1); '
 'poort 8 heeft vandaag geen enkele selectie als eerste tegengehouden, en poort 5 en poort 6 '
 'evenmin. Op de ruwe schaal verschuift dat nauwelijks: 119 op de edge, 6 op de koersband, 2 op '
 'de context en 1 op de tweede methode.'
)

MARKTBALANS = (
 'GEHAALD: JA, maar niet voor de hele runlijst - vijf van de acht competities die vandaag speelden '
 'hebben zowel een doelpuntenmarkt als een uitkomstmarkt gekregen, en drie hadden alleen 1X2. Die '
 'vijf (Allsvenskan, Segunda Division, Serie B, 2. Bundesliga, Austrian Bundesliga) kregen alle '
 'vijf de volle bulk-aanroep van 3 credits, dus h2h + spreads + totals, en acht van hun duels '
 'kregen daarnaast BTTS. De drie andere - Romanian SuperLiga, Keuken Kampioen Divisie en Kategoria '
 'Superiore - hebben geen sportkey bij The Odds API en zijn dus niet in te kopen, tegen welke prijs '
 'dan ook. Belangrijk voor wie dit terugleest: dat is NIET het creditplafond. Dat stond op 485 en er '
 'is 23 van uitgegeven; er bleef 462 over. In die drie competities komt 1X2 van het '
 'BetExplorer-marktgemiddelde, is de bookmaker niet herleidbaar en valt de edge systematisch te laag '
 'uit (1a). Gevolg voor de analyse: in de negen duels van die drie competities kon alleen de '
 'uitkomstmarkt een bet opleveren, en dat is een beperking van de bron en niet van het model. In de '
 'zeven duels van de vijf ingekochte competities deden alle zes de markten mee. Er zijn nul bets, '
 'dus er valt niets scheef te verdelen.'
)

VROEG_SEIZOEN_NOOT = (
 'Factor 1.0661, gepoold over 53 speeldagen in acht competities - qua steekproef de op een na '
 'ruimste van deze maand. Bijzonder aan deze run is dat de acht observaties in twee eenheden '
 'binnenkomen. Vijf competities hebben xG bij Fotmob (Allsvenskan, Segunda Division, Serie B, '
 '2. Bundesliga, Austrian Bundesliga) en leveren de gebruikelijke observatie. Drie hebben dat niet '
 '(Romanian SuperLiga, Keuken Kampioen Divisie, Kategoria Superiore); daar is hetzelfde '
 'niveauverschil op DOELPUNTEN gemeten, want dat is de eenheid waarin die duels sowieso rekenen - '
 'zonder xG komen zowel het competitieniveau als de teamsterktes uit doelpunten voor en tegen. '
 'Roemenie 1.277 -> 1.222 per ploeg per duel, de Keuken Kampioen Divisie 1.597 -> 1.952 en Albanie '
 '1.103 -> 1.433. Alles komt uit de stand; er komt geen enkele bookmakerprijs aan te pas, dus 2 en '
 'de waarschuwing bij early_season_uplift blijven gerespecteerd. De ruwe gepoolde verhouding is '
 '1.0760 en de prior van 8 speeldagen trekt hem terug naar 1.0661. Het effect per duel staat in het '
 'ou25-veld: bij Hacken - Mjallby gaat P(Over 2.5) van 0.6301 naar 0.6723.'
)

CREDITBRON = (
 'suggest_cap(19459, 20) = 485 - 19.459 credits over volgens api_check.py van deze run (20K-plan, '
 '541 gebruikt deze maand), 20 dagen tot de maandwissel, 2 runs per dag. split_budget(485, 5) geeft '
 '5 spreads / 5 totals bij vijf inkoopbare competities, en omdat 3 x 5 = 15 ruim onder 485 ligt gaat '
 'de volle bulk door: h2h + spreads + totals in een aanroep per competitie. Uitgegeven: 23 credits '
 'in 13 aanroepen (5 bulk a 3 = 15, plus 8 BTTS-aanroepen a 1 credit). Dat BTTS 1 credit kost in '
 'plaats van de 2 uit 1a is sinds begin september elke run zo - het maakt BTTS goedkoper dan '
 'begroot, nooit duurder. Nog 19.436 credits over. Drie van de acht competities zijn niet in te '
 'kopen wegens een ontbrekende sportkey; zie marktbalans hieronder.'
)

res = json.load(open("tmp-run/rb11_results.json"))
odds = json.load(open("tmp-run/rb11_odds.json"))
s3 = json.load(open("tmp-run/rb11_stage3.json"))
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
assert not bets, "deze run verwacht nul bets; pas rb11_emit.py aan als dat verandert"

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
    "plafond": odds["cap"], "gebruikt": 23,
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
