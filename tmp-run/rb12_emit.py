"""Run B, 12 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/.

Zelfde opzet als `rb9_emit.py`. Nul bets, dus `picks.jsonl` krijgt geen regel; alles wat de
run heeft gemeten gaat naar `data/run-state/2026-09-12-run-b.json`, waar report.py, shadow.py,
calibration.py, ctxlog.py en toplist.py het uit lezen.
"""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-12"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-12T05:05:00+02:00"

TOELICHTING = (
 'De grootste Run B-dag sinds het bestaan van deze routine: negenenvijftig duels in vijftien van '
 'de zeventien competities. Alleen de Hungarian NB I en de Kosovo Superleague stonden leeg - de '
 'eerste heeft dit weekend geen programma, de tweede komt nog altijd niet voor in de Fotmob-daglijst '
 '(ongewijzigd sinds 13 aug 2026). Belangrijker: dit is de eerste Run B waarin MAX_DEEP_ANALYSES '
 'werkelijk knelt. De cap staat op 55 (zaterdag) en er vielen vier duels buiten. Reken daar meteen '
 'een af: Girona - Castellon zou hoe dan ook op NONE zijn uitgekomen (Girona is uit LaLiga gezakt '
 'en valt buiten het gemeten omrekenbereik), dus de afkapping kostte drie echte analyses - FC '
 'Zbrojovka Brno - Artis Brno en de twee Albanese duels. Dat Girona toch in de afkaplijst staat is '
 'geen fout in de cijfers maar een volgorde-effect: de rangschikking draait voordat de omrekening '
 'van promovendi en degradanten heeft plaatsgevonden, dus een duel met tier PROMO? telt daar nog '
 'als LIGHT mee. Wie de afkapping over meerdere dagen wil vergelijken moet dus de NONE-duels uit '
 'de lijst halen; §3 Stage 4 vraagt om het aantal afgekapte duels en dat is hier 4, waarvan 3 '
 'analyses.\n\n'
 'Van de negenenvijftig duels zijn er vijfenveertig volledig doorgerekend (28 FULL, 17 LIGHT), '
 'samen 641 selecties over alle zes markten, en nul bets. Elf duels vielen op NONE, en die elf '
 'splitsen netjes in twee groepen. Vier struikelden over conversion_in_range - Girona, Cambridge '
 'United, Stockport County en Port Vale liggen na omrekening buiten het waargenomen bereik van de '
 'gemeten factor, en dat is een poort en geen aantekening (§4). De andere zeven hebben helemaal '
 'geen gemeten divisiepaar: Iraklis (Griekenland), Sepsi OSK en FC Voluntari (Roemenie) komen uit '
 'landen waarvoor promotion noch TIER1 noch TIER2 kent, en Ascoli, LR Vicenza, Rochdale en York '
 'City komen uit een DERDE divisie (Serie C respectievelijk de National League) waar geen gemeten '
 'paar voor bestaat - de omrekening zoekt dan in de divisie erboven en vindt de ploeg daar niet.\n\n'
 'De bevinding van de dag staat niet bij een wedstrijd maar bij de herijking. Negentien selecties '
 'verdeeld over acht wedstrijden haalden alle acht poorten op de RUWE kans en sneuvelden uitsluitend '
 'op §1g. Dat is veruit de grootste groep die deze routine op een dag heeft gezien, en het is precies '
 'het verschil dat de correctie van 5 september maakt: zonder haar had dit een dag met acht bets '
 'geweest. De fit van vanochtend staat op a=0.9167, b=-0.4406 over 616 afgerekende gevallen, met een '
 'gemiddelde geclaimde kans van 51.7% tegen een werkelijke trefkans van 41.4% - bijna elf '
 'procentpunt te optimistisch, en dat is de scheefstand die er hier van elke schatting af gaat. Alle '
 'acht gaan als schaduwpick naar data/shadow.jsonl met failed_gate = "herijking", een rij per '
 'wedstrijd, geboekt op de ruwe schaal (§5a). Over enkele weken staat daar dus een hit rate en een '
 'ROI onder, en dan is voor het eerst met cijfers te zeggen of deze correctie geld bespaart of '
 'alleen bets kost. Let bij het teruglezen op wat er NIET in zit: geen enkele van die negentien '
 'sneuvelde op poort 5, 6, 7 of 8. Ze waren op de ruwe schaal compleet.\n\n'
 'Verder viel alles af op de edge (603 van 641) of op de koersband (19). Poort 8 heeft vandaag geen '
 'enkele selectie als eerste tegengehouden - op de ruwe schaal deed hij dat vijf keer en poort 7 '
 'vier keer, maar op de herijkte schaal waren die selecties al eerder op de edge gesneuveld. Dat is '
 'het patroon dat §1e voorspelde toen de poort op 5 september werd verlicht: de herijking pakt de '
 'oorzaak aan waar poort 8 een symptoom van afdekte, en er komen daardoor vanzelf veel minder '
 'underdog-selecties tot aan die poort. Er zijn drie near_misses. De hoogste is Sheffield Wednesday '
 '- Wigan Athletic (1X2 - Wigan wint @ 5.51, herijkt +7.97 pp tegen een LIGHT-drempel van 16.0), '
 'daarna Lillestrom - Valerenga (Asian Handicap -0.5 @ 1.95, ruw +18.31, herijkt +6.61) en Rosenborg '
 '- Tromso (1X2 - Tromso @ 4.92, herijkt +5.36 tegen 8.0). Alle drie wijzen dezelfde kant op: een '
 'ruime edge op het ongecorrigeerde model die na de correctie ruim onder de drempel uitkomt.'
)

