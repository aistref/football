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
    "2. Bundesliga (GER)": "soccer_germany_bundesliga2",
    "Serie B (ITA)": "soccer_italy_serie_b",
    "Segunda División (ESP)": "soccer_spain_segunda_division",
    "Ligue 2 (FRA)": "soccer_france_ligue_two",
}

# Markten die alleen via de per-wedstrijd-endpoint gaan (bevestigd met HTTP 422 op de bulk-call).
EVENT_ONLY_MARKETS = {"btts", "double_chance", "draw_no_bet"}


class OddsApiError(RuntimeError):
    pass


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
