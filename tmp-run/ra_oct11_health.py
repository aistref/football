"""Run A, 11 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 11)
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
    e["detail"] = f"[Run A] 11 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (11 en 12 okt), beide HTTP 200. DERTIEN runlijstcompetities "
        "hadden duels in het inzetvenster, samen 41. Ook de kansbron: fetch_league_stats voor 13 "
        "competities x 2 seizoenen, alle 26 met xG, plus matchDetails voor alle 41 duels "
        "(context, opstelling, uitvallers, vorm, rust, stadion) zonder één fout, en de standen "
        "van de divisies eronder voor veertien omrekeningen. LET OP de bekende beperking, vandaag "
        "bij VIJF van de dertien competities: squad_value komt op 0 terug voor Belgian Pro League "
        "(4 van 4 duels), Super Lig (3 van 3), Ekstraklasa (3 van 3), Scottish Premiership "
        "(2 van 2) en Championship (1 van 1). Bij die 13 duels is de blessurekant van poort 7 "
        "niet meetbaar en vallen ze buiten het contextlogboek: dat groeide met 27 in plaats van "
        "41. De uitvallers zijn er wél bij naam bekend; wat ontbreekt is hun gewicht.")

prepend("betexplorer", "ok",
        "13 fixturepagina's opgehaald plus 5 voor de bekers, alle 18 HTTP 200. Drie rollen deze "
        "run. (1) BEVESTIGING van de runlijst, en vandaag per competitie en niet alleen op het "
        "totaal: dezelfde dertien spelende competities als Fotmob met EXACT hetzelfde aantal "
        "duels van vandaag per competitie (3/5/4/2/3/1/4/3/4/3/2/4/3 = 41), en nul in het "
        "venster bij UCL, UEL en UECL. (2) Het gratis 1X2-MARKTGEMIDDELDE, nodig voor het "
        "kalibratieblok van §6e en voor poort 8. (3) De ENIGE 1X2-bron voor de Scottish "
        "Premiership, die geen sportkey bij The Odds API heeft — twee duels op een "
        "marktgemiddelde in plaats van op een beste prijs. Voor de vijf bekers: FA Cup 32 "
        "teamparen / 0 koersen (ronde 17 okt), League Cup 8 / 24 (27 okt), Coppa Italia 8 / 0 "
        "(vanaf 1 dec), KNVB Beker 26 / 0 (27 okt), DFB Pokal 16 / 48 (27 okt) — geen van de vijf "
        "heeft een ronde in het inzetvenster.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 48 actieve voetbalcompetities, quota 19.666 van de 20.000 over (334 "
        "gebruikt deze maand). Sleutel niet afgewezen. Deze run is er 62 credits uitgegeven: 12 "
        "bulk-aanroepen à 3 (h2h + spreads + totals, één per spelende competitie MET sportkey) "
        "en 26 event-aanroepen à 1 voor BTTS op de duels met een kandidaat-edge. Twaalf van de "
        "dertien spelende competities hebben een sportkey; de Scottish Premiership niet. Na deze "
        "run staat het maandverbruik op 396 van 20.000.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Gebruikt voor alle 62 credits van deze run; "
        "net_price toegepast op elke beurskoers. Matchbook stond vandaag op DRIE van de vijf "
        "gepubliceerde regels als beste prijs (Beşiktaş – Kocaelispor 1,66 bruto / 1,6468 netto, "
        "Arouca – Estrela da Amadora 1,93 / 1,9114, FC Midtjylland – FC København 1,70 / 1,686), "
        "alle drie met 2% commissie verwerkt. De beste prijs lag over de 37 duels met beide "
        "bronnen gemiddeld 6,26% boven het BetExplorer-marktgemiddelde (3,82% tot 13,34%).")

prepend("understat", "ok",
        "aangeroepen als tweede, onafhankelijk xG-model. Alle VIJF Understat-competities speelden "
        "vandaag (Premier League 3, Serie A 5, La Liga 4, Bundesliga 2, Ligue 1 3 = 17 duels) en "
        "TIEN daarvan kregen een eigen kansverdeling voor het kalibratieblok. Waar het paar "
        "onvolledig bleef is dat een promovendus of degradant die niet in de Understat-tabel van "
        "2025 staat (Hull City, Monza, Deportivo A Coruña, Racing Santander, Schalke 04, Troyes).")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert "
        "normaal, dus de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 5,
    "matches_in_window": 41,
    "credits": 62,
}
sh["last_run_bevinding"] = (
    "Run A 11 okt 2026: 41 wedstrijden in het inzetvenster over dertien competities, en vijf "
    "gepubliceerde regels. Vier dingen die deze dag kenmerken. (1) DE DREMPEL EN DE RANGORDE "
    "GEVEN DEZELFDE LIJST: alle vijf regels staan boven hun eigen lat van 8,0 pp op de herijkte "
    "schaal, dus §5b hoeft niemand 'op rangorde' door te laten en de afkapping op lijstlengte "
    "bindt niet. (2) MAAR ÉÉN VAN DE VIJF HAALT DIE LAT ALLEEN HERIJKT: FC Midtjylland – FC "
    "København (Over 2.5 @1,686) staat op +8,30 pp herijkt en +7,99 pp ruw, dus bet_beide is "
    "FALSE. Dat is precies het geval waarvoor §5a die vlag heeft gebouwd nu de fit een kans "
    "VERHOOGT in plaats van verlaagt; publicatie wordt op de herijkte my_prob beslist en dat is "
    "hier gedaan, maar toplist.build schrijft er 'haalt ook de lat' bij zonder de ruwe schaal te "
    "noemen. Lecce – Bologna is hetzelfde geval en haalde de lijst niet; die staat als "
    "schaduwrij 'herijking_omgekeerd'. (3) POORT 5 VANGT VOOR DE VIJFDE DAG OP RIJ het overgrote "
    "deel weg: 417 van de 550 selecties (76%). Het patroon is elke keer hetzelfde en het is in de "
    "lambdas te zien: de splitsmethode zet een ander DOELPUNTENNIVEAU neer dan de xG-methode, "
    "niet een andere winnaar — bij FC Midtjylland – FC København geeft xG 1,59/1,63 en de splits "
    "3,25/1,70, oftewel +27,84 pp tegen +3,03 pp. Opschrijven en volgen, niet op één dag aan "
    "sleutelen (§6d). (4) DE VROEG-SEIZOENSCORRECTIE SCHIET VANDAAG DOOR. Factor 1,0815, en de "
    "controlemeting tegen de markt op P(Over 2.5) over 26 duels gaat van -2,06 pp ZONDER de "
    "correctie naar +3,03 pp MET, met een grotere absolute fout (4,44 -> 5,32 pp). Gisteren kwam "
    "diezelfde controle op 0,0 pp uit. Dat is een diagnose en geen fitopdracht (§3 Stage 5 "
    "verbiedt afregelen op de markt), maar het is het eerste signaal dat de factor over zijn doel "
    "heen gaat nu de lopende seizoenen rijper worden. Verder: poort 7 had zijn breedste dag (23 "
    "selecties over acht duels, alle acht op de blessurekant), poort 8 hield 12 selecties tegen "
    "over vier duels, de cap bond niet (41 van 55) en veertien van de 41 duels hadden een "
    "omgerekende ploeg, waarvan twee op NONE eindigden via conversion_in_range (Hull City – "
    "Everton, Silkeborg – AC Horsens). Stage 0 wikkelde 9 picks en 77 schaduwpicks van 10 oktober "
    "af: 4 van de 9 picks gewonnen, 4 verloren en 1 void (Rayo Vallecano – Athletic Club "
    "afgelast), samen -0,50u; van de vijf eigen Run A-regels van gisteren wonnen Inter – Parma en "
    "Lille – Le Havre, samen -0,19u."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
