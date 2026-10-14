"""Run A, 14 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 14)
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
    e["detail"] = f"[Run A] 14 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (14 en 15 okt), beide HTTP 200, met 49 en 28 competities en 143 "
        "en 93 duels. TWEE runlijstcompetities hadden duels in het inzetvenster, samen 13: "
        "Championship 4 en UEFA Champions League 9. Ook de kansbron: fetch_league_stats voor 2 "
        "competities x 2 seizoenen, alle 4 met xG, plus de standen van de Premier League en "
        "League One voor de twee omrekeningen in Lincoln City - West Ham United (Lincoln omhoog, "
        "West Ham omlaag) en de binnenlandse standen van negen landen voor de "
        "kruis-grensomrekening van de Champions League. matchDetails voor alle 13 duels zonder "
        "een fout. squad_value kwam voor GEEN enkel duel op 0 terug, dus alle 13 duels belanden "
        "in het contextlogboek en geen enkel duel mist het opstellingsblok (9 voorspeld, 4 "
        "laatste basiself). context.check_venue zette EEN keer relocated: Shakhtar Donetsk - AEK "
        "Athens speelt niet in Donetsk maar in het uitwijkstadion dat Fotmob noteert.")

prepend("betexplorer", "ok",
        "16 fixturepagina's opgehaald plus 5 voor de bekers, alle 21 HTTP 200. Drie rollen deze "
        "run. (1) BEVESTIGING van de runlijst, per competitie en niet alleen op het totaal: "
        "dezelfde twee spelende competities als Fotmob met exact hetzelfde aantal duels (4 en 9 = "
        "13), en nul in het venster bij de veertien overige - 16 van 16 eens. Dat is vandaag niet "
        "vrijblijvend: de Championship-lijst bevat LINCOLN CITY - WEST HAM UNITED, voor deze "
        "competitie een ongebruikelijk paar, en BetExplorer noteert datzelfde duel op de "
        "Championship-fixturepagina. Twee losse bronnen die hetzelfde zeggen is hier het antwoord "
        "op 'staat dit wel in de goede competitie'. (2) Het gratis 1X2-MARKTGEMIDDELDE voor het "
        "kalibratieblok van 6e en voor poort 8 (17 en 9 rijen). (3) De aftraptijden als tweede "
        "bron: 'Today 17:45' en 'Today 20:00' in UK-tijd komen uit op 18:45 en 21:00 NL, precies "
        "wat Fotmob in UTC geeft. Voor GEEN enkele competitie was BetExplorer de enige 1X2-bron: "
        "beide spelende competities hebben een sportkey. Voor de vijf bekers: FA Cup 32 teamparen "
        "/ 0 koersen (ronde 17 okt), League Cup 8 / 24 (27 okt), Coppa Italia 8 / 0 (1 dec), KNVB "
        "Beker 26 / 0 (27 okt), DFB Pokal 16 / 48 (27 okt) - geen van de vijf heeft een ronde in "
        "het inzetvenster.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 46 actieve voetbalcompetities, quota 19.487 van de 20.000 over (513 "
        "gebruikt deze maand). Sleutel niet afgewezen. Deze run is er 18 credits uitgegeven: 2 "
        "bulk-aanroepen a 3 (h2h + spreads + totals, een per spelende competitie - beide hebben "
        "een sportkey) en 12 event-aanroepen voor BTTS op de duels met een kandidaat-edge op de "
        "vereniging van beide schalen. Plafond van de run was suggest_cap(19487, 18) = 540, "
        "split_budget(540, 2) -> (2, 2). De marktbalans-controle van 1a slaagt twee op twee: "
        "beide competities hebben zowel een uitkomst- als een doelpuntenmarkt. De beste prijs lag "
        "gemiddeld 5,29% boven het BetExplorer-marktgemiddelde (3,11% tot 9,27% over 12 duels). "
        "Pinnacle leverde een de-vigde 1X2 voor alle 12 duels met een eigen 1X2 (18 events), "
        "gemiddelde marge 3,76%; het eigen xG-1X2 staat daar gemiddeld 5,43 pp van af.")

prepend("oddsapi", "ok",
        "net_price toegepast op elke koers; bij de tweede gepubliceerde regel bindt dat zichtbaar "
        "(Matchbook 1.83 bruto -> 1.8134 na 2% beurscommissie) en bij de selectie die op de "
        "LIGHT-cap afviel ook (Matchbook 1.97 -> 1.9506). Beurzen stonden bij 1X2 in ALLE 12 "
        "duels met een eigen 1X2 op minstens een van de drie beste prijzen - vrijwel altijd "
        "Betfair of Matchbook. Dat is geen randgeval maar de regel, en het is precies waarom 1a "
        "elke koers door net_price haalt voordat er edge op wordt gemeten.")

prepend("understat", "n/a",
        "dekt vijf competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) en geen daarvan speelt "
        "vandaag. Niet aangeroepen, geen storing.")

prepend("api_football", "missing_key",
        "API_FOOTBALL_KEY niet gezet. BESLUIT van de gebruiker van 27 sep 2026 en geen storing of "
        "actiepunt (3): hij wil hier geen geld aan uitgeven en de kanskant komt van Fotmob en "
        "Understat. Fotmob leverde deze run zonder fout, dus 2 is gedekt.")

prepend("interleague", "ok",
        "NIET EEN BRON MAAR EEN GEMETEN TABEL, hier genoteerd omdat hij deze run tweederde van de "
        "runlijst draagt. 27 competities hebben een factor, gefit op 2111 kruis-grensduels uit "
        "UCL/UEL/UECL over 2021/2022 t/m 2025/2026. Alle negen Champions League-duels zijn "
        "hierlangs gegaan: 8 keer gelukt (tier LIGHT, nooit FULL) en 1 keer geweigerd omdat er "
        "voor SVK geen gemeten factor bestaat - Slovan Bratislava - VfB Stuttgart komt daarmee "
        "correct op NONE uit. Anders dan op 13 oktober viel er GEEN duel af op in_range: de acht "
        "omgerekende duels liggen alle acht binnen het gemeten bereik. Hermeten na afloop van het "
        "Europese seizoen 2026/2027 staat nog open.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 3,
    "matches_in_window": 13,
    "credits": 18,
}
sh["last_run_bevinding"] = (
    "Run A 14 okt 2026: 13 wedstrijden in het inzetvenster over TWEE competities (Championship 4, "
    "UEFA Champions League 9) en drie gepubliceerde regels, waarvan er vandaag TWEE wel hun lat "
    "halen - anders dan op 13 oktober, toen alle drie er op rangorde stonden. Vier dingen die "
    "deze dag kenmerken. (1) DE BINDENDE GRENS WAS NIET DE LIJSTLENGTE MAAR MAX_LIGHT_IN_SHORTLIST. "
    "Vier selecties haalden alle acht poorten; drie ervan stonden op LIGHT. De twee LIGHT-plekken "
    "gingen naar Bodo/Glimt - Borussia Dortmund (Under 3.5 @2.00, +26,13 pp, score 9,946) en Roma "
    "- Real Madrid (Under 3.5 @1,8134, +17,61 pp, score 6,407), en de derde plek naar de hoogste "
    "FULL-regel: Norwich City - Southampton (Double Chance Southampton of gelijk @1.60, +6,97 pp, "
    "score 4,842) - die haalt zijn lat van 8,0 op GEEN van beide schalen. Daardoor viel MANCHESTER "
    "CITY - PARIS SAINT-GERMAIN (AH -0.25 @1,9506, +17,13 pp, score 5,857) buiten de lijst, "
    "geboekt als failed_gate = 'lijstlengte' zoals 5b eist. De cap ruilt hier een grotere "
    "geclaimde edge op zwakke data in voor een kleinere op sterke data, en dat is precies "
    "waarvoor hij bestaat. (2) TWEE VAN DE DRIE REGELS ZIJN OPNIEUW EEN UNDER, voor de tweede dag "
    "op rij, en beide op UNDER 3.5 - precies de lijn waar margins.py goalbias meet dat het "
    "scoregrid P(Under 3.5) 2,0 pp te hoog zet (voorspeld 63,7%, werkelijk 61,7% over 1186 "
    "duels). Poort 9 kon geen van beide zien, maar de reden is vandaag anders dan gisteren en "
    "geen nieuw gat: beide staan op LIGHT, en per besluit van de gebruiker van 12 oktober geldt "
    "poort 9 uitsluitend op FULL (unders.TIERS). Van de 58 doorgerekende Over/Under-selecties "
    "stond geen enkele FULL-Under in de band 8-10 pp waar de poort bindt, dus de reeks "
    "doelpunten_onder staat nog op nul rijen. De vormfout zelf - keuze (a) van 11 oktober - staat "
    "nog open en raakt deze twee regels rechtstreeks. (3) POORT 8 HIELD DE OP EEN NA STERKSTE "
    "SELECTIE VAN DE RUWE RANGLIJST TEGEN: Roma of gelijk (Double Chance, AH +0.5 @1.96 bruto / "
    "1,9408 netto) op +20,87 pp herijkt met score 7,555, op een kant waar Pinnacle Roma 26,7% "
    "geeft tegen 49,1% voor Real Madrid. Dat duel kwam daarna alsnog in de lijst met een "
    "Over/Under, dus de poort hield een KANT tegen en geen wedstrijd. Vier selecties over twee "
    "wedstrijden tegengehouden, geboekt als twee rijen underdog (een rij per wedstrijd, 1e); "
    "poort8_ruw is leeg, dus underdog_ruw groeit vandaag niet. (4) DE VROEG-SEIZOENSCORRECTIE "
    "SCHIET VOOR DE VIERDE DAG OP RIJ DOOR: factor 1,0510 en de controlemeting op P(Over 2.5) "
    "gaat van +0,15 pp ZONDER naar +3,36 pp MET over drie duels met een 2.5-lijn aan beide kanten "
    "(11 okt -2,06 -> +3,03; 12 okt +3,83 -> +8,02; 13 okt -0,63 -> +2,11). Dat is een diagnose "
    "tegen de markt en nooit een fitopdracht (2, 6e), maar vier dagen dezelfde richting is wel de "
    "aanleiding om het op UITKOMSTEN te gaan meten. EN HIER IS IETS NIEUWS GEVONDEN: de negen "
    "Champions League-duels leveren wel een waarneming AAN de gepoolde factor maar krijgen die "
    "correctie zelf niet, want kruis-grensduels lopen langs interleague.reference_league() en "
    "niet langs league_level. De correctie raakte vandaag dus feitelijk alleen de vier "
    "Championship-duels terwijl de UCL het getal mede bepaalde. Dat staat als openstaand punt. "
    "Verder: poort 5 vangt voor de ACHTSTE dag op rij het overgrote deel weg (135 van 200 = "
    "67,5%), poort 7 bond bij drie duels (alle drie op blessures; Derby County mist 48% van de "
    "selectiewaarde, Liverpool 42%), de cap bond niet (13 van 40), en progress.py verify staat "
    "groen op alle 12 geanalyseerde duels met alle zes markten. Stage 0 wikkelde 3 picks en 8 "
    "schaduwpicks van 13 oktober af: 2 van de 3 picks gewonnen (+0,69u), en de twee winnaars "
    "waren allebei verkeerd ingeschat - Inter - Club Brugge won met Over 3.5 op een 3-4 terwijl "
    "het model 4,20 doelpunten verwachtte maar met Inter 3,29 tegen Club Brugge 0,91, en Bristol "
    "City - Blackburn Rovers won met Under 2.5 op 0-1 waar 2,47 was voorspeld."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
