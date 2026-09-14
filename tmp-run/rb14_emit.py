"""Run B, 14 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/.

Zelfde opzet als `rb12_emit.py`. Nul bets, dus `picks.jsonl` krijgt geen regel; alles wat de
run heeft gemeten gaat naar `data/run-state/2026-09-14-run-b.json`, waar report.py, shadow.py,
calibration.py, ctxlog.py en toplist.py het uit lezen.
"""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-14"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-14T05:20:00+02:00"

TOELICHTING = (
 'Negen duels in zes van de zeventien competities - een maandag in september, en dat is precies '
 'wat de Run B-runlijst dan oplevert. Elf competities stonden leeg: de Czech First League, de '
 'Greek Super League, de Hungarian NB I, Serie B, de 2. Bundesliga, de Swiss Super League, de '
 'Austrian Bundesliga, English League One, English League Two en de Kategoria Superiore speelden '
 'hun speelronde in het weekend, en de Kosovo Superleague komt nog altijd niet voor in de '
 'Fotmob-daglijst - ongewijzigd sinds 13 aug 2026 en daarmee geen storing van vandaag. De cap '
 'stond op 40 (maandag) tegen negen duels, dus MAX_DEEP_ANALYSES heeft deze run geen enkele '
 'analyse gekost.\n\n'
 'Van de negen duels zijn er acht volledig doorgerekend (3 FULL, 5 LIGHT), samen 61 selecties, en '
 'nul bets. Een duel viel op NONE: Celta Fortuna - Eibar in de Segunda Division. Celta Fortuna is '
 'het beloftenelftal van Celta de Vigo en komt uit de Primera Federacion, het derde Spaanse '
 'niveau. De omrekening van promotion.py zoekt dan eerst een divisie HOGER (La Liga) en vindt de '
 'ploeg daar niet, want hij is geen degradant maar een promovendus - en voor LaLiga2 staat er geen '
 'divisie eronder in TIER2. Dat is geen datagat maar een ontbrekend gemeten divisiepaar, en het '
 'heeft een reden die vandaag is nagetrokken: de Primera Federacion draait bij Fotmob onder EEN '
 'primaryId (8968) voor TWEE parallelle groepen, dus een enkele standopvraag levert geen eenduidige '
 'competitiebasis. Het staat als openstaand punt in dit rapport.\n\n'
 'De dag had een duidelijke kop: Djurgarden - GAIS. Op de RUWE schaal stond GAIS +1 @ 1.96 '
 '(+14.46 pp, score 9.47) bovenaan de ranglijst van de hele run, en die selectie sneuvelde niet op '
 'de herijking maar op poort 7 - de context spreekt hem tegen. Aan beide kanten, en dat is '
 'ongewoon. GAIS mist zes spelers en '
 'daarmee 48% van zijn selectiewaarde tegen 0% bij Djurgarden (drie daarvan zijn het hele seizoen '
 'uit), en Djurgarden speelde vier dagen geleden tegen negen dagen rust voor GAIS. De poort sluit '
 'dus allebei de kanten, en wat overblijft zijn de doelpuntenmarkten zonder kant - die haalden de '
 'drempel niet. Op de herijkte schaal was de sterkste selectie van de hele run 1X2 - GAIS wint @ '
 '6.75 met +8.64 pp, ruim boven de drempel van 8.0, en die viel af op poort 2: een koers van 6.75 '
 'ligt buiten de band 1.30-6.00. Dat is geen randgeval maar de regel die het vaakst bijt bij een '
 'model dat te optimistisch is over outsiders; het schaduwlogboek staat voor "viel af op: odds" '
 'inmiddels op 0 uit 15.\n\n'
 'Verder is het beeld vlak. Alle 61 selecties vielen op de herijkte schaal af op de edge (54) of '
 'op de koersband (7); poort 5, 6, 7 en 8 hebben op die schaal geen enkele selectie als eerste '
 'tegengehouden. Geen enkele selectie haalde alle acht poorten op de ruwe kans, dus er gaat deze '
 'run ook geen schaduwrij met failed_gate = "herijking" mee - voor het eerst sinds 6 sep. Er zijn '
 'ook geen near_misses: de drie hoogste herijkte edges van de dag (+8.64, +4.15 en +2.95 pp) '
 'liggen alle drie op een koers boven de 6.00 en vallen daarmee buiten de near_miss-definitie, die '
 'de koersband meeneemt. De fit van vanochtend staat op a=0.873, b=-0.457 over 660 afgerekende '
 'gevallen, met een gemiddelde geclaimde kans van 51.7% tegen een werkelijke trefkans van 40.9% - '
 'bijna elf procentpunt te optimistisch, en dat is de scheefstand die er van elke schatting af '
 'gaat.'
)

