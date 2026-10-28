#!/usr/bin/env python3
"""Controleer of de API-sleutels werken, en hoeveel quota er over is.

    python3 scripts/api_check.py

`API_FOOTBALL_KEY` ontbreekt met opzet: de gebruiker heeft op 27 sep 2026 besloten daar geen geld
aan uit te geven (`_shared-rules.md` §3, "API_FOOTBALL_KEY komt er niet"). Dit script meldt dat dus
als stand van zaken en niet als actiepunt. Het blijft wél melden dat er geen statistieken-API is,
want dat is waar — en het zegt onder welke voorwaarde die keuze opnieuw ter tafel komt: als Fotmob
wegvalt.

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

    # Welke van de sleutels die de repo kent, leeft er vandaag? Dit is de controle die telt:
    # een sleutel die uit de lijst verdwijnt levert geen foutmelding maar een competitie zonder
    # beste prijs, en dat is van buitenaf niet te zien (§1a).
    live = {s["key"] for s in soccer}
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from scripts.oddsapi import SPORT_KEYS
    except Exception as exc:                                      # pragma: no cover
        print(f"  (sportkeys van de repo niet te lezen: {exc})")
        SPORT_KEYS = {}
    if SPORT_KEYS:
        ontbreekt = sorted(n for n, k in SPORT_KEYS.items() if k not in live)
        print(f"  Sportkeys van de repo: {len(SPORT_KEYS) - len(ontbreekt)} van "
              f"{len(SPORT_KEYS)} actief vandaag.")
        for naam in ontbreekt:
            print(f"    NIET ACTIEF  {naam:30s} {SPORT_KEYS[naam]}")

    # En welke actieve sleutels horen bij een land uit de runlijsten zonder dat de repo ze kent?
    # **Filter op `title` en `description` en niet alleen op de sleutel** — dat laatste deed deze
    # controle tot 28 okt 2026 en het verborg twee sleutels die er wél waren: `soccer_spl`
    # (Scottish Premiership; "scot" staat alleen in de titel) en `soccer_england_efl_cup`
    # (League Cup; de sleutel bevat "england" en dat woord stond niet in de zoeklijst). De
    # Scottish Premiership heeft daardoor zeven weken op het marktgemiddelde gedraaid.
    # **En de lijst dekt alle landen van alle drie de runlijsten, niet alleen Europa** — dat is de
    # correctie van 28 okt 2026 (Run B). Run A repareerde hierboven het veld waarop wordt gefilterd
    # (sleutel -> sleutel + titel + beschrijving) maar liet de woordenlijst zelf Europees: er stond
    # geen "usa", geen "brazil" en geen "hungar" in. Gevolg: `soccer_usa_mls` en
    # `soccer_brazil_campeonato` stonden actief bij de bron, ontbraken in `SPORT_KEYS`, en waren
    # voor deze controle **onzichtbaar** — terwijl MLS en Série A samen vier van de zeventien
    # competities van `run-b.md` zijn en op 28 okt 2026 19 van de 26 duels leverden.
    #
    # Dat is dezelfde stille faalstand als het Serie B-id en als `soccer_spl`, nu in een derde
    # gedaante: niet een verkeerd veld maar een te korte woordenlijst. Een controle die groen staat
    # omdat ze de verkeerde grootheid meet (§6g) — en bij een onvolledige lijst klaagt niets.
    landen = ("england", "scot", "italy", "italian", "spain", "spanish", "germany", "german",
              "france", "french", "netherl", "dutch", "portug", "belgi", "poland", "polish",
              "denmark", "danish", "turk", "uefa", "europa", "champions", "conference",
              "sweden", "swedish", "norway", "norwegian", "swiss", "switzerl", "austria",
              "greece", "greek", "czech", "romania", "croatia",
              # buiten Europa, en daarom tot 28 okt 2026 niet gezien
              "usa", "mls", "major league", "brazil", "brasil", "hungar", "concacaf")
    bekend = set(SPORT_KEYS.values())
    extra = sorted(f'{s["key"]}  ({s.get("title")} / {s.get("description")})' for s in soccer
                   if s["key"] not in bekend
                   and any(w in " ".join(str(s.get(f, "")) for f in
                                         ("key", "title", "description")).lower()
                           for w in landen))
    if extra:
        print("  Actieve sportkeys die de repo NIET kent (mogelijk een gat in SPORT_KEYS):")
        for k in extra:
            print(f"    {k}")
    return True


def check_api_football() -> bool:
    """API-Football: statistieken, opstellingen, blessures."""
    print("\n=== API-Football (statistieken) ===")
    key = os.environ.get("API_FOOTBALL_KEY")
    if not key:
        print("  API_FOOTBALL_KEY niet gezet — overgeslagen.")
        print("  Dat is een besluit van de gebruiker (27 sep 2026), geen storing: hij wil hier geen")
        print("  geld aan uitgeven. De kanskant komt van Fotmob en Understat. Zie")
        print("  _shared-rules.md §3, 'API_FOOTBALL_KEY komt er niet'. Niet als actiepunt melden.")
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
        print("\n  Er is geen statistieken-API. Dat is sinds 27 sep 2026 de bewuste opzet en geen")
        print("  gat: de onafhankelijke kansinput komt van Fotmob (alle competities) en Understat")
        print("  (vijf). Zolang die twee leveren, is §2 gedekt en is er niets te doen.")
        print("  WEL melden, vooraan in de notificatie: als Fotmob niet meer levert. Dan is er voor")
        print("  vrijwel elke wedstrijd geen kansbron meer, wordt alles data_tier = NONE en levert")
        print("  elke run gegarandeerd nul bets. Pas dán is een betaald plan een reële vraag.")
    if not odds_ok:
        print("\n  Zonder odds-API blijft Oddschecker de prijsbron. Dat werkt, maar de")
        print("  individuele bookmaker is daar niet altijd herleidbaar.")

    return 0 if (odds_ok or stats_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
