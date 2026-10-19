"""Run A, 19 okt 2026 — bronprobe voor source-health.json.

8 duels in het inzetvenster over zeven competities: de maandag na een volle speelronde, de
kleinste runlijstdag sinds 13 oktober, maar met alle drie de bronkanten werkelijk in gebruik.
Fotmob voor de daglijsten, de 33 standen, de context van alle 8 duels, de divisies eronder voor
twee omrekeningen, de voorbeschouwingsblokken van de drie bets en de marktvormtelling van alle 8
duels. The Odds API voor de bulk (zeven competities) en BTTS (8 duels). BetExplorer voor het
gratis 1X2-marktgemiddelde van alle zeven competities, als tweede bron op de vraag wélke
wedstrijden er zijn, én als enige bron voor de vijf bekers. De statusregels komen dus uit echte
aanroepen en niet uit een probe.

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
     "19 okt (run A): daglijsten 19 en 20 okt opgehaald (65 resp. 46 competities, 111 resp. 161 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. "
     "Standen van alle zeven spelende competities geleverd, alle zeven met xG in zowel 2025/2026 "
     "als het lopende seizoen. Context opgehaald voor alle 8 duels, zonder één fout, en relocated "
     "is overal False. Daarnaast de standen van twee divisies eronder voor de twee omrekeningen "
     "van §4: Championship (48, voor Coventry City) en Serie B (86, voor Monza). Ook het "
     "voorbeschouwingsblok van de drie gepubliceerde duels (preview.match_block: h2h, insights, "
     "weer, weekoverzicht) en de marktvormtelling van alle 8 duels (marketform.match_block) komen "
     "hiervandaan — 8 van 8, nul fouten. ÉÉN GAT, en het is de bron en niet de code: bij VIBORG "
     "geeft Fotmob `squad_value` 0 voor de vermoedelijke basiself, terwijl er wél vijf uitvallers "
     "met een waarde van 1,78 mln in staan. `ctxlog.out_share` weigert dan terecht te rekenen "
     "(noemer 0) en Viborg – FC Midtjylland is daardoor de enige van de 8 die NIET in het "
     "contextlogboek staat — 7 van 8. Poort 7 stond daar hoe dan ook open (de bet is BTTS, dus "
     "side = None), en een ontbrekende meting laat de poort per §1c open; het kost dus geen bet, "
     "alleen een rij in de steekproef.")

note("the_odds_api", "ok",
     "19 okt (run A): api_check.py OK, 49 actieve voetbalcompetities, quota 19131 over / 869 "
     "gebruikt deze maand. 29 credits uitgegeven: 7 bulk-aanroepen (h2h+spreads+totals, 3 credits "
     "per competitie) en 8 BTTS-aanroepen à 1 credit. ALLE ZEVEN spelende competities hebben een "
     "sportkey, dus er is deze run geen enkel duel waar BetExplorer de enige 1X2-bron is — anders "
     "dan gisteren, toen de Scottish Premiership daarin viel.")

note("oddsapi", "ok",
     "19 okt (run A): fetch_bulk gaf voor alle zeven sportkeys events met h2h, spreads en totals "
     "(21, 22, 21, 10, 7, 7 en 10 events); fetch_event_markets gaf btts voor 8 van de 8 duels met "
     "een kandidaat-edge. store['errors'] is LEEG — nul fouten over de hele run. Pinnacle in de "
     "respons voor ALLE 8 duels (Stage 5 stap 2, gemiddelde marge 3,81%, gemiddelde afstand tot "
     "het eigen model 6,35 pp — ruim boven de 4,33 van gisteren, op een steekproef van acht). "
     "Betfair en Matchbook ook, en net_price is toegepast op de Matchbook-koers van alle drie de "
     "gepubliceerde regels (1.99/1.9702, 2.64/2.6072 en 2.14/2.1172 bruto/netto) — alle drie "
     "staan dus op een BEURSKOERS en de gebruiker ziet op de site de hogere, kale prijs. De winst "
     "van de beste prijs boven het BetExplorer-marktgemiddelde liep van +4,46% (Wisła Płock – "
     "Radomiak Radom) tot +7,24% (Viborg – FC Midtjylland) over alle 8 duels.")

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
     "19 okt (run A): " + "; ".join(det) + ". Deze run in drie rollen gebruikt: (1) het gratis "
     "1X2-marktgemiddelde voor alle zeven competities, voor het kalibratieblok van §6e en poort 8 "
     "(10 tot 17 boeken per duel); (2) als TWEEDE BRON op de vraag wélke wedstrijden er zijn — "
     "zestien van de zestien competities met een fotmob_id eens, 8 duels tegen 8, nul afwijkingen; "
     "(3) als ENIGE bron voor de vijf bekers zonder fotmob_id, die alle vijf teamparen op de "
     "fixturepagina leveren (11, 8, 8, 26, 16) en geen ronde in het venster hebben. GEEN HAPERING "
     "deze run, en geen enkele slug viel in de homepage-redirect-faalmodus.")

note("understat", "ok",
     "19 okt (run A): fetch_league voor alle VIJF de Understat-competities (Premier League, Serie "
     "A, La Liga, Bundesliga, Ligue 1, seizoen 2025) gaf een volledige stand. DRIE van die vijf "
     "speelden vandaag (Premier League 1, Serie A 2, La Liga 1 — Bundesliga en Ligue 1 niet), "
     "samen 4 duels, en werkelijk BRUIKBAAR voor 2 van die 4: Parma – Torino en Getafe – Rayo "
     "Vallecano. De twee die het niet hebben zijn precies de twee met een omgerekende ploeg — "
     "Tottenham Hotspur – Coventry City en Monza – Cagliari — en dat is terecht: een promovendus "
     "staat niet in de stand van 2025/2026. Er is dus GEEN enkel duel waar understat_pair None "
     "gaf zonder promotiereden, anders dan gisteren (Borussia Mönchengladbach – Hoffenheim, "
     "naamkoppeling).")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "A", "date": "2026-10-19",
                 "matches_in_window": 8, "bets": 3,
                 "note": "8 duels in het inzetvenster [08:00 NL 19 okt, 08:00 NL 20 okt) over "
                         "zeven competities: Serie A 2 en Premier League, La Liga, Primeira Liga, "
                         "Super Lig, Danish Superliga en Ekstraklasa elk 1. Geen enkel duel op "
                         "tier NONE — 6 FULL en 2 LIGHT (de twee omgerekende promovendi Coventry "
                         "City en Monza) — en geen kruis-grensduel, want de drie Europese "
                         "toernooien spelen 21 en 22 oktober. Drie gepubliceerde regels, de volle "
                         "MAX_SHORTLIST van een maandag, waarvan ÉÉN boven zijn eigen lat en ook "
                         "op de ruwe schaal."}
H["last_run_bevinding"] = (
    "Drie dingen. (1) DE `underdog`-REEKS IS VAN TEKEN GEDRAAID EN DE POORT BESPAART NU GELD. Op "
    "5 oktober stond die reeks op +16,9% over 36 afgewikkelde kandidaten en was dat de meting die "
    "de vraag van 25 september moest beantwoorden; vandaag staat hij op -4,4% over 162 "
    "afgewikkelde kandidaten (78 winnaars, 48,1% trefkans). De eerste van de twee uitwegen van "
    "§1e — positieve ROI over >=30 gevallen — is daarmee DICHT. Dat is geen aanleiding om de vraag "
    "opnieuw voor te leggen: hij draait naar de kant waarop de poort blijft staan, en de "
    "kalibratiefout die hij afdekt is er nog (+1,66 pp te veel kans op longshots, -3,35 pp te "
    "weinig op favorieten over 5427 uitkomsten). `underdog_ruw` staat op -8,8% over 17 gevallen; "
    "die twee blijven twee populaties en worden nooit opgeteld. (2) DIE POORT WAS VANDAAG "
    "BINDEND OP DE HELE LIJST. Zonder poort 8 hadden plek 1 en 3 van de ruwe top drie een "
    "underdog-handicap gestaan: Coventry City +1.5 @1.67 (+14,52 pp) bij Tottenham en Gil Vicente "
    "+1 @1.8428 (+8,18 pp) bij Braga. Twee van de drie regels van de dag, allebei op de kant "
    "waarvan §1e op uitkomsten heeft gemeten dat het model er structureel naast zit (z = -3,14 "
    "over 89 gevallen). (3) GEEN ENKELE REGEL OP DE UNDER-KANT, VOOR HET EERST DEZE WEEK, MAAR "
    "TWEE OP BTTS 'NEE'. §6g meet Under op -16,5% over 76 picks tegen Over op +10,6% over 62, en "
    "`goalbias` zet P(Under 2.5) 2,1 pp te hoog over 1410 duels. Poort 9 houdt die kant tegen in "
    "de band 8-10 pp op FULL en had vandaag niets te toetsen. Maar BTTS 'nee' deelt vermoedelijk "
    "dezelfde vormfout en staat per besluit van 11 oktober BUITEN poort 9, omdat 15 afgewikkelde "
    "BTTS-picks geen meting zijn. Twee van de drie regels van vandaag staan daar, zonder rem. Dat "
    "is het eerste wat opnieuw bekeken hoort te worden zodra die reeks ~30 haalt — en vandaag "
    "komt hij twee rijen naderbij.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")
