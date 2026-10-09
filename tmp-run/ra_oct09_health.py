"""Run A, 9 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
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
    e["detail"] = f"[Run A] 9 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (9 en 10 okt), beide HTTP 200: 97 competities / 204 wedstrijden "
        "op 9 okt en 178 / 672 op 10 okt. Tien runlijstcompetities hadden duels in het "
        "inzetvenster, samen 12. Ook de kansbron: fetch_league_stats voor 10 competities x 2 "
        "seizoenen, alle twintig met xG, plus matchDetails voor alle 12 duels (context, "
        "opstelling, uitvallers, vorm, rust, stadion) zonder één fout. idcheck.py gaf voor alle "
        "33 fotmob_id's uit coverage.json een bruikbare stand. LET OP de bekende beperking, "
        "vandaag bij 4 van de 10 competities: squad_value komt op 0 terug voor Championship, "
        "Belgian Pro League, Super Lig en Ekstraklasa, waardoor de blessurekant van poort 7 daar "
        "niet meetbaar is en 5 van de 12 duels buiten het contextlogboek vallen.")

prepend("betexplorer", "ok",
        "26 fixturepagina's opgehaald, allemaal HTTP 200: 16 competitiepagina's als tweede "
        "fixturebron plus 10 voor de bekers en de afgekeurde slugs. Twee rollen deze run. (1) "
        "BEVESTIGING van de runlijst: dezelfde 12 duels als Fotmob, en nul in het venster bij "
        "Premier League, Serie A, Scottish Premiership, UCL, UEL en UECL — de twee bronnen zijn "
        "volledig eens. (2) Het gratis 1X2-MARKTGEMIDDELDE voor alle 12 duels (3 tot 17 boeken "
        "per duel), nodig voor het kalibratieblok van §6e en voor poort 8. Dat laatste was bij "
        "West Ham – QPR eerst leeg door een naamkoppelingsfout aan onze kant (niet aan die van "
        "de bron) — zie het runrapport, Bevinding 1. Voor de vijf bekers: FA Cup 32 teamparen / "
        "0 koersen, League Cup 8 / 24, Coppa Italia 8 / 0, KNVB Beker 26 / 0, DFB Pokal 16 / 48, "
        "en geen van de vijf heeft een ronde in het inzetvenster.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 48 actieve voetbalcompetities, quota 19.857 van de 20.000 over (143 "
        "gebruikt deze maand). Sleutel niet afgewezen. Deze run is er 39 credits uitgegeven: 10 "
        "bulk-aanroepen à 3 (h2h + spreads + totals, één per spelende competitie) en 9 "
        "event-aanroepen à 1 voor BTTS op de duels met een kandidaat-edge. Alle 10 spelende "
        "competities hebben een sportkey; alle 12 duels stonden in de respons.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Gebruikt voor alle 39 credits van deze run; "
        "net_price toegepast op elke beurskoers (Betfair en Matchbook stonden vandaag beide als "
        "beste prijs op een gepubliceerde regel).")

prepend("understat", "ok",
        "aangeroepen als tweede, onafhankelijk xG-model voor de drie competities die Understat "
        "dekt en die vandaag speelden: Bundesliga en Ligue 1 koppelden beide ploegen en leverden "
        "een eigen kansverdeling voor het kalibratieblok (Dortmund – Werder, Lens – Lyon). La "
        "Liga speelde ook, maar Málaga is promovendus en staat niet in de Understat-tabel van "
        "2025, dus daar bleef het paar onvolledig. Serie A en Premier League speelden niet.")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert "
        "normaal, dus de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 4,
    "matches_in_window": 12,
    "credits": 39,
}
sh["last_run_bevinding"] = (
    "Run A 9 okt 2026: 12 wedstrijden in het inzetvenster over tien competities, vier "
    "gepubliceerde regels, en de belangrijkste uitkomst van de dag is een REPARATIE die een bet "
    "heeft gekost. §4 eist dat het lopende seizoen ALTIJD via blend_seasons meeweegt; dat "
    "gebeurde niet voor ploegen die uit promotion.convert komen, en juist bij die groep zegt §4 "
    "zelf dat het hardst telt. Gemeten gevolg: SK Beveren – Lommel stond met +20,04 pp als "
    "grootste edge van de dag in de lijst, en met de blend erin zakt P(thuiszege) van 0,745 naar "
    "0,576, valt de edge terug naar +6,56 pp en sneuvelt de selectie óók op poort 6. Beveren "
    "kwam uit First Division B met een relatieve verdediging van 0,509 (vlak boven de ondergrens "
    "van het gemeten bereik) maar staat dit seizoen op 1,06 xG / 2,01 xGA per duel — ruim onder "
    "het competitiegemiddelde van 1,57. De bet is daarom NIET gepubliceerd. Wat er blijft staan: "
    "Nordsjælland – OB Over 3.25 +12,60 pp, Dortmund – Werder Under 3.5 +12,13 pp en Lens – Lyon "
    "thuiszege +10,57 pp, alle drie FULL en alle drie boven de lat van 8,0, plus Málaga – "
    "Espanyol Over 2.5 op rangorde onder de LIGHT-lat (+8,48 pp). Tweede reparatie: "
    "ra_names.resolve las de aliastabel maar één kant op, waardoor West Ham – QPR geen "
    "1X2-marktgemiddelde kreeg en poort 8 daar ongetoetst openstond; na de fix hebben alle twaalf "
    "duels een marktgemiddelde en een kalibratieblok. Verder: niets afgekapt (12 op een cap van "
    "55), geen competitie buiten datadekking, 39 van 20.000 credits uitgegeven, poort 8 hield "
    "voor het eerst sinds 24 september weer tegen (2 wedstrijden, 6 selecties) en poort 5 vangt "
    "voor de derde dag op rij het overgrote deel weg (130 van 174). Stage 0 wikkelde de twee "
    "openstaande picks van 8 oktober af: Palmeiras – Bahia Under 3 gewonnen (1-0), Santos – "
    "Flamengo Under 2.5 verloren (2-2)."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
