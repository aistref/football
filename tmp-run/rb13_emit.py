"""Run B, 13 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/.

Zelfde opzet als `rb12_emit.py`. Nul bets, dus `picks.jsonl` krijgt geen regel; alles wat de
run heeft gemeten gaat naar `data/run-state/2026-09-13-run-b.json`, waar report.py, shadow.py,
calibration.py, ctxlog.py en toplist.py het uit lezen.
"""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-13"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-13T05:20:00+02:00"

TOELICHTING = (
 'Negenendertig duels in dertien van de zeventien competities, en voor het eerst sinds de cap op '
 '55 staat viel er op een Run B-weekenddag niets af: 39 is ruim onder 55, dus MAX_DEEP_ANALYSES '
 'heeft vandaag geen enkele analyse gekost. Vier competities stonden leeg. De Hungarian NB I heeft '
 'dit weekend geen programma, English League One en League Two spelen hun speelronde op zaterdag '
 '(gisteren dus, buiten deze run), en de Kosovo Superleague komt nog altijd niet voor in de '
 'Fotmob-daglijst - ongewijzigd sinds 13 aug 2026 en daarmee geen storing van vandaag.\n\n'
 'Van de negenendertig duels zijn er negenentwintig volledig doorgerekend (14 FULL, 15 LIGHT), '
 'samen 325 selecties over alle zes markten, en nul bets. Tien duels vielen op NONE, en die tien '
 'splitsen in twee even grote groepen die iets verschillends zeggen. Vijf ploegen komen uit een '
 'land waarvoor promotion helemaal geen gemeten divisiepaar kent - Kalamata (Griekenland), Rudes '
 '(Kroatie), Corvinul Hunedoara (Roemenie), Austria Lustenau (Oostenrijk) en Laci (Albanie). Daar '
 'is geen omrekening mogelijk en dus geen onafhankelijke kansinput op het niveau waarop gespeeld '
 'wordt (§4). De andere vijf zijn subtieler: Eldense, Sabadell, Tenerife, Energie Cottbus en VfL '
 'Osnabruck staan niet in de stand van de divisie BOVEN hun huidige, omdat ze uit de divisie '
 'ERONDER komen - Primera Federacion respectievelijk 3. Liga, een derde niveau waarvoor geen '
 'gemeten paar bestaat. De omrekening zoekt dan een divisie hoger en vindt de ploeg daar niet. Dat '
 'zijn vijf tweededivisieduels die op een gemeten derde-niveaufactor wel doorgerekend zouden '
 'kunnen worden; het staat als openstaand punt in het runrapport.\n\n'
 'De bevinding van de dag is opnieuw de herijking, maar veel smaller dan gisteren. Vier selecties '
 'in twee wedstrijden haalden alle acht poorten op de RUWE kans en sneuvelden uitsluitend op §1g: '
 'Kifisia - Levadiakos (Over 2.25 @ 1.90, ruw +9.66 pp, herijkt -2.89) en Hammarby - '
 'Brommapojkarna (Under 3.5 @ 2.02, ruw +12.58, herijkt +0.04). Beide gaan als schaduwpick naar '
 'data/shadow.jsonl met failed_gate = "herijking", een rij per wedstrijd en geboekt op de ruwe '
 'schaal (§5a). Ter vergelijking: gisteren waren dat negentien selecties in acht wedstrijden. De '
 'fit van vanochtend staat op a=0.8789, b=-0.4514 over 646 afgerekende gevallen, met een '
 'gemiddelde geclaimde kans van 51.7% tegen een werkelijke trefkans van 41.0% - ruim tien '
 'procentpunt te optimistisch, en dat is de scheefstand die er van elke schatting af gaat.\n\n'
 'Op de herijkte schaal viel vrijwel alles af op de edge (308 van 325) of op de koersband (13). '
 'Poort 5, 6, 7 en 8 hebben op die schaal geen enkele selectie als eerste tegengehouden; op de '
 'RUWE schaal deed poort 8 dat acht keer en poort 5 twee keer. Dat is precies het patroon dat §1e '
 'bij de verlichting van poort 8 voorspelde: de herijking pakt de oorzaak aan waar die poort een '
 'symptoom van afdekte, en op de herijkte schaal is de underdog-selectie al eerder op de edge '
 'gesneuveld. Er zijn twee near_misses, allebei ruim onder hun drempel: HamKam - Molde (1X2 - '
 'HamKam wint @ 4.35, xG-model +9.80, splitsmethode +21.75, zwakste stand +6.22, herijkt +4.13 pp '
 'tegen 8.0) en Hammarby - Brommapojkarna (Asian Handicap Brommapojkarna +2 @ 1.99, +19.08 / '
 '+19.89 / +14.43 ruw, herijkt +6.51 pp tegen 8.0). Beide wijzen dezelfde kant op als altijd: een '
 'ruime edge op het ongecorrigeerde model die na de correctie onder de drempel uitkomt.'
)

