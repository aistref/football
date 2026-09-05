#!/usr/bin/env python3
"""The Odds API-ophaalcode: bookmakerprijzen als JSON, credit-bewust.

Werkend sinds de gebruiker op 8 aug 2026 een ODDS_API_KEY toevoegde. Twee dingen die de vorige
run met de hand moest ontdekken en die hier vastliggen:

1. De bulk-endpoint (`/v4/sports/{sport}/odds`) ondersteunt alleen `h2h`, `spreads` en `totals`.
   `btts`, `double_chance` en `draw_no_bet` geven daar HTTP 422 en moeten via de
   per-wedstrijd-endpoint (`/events/{id}/odds`), die apart afrekent.
2. Kosten = markten x regio's, per verzoek. Bij 500 credits/maand en twee runs per dag is het
   budget circa 8 credits per run (zie README "Sleutels toevoegen" en het naschrift in
   runs/2026-08-08-run-a-2.md). Gebruik de bulk-endpoint voor `totals` (1X2 komt gratis van
   BetExplorer) en bewaar de per-wedstrijd-endpoint voor markten op wedstrijden die al een
   kandidaat-edge tonen — niet voor alles tegelijk.

    from scripts.oddsapi import fetch_totals, fetch_event_markets

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field

TIMEOUT = 35
BASE = "https://api.the-odds-api.com/v4"

# Sportkeys bevestigd aanwezig op 8 aug 2026 (zie python3 scripts/api_check.py). Vul aan zodra
# een competitie is nagetrokken — een geraden key faalt met een duidelijke 404, geen stille fout.
SPORT_KEYS: dict[str, str] = {
    "Premier League (ENG)": "soccer_epl",
    "Serie A (ITA)": "soccer_italy_serie_a",
    "La Liga (ESP)": "soccer_spain_la_liga",
    "Bundesliga (GER)": "soccer_germany_bundesliga",
    "Ligue 1 (FRA)": "soccer_france_ligue_one",
    "Championship (ENG)": "soccer_efl_champ",
    "Eredivisie (NED)": "soccer_netherlands_eredivisie",
    "Primeira Liga (POR)": "soccer_portugal_primeira_liga",
    "Belgian Pro League (BEL)": "soccer_belgium_first_div",
    "Süper Lig (TUR)": "soccer_turkey_super_league",
    "Danish Superliga (DEN)": "soccer_denmark_superliga",
    "Ekstraklasa (POL)": "soccer_poland_ekstraklasa",
    "DFB Pokal (GER)": "soccer_germany_dfb_pokal",
    "League Cup (ENG)": "soccer_england_efl_cup",  # bevestigd 10 aug 2026
    "League One (ENG)": "soccer_england_league1",
    "League Two (ENG)": "soccer_england_league2",
    "2. Bundesliga (GER)": "soccer_germany_bundesliga2",
    "Serie B (ITA)": "soccer_italy_serie_b",
    "Segunda División (ESP)": "soccer_spain_segunda_division",
    "Ligue 2 (FRA)": "soccer_france_ligue_two",
    "Coppa Italia (ITA)": "soccer_italy_coppa_italia",  # bevestigd 14 aug 2026 via api_check.py
    # Bevestigd 29 aug 2026 (Run B). Deze vier stonden hier nog niet, terwijl ze wel in de
    # /sports/-lijst staan — vier competities van de Run B-runlijst hadden daardoor elke run
    # alleen 1X2 van BetExplorer, zonder dat er een reden voor was. De /sports/-lijst opvragen
    # kost 0 credits (x-requests-last: 0), dus een key natrekken is gratis.
    "Allsvenskan (SWE)": "soccer_sweden_allsvenskan",
    "Swiss Super League (SUI)": "soccer_switzerland_superleague",
    "Austrian Bundesliga (AUT)": "soccer_austria_bundesliga",
    "Greek Super League (GRE)": "soccer_greece_super_league",
}

# Markten die alleen via de per-wedstrijd-endpoint gaan (bevestigd met HTTP 422 op de bulk-call).
EVENT_ONLY_MARKETS = {"btts", "double_chance", "draw_no_bet"}

# Boeken die geen bookmaker zijn maar een beurs: je speelt daar tegen een andere klant en betaalt
# commissie over je nettowinst. De genoteerde prijs is dus niet de prijs die je krijgt.
EXCHANGES = {"betfair", "matchbook", "smarkets", "betdaq"}

EXCHANGE_COMMISSION = 0.02
"""Commissie over de nettowinst bij een beurs. 2% is de gangbare standaard bij Betfair en
Matchbook; het exacte tarief hangt van je account af, dus dit is met opzet aan de voorzichtige
kant en niet exact."""


def is_exchange(bookmaker: str) -> bool:
    return any(name in (bookmaker or "").lower() for name in EXCHANGES)


def net_price(price: float, bookmaker: str, commission: float = EXCHANGE_COMMISSION) -> float:
    """De koers die je werkelijk krijgt, na commissie bij een beurs.

    Bij een gewone bookmaker verandert er niets. Bij een beurs gaat de commissie van de
    **nettowinst** af, dus 3.00 bij 2% commissie is effectief 1 + 2.00 * 0.98 = 2.96.

    Dit is geen detail. Gemeten op 5 sep 2026 stond de beste 1X2-prijs in **61%** van de gevallen
    bij een beurs; wie de kale prijs gebruikt overschat zijn edge dan structureel.
    """
    if not is_exchange(bookmaker):
        return price
    return 1 + (price - 1) * (1 - commission)


def best_h2h(event: dict) -> dict[str, tuple[float, str]]:
    """Beste 1X2-prijs per uitkomst uit een bulk-respons: {"home"|"draw"|"away": (koers, boek)}.

    De uitkomstnamen in een `h2h`-markt zijn exact `event["home_team"]`, `event["away_team"]` en
    "Draw" — allemaal uit dezelfde respons, dus hier is geen naamkoppeling nodig en hoort er ook
    geen fuzzy vergelijking te staan. Geeft een onvolledige dict terug als een uitkomst ontbreekt;
    de aanroeper hoort op `len(...) == 3` te controleren.

    De koers is de **kale** prijs met de boeknaam erbij; haal `net_price` erover voor de prijs die
    je werkelijk krijgt.
    """
    home, away = event.get("home_team"), event.get("away_team")
    out: dict[str, tuple[float, str]] = {}
    for (name, _point), (price, book) in best_by_line(event, "h2h").items():
        if name == home:
            slot = "home"
        elif name == away:
            slot = "away"
        elif str(name).lower() == "draw":
            slot = "draw"
        else:
            continue
        if slot not in out or price > out[slot][0]:
            out[slot] = (price, book)
    return out


class OddsApiError(RuntimeError):
    pass


class BudgetExhausted(RuntimeError):
    """De run heeft zijn creditplafond bereikt. Geen fout: stop met opvragen en meld het."""


def suggest_cap(remaining: int, days_left: int, runs_per_day: int = 2, reserve: int = 20) -> int:
    """Hoeveel credits mag één run uitgeven om het einde van de periode te halen?

    `remaining` komt uit `x-requests-remaining` — dat is de enige harde waarheid over het budget;
    zelf bijhouden loopt scheef zodra een run halverwege afbreekt. `reserve` blijft over voor
    api_check.py en voor een dag die uitloopt.
    """
    usable = max(0, remaining - reserve)
    slots = max(1, days_left * runs_per_day)
    return usable // slots


def split_budget(cap: int, n_competitions: int, totals_share: float = 0.25,
                 min_totals: int = 1) -> tuple[int, int]:
    """Verdeel het creditplafond over `spreads` (stap 0) en `totals` (stap 1).

    Geeft `(aantal_spreads, aantal_totals)` terug — allebei in competities, want beide aanroepen
    kosten 1 credit per competitie.

    **Waarom dit bestaat (30 aug 2026, op verzoek van de gebruiker).** §1a zegt sinds 29 aug
    "spreads eerst, en voor zoveel mogelijk competities", omdat één credit daar drie markten
    oplevert (AH + DNB + DC) tegen één bij `totals`. Puur op markten-per-credit is dat juist, en
    aan het begin van de maand valt er niets te kiezen: het plafond is dan groter dan het aantal
    competities en er blijft vanzelf geld over voor `totals`.

    Aan het **eind** van de maand niet. Op 30 aug 2026 gaf `suggest_cap(68, 2)` een plafond van 12
    bij elf inkoopbare competities. "Zoveel mogelijk" betekende toen elf keer spreads, en er bleef
    één credit over voor `totals` — de doelpuntenmarkt kon dus in **één van de twaalf** competities
    meedingen. De marktbalans-controle van §1a werd gehaald, maar met de kleinst mogelijke marge,
    en dat is de spiegel van 29 aug (toen negen van de elf competities alleen een doelpuntenmarkt
    hadden en 12 van de 14 bets uit die ene markt kwamen). Beide keren was de uitkomst niet de
    analyse maar de inkoop.

    Deze functie reserveert daarom **eerst** een deel voor `totals` en geeft de rest aan `spreads`,
    in plaats van andersom. De volgorde van uitgeven verandert niet — spreads blijft stap 0 — maar
    het aantal ligt vooraf vast in plaats van dat het de restpost is.

    Drie gevallen, en let op het derde:

    >>> split_budget(12, 11)      # eind van de maand: krap plafond
    (9, 3)
    >>> split_budget(20, 11)      # ruim plafond: alle competities spreads, rest naar totals
    (11, 9)
    >>> split_budget(1, 11)       # één credit: dan is totals de enige juiste keuze
    (0, 1)

    Dat laatste is geen afrondingsartefact. Met één credit kun je óf één competitie spreads geven
    óf één competitie totals. Spreads levert AH, DNB en DC — maar dat zijn alle drie
    **uitkomstmarkten**, net als het gratis 1X2 van BetExplorer, dus dan heeft de run geen enkele
    doelpuntenmarkt en faalt de marktbalans-controle. Eén `totals` haalt hem wel. Meer markten is
    hier dus niet meer informatie.

    `totals_share` is niet gemeten en dat staat er met opzet bij: er is geen waarneming die zegt
    dat een kwart de juiste verhouding is. Wat de waarde wél doet, is de doelpuntenmarkt een vaste
    plaats in de inkoop geven in plaats van een restpost, zodat een scheve bettenlijst voortaan
    over de analyse gaat en niet over de portemonnee. Zie `data/calibration.jsonl` en de
    marktbalans-tabel in het runrapport om hem over enkele weken tegen uitkomsten te leggen.
    """
    if cap <= 0 or n_competitions <= 0:
        return (0, 0)
    want = max(min_totals, round(cap * totals_share))
    totals = min(want, cap, n_competitions)
    spreads = min(cap - totals, n_competitions)
    leftover = cap - spreads - totals
    if leftover > 0:                      # meer plafond dan competities: rest naar de doelpunten
        totals = min(totals + leftover, n_competitions)
    return (spreads, totals)


def rotate_for_day(items: list, day, take: int) -> list:
    """Kies `take` items uit `items`, en schuif elke dag op zodat na een paar dagen alles is geweest.

    Nodig sinds 15 aug 2026: het creditplafond laat maar een handvol competities per run toe voor
    `spreads,totals`. Altijd dezelfde vier nemen betekent dat vier competities structureel nooit een
    handicap of totaal te zien krijgen — en dat is precies de stille blinde vlek die §6b-5b moest
    wegnemen. Met roulatie heeft elke competitie om de zoveel dagen zijn beurt, en `1X2` is er via
    BetExplorer sowieso elke dag voor allemaal.

    Geef `items` in volgorde van datakwaliteit mee; bij gelijke beurt wint dan de betere bron.
    """
    if take >= len(items) or not items:
        return list(items)
    offset = (day.toordinal() * take) % len(items)
    doubled = list(items) + list(items)
    return doubled[offset:offset + take]


@dataclass
class CreditGuard:
    """Bewaakt het creditverbruik binnen één run.

    Bestaansreden (15 aug 2026). Op die dag verbruikten Run A en Run B samen **132 credits** —
    ruim een kwart van het maandbudget van 500 op één dag — doordat alle zes markten voor het
    eerst echt werden doorgerekend. Zonder plafond is het budget dan in twee dagen op en leveren
    de runs daarna nul bets, want zonder prijzen is er geen edge te meten.

    Gebruik:

        guard = CreditGuard(cap=8)
        ...
        if guard.can_afford(2):
            resp = fetch_event_markets(...)
            guard.record(resp)
        else:
            # noteer de markt als bekeken-met-reden (§6b-5b), niet als gat
            ...

    De bewaker telt wat een aanroep werkelijk kostte (`x-requests-last`), niet wat hij zou moeten
    kosten — een 422 of een gewijzigd prijsmodel valt dan meteen op.
    """
    cap: int
    spent: int = 0
    remaining: int | None = None
    calls: list[tuple[str, int]] = field(default_factory=list)

    def can_afford(self, cost: int) -> bool:
        return self.spent + cost <= self.cap

    def require(self, cost: int, what: str = "") -> None:
        """Zelfde als `can_afford`, maar werpt `BudgetExhausted` in plaats van False te geven."""
        if not self.can_afford(cost):
            raise BudgetExhausted(
                f"plafond {self.cap} credits bereikt (al {self.spent} uitgegeven); "
                f"{what or 'deze aanroep'} kost er {cost}")

    def record(self, response: "OddsResponse", what: str = "") -> None:
        cost = response.cost if response.cost is not None else 0
        self.spent += cost
        self.remaining = response.requests_remaining
        self.calls.append((what, cost))

    def report(self) -> str:
        """Eén regel voor het runrapport."""
        rest = f", nog {self.remaining} over" if self.remaining is not None else ""
        return f"{self.spent} van {self.cap} credits gebruikt in {len(self.calls)} aanroep(en){rest}"


class QuotaWarning(RuntimeError):
    """Geen fout, maar een signaal om te stoppen: quota bijna op."""


@dataclass
class OddsResponse:
    data: list | dict
    requests_remaining: int | None
    requests_used: int | None
    cost: int | None


def _get(url: str) -> tuple[int, dict, bytes]:
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=TIMEOUT) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), exc.read() or b""


def _api_key() -> str:
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        raise OddsApiError("ODDS_API_KEY niet gezet — zie README 'Sleutels toevoegen'.")
    return key


def _check_quota(headers: dict, reserve: int = 20) -> None:
    remaining = headers.get("x-requests-remaining")
    if remaining is not None:
        try:
            if float(remaining) < reserve:
                raise QuotaWarning(f"nog maar {remaining} credits over (reserve is {reserve}) — stop met opvragen")
        except ValueError:
            pass


def fetch_bulk(sport_key: str, markets: list[str], regions: str = "eu") -> OddsResponse:
    """`h2h`, `spreads` en `totals` in één verzoek voor een hele competitie.

    Kost `len(markets) x regio's` credits — precies evenveel als dezelfde markten los opvragen,
    maar het scheelt verzoeken en het houdt alle markten van één wedstrijd bij elkaar in één
    event-object, zodat `best_by_line(event, "h2h" | "spreads" | "totals")` er alle drie uit haalt.
    Toegevoegd 15 aug 2026: `_shared-rules.md` §6b-5b eist dat elke wedstrijd op alle zes markten
    is nagelopen, en dan wil je die drie bulkmarkten in één keer binnen hebben.

    `btts` en `double_chance` kunnen hier niet bij (HTTP 422) — die gaan via
    `fetch_event_markets`, en die rekent per wedstrijd af.
    """
    bad = [m for m in markets if m in EVENT_ONLY_MARKETS]
    if bad:
        raise OddsApiError(f"markt(en) {bad} kunnen niet via de bulk-endpoint — gebruik fetch_event_markets")
    key = _api_key()
    status, headers, body = _get(
        f"{BASE}/sports/{sport_key}/odds/?apiKey={key}&regions={regions}"
        f"&markets={','.join(markets)}&oddsFormat=decimal")
    if status != 200:
        raise OddsApiError(f"HTTP {status} op sport={sport_key}: {body[:200].decode(errors='replace')}")
    _check_quota(headers)
    remaining = headers.get("x-requests-remaining")
    used = headers.get("x-requests-used")
    return OddsResponse(json.loads(body), int(remaining) if remaining else None,
                         int(used) if used else None, cost=int(headers.get("x-requests-last", 0) or 0))


def fetch_totals(sport_key: str, regions: str = "eu") -> OddsResponse:
    """Over/under-lijnen voor alle wedstrijden van één competitie. Kost 1 credit per regio."""
    key = _api_key()
    status, headers, body = _get(
        f"{BASE}/sports/{sport_key}/odds/?apiKey={key}&regions={regions}&markets=totals&oddsFormat=decimal")
    if status != 200:
        raise OddsApiError(f"HTTP {status} op sport={sport_key}: {body[:200].decode(errors='replace')}")
    _check_quota(headers)
    remaining = headers.get("x-requests-remaining")
    used = headers.get("x-requests-used")
    return OddsResponse(json.loads(body), int(remaining) if remaining else None,
                         int(used) if used else None, cost=int(headers.get("x-requests-last", 0) or 0))


def fetch_spreads(sport_key: str, regions: str = "eu") -> OddsResponse:
    """Asian-Handicaplijnen voor alle wedstrijden van één competitie. Kost 1 credit per regio.

    Bevestigd werkend op 14 aug 2026. Dit stond hierboven al in de docstring ("de bulk-endpoint
    ondersteunt h2h, spreads en totals") maar er was nooit een functie voor, waardoor Asian
    Handicap in de praktijk nooit is meegenomen: van de eerste 15 picks was er niet één een
    handicap. De markt kost hetzelfde als `totals` — 1 credit — dus er was ook geen budgetreden.

    Let op: de respons bevat per bookmaker één lijn, en die lijn verschilt per boek (gemeten op
    Viborg - AGF: -0.5, -1.0 en 0.0 naast elkaar). Groepeer dus op `point` en vergelijk alleen
    prijzen binnen dezelfde lijn — de beste prijs over verschillende lijnen heen vergelijken is
    appels met peren, want een andere lijn is een andere bet.
    """
    key = _api_key()
    status, headers, body = _get(
        f"{BASE}/sports/{sport_key}/odds/?apiKey={key}&regions={regions}&markets=spreads&oddsFormat=decimal")
    if status != 200:
        raise OddsApiError(f"HTTP {status} op sport={sport_key}: {body[:200].decode(errors='replace')}")
    _check_quota(headers)
    remaining = headers.get("x-requests-remaining")
    used = headers.get("x-requests-used")
    return OddsResponse(json.loads(body), int(remaining) if remaining else None,
                         int(used) if used else None, cost=int(headers.get("x-requests-last", 0) or 0))


def fetch_event_markets(sport_key: str, event_id: str, markets: list[str], regions: str = "eu") -> OddsResponse:
    """Markten die niet in de bulk-call zitten (btts, double_chance, draw_no_bet), per wedstrijd.

    Kost 1 credit per markt per regio — gebruik dit gericht, niet voor elke wedstrijd van de dag.
    """
    key = _api_key()
    market_str = ",".join(markets)
    status, headers, body = _get(
        f"{BASE}/sports/{sport_key}/events/{event_id}/odds/"
        f"?apiKey={key}&regions={regions}&markets={market_str}&oddsFormat=decimal")
    if status != 200:
        raise OddsApiError(f"HTTP {status} op event={event_id}: {body[:200].decode(errors='replace')}")
    _check_quota(headers)
    remaining = headers.get("x-requests-remaining")
    used = headers.get("x-requests-used")
    return OddsResponse(json.loads(body), int(remaining) if remaining else None,
                         int(used) if used else None, cost=int(headers.get("x-requests-last", 0) or 0))


def best_totals_2_5(event: dict) -> dict[str, tuple[float, str]] | None:
    """Beste prijs per uitkomst (Over/Under 2.5) uit één event uit `fetch_totals`."""
    best: dict[str, tuple[float, str]] = {}
    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market["key"] != "totals":
                continue
            for outcome in market["outcomes"]:
                if abs(outcome["point"] - 2.5) > 0.01:
                    continue
                current = best.get(outcome["name"])
                if current is None or outcome["price"] > current[0]:
                    best[outcome["name"]] = (outcome["price"], bookmaker["title"])
    return best or None


def best_by_line(event: dict, market_key: str) -> dict[tuple[str, float | None], tuple[float, str]]:
    """Beste prijs per (uitkomst, lijn) uit één event, voor elke markt.

    Werkt op `h2h`, `spreads`, `totals`, `btts` en `double_chance` tegelijk — de sleutel is
    `(naam, point)`, waarbij `point` `None` is voor markten zonder lijn. Dit vervangt het
    overtypen van dezelfde geneste lus per markt, en het houdt de lijnen uit elkaar: bij
    `spreads` en `totals` geeft elke bookmaker zijn eigen lijn, en de beste prijs op -0.5
    hoort niet vergeleken te worden met de beste prijs op -1.0.

    Exchanges staan in de respons als gewone bookmaker (Betfair, Matchbook) maar hun `h2h_lay`-
    regels zijn lay-prijzen — daar kun je niet op inzetten. Die worden hier overgeslagen.
    """
    best: dict[tuple[str, float | None], tuple[float, str]] = {}
    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market["key"] != market_key or market_key.endswith("_lay"):
                continue
            for outcome in market["outcomes"]:
                key = (outcome["name"], outcome.get("point"))
                current = best.get(key)
                if current is None or outcome["price"] > current[0]:
                    best[key] = (outcome["price"], bookmaker["title"])
    return best


if __name__ == "__main__":
    # Zelftest: haalt de Eredivisie-totals op en controleert dat er events met een Over/Under-
    # lijn in zitten. Vereist een werkende ODDS_API_KEY in de omgeving.
    resp = fetch_totals(SPORT_KEYS["Eredivisie (NED)"])
    print(f"{len(resp.data)} events, {resp.requests_remaining} credits over, deze call kostte {resp.cost}")
    with_totals = [e for e in resp.data if best_totals_2_5(e)]
    assert with_totals, "geen enkel event had een Over/Under 2.5-lijn — respons kan gewijzigd zijn"
    example = with_totals[0]
    print(f"  voorbeeld: {example['home_team']} - {example['away_team']}  {best_totals_2_5(example)}")
    print("Zelftest geslaagd.")
