"""Run A, 13 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 13)
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
    e["detail"] = f"[Run A] 13 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (13 en 14 okt), beide HTTP 200, met 54 en 48 competities en 186 "
        "en 137 duels. TWEE runlijstcompetities hadden duels in het inzetvenster, samen 17: "
        "Championship 8 en UEFA Champions League 9. Ook de kansbron: fetch_league_stats voor 2 "
        "competities x 2 seizoenen, alle 4 met xG, plus de standen van de Premier League en "
        "League One voor vier omrekeningen (Burnley en Wolverhampton omlaag, Cardiff City en "
        "Bolton omhoog) en de binnenlandse standen van negen landen voor de kruis-grensomrekening "
        "van de Champions League. matchDetails voor alle 17 duels zonder één fout. squad_value "
        "kwam deze run voor GEEN enkel duel op 0 terug — dat is ongebruikelijk gunstig en de "
        "reden dat alle 17 duels in het contextlogboek belanden en dat geen enkel duel het "
        "opstellingsblok mist (9 voorspeld, 8 laatste basiself). context.check_venue zette ÉÉN "
        "keer relocated: Sabah FK - Slavia Prague in het Baki Olimpiya Stadionu in plaats van de "
        "Bank Respublika Arena.")

prepend("betexplorer", "ok",
        "16 fixturepagina's opgehaald plus 5 voor de bekers, alle 21 HTTP 200. Drie rollen deze "
        "run. (1) BEVESTIGING van de runlijst, per competitie en niet alleen op het totaal: "
        "dezelfde twee spelende competities als Fotmob met exact hetzelfde aantal duels (8 en 9 = "
        "17), en nul in het venster bij de veertien overige. LET OP, HIER IS DEZE RUN EEN STILLE "
        "FOUT GEREPAREERD: het uitleesscript gebruikte `\\s+` na de dubbele punt in de META-tabel "
        "en de regel \"Scottish Premiership (SCO)\":(\"SCO\", ... heeft daar geen ruimte, dus die "
        "competitie werd door GEEN tweede bron bevestigd terwijl het totaal ('15 van 15') "
        "compleet leek. Met `\\s*` zijn het er zestien van zestien. (2) Het gratis "
        "1X2-MARKTGEMIDDELDE voor het kalibratieblok van §6e en voor poort 8 (24 en 18 rijen). "
        "(3) De aftraptijden als tweede bron: 'Today 17:45' en 'Today 20:00' in UK-tijd komen uit "
        "op 18:45 en 21:00 NL, precies wat Fotmob in UTC geeft. Anders dan op 11 okt was "
        "BetExplorer deze run voor GEEN enkele competitie de enige 1X2-bron: beide spelende "
        "competities hebben een sportkey. Voor de vijf bekers: FA Cup 32 teamparen / 0 koersen "
        "(ronde 17 okt), League Cup 8 / 24 (27 okt), Coppa Italia 8 / 0 (1 dec), KNVB Beker 26 / "
        "0 (27 okt), DFB Pokal 16 / 48 (27 okt) — geen van de vijf heeft een ronde in het "
        "inzetvenster.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 46 actieve voetbalcompetities, quota 19.503 van de 20.000 over (497 "
        "gebruikt deze maand). Sleutel niet afgewezen. Deze run is er 26 credits uitgegeven: 2 "
        "bulk-aanroepen à 3 (h2h + spreads + totals, één per spelende competitie — beide hebben "
        "een sportkey) en 10 event-aanroepen à 2 voor BTTS op de duels met een kandidaat-edge op "
        "de vereniging van beide schalen. Plafond van de run was suggest_cap(19503, 19) = 512, "
        "split_budget(512, 2) -> (2, 2). De marktbalans-controle van §1a slaagt twee op twee: "
        "beide competities hebben zowel een uitkomst- als een doelpuntenmarkt. De beste prijs lag "
        "gemiddeld 6,30% boven het BetExplorer-marktgemiddelde (3,03% tot 12,78% over 15 duels). "
        "Pinnacle leverde een de-vigde 1X2 voor alle 15 duels met een eigen 1X2 (30 events), "
        "gemiddelde marge 3,93%.")

prepend("oddsapi", "ok",
        "net_price toegepast op elke koers; bij de derde gepubliceerde regel bindt dat zichtbaar "
        "(Matchbook 1.95 bruto -> 1.931 na 2% beurscommissie). Beurzen stonden bij 1X2 in 2 van "
        "de 15 duels op de beste prijs (Matchbook bij Bristol City - Blackburn Rovers, Betfair "
        "bij Galatasaray - Barcelona).")

prepend("understat", "n/a",
        "dekt vijf competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) en geen daarvan speelt "
        "vandaag. Niet aangeroepen, geen storing.")

prepend("api_football", "missing_key",
        "API_FOOTBALL_KEY niet gezet. BESLUIT van de gebruiker van 27 sep 2026 en geen storing of "
        "actiepunt (§3): hij wil hier geen geld aan uitgeven en de kanskant komt van Fotmob en "
        "Understat. Beide leverden deze run zonder fout, dus §2 is gedekt.")

prepend("interleague", "ok",
        "NIET EEN BRON MAAR EEN GEMETEN TABEL, hier genoteerd omdat hij deze run de helft van de "
        "runlijst draagt. 27 competities hebben een factor, gefit op 2111 kruis-grensduels uit "
        "UCL/UEL/UECL over 2021/2022 t/m 2025/2026. Alle negen Champions League-duels zijn "
        "hierlangs gegaan: 7 keer gelukt (tier LIGHT, nooit FULL) en 2 keer geweigerd door "
        "in_range — Arsenal (verdediging 0.373 onder de ondergrens 0.388) en Bayern München "
        "(aanval 2.742 boven de bovengrens 2.432). Dat is de Coventry-val die correct dichtgaat, "
        "geen storing. Hermeten na afloop van het Europese seizoen 2026/2027 staat nog open.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 3,
    "matches_in_window": 17,
    "credits": 26,
}
sh["last_run_bevinding"] = (
    "Run A 13 okt 2026: 17 wedstrijden in het inzetvenster over TWEE competities (Championship 8, "
    "UEFA Champions League 9) en drie gepubliceerde regels. Vier dingen die deze dag kenmerken. "
    "(1) ALLE DRIE DE REGELS STAAN OP RANGORDE EN GEEN ENKELE HAALT ZIJN LAT, voor het eerst alle "
    "drie: nul van de 229 doorgerekende selecties kwam met alle poorten open boven zijn drempel "
    "uit. Inter - Club Brugge (Over 3.5 @2.15, LIGHT) komt met +14,75 pp het dichtst bij de "
    "LIGHT-lat van 16,0; Galatasaray - Barcelona (Under 4.5 @1.78, LIGHT) staat op +7,76 en "
    "Bristol City - Blackburn Rovers (Under 2.5 @1.931, FULL) op +3,84 tegen een lat van 8,0. "
    "(2) TWEE VAN DE DRIE ZIJN EEN UNDER EN POORT 9 KON GEEN VAN BEIDE ZIEN, en bij de tweede is "
    "de reden NIEUW en structureel: unders.check bindt met opzet alleen in de band 8-10 pp op "
    "FULL, maar sinds §5b de edge-drempel uit de poorten heeft gehaald kan een FULL-Under ONDER "
    "de 8,0 pp alsnog op rangorde gepubliceerd worden zonder dat de poort hem ooit evalueert. Dat "
    "gebeurt vandaag bij Bristol City (+3,84 pp), in de band die in de tabel van §1h op -34,1% "
    "staat over 26 gevallen. §5b's opsomming 'de zeven andere poorten' is bij het toevoegen van "
    "poort 9 op 11 okt niet meegegroeid; de code kiest de lezing 'drempelverhoging' en deze run "
    "volgt de code. Of de poort ook onder de 8,0 moet binden is als BESLUIT aan de gebruiker "
    "voorgelegd in het dagrapport — risicobereidheid, niet data (§1h punt 3, §1e). "
    "(3) POORT 8 HIELD DE ENIGE SELECTIE TEGEN DIE ZIJN LAT ECHT HAALDE: Galatasaray +1.5 @2.32 "
    "op +23,88 pp herijkt, de hoogste selection_score van de run (7,574), op een kant waar "
    "Pinnacle Galatasaray 11,4% geeft. Dat duel kwam daarna alsnog in de lijst met een "
    "Over/Under, dus de poort hield een KANT tegen en geen wedstrijd. De reeks `underdog` zakte "
    "wel van +11,0% naar -1,0% over 94 afgewikkelde gevallen, dus de uitweg die §1e beschrijft "
    "('positieve ROI over >=30 gevallen') is niet langer waar — en die draai steunt de poort, dus "
    "er is niets aan de gebruiker te vragen. (4) DE VROEG-SEIZOENSCORRECTIE SCHIET VOOR DE DERDE "
    "DAG OP RIJ DOOR: factor 1,0424 en de controlemeting op P(Over 2.5) gaat van -0,63 pp ZONDER "
    "naar +2,11 pp MET over vijf duels met een 2.5-lijn aan beide kanten (11 okt: -2,06 -> +3,03; "
    "12 okt: +3,83 -> +8,02). Dat is een diagnose tegen de markt en nooit een fitopdracht (§2, "
    "§6e), maar drie dagen dezelfde richting is wel de aanleiding om het op UITKOMSTEN te gaan "
    "meten; dat staat als openstaand punt. Verder: poort 5 vangt voor de ZEVENDE dag op rij het "
    "overgrote deel weg (160 van 229 = 69,9%), poort 7 bond bij drie van de acht "
    "Championship-duels (alle drie op blessures, Millwall mist 55% van de selectiewaarde), de cap "
    "bond niet (17 van 40), en twee kruis-grensduels eindigden correct op NONE via in_range. "
    "Stage 0 wikkelde 6 picks en 14 schaduwpicks van 12 oktober af: 3 van de 6 picks gewonnen, 3 "
    "verloren, samen +0,26u; van de drie EIGEN Run A-regels won alleen GKS Katowice, samen "
    "-0,88u. Alle drie de verliezers van de dag gingen aan dezelfde kant mis — er viel meer dan "
    "voorspeld — en de reeks 'Under gespeeld' in margins.py goalbias groeide van 56 naar 58 "
    "gevallen zonder dat de z zakte (+0,571 doelpunt per duel, z = +2,66)."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
