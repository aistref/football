"""Run B, 10 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date

DAY = date(2026, 10, 10)
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
    e["detail"] = f"[Run B] 10 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (10 en 11 okt), beide HTTP 200. ZESTIEN van de zeventien "
        "runlijstcompetities hadden duels in het inzetvenster, samen 77 — met afstand de "
        "grootste Run B-dag tot nu toe (19 op 9 oktober). Alleen de Keuken Kampioen Divisie "
        "speelde niet. Ook de kansbron: fetch_league_stats voor 16 competities x 2 seizoenen "
        "zonder één fout, plus de standen van de divisies eronder/erboven voor de omrekening van "
        "25 duels, plus matchDetails voor alle 77 duels (nul ctx-fouten). idcheck.py gaf voor "
        "alle 33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode 0). "
        "GEEN xG voor vijf van de zeventien competities, zoals coverage.json al vastlegt: Czech "
        "First League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189) "
        "en Keuken Kampioen Divisie (111). Die draaien op doelpunten en komen altijd op LIGHT "
        "uit; dat is geen storing. "
        "NIEUW VASTGELEGD, EN HET CORRIGEERT DE LEZING VAN 9 OKTOBER NIET MAAR BEVESTIGT HAAR "
        "MET CIJFERS: squad_value komt op 0 terug bij 90 van de 154 ploegzijden, waardoor 52 "
        "van de 77 duels buiten het contextlogboek vallen (25 kwamen erin). De kruistabel van "
        "lineup_type tegen squad_value wijst de klok aan en niet de competitie: lineup_type "
        "'unavailable' 52 ploegzijden, alle 52 op 0; 'standard' 6, alle op 0; leeg 14, alle op "
        "0; 'lastStarting11' 78 waarvan 60 MET waarde; 'predicted' 4, alle met waarde. Zodra er "
        "een opstelling staat is er in 64 van de 82 gevallen ook een marktwaarde. Om 05:10 NL "
        "staat er bij een aftrap van 13:00-16:00 nog geen opstelling, en dat is inherent aan de "
        "deadline van §0 (rapporten klaar om 06:30). Zie BEVINDING_3 in "
        "data/run-state/2026-10-10-run-b.json. "
        "DERDE DIVISIES BESTAAN WEL BIJ FOTMOB, en dat is deze run nagetrokken in "
        "api/data/allLeagues: Serie C (ITA) id 147, 3. Liga (GER) id 208, National League (ENG) "
        "id 117 — alle drie met een bruikbare stand van 2025/2026 en alle drie ZONDER xG. Let "
        "op: fetch_league_stats(147) geeft stil ÉÉN van de DRIE parallelle Serie C-groepen terug "
        "(20 ploegen). Dat is de groepsval die §4 op 5 oktober voor de Primera Federación "
        "beschrijft.")

prepend("betexplorer", "ok",
        "16 competitiepagina's opgehaald, allemaal HTTP 200, voor de zestien spelende "
        "competities: 183 fixturerijen in totaal. Twee rollen deze run. (1) BEVESTIGING van de "
        "runlijst — de tweede methode die poort 1 van §1 eist. (2) Het gratis "
        "1X2-MARKTGEMIDDELDE, nodig voor het kalibratieblok van §6e en voor poort 8, en voor de "
        "VIER competities ZONDER sportkey bij The Odds API de enige prijsbron die er is: Czech "
        "First League, Croatian HNL, Hungarian NB I en Romanian SuperLiga, samen 11 van de 77 "
        "duels. "
        "ÉÉN BEPERKING OM TE NOTEREN: bij MLS gaf de pagina 30 fixturerijen maar slechts 2 met "
        "is_today, en bij Série A (BRA) 20 rijen met 1 is_today, terwijl Fotmob daar 14 "
        "respectievelijk 2 duels in het inzetvenster zag. Dat is de tijdzonekant van dezelfde "
        "vraag als Stage 1: BetExplorer markeert 'today' op zijn eigen kalenderdag, en een "
        "MLS-duel dat om 01:30 NL aftrapt valt daar buiten. Het raakt de prijzen niet (die "
        "kwamen voor MLS van The Odds API) en de bets niet, maar wie het marktgemiddelde ooit "
        "als enige 1X2-bron voor MLS wil gebruiken, loopt hier tegenaan.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 48 actieve voetbalcompetities, quota 19.735 van de 20.000 over (265 "
        "gebruikt deze maand). Sleutel niet afgewezen. Deze run is er 69 credits uitgegeven: 12 "
        "bulk-aanroepen à 3 (h2h + spreads + totals) voor ALLE twaalf spelende competities MET "
        "sportkey, en 33 event-aanroepen à 1 voor BTTS op alle 33 duels met een kandidaat-edge. "
        "Dat laatste leverde twee extra gekwalificeerde selecties op (Bradford City – Leyton "
        "Orient en Wycombe Wanderers – Luton Town, beide BTTS nee). "
        "DE WAARNEMING VAN 9 OKTOBER STAAT NOG EN IS VANDAAG BREDER BEVESTIGD: api_check.py "
        "noemt van de twaalf gekochte competities maar DRIE onder 'Relevante sportkeys' "
        "(soccer_spain_segunda_division, soccer_italy_serie_b, soccer_germany_bundesliga2), en "
        "toch leverden alle twaalf events — Greek Super League 14, Eliteserien 7, Allsvenskan 8, "
        "Swiss Super League 6, Austrian Bundesliga 12, English League One 13, English League Two "
        "12, MLS 30 en Série A 20. Die lijst is een handmatige selectie in het script en geen "
        "uitspraak over wat de API aanbiedt; lees hem niet als 'deze competitie heeft geen "
        "prijzen'.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Gebruikt voor alle 69 credits van deze run; "
        "net_price toegepast op elke beurskoers. MATCHBOOK stond vandaag op twee van de vijf "
        "gepubliceerde regels als beste prijs (Sporting Kansas City – Portland Timbers 2,02 "
        "bruto / 1,9996 netto en Magdeburg – Hannover 96 1,98 / 1,9604); de andere drie staan "
        "bij gewone bookmakers (1xBet, Tipico, Pinnacle) zonder commissie.")

prepend("understat", "ok",
        "NIET aangeroepen deze run, en dat is geen storing: Understat dekt vijf competities (PL, "
        "La Liga, Bundesliga, Serie A, Ligue 1) en geen van die vijf staat op de runlijst van "
        "Run B. Er is dus niets te halen; het tweede xG-model is per ontwerp een Run A-bron.")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert "
        "normaal, dus de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "B",
    "date": DAY.isoformat(),
    "bets": 5,
    "matches_in_window": 77,
    "credits": 69,
}
sh["last_run_bevinding"] = (
    "Run B 10 okt 2026: 77 wedstrijden in het inzetvenster over ZESTIEN van de zeventien "
    "competities — met afstand de grootste Run B-dag tot nu toe — en VIJF gepubliceerde regels "
    "die voor het eerst ALLE VIJF hun eigen drempel halen. Op 9 oktober stonden alle vier de "
    "regels nog op rangorde zonder dat één selectie haar lat haalde. Gevolg: de §5b-afkapping "
    "op LIJSTLENGTE bindt voor het eerst sinds 26 september — acht selecties haalden alle acht "
    "poorten én hun drempel, er passen vijf regels in, dus Rosenborg – Sandefjord (+8,42 pp), "
    "Wycombe Wanderers – Luton Town (+11,89 pp) en Bradford City – Leyton Orient (+8,29 pp) "
    "vallen af op niets anders dan de lengte van de lijst en gaan als failed_gate = "
    "'lijstlengte' het schaduwlogboek in. Gepubliceerd: Toronto FC – CF Montréal Under 3.5 "
    "@1,71 +16,38 pp, Sporting Kansas City – Portland Timbers Under 3.5 @1,9996 +12,03 pp, AIK "
    "– Brommapojkarna Under 3.5 @1,55 +9,28 pp, Magdeburg – Hannover 96 DNB Hannover @1,9604 "
    "+10,97 pp en Austria Wien – Sturm Graz handicap Sturm Graz -0.25 @1,98 +10,60 pp; alle vijf "
    "FULL. "
    "DRIE BEVINDINGEN. (1) ACHT van de 77 duels komen op data_tier NONE omdat promotion.TIER2 "
    "geen DERDE divisie kent voor Serie B, 2. Bundesliga en English League Two — vier "
    "Serie B-duels, twee 2. Bundesliga en twee League Two, alle acht met een promovendus uit de "
    "derde divisie. En de foutmelding noemt ze alle acht 'degradant' die niet in de divisie "
    "BOVEN hun competitie staat, omdat de promovendi-tak zonder melding wordt overgeslagen als "
    "TIER2 geen ingang heeft. De uitkomst NONE is correct (§4 verbiedt een gepoolde factor), de "
    "reden wijst de verkeerde richting aan. Anders dan bij Kroatië is dit WEL meetbaar: Serie C "
    "(147), 3. Liga (208) en National League (117) staan alle drie bij Fotmob met een bruikbare "
    "stand. Niet vandaag gemeten en niet met terugwerkende kracht toegepast, zoals §4 sinds "
    "9 oktober voorschrijft; het staat als besluit bij de gebruiker. Let bij Serie C op de drie "
    "parallelle groepen. (2) Poort 5 vangt voor de VIJFDE dag op rij driekwart weg: 538 van 703 "
    "selecties (76,5%), na 40/60, 29/37, 84/110 en 553/754. Het schaduwlogboek zegt dat die "
    "poort per saldo geld KOST (+2,1% over 103 afgewikkelde kandidaten) in plaats van bespaart. "
    "Volgen, niet vandaag verzetten (§6d). (3) 52 van de 77 duels komen het contextlogboek niet "
    "in omdat squad_value ontbreekt bij 90 van de 154 ploegzijden; de kruistabel wijst de KLOK "
    "aan en niet de competitie (lineup_type 'unavailable' bij 52 zijden, alle 52 zonder waarde), "
    "en dat botst met de deadline van 06:30 uit §0. "
    "VERDER: de cap bindt voor de tweede dag op rij — 22 van de 77 duels afgekapt op een "
    "zaterdagcap van 55, de laagste die het haalde op datarijkdom 5,0 (Eldense – Córdoba) tegen "
    "4,75 voor de hoogste die afviel (Mansfield Town – Bromley). Zes duels stonden op de "
    "daglijst van 11 oktober en horen tóch bij deze run; één daarvan (Sporting Kansas City, "
    "aftrap 02:30 NL) is een gepubliceerde bet, precies waarvoor runwindow.py op 24 september is "
    "gebouwd. Poort 8 hield 33 selecties tegen over 12 wedstrijden, geen daarvan zou de lijst "
    "hebben aangevoerd; zijn `underdog`-reeks is VAN TEKEN GEDRAAID — -2,5% over 50 afgewikkelde "
    "gevallen, tegen +4,6% over 45 op 9 oktober en +16,9% over 36 op 5 oktober — en dat is de "
    "verkeerde kant op om de vraag van 25 september opnieuw voor te leggen: de uitweg was juist "
    "een POSITIEVE ROI. Stage 0 had niets af te wikkelen; de vijf openstaande picks en 85 "
    "openstaande schaduwrijen zijn de duels van vandaag van Run A, die nog niet gespeeld zijn. "
    "69 van 448 credits gebruikt, maandverbruik 334 van 20.000."
)
json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
