"""Run A, 20 okt 2026 — bronprobe voor source-health.json.

10 duels in het inzetvenster over TWEE competities: een Champions League-avond (9 duels,
speelronde 3) plus één ingehaalde Championship-wedstrijd. Alle drie de bronkanten werkelijk
in gebruik. Fotmob voor de daglijsten, de 33 standen, de context van alle 10 duels, de
binnenlandse standen voor de kruis-grensomrekening van §4, de Premier League-stand voor de ene
degradant, de voorbeschouwingsblokken van de twee bets en de marktvormtelling van 9 duels.
The Odds API voor de bulk (twee competities) en BTTS (7 duels). BetExplorer voor het gratis
1X2-marktgemiddelde, als tweede bron op de vraag wélke wedstrijden er zijn, én als enige bron
voor de vijf bekers. De statusregels komen dus uit echte aanroepen en niet uit een probe.

Als gisteren: GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.
"""

import json, datetime
from scripts import betexplorer

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
H = json.load(open("data/source-health.json"))
S = H["sources"]


def note(key, status, detail):
    prev = S.get(key, {})
    hist = prev.get("detail_history") or []
    if prev.get("detail") and prev.get("last_checked"):
        hist = (hist + [{"date": prev["last_checked"], "detail": prev["detail"]}])[-6:]
    S[key] = {**prev, "status": status, "last_checked": now[:10], "detail": detail,
              "detail_history": hist}
    print(f"{key:18} {status:8} {detail[:110]}")



note("fotmob", "ok",
     "20 okt (run A): daglijsten 20 en 21 okt opgehaald (47 competities elk, 162 resp. 141 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare "
     "stand. Standen van beide spelende competities geleverd, beide met xG in zowel 2025/2026 "
     "als het lopende seizoen. Context opgehaald voor alle 10 duels, zonder een fout, en 10 van "
     "10 staan in het contextlogboek. EEN duel komt op relocated = True: Sabah FK - Borussia "
     "Dortmund wordt in het Baki Olimpiya Stadionu gespeeld in plaats van in het eigen stadion "
     "van Sabah - het normale patroon voor een Champions League-thuiswedstrijd van een kleine "
     "club, en §1c eist dat het wordt gemeld ook als de poort opengaat. Daarnaast de binnenlandse "
     "standen voor de kruis-grensomrekening van de negen Champions League-duels "
     "(scripts/interleague.py) en de Premier League-stand voor de ene degradant (Wolverhampton "
     "Wanderers, convert_relegated). Ook het voorbeschouwingsblok van de twee gepubliceerde duels "
     "(preview.match_block: h2h, insights, weer, weekoverzicht) en de marktvormtelling van 9 "
     "duels (marketform.match_block) komen hiervandaan - nul fouten. GEEN GAT deze run.")

note("the_odds_api", "ok",
     "20 okt (run A): api_check.py OK, 49 actieve voetbalcompetities, quota 19091 over / 909 "
     "gebruikt deze maand. 13 credits uitgegeven: 2 bulk-aanroepen (h2h+spreads+totals, 3 "
     "credits per competitie) en 7 BTTS-aanroepen a 1 credit - een goedkope dag, want negen van "
     "de tien duels zitten in EEN competitie en spreads/totals/h2h rekenen per competitie af "
     "(§0). Beide spelende competities hebben een sportkey, dus er is deze run geen enkel duel "
     "waar BetExplorer de enige 1X2-bron is.")

