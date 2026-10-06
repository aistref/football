"""Run B, 6 okt 2026 — source-health.json bijwerken met wat deze run werkelijk heeft gemeten."""
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
    e["detail"] = f"[Run B] 6 okt 2026: {text}" + (f"  || eerder: {old}" if old else "")


prepend("fotmob", "ok",
        "Twee daglijsten opgehaald (6 en 7 okt), beide HTTP 200: 59 competities / 111 duels op "
        "6 okt en 24 / 62 op 7 okt. 34 standenverzoeken voor scripts/idcheck.py (alle 17 "
        "runlijst-id's uit coverage.json, alle 17 een bruikbare stand, afsluitcode 0), twee "
        "standen voor MLS (2025 en 2026) en de wedstrijdcontext van het enige duel in het "
        "inzetvenster. Alles HTTP 200, geen storing. Fotmob was opnieuw de ENIGE kansbron: de "
        "uitzondering van §3 punt 3 (melden zodra Fotmob niet meer levert) is niet aan de orde. "
        "Let op het verschil met Run A van vanochtend: die vond de FA Cup níet op de "
        "Fotmob-daglijsten en had BetExplorer als tweede fixturebron nodig. Voor déze runlijst "
        "klopten de daglijsten wél — MLS stond er gewoon op, op de lijst van 7 okt.")

prepend("the_odds_api", "ok",
        "api_check.py geeft 49 actieve voetbalcompetities en 19.885 van de 20.000 credits over "
        "(115 deze maand). Sleutel niet afgewezen, geen quotawaarschuwing. 4 credits "
        "uitgegeven op een plafond van 382: één bulk-aanroep à 3 credits (h2h + spreads + "
        "totals) voor soccer_usa_mls — de enige spelende competitie, en die hééft een sportkey "
        "— plus 1 credit BTTS voor het ene duel met een kandidaat-edge (§1a stap 2). Quota "
        "daarna 19.881. Anders dan op 5 okt is dit geld niet aan een niet-doorgerekend duel "
        "besteed: het duel kwam op FULL uit en alle zes markten hebben meegedongen.")

prepend("oddsapi", "ok",
        "Sleutel geaccepteerd (api_check.py 6 okt 2026). Gebruikt voor MLS (USA): 3 credits "
        "bulk + 1 credit BTTS. oddsapi.net_price toegepast op de beste prijzen; de beste "
        "Over/Under-prijs stond bij Matchbook (beurs) en is met 2% commissie doorgerekend.")

prepend("betexplorer", "ok",
        "Eén fixturepagina opgehaald (usa/mls), HTTP 200, 31 rijen. Het marktgemiddelde over 11 "
        "boeken voor Chicago Fire – Vancouver Whitecaps (2,81 / 3,77 / 2,23) is gebruikt waar "
        "§1a het voorschrijft: het kalibratieblok van §6e en poort 8. De bet zelf rekent met de "
        "beste prijs. De rijen stonden alle 31 op is_today = False, want BetExplorer dateert "
        "een MLS-duel op de Amerikaanse kalenderdag; dat is geen storing en de koppeling op "
        "ploegnaam vond de wedstrijd gewoon.")

prepend("understat", "ok",
        "Niet aangeroepen — MLS (USA) zit niet in de vijf competities die Understat dekt (§4). "
        "Status ongewijzigd overgenomen. Geen storing, maar wél de reden dat deze run geen "
        "tweede, onafhankelijk xG-model had: p_xg_understat ontbreekt in het kalibratieblok.")

prepend("api_football", "missing_key",
        "Sleutel ontbreekt, en dat is het besluit van de gebruiker van 27 sep 2026 (§3) en geen "
        "storing. Niet als gat of actiepunt gemeld en niet in de notificatie. api_check.py "
        "meldt het onveranderd als feit en dringt niet aan. Fotmob levert, dus de uitzondering "
        "van §3 punt 3 is niet aan de orde.")

sh["last_run"] = {
    "run": "B",
    "date": DAY.isoformat(),
    "bets": 1,
    "matches_in_window": 1,
    "credits": 4,
}
sh["last_run_bevinding"] = (
    "Run B 6 okt 2026: één wedstrijd in het inzetvenster van de hele runlijst van zeventien "
    "competities — Chicago Fire FC – Vancouver Whitecaps (MLS), 02:30 NL op 7 oktober — en één "
    "gepubliceerde regel, op RANGORDE en niet op voordeel: Under 3,5 @1,78 bij Matchbook "
    "(1,7644 na commissie), +5,15 pp tegen een lat van 8,0. Van de 23 doorgerekende selecties "
    "haalde er geen enkele zijn drempel. Drie dingen die een volgende run moet weten. "
    "(1) HET INZETVENSTER DEED VANDAAG PRECIES WAARVOOR HET IS GEBOUWD. Het duel staat op de "
    "Fotmob-daglijst van 7 OKTOBER (02:30 NL) en hoort toch bij de run van 6 oktober, want het "
    "venster loopt van 08:00 NL tot 08:00 NL. Op de UTC-datum filteren — wat elke run tot 24 "
    "september deed — zou het aan de run van morgen hebben gegeven, die het om 05:15 al "
    "gespeeld aantreft. Zestien van de zeventien competities hadden GEEN WEDSTRIJD "
    "(interlandvenster); idcheck.py bevestigde met afsluitcode 0 dat geen enkel id stil kapot "
    "is, en dat is precies de controle waarvoor dat script op 29 september is gebouwd. "
    "(2) POORT 6 (ROBUUSTHEID) BEPAALDE DE LIJST, NIET DE EDGE-LAT. De twee sterkste selecties "
    "op ruwe score stonden allebei op Vancouver — Draw No Bet @1,75 (+6,33 pp ruw) en 1X2 "
    "@2,35 (+7,26 pp) — en allebei draait hun edge om in het (shrink, rho)-grid (min_edge "
    "-0,90 en -0,11 pp), net als alle zeven Asian Handicap-lijnen op diezelfde kant. Wat "
    "overbleef is de doelpuntenmarkt, die +2,62 pp overhoudt op het zwakste punt van het grid. "
    "Dat is poort 6 die precies doet wat §1 van hem vraagt, en het verklaart waarom de "
    "gepubliceerde regel een Under is en geen kant. "
    "(3) DE VASTGELOPEN AFWIKKELING BLIJFT GEREPAREERD EN DE RESTSTAPEL IS STABIEL. "
    "calibration.py settle en ctxlog.py settle zijn beide gedraaid; "
    "recalibrate.load_fit().fitted_through staat op 2026-10-05, de vórige rundag, dus de "
    "controle van §6b-5c is groen. De zeven wedstrijden die Run B op 5 oktober als echte "
    "BRONLACUNE aanwees (vier FA Cup-kwalificatieduels van 3 okt, Levante – Athletic Club, FC "
    "Utrecht – Go Ahead Eagles en Red Bull New York – St. Louis City) staan er nog, en er "
    "kwamen er géén bij: de drie andere open rijen zijn van vandaag of nog bezig (Honduras – "
    "Jamaica stond bij deze run live op 49 minuten)."
)
sh["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(sh, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt voor", DAY)
