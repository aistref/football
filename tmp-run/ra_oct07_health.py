"""Run A, 7 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 7)
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
    e["detail"] = f"[Run A] 7 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (7 en 8 okt), beide HTTP 200: 28 competities op 7 okt en 20 op "
        "8 okt. Geen van de 21 runlijstcompetities staat erop. Wat er wél op staat is het "
        "interlandvenster en de kalenderjaarcompetities — Friendlies, CONCACAF Nations League, "
        "MLS, Brazilie Serie A/B, Japanse en Chileense beker — dus dit is een lege runlijst en "
        "geen storing: de bron levert normaal.")

prepend("betexplorer", "ok",
        "18 fixturepagina's opgehaald als tweede fixturebron, allemaal HTTP 200, plus 3 die een "
        "lege tabel gaven (FA Cup, Coppa Italia, KNVB Beker). Geen enkele competitie had een duel "
        "in het inzetvenster van vandaag. De eerstvolgende rijen beginnen op 9 okt (La Liga, "
        "Bundesliga, Ligue 1, Championship, Eredivisie, Primeira Liga, Pro League, Super Lig, "
        "Superliga, Ekstraklasa), 10 okt (Premier League, Serie A, Premiership) en 13/15 okt "
        "(UCL, UEL, UECL). Daarmee bevestigt de tweede bron de nul van Fotmob in plaats van hem "
        "tegen te spreken — het omgekeerde van 6 oktober, toen zij de enige was die de FA Cup zag.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 48 actieve voetbalcompetities, quota 19.868 van de 20.000 over "
        "(132 gebruikt deze maand). Sleutel niet afgewezen. Deze run is er niets uitgegeven: er "
        "was geen enkele wedstrijd in het venster, dus geen competitie om prijzen voor te kopen.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Niet gebruikt deze run — nul wedstrijden in het "
        "venster.")

prepend("understat", "ok",
        "niet aangeroepen — geen doorgerekende wedstrijd vandaag. Geen eigen uitspraak over de "
        "status deze run; de laatste meting is die van 6 okt.")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert, "
        "dus de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 0,
    "matches_in_window": 0,
    "credits": 0,
}
sh["last_run_bevinding"] = (
    "Run A 7 okt 2026: nul wedstrijden in het inzetvenster, nul bets. Alle 21 competities van de "
    "runlijst staan op GEEN WEDSTRIJD, en dat is deze week de normale stand: het interlandvenster "
    "loopt van 6 t/m 14 oktober, de clubcompetities hervatten op 9, 10 en 11 oktober en de drie "
    "Europese toernooien op 13 en 15 oktober. Twee onafhankelijke fixturebronnen zeggen hetzelfde "
    "— Fotmob (28 + 20 competities in de twee daglijsten, geen enkele uit de runlijst) en "
    "BetExplorer (21 pagina's, nul duels vandaag, eerstvolgende op 9 okt). Er is dus niets "
    "afgekapt, niets buiten datadekking gevallen en geen credit uitgegeven. Het werk van deze run "
    "zat volledig in Stage 0: 3 picks en 18 schaduwpicks van 5 en 6 oktober afgewikkeld."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
