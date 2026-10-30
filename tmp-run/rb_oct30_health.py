"""Run B, 30 okt 2026 — bronprobe voor source-health.json.

TWAALF duels in het inzetvenster over ACHT competities, alle twaalf onder de vrijdagcap van 55.
Alle vier de bronkanten werkelijk in gebruik; Understat deed niet mee (geen van zijn vijf
competities staat op deze runlijst).

GEEN ENKELE BRONSTORING. `store["errors"]` is over de hele run leeg gebleven.

DE BRONBEVINDING VAN VANDAAG ZIT IN DE NAAMKOPPELING EN NIET IN EEN BRON. BetExplorer leverde de
Keuken-Kampioen-Divisie-rij van Roda JC Kerkrade – Jong AZ Alkmaar gewoon aan ('Roda – Jong AZ',
1,72/4,01/3,91), maar `ra_names.best_pair` koppelde hem niet: de paarscore kwam op 0,518 uit tegen
een vloer van 0,62, omdat BEIDE namen een staart missen die `_DROP` niet kent. Dat duel kwam
daardoor met NUL PRIJZEN in alle zes de markten de analyse binnen. Gerepareerd in deze run met een
terugval op woordniveau; zie bevinding 1 van het runrapport en `ra_names.selftest`.

TWEEDE WAARNEMING, EN ZE IS GEEN FOUT: Jong AZ Alkmaar heeft bij Fotmob `squad_value = 0`. Dat is
een reserveteam zonder genoteerde marktwaarden, dus `ctxlog.out_share` kan er geen aandeel van
maken en de wedstrijd valt uit het contextlogboek (11 van de 12 in plaats van 12 van de 12). Een
meting die er niet is, is geen gat — maar het hoort opgeschreven, want de Keuken Kampioen Divisie
heeft vier van zulke Jong-ploegen en die komen elke speelronde terug.
"""

import json, datetime

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
    print(f"{key:18} {status:12} {detail[:100]}")


note("fotmob", "ok",
     "30 okt (run B): daglijsten 30 en 31 okt opgehaald (170 duels over 94 competities en 723 over "
     "184); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand, "
     "afsluitcode 0 - ook voor de negen competities van deze runlijst die vandaag stil zijn, en dat "
     "is precies de kant van de controle die iets kan opleveren. Standen van alle acht de spelende "
     "competities geleverd. DRIE VAN DE ACHT HEBBEN GEEN xG EN DAT IS DE BEKENDE, VASTGELEGDE "
     "STAND, geen storing: Croatian HNL (252), Romanian SuperLiga (189) en Keuken Kampioen Divisie "
     "(111) staan in coverage.json met xG=False en idcheck.py bevestigt dat per competitie. Die "
     "drie leveren samen zes van de twaalf duels, dus de helft van deze run draait op doelpunten "
     "als sterktemaat (LIGHT, lat 16,0 pp). Context voor alle twaalf duels zonder fout en de "
     "stadionvelden zijn alle twaalf gevuld; context.check_venue sloeg NERGENS aan (relocated = "
     "False overal, elke ploeg op het eigen veld). EEN SQUAD_VALUE OP NUL: Jong AZ Alkmaar, het "
     "reserveteam van AZ, heeft geen genoteerde marktwaarden, dus ctxlog.out_share geeft daar None "
     "en dat duel valt uit het contextlogboek (11 van 12). Dat is geen bronfout maar een meting die "
     "niet bestaat; de KKD heeft vier Jong-ploegen en dit komt elke speelronde terug. lineupType: "
     "11 van de 12 op 'lastStarting11' en 1 op 'predicted', geen enkel 'confirmed' - te verwachten "
     "bij een run die om 10:20 NL de prijzen uitleest en aftrappen van 18:00 tot 00:00 de volgende "
     "nacht. Voorbeschouwingsblokken (preview.py) voor alle drie de bets zonder fout, en "
     "marketform.match_block voor alle elf doorgerekende duels zonder fout.")

note("the_odds_api", "ok",
     "30 okt (run B): sleutel geldig, 47 actieve voetbalcompetities, quota 18.547 over en 1.453 "
     "verbruikt bij de start van de run. Geen afgewezen sleutel en geen quotaprobleem. VIJF VAN DE "
     "ACHT SPELENDE COMPETITIES HEBBEN EEN SPORTKEY en kregen de volledige bulk-aanroep: "
     "Eliteserien, 2. Bundesliga, Austrian Bundesliga, English League Two en Serie A (BRA). DRIE "
     "HEBBEN ER GEEN - Croatian HNL, Romanian SuperLiga en Keuken Kampioen Divisie - en die draaien "
     "op het gratis BetExplorer-marktgemiddelde, dus zonder herleidbare bookmaker en zonder enige "
     "doelpunten- of handicapmarkt. Dat raakt zes van de twaalf duels en een van de drie "
     "gepubliceerde regels (FC Volendam, 1 @1,97 op 17 boeken). DE SPORTKEY-CONTROLE GEEFT VANDAAG "
     "VOOR HET EERST GEEN ENKELE AFWIJKING: de sleutels van MLS, Serie A (BRA) en Eliteserien zijn "
     "op 28 oktober aan oddsapi.SPORT_KEYS toegevoegd, dus alle elf inkoopbare competities van deze "
     "runlijst staan nu in de registratie en api_check.py kan ze zelf nalopen. Wat api_check.py nog "
     "wel meldt: vier actieve sportkeys die de repo niet kent (soccer_brazil_serie_b, "
     "soccer_germany_liga3, soccer_sweden_superettan, soccer_uefa_nations_league) en twee bekende "
     "sleutels die vandaag niet actief zijn (Coppa Italia, DFB Pokal). Geen van die zes staat op "
     "deze runlijst; de eerste drie zijn juist de divisies ONDER drie competities van de runlijst "
     "en dus interessant voor de promovendi-omrekening van §4, niet voor de prijzen.")