MARKTBALANS = (
 'GEHAALD, maar krapper dan het aantal competities doet vermoeden. Drie van de zes competities die '
 'vandaag speelden hebben een sportkey bij The Odds API en kregen alle drie de volle bulk-aanroep '
 'van 3 credits (h2h + spreads + totals): Eliteserien, Allsvenskan en Segunda Division. De '
 'Segunda-aanroep heeft niets opgeleverd, want het enige Spaanse duel viel op NONE en is dus nooit '
 'doorgerekend - de prijzen zijn gekocht voordat de tier vaststond. Blijven over: twee competities '
 'met een volle markt. Over de zes competities waarin iets is doorgerekend staat de verdeling zo: '
 '1X2 in 5 van 5 competities met een doorgerekend duel (23 selecties), Asian Handicap in 2 van 5 '
 '(11), Draw No Bet in 0 van 5 (0), Double Chance in 1 van 5 (1), Over/Under in 2 van 5 (24) en '
 'BTTS in 1 van 5 (2 selecties over 1 wedstrijd). Er is dus zowel een uitkomstmarkt als een '
 'doelpuntenmarkt ingekocht - de controle van §1a slaagt - maar met twee competities is dat geen '
 'ruime marge, en dat hoort erbij te staan.\n\n'
 'Twee dingen om apart te noemen. Draw No Bet stond deze run op nul, en dat is niet het geld: bij '
 'geen van de drie ingekochte competities zat er een 0.0-lijn in de spreads-respons, dus er viel '
 'niets af te leiden. Double Chance (de +-0.5-lijn) lag er alleen bij de Allsvenskan. En de drie '
 'competities zonder handicap- en doelpuntenmarkt zijn dezelfde drie zonder sportkey - Croatian '
 'HNL, Romanian SuperLiga en Keuken Kampioen Divisie - waar de reden niet het geld is maar de '
 'inkoopbaarheid: daar komt 1X2 van het BetExplorer-marktgemiddelde, is de bookmaker niet '
 'herleidbaar en valt de edge systematisch te laag uit (§1a). Het plafond stond op 564 credits en '
 'er is 10 van uitgegeven; 554 bleef ongebruikt. De inkoop was deze run dus aantoonbaar niet de '
 'beperkende factor. BTTS is voor een duel gekocht (Djurgarden - GAIS, de enige met een '
 'kandidaat-edge op de ruwe of de herijkte schaal), a 1 credit; bij de zeven andere doorgerekende '
 'duels staat BTTS als "niet opgevraagd" met de reden erbij (§6b-5b).'
)

VROEG_SEIZOEN_NOOT = (
 'Factor 1.0621, gepoold over 69 speeldagen in zes competities. Drie competities leveren de '
 'observatie in xG (Eliteserien, Allsvenskan, Segunda Division); drie hebben geen xG bij Fotmob en '
 'leveren hetzelfde niveauverschil in DOELPUNTEN, want dat is de eenheid waarin die duels sowieso '
 'rekenen: Kroatie 1.331 -> 1.606 per ploeg per duel, Roemenie 1.277 -> 1.261 en de Keuken '
 'Kampioen Divisie 1.597 -> 1.903. Alles komt uit de stand; er komt geen enkele bookmakerprijs aan '
 'te pas, dus §2 en de waarschuwing bij early_season_uplift blijven gerespecteerd. De ruwe gepoolde '
 'verhouding is 1.0693 en de prior van 8 speeldagen trekt hem terug naar 1.0621. Twee '
 'kanttekeningen die erbij horen. De Eliteserien en de Allsvenskan zijn kalenderjaarcompetities en '
 'staan op speeldag 20 en 21; daar meet deze correctie geen vroeg seizoen meer maar het '
 'niveauverschil tussen twee jaargangen, en met 41 van de 69 speeldagen wegen die twee vandaag '
 'zwaarder dan ooit. En Roemenie levert een observatie onder de 1.0 (1.277 -> 1.261) - de correctie '
 'is dus geen automatische verhoging maar een meting die ook omlaag kan wijzen.'
)

CREDITBRON = (
 'suggest_cap(19207, 17) = 564 - 19.207 credits over volgens api_check.py van deze run (20K-plan, '
 '793 gebruikt deze maand), 17 dagen tot de maandwissel, 2 runs per dag. split_budget(564, 3) '
 'geeft 3 spreads / 3 totals bij drie inkoopbare competities, en omdat 3 x 3 = 9 ruim onder 564 '
 'ligt gaat de volle bulk door: h2h + spreads + totals in een aanroep per competitie. Uitgegeven: '
 '9 credits in 3 bulk-aanroepen, plus 1 credit voor de enige BTTS-aanroep van de tweede ronde '
 '= 10 van 564. Dat BTTS 1 credit kost in plaats van de 2 uit §1a is sinds begin september elke '
 'run zo - het maakt BTTS goedkoper dan begroot, nooit duurder. Nog 19.197 credits over. Drie van '
 'de zes competities zijn niet in te kopen wegens een ontbrekende sportkey (Croatian HNL, Romanian '
 'SuperLiga, Keuken Kampioen Divisie); zie marktbalans hieronder.'
)

res = json.load(open("tmp-run/rb14_results.json"))
odds = json.load(open("tmp-run/rb14_odds.json"))
s3 = json.load(open("tmp-run/rb14_stage3.json"))
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
assert not bets, "deze run verwacht nul bets; pas rb14_emit.py aan als dat verandert"

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
    # odds["spent"] is alleen de bulk-ronde; de BTTS-ronde van rb14_btts.py telt erbij op,
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