MARKTBALANS = (
 'GEHAALD. Acht van de dertien competities die vandaag speelden hebben een sportkey bij The Odds '
 'API en kregen alle acht de volle bulk-aanroep van 3 credits (h2h + spreads + totals), dus daar '
 'deden alle zes markten mee. Over de dertien competities waarin iets is doorgerekend staat de '
 'verdeling zo: 1X2 in 13 van 13 competities (86 selecties), Asian Handicap in 8 van 13 (81), Draw '
 'No Bet in 8 van 13 (27), Double Chance in 5 van 13 (9), Over/Under in 8 van 13 (112) en BTTS in '
 '3 van 13 (10 selecties over 5 wedstrijden). Er is dus zowel een uitkomstmarkt als een '
 'doelpuntenmarkt ingekocht, en niet nipt. De vijf competities zonder handicap- en '
 'doelpuntenmarkt zijn dezelfde vijf zonder sportkey - Czech First League, Croatian HNL, Romanian '
 'SuperLiga, Keuken Kampioen Divisie en Kategoria Superiore - en de reden is niet het geld maar de '
 'inkoopbaarheid: daar komt 1X2 van het BetExplorer-marktgemiddelde, is de bookmaker niet '
 'herleidbaar en valt de edge systematisch te laag uit (§1a). Het plafond stond op 534 credits en '
 'er is 29 van uitgegeven; 505 bleef ongebruikt. Nul bets, dus er valt niets scheef te verdelen - '
 'maar de inkoop was deze run aantoonbaar niet de beperkende factor.\n\n'
 'Nieuw vandaag, en het raakt deze tabel: BTTS wordt sinds deze run in een TWEEDE ronde gekocht, '
 'na de eerste analyse, voor de duels met een kandidaat-edge op de ruwe of de herijkte schaal '
 '(§1a stap 2, vastgelegd in _shared-rules.md op 13 sep). Dat waren er vijf van de negenendertig, '
 'a 1 credit. Tot en met 12 sep kocht Run B BTTS vooraf voor de bovenste MAX_DEEP_ANALYSES duels '
 '- 46 stuks gisteren - en dan is "toont al een kandidaat-edge" geen criterium maar een '
 'rangschikking. Gevolg voor de administratie: bij 16 doorgerekende duels staat BTTS nu als "niet '
 'opgevraagd" met de reden erbij in plaats van als "opgevraagd, geen boek noteerde de markt". Dat '
 'onderscheid is §6b-5b en het is vandaag in de code gerepareerd; de Run A van vanochtend, die '
 'dezelfde tweede ronde voor het eerst draaide, noteert het nog met de oude tekst.'
)

VROEG_SEIZOEN_NOOT = (
 'Factor 1.0779, gepoold over 108 speeldagen in dertien competities. Acht competities leveren de '
 'observatie in xG (Griekenland, Eliteserien, Allsvenskan, Segunda Division, Serie B, 2. '
 'Bundesliga, Zwitserland, Oostenrijk); vijf hebben geen xG bij Fotmob en leveren hetzelfde '
 'niveauverschil in DOELPUNTEN, want dat is de eenheid waarin die duels sowieso rekenen: Tsjechie '
 '1.298 -> 1.432 per ploeg per duel, Kroatie 1.331 -> 1.613, Roemenie 1.277 -> 1.276, de Keuken '
 'Kampioen Divisie 1.597 -> 1.918 en Albanie 1.103 -> 1.472. Alles komt uit de stand; er komt geen '
 'enkele bookmakerprijs aan te pas, dus §2 en de waarschuwing bij early_season_uplift blijven '
 'gerespecteerd. De ruwe gepoolde verhouding is 1.0837 en de prior van 8 speeldagen trekt hem '
 'terug naar 1.0779. Het effect per duel staat in het ou25-veld: P(Over 2.5) gaat gemiddeld '
 'ruim 4 procentpunt omhoog over de negenentwintig doorgerekende duels. Twee kanttekeningen die '
 'erbij horen. De Eliteserien en de Allsvenskan zijn kalenderjaarcompetities en staan op speeldag '
 '20 en 21; daar meet deze correctie geen vroeg seizoen meer maar het niveauverschil tussen twee '
 'jaargangen, en met 41 van de 108 speeldagen wegen die twee zwaar mee. En Roemenie levert een '
 'observatie van vrijwel exact 1.0 (1.277 -> 1.276) - de correctie is dus geen automatische '
 'verhoging maar een meting die ook nul kan zijn.'
)

CREDITBRON = (
 'suggest_cap(19261, 18) = 534 - 19.261 credits over volgens api_check.py van deze run (20K-plan, '
 '739 gebruikt deze maand), 18 dagen tot de maandwissel, 2 runs per dag. split_budget(534, 8) '
 'geeft 8 spreads / 8 totals bij acht inkoopbare competities, en omdat 3 x 8 = 24 ruim onder 534 '
 'ligt gaat de volle bulk door: h2h + spreads + totals in een aanroep per competitie. Uitgegeven: '
 '24 credits in 8 bulk-aanroepen, plus 5 credits voor de vijf BTTS-aanroepen van de tweede ronde '
 '= 29 van 534. Dat BTTS 1 credit kost in plaats van de 2 uit §1a is sinds begin september elke '
 'run zo - het maakt BTTS goedkoper dan begroot, nooit duurder. Nog 19.232 credits over. Vijf van '
 'de dertien competities zijn niet in te kopen wegens een ontbrekende sportkey (Tsjechie, Kroatie, '
 'Roemenie, Keuken Kampioen Divisie, Albanie); zie marktbalans hieronder.'
)

res = json.load(open("tmp-run/rb13_results.json"))
odds = json.load(open("tmp-run/rb13_odds.json"))
s3 = json.load(open("tmp-run/rb13_stage3.json"))
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
assert not bets, "deze run verwacht nul bets; pas rb13_emit.py aan als dat verandert"

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
    "plafond": odds["cap"], "gebruikt": odds["spent"],
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
