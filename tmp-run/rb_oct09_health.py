"""Run B, 9 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 9)
P = "data/source-health.json"
sh = json.load(open(P))
S = sh["sources"]


def prepend(key, status, text, role=None):
    e = S.setdefault(key, {})
    old = e.get("detail", "")
    e["status"] = status
    e["last_checked"] = DAY.isoformat()
    if role:
        e["role"] = role
    e["detail"] = f"[Run B] 9 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (9 en 10 okt), beide HTTP 200: 97 competities / 204 wedstrijden "
        "op 9 okt en 178 / 672 op 10 okt. Acht van de zeventien runlijstcompetities hadden duels "
        "in het inzetvenster, samen 19 — de breedste Run B-dag sinds de competities zijn hervat. "
        "Ook de kansbron: fetch_league_stats voor 8 competities x 2 seizoenen zonder één fout, "
        "plus de standen van de divisies eronder/erboven voor de omrekening van acht duels, plus "
        "matchDetails voor alle 19 duels. idcheck.py gaf voor alle 33 fotmob_id's uit "
        "coverage.json een bruikbare stand (afsluitcode 0); Serie B staat op 86 met xG voor alle "
        "twintig ploegen en is vandaag voor het eerst in een echte wedstrijd gebruikt. "
        "GEEN xG voor vijf van de zeventien competities, zoals coverage.json al vastlegt: Czech "
        "First League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189) "
        "en Keuken Kampioen Divisie (111). Die draaien op doelpunten en komen altijd op LIGHT "
        "uit; dat is geen storing. "
        "LET OP de bekende beperking, vandaag bij ELF van de 19 duels: squad_value komt op 0 "
        "terug zodra lineup_type 'unavailable', leeg of 'standard' is, en dan is de blessurekant "
        "van poort 7 niet meetbaar en valt het duel buiten het contextlogboek. Slechts 6 van de "
        "19 duels konden §1c in; de zeven met een waarde hadden lineup_type 'predicted' of "
        "'lastStarting11'. Oorzaak is timing: om 05:00 NL staat er voor een tweede divisie met "
        "een aftrap om 18:00-20:30 nog geen opstelling bij Fotmob.")

prepend("betexplorer", "ok",
        "8 competitiepagina's opgehaald, allemaal HTTP 200, voor de acht spelende competities. "
        "Twee rollen deze run. (1) BEVESTIGING van de runlijst: 75 fixturerijen, waarvan 19 met "
        "is_today — exact dezelfde 19 duels als Fotmob, dus de twee bronnen zijn volledig eens. "
        "Dat is de tweede methode die §1 van poort 1 eist en het is sinds de is_today-reparatie "
        "van 7 oktober weer een echte controle in plaats van een lege lijst. (2) Het gratis "
        "1X2-MARKTGEMIDDELDE voor alle 19 duels (3 tot 16 boeken per duel), nodig voor het "
        "kalibratieblok van §6e en voor poort 8 — en voor de vier competities ZONDER sportkey "
        "bij The Odds API is het de enige prijsbron die er is: Czech First League, Croatian HNL, "
        "Romanian SuperLiga en Keuken Kampioen Divisie, samen 13 van de 19 duels.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 48 actieve voetbalcompetities, quota 19.818 van de 20.000 over (182 "
        "gebruikt deze maand). Sleutel niet afgewezen. Deze run is er 15 credits uitgegeven: 4 "
        "bulk-aanroepen à 3 (h2h + spreads + totals) voor de vier spelende competities MET "
        "sportkey — Eliteserien, Allsvenskan, Serie B en 2. Bundesliga — en 3 event-aanroepen à 1 "
        "voor BTTS op de duels met een kandidaat-edge waar een event-id bij hoorde. "
        "EEN WAARNEMING OM VAST TE LEGGEN: api_check.py noemt soccer_norway_eliteserien en "
        "soccer_sweden_allsvenskan NIET onder 'Relevante sportkeys', en toch leverden beide "
        "gewoon acht events. Die lijst is een handmatige selectie in het script en geen uitspraak "
        "over wat de API aanbiedt; lees hem niet als 'deze competitie heeft geen prijzen'.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Gebruikt voor alle 15 credits van deze run; "
        "net_price toegepast op elke beurskoers. Matchbook en Betfair stonden vandaag beide als "
        "beste prijs op een gepubliceerde regel (Avellino – Sampdoria respectievelijk FC "
        "Heidenheim – Kaiserslautern).")

prepend("understat", "ok",
        "NIET aangeroepen deze run, en dat is geen storing: Understat dekt vijf competities (PL, "
        "La Liga, Bundesliga, Serie A, Ligue 1) en geen van die vijf staat op de runlijst van Run "
        "B. Er is dus niets te halen; het tweede xG-model is per ontwerp een Run A-bron.")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert "
        "normaal, dus de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "B",
    "date": DAY.isoformat(),
    "bets": 4,
    "matches_in_window": 19,
    "credits": 15,
}
sh["last_run_bevinding"] = (
    "Run B 9 okt 2026: 19 wedstrijden in het inzetvenster over acht competities, vier "
    "gepubliceerde regels — alle vier op RANGORDE, want geen enkele selectie haalde haar eigen "
    "drempel. Belangrijkste uitkomst is het VERVOLG op de reparatie van Run A van vanmorgen. Die "
    "trok §4 (het lopende seizoen weegt altijd mee via blend_seasons) door naar ploegen uit "
    "promotion.convert; die reparatie testte op xG en viel bij een competitie ZONDER xG terug op "
    "dezelfde ongeblende sterkte. Voor Run A maakte dat niets uit, want al zijn competities "
    "hebben xG — op de Run B-lijst hebben vijf van de zeventien er geen, en juist daar zitten de "
    "omgerekende ploegen: acht van de negentien duels van vandaag. Nu uitgebreid naar de "
    "doelpunteneenheid, en de eenheid klopt omdat promotion.convert terugrekent naar het niveau "
    "van de DOELcompetitie. Gemeten gevolg over drie Nederlandse degradanten: bij Heracles – RKC "
    "Waalwijk zakt de kans op een RKC-zege van 40,5% naar 28,6% en de geclaimde edge van +21,46 "
    "naar +9,51 pp — dat was de hoogste edge van de dag en de nummer 1 van de ruwe ranglijst, en "
    "na de reparatie staat die selectie niet meer in de top vijf. Poort 8 hield hem hoe dan ook "
    "tegen, dus het heeft geen bet gekost; wel een runrapport dat met een artefact had geopend. "
    "Bij FC Volendam – Vitesse valt de edge van +9,83 naar +6,91 pp en zakt die regel van plek 3 "
    "naar plek 4. Wat er gepubliceerd is: Avellino – Sampdoria Under 2.5 @1,8526 +6,82 pp (FULL, "
    "lat 8,0), FC Heidenheim – Kaiserslautern thuiszege @1,9114 +10,84 pp (LIGHT, lat 16,0), "
    "Eintracht Braunschweig – Holstein Kiel Under 3 @1,99 +4,11 pp en FC Volendam – Vitesse "
    "thuiszege @2,31 +6,91 pp. Verder: niets afgekapt (19 op een cap van 55), DRIE duels op "
    "data_tier NONE omdat promotion.TIER1/TIER2 geen divisiepaar kent voor Croatian HNL en "
    "Romanian SuperLiga (de hele Roemeense lijst plus het Kroatische duel — eerlijke NONE, geen "
    "omissie), poort 8 hield drie KKD-selecties tegen, en poort 5 vangt voor de DERDE dag op rij "
    "het overgrote deel weg: 84 van de 110 selecties (76%), na 40 van 60 op 7 okt en 29 van 37 "
    "op 8 okt. Dat is nu een reeks en geen waarneming. Stage 0 had niets af te wikkelen: de vier "
    "picks en zes schaduwpicks die openstaan zijn alle tien van Run A van vandaag, met een "
    "aftrap die nog moet komen."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