note("oddsapi", "ok",
     "30 okt (run B): 17 van een plafond van 4631 credits gebruikt - 15 aan de bulk (h2h + spreads "
     "+ totals voor vijf competities, 3 per competitie) en 2 aan BTTS voor de twee duels met een "
     "kandidaat-edge waar dat kon. suggest_cap(18547, 2) gaf 4631 en split_budget(4631, 5) gaf "
     "(5, 5); het plafond bond nergens. MARKTBALANS-CONTROLE GEHAALD: vijf van de vijf inkoopbare "
     "competities kregen uit dezelfde bulk zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een "
     "doelpuntenmarkt (O/U), dus er is geen enkele competitie met alleen het een of het ander. Voor "
     "de drie zonder sportkey is er alleen het gratis 1X2 - dat is de grens van de gratis bron en "
     "niet van het plafond. Alle zes markten dongen mee: 1X2 32 selecties, Over/Under 20, Asian "
     "Handicap 16, Draw No Bet 8, BTTS 4 en Double Chance 2. BTTS kon bij FC Volendam - De "
     "Graafschap NIET worden gekocht omdat de KKD geen sportkey heeft; dat staat als zodanig in "
     "markets_checked ('niet opgevraagd') en niet als gat (§1a). TWEE VAN DE DRIE GEPUBLICEERDE "
     "REGELS STAAN OP EEN BEURSKOERS (Matchbook), dus op net_price na 2% commissie: 2,22 bruto -> "
     "2,1956 en 1,91 bruto -> 1,8918. Bij de bovenste regel is die commissie 0,50 pp edge, zestien "
     "keer de marge waarmee poort 9 is gehaald.")

note("betexplorer", "ok",
     "30 okt (run B): fixturepagina's van alle zeventien competities van de runlijst opgehaald, "
     "geen enkele HTTP-fout en geen enkele verhuisde slug. De bevestigingscontrole (poort "
     "'bevestiging door een tweede methode', §1) komt op 17 VAN DE 17 COMPETITIES EENS MET Fotmob, "
     "twaalf duels tegen twaalf - ook op de negen competities die vandaag niets op de kalender "
     "hebben, waar BetExplorer eveneens nul duels in het venster geeft en 1 tot 3 november als "
     "eerstvolgende datum noemt. HET MARKTGEMIDDELDE IS VANDAAG VOOR DRIE COMPETITIES DE ENIGE "
     "1X2-BRON (Croatian HNL, Romanian SuperLiga, Keuken Kampioen Divisie), met 5, 16 en 10 rijen "
     "op de pagina. EEN KOPPELING FAALDE EN IS GEREPAREERD: 'Roda - Jong AZ' koppelde niet aan "
     "'Roda JC Kerkrade - Jong AZ Alkmaar' (paarscore 0,518 onder de vloer van 0,62), waardoor dat "
     "duel met nul prijzen de analyse binnenkwam. De rij zelf was in orde - 1,72/4,01/3,91 over 15 "
     "boeken - dus dit is geen bronprobleem maar een koppelingsprobleem aan onze kant. Na de "
     "reparatie koppelen alle vier de KKD-duels. Zie bevinding 1.")

note("understat", "niet_bevraagd",
     "30 okt (run B): NIET bevraagd en dat is geen storing. Understat dekt vijf competities (PL, "
     "La Liga, Bundesliga, Serie A ITA, Ligue 1) en geen van die vijf staat op de Run B-runlijst, "
     "dus er was vandaag niets te halen. De redundantie die §4 beschrijft geldt voor Run A; voor "
     "Run B is Fotmob de enige xG-bron, en dat is precies waarom §3 voorschrijft dat een omgevallen "
     "Fotmob vooraan in de notificatie hoort. Vandaag leverde Fotmob zonder fout.")

note("api_football", "missing_key",
     "30 okt (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT VAN DE GEBRUIKER van 27 sep "
     "2026 en geen storing: hij wil hier geen geld aan uitgeven, en de kanskant komt van Fotmob en "
     "Understat (§3). Niet als gat melden, niet als actiepunt en niet in de notificatie. De "
     "uitzondering blijft staan: zodra Fotmob niet meer levert is er voor vrijwel elke competitie "
     "van deze runlijst geen onafhankelijke kansbron meer, wordt elk duel data_tier = NONE en "
     "levert elke run gegarandeerd nul bets - en pas dan is een betaald plan een reele vraag.")

note("settling", "ok",
     "30 okt (run B): niets af te wikkelen en dat is de juiste uitkomst, geen overgeslagen stap. "
     "ledger.py open geeft vier openstaande picks en alle vier zijn van Run A van vandaag met een "
     "aftrap die nog moet komen; shadow.py open geeft vijf openstaande schaduwpicks, vier van Run A "
     "van vandaag en een van deze run. Run A heeft vanmorgen zes picks afgewikkeld, waarvan drie "
     "van Run B van 28 oktober - alle drie GEWONNEN (Toronto FC - DC United 2-1, Santos - Palmeiras "
     "0-0, New York City - Atlanta United 2-1). calibration.py settle en ctxlog.py settle zijn "
     "beide gedraaid en gaven elk nul afwikkelingen, omdat de twaalf duels van deze run vanavond "
     "pas worden gespeeld. recalibrate.load_fit().fitted_through staat op 2026-10-28; dat is de "
     "VORIGE RUNDAG en niet de vorige kalenderdag, want op 29 oktober heeft geen enkele run "
     "gedraaid - de controle van §6b-5c is daarmee gehaald.")

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt")
