"""Run A, 6 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
import json
from datetime import date, datetime, timezone

DAY = date(2026, 10, 6)
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
    e["detail"] = f"[Run A] 6 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "2 daglijsten opgehaald (6 en 7 okt), beide HTTP 200: 59 competities op 6 okt en 24 op "
        "7 okt. Geen van de 21 runlijstcompetities staat erop, de FA Cup inbegrepen — de "
        "bevinding van 2 en 5 okt is daarmee voor de derde keer gemeten en de tweede "
        "fixturebron was vandaag het verschil tussen vijf duels en nul. Wél gebruikt als "
        "KANSbron: fetch_league_stats voor National League North (id 8944, group= expliciet) "
        "over 2025/2026 en 2026/2027 gaf beide keren 24 ploegen met doelpunten en thuis/uit-"
        "splits, zonder xG. Ook de andere non-league-standen opgehaald om de clubs van de vier "
        "overige duels te zoeken (id 117, en id 8947 voor alle vier zijn groepen).")

prepend("betexplorer", "ok",
        "21 fixturepagina's opgehaald als tweede fixturebron, allemaal HTTP 200. Eén competitie "
        "had duels in het inzetvenster: de FA Cup, met 5 rijen op 'Today 19:45' en een "
        "1X2-marktgemiddelde over 2 boeken per duel. Dat is ook meteen de enige prijsbron van "
        "deze run — de FA Cup heeft geen sportkey bij The Odds API. Coppa Italia en KNVB Beker "
        "gaven opnieuw HTTP 200 met een lege tabel; de overige 18 gaven rijen maar niets vóór "
        "9 okt.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 49 actieve voetbalcompetities, quota 19.885 van de 20.000 over "
        "(115 gebruikt deze maand). Sleutel niet afgewezen. Deze run is er niets uitgegeven: de "
        "enige competitie met duels in het venster (FA Cup) heeft geen sportkey, dus er viel "
        "niets te kopen — spreads, totals en BTTS staan daarom als 'niet opgevraagd' in "
        "markets_checked en niet als gat.")

prepend("oddsapi", "ok",
        "sleutel geaccepteerd (api_check.py). Niet gebruikt deze run: de enige actieve "
        "competitie heeft geen sportkey.")

prepend("understat", "ok",
        "niet aangeroepen — Understat dekt vijf topcompetities en de enige doorgerekende "
        "wedstrijd staat in de Engelse zesde divisie. Geen eigen uitspraak over de status "
        "deze run.")

prepend("api_football", "missing_key",
        "sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld, en niet in de notificatie. Fotmob levert, "
        "dus de uitzondering van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "A",
    "date": DAY.isoformat(),
    "bets": 0,
    "matches_in_window": 5,
    "credits": 0,
}
sh["last_run_bevinding"] = (
    "Run A 6 okt 2026: vijf FA Cup-kwalificatieduels in het venster, nul bets. De vijf stonden "
    "uitsluitend bij BetExplorer — de Fotmob-daglijsten van 6 en 7 okt noemen de FA Cup niet — "
    "dus zonder de tweede fixturebron was deze dag stil als 'GEEN WEDSTRIJD' gepasseerd. Vier "
    "duels kwamen op data_tier NONE omdat de twee ploegen in verschillende (of in geen enkele "
    "door Fotmob gedekte) divisie staan. Eén duel was wél door te rekenen: Scarborough Athletic "
    "– Macclesfield FC, beide in National League North, dus niets te overbruggen (§4, 15 sep "
    "2026). Geen xG in die divisie, dus doelpunten als sterktemaat en data_tier LIGHT; de "
    "hoogste edge was +2,5 pp tegen een drempel van 16,0."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