MARKTBALANS = (
 'GEHAALD, en ruimer dan op welke Run B-dag dan ook: tien van de vijftien competities die vandaag '
 'speelden kregen de volle bulk-aanroep van 3 credits (h2h + spreads + totals), dus alle zes de '
 'markten deden daar mee. Over de dertien competities waarin daadwerkelijk iets is doorgerekend '
 'staat de verdeling zo: 1X2 in 13 van 13 competities (134 selecties), Asian Handicap plus Draw No '
 'Bet plus Double Chance in 10 van 13 (219 selecties), Over/Under in 10 van 13 (212 selecties) en '
 'BTTS in 10 van 13 (76 selecties, 46 wedstrijden a 1 credit). De drie competities zonder '
 'doelpuntenmarkt zijn dezelfde drie zonder handicapmarkt, en de reden is niet het geld: de Czech '
 'First League, de Croatian HNL en de Keuken Kampioen Divisie hebben geen sportkey bij The Odds API '
 'en zijn dus tegen geen enkele prijs in te kopen. Daar komt 1X2 van het BetExplorer-marktgemiddelde, '
 'is de bookmaker niet herleidbaar en valt de edge systematisch te laag uit (§1a). Hetzelfde geldt '
 'voor de Romanian SuperLiga en de Kategoria Superiore, maar daar is geen enkel duel doorgerekend '
 '(twee keer NONE respectievelijk twee keer afgekapt). Het creditplafond stond op 509 en er is 76 '
 'van uitgegeven; er bleef 433 ongebruikt. Er zijn nul bets, dus er valt niets scheef te verdelen - '
 'maar de inkoop was deze run aantoonbaar niet de beperkende factor.'
)

VROEG_SEIZOEN_NOOT = (
 'Factor 1.0829, gepoold over 114 speeldagen in vijftien competities. Dat is met afstand de ruimste '
 'steekproef die deze correctie ooit heeft gehad - de vorige recordhouder was 53 speeldagen in acht '
 'competities op 11 september. Tien competities leveren de observatie in xG (Griekenland, '
 'Eliteserien, Allsvenskan, Segunda Division, Serie B, 2. Bundesliga, Zwitserland, Oostenrijk, '
 'League One, League Two); vijf hebben geen xG bij Fotmob en leveren hetzelfde niveauverschil in '
 'DOELPUNTEN, want dat is de eenheid waarin die duels sowieso rekenen: Tsjechie 1.298 -> 1.445 per '
 'ploeg per duel, Kroatie 1.331 -> 1.586, Roemenie 1.277 -> 1.262, de Keuken Kampioen Divisie 1.597 '
 '-> 1.942 en Albanie 1.103 -> 1.406. Alles komt uit de stand; er komt geen enkele bookmakerprijs '
 'aan te pas, dus §2 en de waarschuwing bij early_season_uplift blijven gerespecteerd. De ruwe '
 'gepoolde verhouding is 1.0888 en de prior van 8 speeldagen trekt hem terug naar 1.0829 - met '
 '114 speeldagen is dat terugtrekken nu marginaal, wat het punt van de prior is. Het effect per duel '
 'staat in het ou25-veld en is deze run groter dan gebruikelijk: P(Over 2.5) gaat gemiddeld 5.20 '
 'procentpunt omhoog over de vijfenveertig doorgerekende duels. Twee kanttekeningen die erbij horen. '
 'De Eliteserien en de Allsvenskan zijn kalenderjaarcompetities en staan op speeldag 19 en 21; daar '
 'meet deze correctie geen vroeg seizoen meer maar gewoon het niveauverschil tussen twee jaargangen, '
 'en met 40 van de 114 speeldagen wegen die twee zwaar mee. En de correctie dooft per definitie uit '
 'naarmate het seizoen vordert - dat ze hier juist oploopt komt doordat de meeste competities pas '
 'vier tot zeven speeldagen ver zijn.'
)

CREDITBRON = (
 'suggest_cap(19386, 19) = 509 - 19.386 credits over volgens api_check.py van deze run (20K-plan, '
 '614 gebruikt deze maand), 19 dagen tot de maandwissel, 2 runs per dag. split_budget(509, 10) geeft '
 '10 spreads / 10 totals bij tien inkoopbare competities, en omdat 3 x 10 = 30 ruim onder 509 ligt '
 'gaat de volle bulk door: h2h + spreads + totals in een aanroep per competitie. Uitgegeven: 76 '
 'credits in 56 aanroepen (10 bulk a 3 = 30, plus 46 BTTS-aanroepen a 1 credit). Dat BTTS 1 credit '
 'kost in plaats van de 2 uit §1a is sinds begin september elke run zo - het maakt BTTS goedkoper '
 'dan begroot, nooit duurder. Nog 19.310 credits over. Vijf van de vijftien competities zijn niet '
 'in te kopen wegens een ontbrekende sportkey (Tsjechie, Kroatie, Roemenie, Keuken Kampioen Divisie, '
 'Albanie); zie marktbalans hieronder.'
)

res = json.load(open("tmp-run/rb12_results.json"))
odds = json.load(open("tmp-run/rb12_odds.json"))
s3 = json.load(open("tmp-run/rb12_stage3.json"))
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
assert not bets, "deze run verwacht nul bets; pas rb12_emit.py aan als dat verandert"

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