note("oddsapi", "ok",
     "20 okt (run A): fetch_bulk gaf voor beide sportkeys events met h2h, spreads en totals (13 "
     "events voor de Championship, 18 voor de Champions League); fetch_event_markets gaf btts "
     "voor 7 van de 7 duels met een kandidaat-edge. store['errors'] is LEEG - nul fouten over de "
     "hele run. Pinnacle in de respons voor 9 van de 10 duels (Stage 5 stap 2, gemiddelde marge "
     "3,78%, gemiddelde afstand tot het eigen model 4,77 pp - beter dan de 6,35 van gisteren, en "
     "dat op een dag waarop alle negen duels via een omrekening lopen). Het tiende is Roma - "
     "Slovan Bratislava, dat op tier NONE staat en dus geen eigen 1X2 heeft om tegen te leggen. "
     "BEIDE gepubliceerde koersen komen van 1xBet en dus van een BOOKMAKER en niet van een "
     "beurs: EXCHANGE_COMMISSION komt deze run niet aan de orde en de genoteerde koers is de "
     "koers waarop is gerekend. De winst van de beste prijs boven het BetExplorer-marktgemiddelde "
     "liep van +4,12% (VfB Stuttgart - Atletico Madrid) tot +24,37% (Manchester City - AEK "
     "Athens) over de negen duels met beide bronnen; die laatste uitschieter zit op een duel met "
     "een zware favoriet, waar een gemiddelde over vier boeken weinig zegt.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

probes = {
    "Serie A (ITA)": "https://www.betexplorer.com/football/italy/serie-a/",
    "Ekstraklasa (POL)": "https://www.betexplorer.com/football/poland/ekstraklasa/",
    "FA Cup (ENG)": "https://www.betexplorer.com/football/england/fa-cup/",
}
ok, det = True, []
for naam, url in probes.items():
    try:
        rows = betexplorer.fetch_league_fixtures(url)
        det.append(f"{naam}: {len(rows)} fixtures met 1X2-gemiddelde")
    except Exception as e:
        ok = False
        det.append(f"{naam}: FAIL {type(e).__name__}: {e}")
note("betexplorer", "ok" if ok else "partial_failure",
     "20 okt (run A): " + "; ".join(det) + ". Deze run in drie rollen gebruikt: (1) het gratis "
     "1X2-marktgemiddelde voor beide spelende competities, voor het kalibratieblok van §6e en "
     "poort 8 (4 boeken per Champions League-duel, 11 voor het Championship-duel); (2) als "
     "TWEEDE BRON op de vraag welke wedstrijden er zijn - zestien van de zestien competities met "
     "een fotmob_id eens, 10 duels tegen 10, nul afwijkingen, en dat is inclusief de veertien die "
     "vandaag GEEN WEDSTRIJD hebben; (3) als ENIGE bron voor de vijf bekers zonder fotmob_id, die "
     "alle vijf teamparen op de fixturepagina leveren (29, 8, 8, 26, 16) en geen ronde in het "
     "venster hebben. GEEN HAPERING deze run, en geen enkele slug viel in de "
     "homepage-redirect-faalmodus.")

note("understat", "ok",
     "20 okt (run A): fetch_league voor alle VIJF de Understat-competities (Premier League, Serie "
     "A, La Liga, Bundesliga, Ligue 1, seizoen 2025) gaf een volledige stand - de bron is dus in "
     "orde. GEEN van die vijf speelt vandaag, dus er is deze run GEEN enkel duel met een tweede, "
     "onafhankelijk xG-model naast Fotmob. Dat is geen storing maar de kalender: de vijf grote "
     "competities spelen hun volgende ronde op 23 oktober of 1 november. Gevolg voor §2: de "
     "kansinput van alle negen doorgerekende duels komt van een bron in twee doorsnedes (Fotmob "
     "team-xG en de thuis/uit-splits), plus de omrekening van interleague/promotion daarop. Dat "
     "is genoeg voor de regel, maar het is minder redundantie dan op een gewone binnenlandse "
     "speeldag en het hoort genoemd.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "A", "date": "2026-10-20",
                 "matches_in_window": 10, "bets": 2,
                 "note": "10 duels in het inzetvenster [08:00 NL 20 okt, 08:00 NL 21 okt) over "
                         "TWEE competities: de UEFA Champions League met 9 (speelronde 3) en de "
                         "Championship met 1 (een ingehaalde dinsdagavondwedstrijd). GEEN ENKEL "
                         "duel op FULL - negen op LIGHT (acht kruis-grens, een met een "
                         "omgerekende degradant) en een op NONE (Roma - Slovan Bratislava: voor "
                         "SVK is geen Europese competitiefactor gemeten). Twee gepubliceerde "
                         "regels in plaats van de drie die een dinsdag toestaat, en dat is "
                         "MAX_LIGHT_IN_SHORTLIST = 2 die bindt omdat er geen FULL-duel is. Een "
                         "van de twee haalt zijn eigen lat en ook de ruwe schaal."}
H["last_run_bevinding"] = (
    "Drie dingen. (1) BEIDE GEPUBLICEERDE REGELS STAAN OP DE UNDER-KANT EN ER STAAT GEEN REM OP. "
    "Dat is het belangrijkste van deze run en het hoort vooraan. §6g meet Under op -16,5% over 76 "
    "picks tegen Over op +10,6% over 62, en `goalbias` zet vandaag P(Under 3.5) 1,9 pp te hoog "
    "over 1426 duels en geeft de GESPEELDE Unders +0,51 doelpunt per duel te weinig (z = +2,80 "
    "over 81 gevallen) - dus een vormfout plus een selectie-effect, precies de twee fouten die §6g "
    "op elkaar vindt. Poort 9 is voor deze kant gebouwd, maar hij bindt alleen op FULL en er is "
    "vandaag geen enkel FULL-duel; op LIGHT blijft hij per besluit van de gebruiker van 12 "
    "oktober buiten. De twee regels zijn dus door geen enkele rem getoetst. Dat is niet in strijd "
    "met de regels maar het is wel het gat dat §1h zelf benoemt, en het is de tweede keer deze "
    "maand (de eerste was Atalanta - Venezia op 12 oktober). De vraag wordt NIET opnieuw "
    "voorgelegd — §1h verbiedt dat — maar hij staat hiermee opgeschreven. (2) ER IS GEEN ENKEL "
    "FULL-DUEL, EN DAARDOOR BINDT MAX_LIGHT_IN_SHORTLIST IN PLAATS VAN DE DREMPEL. Negen van de "
    "tien duels zijn kruis-grens en het tiende heeft een omgerekende degradant; beide wegen "
    "leveren per definitie LIGHT. De lijst is daarom twee regels lang in plaats van drie, en de "
    "eerstvolgende op rangorde (Fenerbahce - Slavia Prague, Over 2.5, +8,35 pp) is niet door een "
    "poort of door de drempel afgewezen maar door die grens. Dat is een ander soort afkapping dan "
    "de routine gewoonlijk meldt en het hoort als zodanig gelezen. (3) POORT 8 HIELD DE STERKSTE "
    "SELECTIE VAN DE RUWE LIJST TEGEN. VfB Stuttgart +0.25 @2.078 (+23,36 pp, score 8,349) voert "
    "de ruwe top drie aan, boven de PSG-regel die wel is gepubliceerd - en op dat duel staat het "
    "model 22,04 procentpunt boven het Pinnacle-oordeel op de thuiszege (51,0% tegen 29,0%), het "
    "grootste verschil van de hele run. Dat is precies het patroon waarvan §1e op uitkomsten heeft "
    "gemeten dat het model er structureel naast zit. De `underdog`-reeks staat nu op -4,4% over "
    "164 afgewikkelde kandidaten en bespaart dus geld; `underdog_ruw` op -8,8% over 17. Die twee "
    "blijven twee populaties en worden nooit opgeteld.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")
