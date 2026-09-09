"""Run B, 9 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/.

Zelfde opzet als `rb7_emit.py`. Nul bets, dus `picks.jsonl` krijgt geen regel; alles wat de
run heeft gemeten gaat naar `data/run-state/2026-09-09-run-b.json`, waar report.py, shadow.py,
calibration.py, ctxlog.py en toplist.py het uit lezen.
"""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-09"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-09T05:20:00+02:00"

TOELICHTING = (
 'Twee wedstrijden op de hele runlijst vandaag, allebei in de Czech First League; de andere '
 'zestien competities hadden niets op de kalender. Dat is midden in de interlandperiode geen '
 'storing: van Griekenland staat alleen de Super League 2 in de Fotmob-daglijst, van Zweden '
 'alleen de Superettan, van Kroatie alleen de beker en van Nederland alleen de Eredivisie - de '
 'tweede divisies en de kleinere competities uit deze lijst spelen deze week niet. Voor Kosovo '
 'geldt onveranderd wat sinds 13 aug 2026 elke run geldt: geen enkele competitie met ccode KOS '
 'in de daglijst. De cap van 40 (woensdag) is niet in de buurt gekomen: nul duels afgekapt, '
 'beide duels volledig doorgerekend. Allebei op LIGHT, en dat is de kern van deze run: de Czech '
 'First League heeft geen xG bij Fotmob (opnieuw bevestigd voor 2025/2026 en 2026/2027, zoals op '
 '22 aug en 2 sep), dus de kansinput komt uit doelpunten voor en tegen. LIGHT betekent een '
 'drempel van 16.0 procentpunt, en daar gaat de herijking van 1g nog overheen. De hoogste '
 'herijkte edge van de hele run is -2.35 pp (Jablonec wint @ 1.93); dezelfde selectie stond ruw '
 'op +9.30 pp, nog altijd ruim onder de 16.0. Er is dus geen enkele near miss - de NEAR-'
 'ondergrens voor LIGHT ligt op 6.0 pp en geen enkele selectie komt daar herijkt boven - en er '
 'is ook geen selectie die zonder de herijking wel een bet was geweest, want ook ruw haalt niets '
 'de LIGHT-drempel. Poort 7 en poort 8 hebben vandaag niets tegengehouden: bij beide duels is de '
 'opstellingsinformatie compleet, staat er niemand als afwezig gemeld, en hebben beide ploegen '
 'ongeveer evenveel rust (3.1 tegen 3.2 dagen bij Jablonec, 3.0 tegen 4.0 bij Hradec Kralove). '
 'Zes selecties doorgerekend, alle zes 1X2 - dat is geen keuze van de analyse maar van de '
 'inkoop, zie de marktbalans-controle hieronder.'
)

MARKTBALANS = (
 'GEHAALD: NEE - 1 competitie met een uitkomstmarkt, 0 met een doelpuntenmarkt. Belangrijk voor '
 'wie dit over een week terugleest: de oorzaak is NIET het creditplafond. Dat stond op 443 '
 'credits en er is er nul van uitgegeven. De enige competitie die vandaag speelt, de Czech First '
 'League, heeft geen sportkey bij The Odds API - vastgelegd in coverage.json sinds 9 aug 2026 en '
 'sindsdien niet veranderd - en daarmee is er niets in te kopen. Asian Handicap, Draw No Bet, '
 'Double Chance, Over/Under en BTTS waren vandaag dus voor geen enkel duel te koop, tegen welke '
 'prijs dan ook. 1X2 komt van het BetExplorer-marktgemiddelde over 3 boeken; de bookmaker is '
 'daar niet herleidbaar en de edge valt er systematisch te laag uit (1a). De regel in 1a zegt '
 'dat een gefaalde marktbalans-controle betekent dat het plafond te krap is voor deze runlijst; '
 'dat klopt vandaag niet, en die uitzondering hoort genoteerd te staan in plaats van als '
 'plafondprobleem te worden gelezen. Wat het wel betekent: op een dag als vandaag kan alleen de '
 'uitkomstmarkt een bet opleveren, en dat is een beperking van de bron en niet van het model.'
)

VROEG_SEIZOEN_NOOT = (
 'Afwijking van de gebruikelijke vorm, met opzet en hier genoteerd. De vroeg-seizoenscorrectie '
 'wordt normaal gepoold over de competities met xG in beide seizoenen. De enige competitie die '
 'vandaag speelt heeft geen xG, dus die observatie bestaat niet en early_season_uplift([]) zou '
 'stilzwijgend op factor 1.0 uitkomen - dat is niet "geen correctie nodig" maar "niet gemeten". '
 'In plaats daarvan is hetzelfde niveauverschil op DOELPUNTEN gemeten: 1.298 per ploeg per duel '
 'in 2025/2026 tegen 1.472 na 7 speeldagen van 2026/2027, ruwe verhouding 1.1339, na de prior '
 'van 8 speeldagen factor 1.0625. Dat is de eenheid waarin deze run sowieso rekent (zonder xG '
 'komen zowel het competitieniveau als de teamsterktes uit doelpunten), en het komt volledig uit '
 'de stand - geen enkele bookmakerprijs, dus 2 en de waarschuwing bij early_season_uplift '
 'blijven gerespecteerd. Wat het NIET is: gepoold over competities. Het is een waarneming uit '
 'een enkele competitie na zeven speeldagen, precies de ruis waar de docstring voor waarschuwt; '
 'de prior trekt hem daarom van +13.4% terug naar +6.3%. Het effect op de uitkomst is te zien in '
 'het ou25-veld per duel: P(Over 2.5) gaat van 0.4009 naar 0.4385 bij Jablonec en van 0.5725 '
 'naar 0.6132 bij Hradec Kralove. Op de bets maakt het niets uit - er waren geen '
 'doelpuntenmarkten te koop en op 1X2 verandert een niveaucorrectie vrijwel niets.'
)

CREDITBRON = (
 'suggest_cap(19520, 22) = 443 - 19.520 credits over volgens api_check.py van deze run (20K-plan, '
 '480 gebruikt deze maand), 22 dagen tot de maandwissel, 2 runs per dag. Uitgegeven: 0 credits in '
 '0 aanroepen. Reden: de enige competitie met wedstrijden vandaag (Czech First League) heeft geen '
 'sportkey bij The Odds API, dus buyable is leeg en split_budget is niet eens aangeroepen. Er is '
 'vandaag dus geen beste prijs opgehaald en geen enkele doelpunten- of handicapmarkt; 1X2 komt '
 'gratis van BetExplorer (marktgemiddelde over 3 boeken, bookmaker niet herleidbaar). Zie '
 'marktbalans hieronder - de controle faalt, maar niet door het plafond.'
)

res = json.load(open("tmp-run/rb9_results.json"))
odds = json.load(open("tmp-run/rb9_odds.json"))
s3 = json.load(open("tmp-run/rb9_stage3.json"))
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
assert not bets, "deze run verwacht nul bets; pas rb7_emit.py aan als dat verandert"

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
    "plafond": odds["cap"], "gebruikt": 0,
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
