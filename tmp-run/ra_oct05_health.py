"""Run A, 5 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 5)
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
    e["detail"] = f"[Run A] 5 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (5 en 6 okt, de twee van het inzetvenster), beide HTTP 200: "
        "30 competities op 5 okt en 58 op 6 okt. Levert dus normaal. Geen van de 21 "
        "runlijstcompetities staat erop, gemeten met fotmob.find_league inclusief aliassen — "
        "wat erop staat (Nations League, Friendlies, EURO U21-kwalificatie, tweede en derde "
        "niveaus, Zuid-Amerika) is consistent met een interlandperiode. Geen league-stats "
        "aanroepen: niets om door te rekenen. De bevinding van 2 okt staat nog: de FA Cup "
        "staat in geen van beide daglijsten, terwijl BetExplorer er 5 duels voor 6 okt voor "
        "geeft.")

prepend("betexplorer", "ok",
        "21 fixturepagina's opgehaald als tweede fixturebron. 19 gaven rijen (PL 20, Serie A 20, "
        "La Liga 20, Bundesliga 18, Ligue 1 18, Championship 12, Eredivisie 18, Primeira Liga 8, "
        "Pro League 9, Süper Lig 9, Premiership 12, Superliga 6, Ekstraklasa 10, UCL/UEL/UECL elk "
        "18, FA Cup 5, League Cup 8, DFB Pokal 16); Coppa Italia en KNVB Beker gaven HTTP 200 met "
        "een lege tabel. NUL duels in het inzetvenster van vandaag — de eerste staan op 9 okt. "
        "Verandering t.o.v. 4 okt: de FA Cup gaf toen 0 rijen en nu 5, alle vijf op 6 okt 19:45 "
        "(Atherton–Trafford, Halesowen–Stafford, Scarborough–Macclesfield, Spalding United–Bury "
        "Town, Wingate & Finchley–Bedford). Die vallen buiten het venster van vandaag en zijn dus "
        "werk voor de run van 6 oktober.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 48 actieve voetbalcompetities, quota 19.901 van de 20.000 over "
        "(99 gebruikt deze maand). Sleutel niet afgewezen. Deze run is er niets uitgegeven: geen "
        "wedstrijd in de runlijst om prijzen voor te kopen.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Niet gebruikt deze run: nul competities om prijzen "
        "voor te kopen.")

prepend("understat", "ok",
        "niet aangeroepen — nul actieve runlijstcompetities, dus geen competitiecontext op te "
        "halen. Geen eigen uitspraak over de status deze run.")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert, dus "
        "de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 0,
    "matches_in_window": 0,
    "credits": 0,
}
sh["last_run_bevinding"] = (
    "Run A 5 okt 2026: nul wedstrijden in de runlijst (FIFA-interlandvenster), dus nul bets. Met "
    "twee onafhankelijke fixturebronnen bevestigd dat dat de kalender is en geen storing — "
    "BetExplorer geeft bovendien de datums waarop het weer begint (9 en 10 okt voor de "
    "competities, 13 en 15 okt voor de UEFA-toernooien). Vooruitblik voor de run van 6 oktober: "
    "vijf FA Cup-kwalificatieduels op 6 okt 19:45 staan uitsluitend bij BetExplorer en in geen "
    "Fotmob-daglijst; zonder de tweede fixturebron verdwijnen die stil langs de competitiepoort."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
