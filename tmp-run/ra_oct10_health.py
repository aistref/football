"""Run A, 10 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

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
    e["detail"] = f"[Run A] 10 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (10 en 11 okt), beide HTTP 200. TWAALF runlijstcompetities "
        "hadden duels in het inzetvenster, samen 56 — de grootste rundag tot nu toe. Ook de "
        "kansbron: fetch_league_stats voor 12 competities x 2 seizoenen, alle 24 met xG, plus "
        "matchDetails voor alle 56 duels (context, opstelling, uitvallers, vorm, rust, stadion) "
        "zonder één fout, en de standen van de divisies eronder voor zeventien omrekeningen. "
        "LET OP de bekende beperking, vandaag bij VIJF van de twaalf competities: squad_value "
        "komt op 0 terug voor Championship (10 duels), Belgian Pro League (4), Super Lig (4), "
        "Scottish Premiership (4) en Ekstraklasa (3). Bij die 25 duels is de blessurekant van "
        "poort 7 niet meetbaar en vallen ze buiten het contextlogboek: dat groeide met 31 in "
        "plaats van 56. De uitvallers zijn er wél bij naam bekend; wat ontbreekt is hun gewicht.")

prepend("betexplorer", "ok",
        "12 fixturepagina's opgehaald plus 5 voor de bekers, alle 17 HTTP 200. Drie rollen deze "
        "run. (1) BEVESTIGING van de runlijst: dezelfde twaalf spelende competities als Fotmob, "
        "7 tot 24 rijen per competitie, en nul in het venster bij Danish Superliga, UCL, UEL en "
        "UECL. (2) Het gratis 1X2-MARKTGEMIDDELDE voor 50 van de 56 duels, nodig voor het "
        "kalibratieblok van §6e en voor poort 8. (3) De ENIGE 1X2-bron voor de Scottish "
        "Premiership, die geen sportkey bij The Odds API heeft — vier duels op een "
        "marktgemiddelde over 5 boeken in plaats van op een beste prijs. Voor de vijf bekers: FA "
        "Cup 32 teamparen / 0 koersen (ronde 17 okt), League Cup 8 / 24 (27-29 okt), Coppa "
        "Italia 8 / 0 (vanaf 1 dec), KNVB Beker 26 / 0 (27-28 okt), DFB Pokal 16 / 48 "
        "(27-28 okt) — geen van de vijf heeft een ronde in het inzetvenster.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 48 actieve voetbalcompetities, quota 19.803 van de 20.000 over (197 "
        "gebruikt deze maand). Sleutel niet afgewezen. Deze run is er 68 credits uitgegeven: 11 "
        "bulk-aanroepen à 3 (h2h + spreads + totals, één per spelende competitie MET sportkey) "
        "en 35 event-aanroepen à 1 voor BTTS op de duels met een kandidaat-edge. Elf van de "
        "twaalf spelende competities hebben een sportkey; de Scottish Premiership niet.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Gebruikt voor alle 68 credits van deze run; "
        "net_price toegepast op elke beurskoers. Matchbook stond vandaag op DRIE van de vijf "
        "gepubliceerde regels als beste prijs (Inter – Parma, RAAL La Louvière – Club Brugge, "
        "Cracovia – Zagłębie Lubin), alle drie met 2% commissie verwerkt.")

prepend("understat", "ok",
        "aangeroepen als tweede, onafhankelijk xG-model. Alle VIJF Understat-competities "
        "speelden vandaag (Premier League, Serie A, La Liga, Bundesliga, Ligue 1) en 17 duels "
        "kregen een eigen kansverdeling voor het kalibratieblok — het hoogste aantal tot nu toe. "
        "Waar het paar onvolledig bleef is dat een promovendus die niet in de Understat-tabel "
        "van 2025 staat (Ipswich Town, Frosinone, Paderborn, Elversberg, Le Mans).")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert "
        "normaal, dus de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 5,
    "matches_in_window": 56,
    "credits": 68,
}
sh["last_run_bevinding"] = (
    "Run A 10 okt 2026: 56 wedstrijden in het inzetvenster over twaalf competities — vier keer "
    "zoveel als gisteren en de grootste rundag tot nu toe — en vijf gepubliceerde regels. Drie "
    "dingen die deze dag kenmerken. (1) DE CAP BINDT VOOR HET EERST sinds hij op 5 september "
    "naar 40/55 ging: 56 duels op een zaterdagcap van 55, dus Genk – Kortrijk is afgekapt. De "
    "wedstrijd die net wél meedeed (Śląsk Wrocław – Lech Poznań) heeft exact dezelfde "
    "datarijkdom 4,5 en dezelfde vijf markten, dus het verschil zat in de vierde sorteersleutel: "
    "de aftrap. Dat is precies wat §0 bedoelt met 'afkappen kost naar rato'. (2) POORT 5 VANGT "
    "VOOR DE VIERDE DAG OP RIJ het overgrote deel weg: 553 van de 754 selecties (73%), nu over "
    "twaalf competities en 56 duels in plaats van over één of twee. Het patroon is elke keer "
    "hetzelfde en het is in de lambdas te zien: de splitsmethode zet een ander DOELPUNTENNIVEAU "
    "neer dan de xG-methode, niet een andere winnaar — bij de drie regels onder de lat staat de "
    "splitsarm op +20,5 tot +20,7 pp tegen +3,2 tot +4,7 pp op de xG-arm. Opschrijven en volgen, "
    "niet op één dag aan sleutelen (§6d). (3) ZEVENTIEN OMREKENINGEN van promovendi en "
    "degradanten, tegen vier gisteren, dus de §4-blend die gisteren is gerepareerd was vandaag de "
    "hoofdroute; zestien kwamen erdoor op LIGHT en één (Alanyaspor – Erzurumspor FK) viel op "
    "conversion_in_range op NONE. Geen van de zeventien heeft de lijst gehaald. De vijf regels: "
    "Inter – Parma Under 3.5 +8,74 pp en Cracovia – Zagłębie Lubin Under 2.5 +8,68 pp halen óók "
    "de lat van 8,0; RAAL La Louvière – Club Brugge Under 3.5 +7,74 pp, Lille – Le Havre Under 3 "
    "+7,81 pp en Rayo Vallecano – Athletic Club Draw No Bet +6,63 pp staan er op rangorde (§5b). "
    "Vier van de vijf zijn een Under, en dat is eenzijdig — maar het is geen inkoopeffect: "
    "Over/Under en Asian Handicap waren met 232 en 214 selecties de twee breedste markten van de "
    "dag. Verder: poort 8 had met 41 tegengehouden selecties over 16 wedstrijden zijn drukste "
    "dag ooit, poort 7 hield 15 selecties tegen over drie duels (Ajax – NEC, Union Berlin – "
    "Elversberg, Brest – Angers) en de vroeg-seizoenscorrectie van 1,0972 komt tegen de markt op "
    "P(Over 2.5) uit op gemiddeld 0,0 pp over 50 duels — de vlakste controlemeting sinds die "
    "controle bestaat. Stage 0 wikkelde 8 picks en 10 schaduwpicks van 9 oktober af: 3 van de 8 "
    "picks gewonnen (Braunschweig Under 3, Volendam, Lens)."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
