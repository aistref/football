"""Run A, 2 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten.

De bestaande detailtekst blijft staan en de meting van vandaag komt ervóór met een [Run A]-prefix,
zoals de vorige runs dat ook doen: §3 eist 'wat je deze run gemeten hebt', niet 'alleen wat je
vandaag gemeten hebt'.
"""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 2)
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
    e["detail"] = f"[Run A] {DAY.strftime('%-d okt %Y')}: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "16 daglijsten opgehaald (2 t/m 15 okt, waaronder de twee van het inzetvenster), alle "
        "HTTP 200. 55 competities op 2 okt, 107 op 3 okt. Levert normaal; dit is de enige xG-bron "
        "voor vrijwel elke competitie (§3), dus zolang hij staat is er niets te melden. "
        "WEL GEMETEN EN HET VERMELDEN WAARD: de FA Cup-kwalificatieronde van 3 oktober (39 duels "
        "volgens BetExplorer) staat in GEEN van de 16 daglijsten. Fotmob zet de kwalificatierondes "
        "van de FA Cup dus niet in zijn daglijsten; voor die competitie is de daglijst alleen geen "
        "volledige bron.")

prepend("betexplorer", "ok",
        "21 fixturepagina's opgehaald als tweede bron voor de lege runlijst. 19 gaven rijen "
        "(PL 20, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Championship 12, Eredivisie "
        "18, Primeira Liga 9, Pro League 9, Süper Lig 9, Premiership 12, Superliga 6, Ekstraklasa "
        "10, UCL/UEL/UECL elk 18, League Cup 8, FA Cup 39, DFB Pokal 16); Coppa Italia en KNVB "
        "Beker gaven HTTP 200 met een lege tabel. Nul duels op vandaag. Twee veranderingen t.o.v. "
        "1 oktober: Ekstraklasa geeft nu 10 rijen waar de pagina toen leeg was, en de FA Cup "
        "springt van 8 naar 39 rijen doordat de kwalificatieronde van 3 oktober erin staat — rijen "
        "die Fotmob niet heeft.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 45 actieve voetbalcompetities, quota 19.979 van de 20.000 over "
        "(21 gebruikt deze maand, alle 21 door Run C op 1 oktober). Sleutel niet afgewezen. Deze "
        "run is er niets uitgegeven: geen wedstrijd in de runlijst.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Niet gebruikt deze run: nul competities om prijzen "
        "voor te kopen.")

prepend("understat", "ok",
        "niet aangeroepen — nul actieve competities, dus geen competitiecontext op te halen. Geen "
        "uitspraak over de status.")

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
    "Run A 2 okt 2026: nul wedstrijden in de runlijst (FIFA-interlandvenster), dus nul bets. Met "
    "vier methodes bevestigd dat dat de werkelijkheid is en geen naam- of bronfout. Eén echte "
    "bronbevinding: de FA Cup-kwalificatieronde van 3 oktober staat bij BetExplorer (39 duels) en "
    "in geen enkele Fotmob-daglijst tot en met 15 oktober."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
