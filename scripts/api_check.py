#!/usr/bin/env python3
"""Controleer of de API-sleutels werken, en hoeveel quota er over is.

    python3 scripts/api_check.py

Draai dit nadat je een sleutel hebt toegevoegd aan de omgeving van de geplande taak.
Het script kost bijna geen quota: de sportenlijst van The Odds API is gratis, en de
statuscall van API-Football kost één verzoek van je dagbudget.

De sleutel zelf wordt nooit afgedrukt.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

TIMEOUT = 25


def get(url: str, headers: dict[str, str] | None = None) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), exc.read() or b""
    except Exception as exc:  # netwerk, DNS, TLS
        return 0, {}, str(exc).encode()


def check_odds_api() -> bool:
    """The Odds API: bookmakerprijzen. Sportenlijst kost 0 credits."""
    print("\n=== The Odds API (odds per bookmaker) ===")
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        print("  ODDS_API_KEY niet gezet — overgeslagen.")
        print("  Zet hem in de omgeving van de geplande taak (zie README, 'Sleutels toevoegen').")
        return False

    status, headers, body = get(f"https://api.the-odds-api.com/v4/sports/?apiKey={key}")

    if status == 401:
        print("  401 — sleutel afgewezen. Controleer of je hem volledig hebt gekopieerd.")
        return False
    if status != 200:
        print(f"  HTTP {status} — {body[:200].decode(errors='replace')}")
        return False

    try:
        sports = json.loads(body)
    except json.JSONDecodeError:
        print("  Antwoord was geen JSON — onverwacht.")
        return False

    soccer = [s for s in sports if str(s.get("key", "")).startswith("soccer_") and s.get("active")]
    print(f"  OK — {len(soccer)} actieve voetbalcompetities beschikbaar.")

    remaining = headers.get("x-requests-remaining")
    used = headers.get("x-requests-used")
    if remaining is not None:
        print(f"  Quota: {remaining} over, {used} gebruikt deze maand.")
        try:
            if float(remaining) < 60:
                print("  LET OP: minder dan 60 credits over. Kosten = markten x regio's per verzoek.")
        except ValueError:
            pass

    # Welke van onze competities zitten erin? Handig voor coverage.json.
    wanted = ("eredivisie", "portugal", "belgium", "poland", "scot", "epl", "italy",
              "spain", "germany", "france", "efl_champ", "denmark", "turkey", "uefa")
    hits = sorted(s["key"] for s in soccer if any(w in s["key"] for w in wanted))
    if hits:
        print("  Relevante sportkeys:")
        for k in hits:
            print(f"    {k}")
    return True


def check_api_football() -> bool:
    """API-Football: statistieken, opstellingen, blessures."""
    print("\n=== API-Football (statistieken) ===")
    key = os.environ.get("API_FOOTBALL_KEY")
    if not key:
        print("  API_FOOTBALL_KEY niet gezet — overgeslagen.")
        print("  Zet hem in de omgeving van de geplande taak (zie README, 'Sleutels toevoegen').")
        return False

    status, _, body = get("https://v3.football.api-sports.io/status",
                          {"x-apisports-key": key, "Accept": "application/json"})

    if status in (401, 403):
        print(f"  HTTP {status} — sleutel afgewezen of ontbrekende header.")
        print(f"  Antwoord: {body[:200].decode(errors='replace')}")
        return False
    if status != 200:
        print(f"  HTTP {status} — {body[:200].decode(errors='replace')}")
        return False

    try:
        envelope = json.loads(body)
    except json.JSONDecodeError:
        print("  Antwoord was geen JSON — onverwacht.")
        return False

    # API-Football antwoordt ook bij een foute sleutel met HTTP 200 en zet de fout in de body.
    errors = envelope.get("errors")
    if errors:
        detail = errors if isinstance(errors, list) else list(errors.values())
        print(f"  Sleutel afgewezen (HTTP 200 met fout in de body): {'; '.join(map(str, detail))[:200]}")
        return False

    payload = envelope.get("response")
    if not isinstance(payload, dict):
        print(f"  Onverwacht antwoord: 'response' is {type(payload).__name__}, geen object.")
        print(f"  Ruwe body: {body[:200].decode(errors='replace')}")
        return False

    subscription = payload.get("subscription", {})
    requests_info = payload.get("requests", {})
    print(f"  OK — plan: {subscription.get('plan', 'onbekend')}, "
          f"actief tot {subscription.get('end', 'onbekend')}")
    print(f"  Vandaag gebruikt: {requests_info.get('current', '?')} van "
          f"{requests_info.get('limit_day', '?')}")
    print("  Let op: xG-dekking is per competitie en seizoen wisselend. Controleer per")
    print("  competitie of er echt xG in zit voordat je hem als FULL-databron rekent.")
    return True


def main() -> int:
    print("Controle van de databronnen die een sleutel nodig hebben.")
    odds_ok = check_odds_api()
    stats_ok = check_api_football()

    print("\n=== Samenvatting ===")
    print(f"  odds (prijzen)        {'OK' if odds_ok else 'niet beschikbaar'}")
    print(f"  statistieken (kansen) {'OK' if stats_ok else 'niet beschikbaar'}")

    if not stats_ok:
        print("\n  Zonder een werkende statistiekenbron blijft de routine bets overslaan:")
        print("  zonder onafhankelijke kansinput zou 'my_prob' uit de odds zelf komen, en dat")
        print("  is precies wat _shared-rules.md §2 verbiedt. Dit is dus de sleutel die telt.")
    if not odds_ok:
        print("\n  Zonder odds-API blijft Oddschecker de prijsbron. Dat werkt, maar de")
        print("  individuele bookmaker is daar niet altijd herleidbaar.")

    return 0 if (odds_ok or stats_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
