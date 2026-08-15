#!/usr/bin/env python3
"""BetExplorer-ophaalcode: gratis 1X2-odds, server-side in de HTML.

Stond tot 8 aug 2026 als `js_only` in data/source-health.json — dat was gemeten op de
wedstrijdpagina, die inderdaad leeg is. De "Next matches"-tabel op een competitiepagina levert
1X2 wél server-side, in `data-odd` (gemiddelde). Alleen 1X2 — de ou/bts/ah-ajax-endpoints gaven
404 bij het natrekken.

LET OP (gemeten 10 aug 2026): `data-odd-max` (beste prijs) en `data-bookmaker` stonden op 8 aug nog
in de rijen maar zijn daar nu uit verdwenen — alleen het gemiddelde is er nog. Heb je de béste prijs
nodig, gebruik dan The Odds API; deze bron levert een marktgemiddelde, geen prijs waar je op kunt
inleggen.

    from scripts.betexplorer import fetch_league_odds

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass

TIMEOUT = 45
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Referer": "https://www.betexplorer.com/",
}

_ROW_RE = re.compile(r"<tr>(?:(?!</tr>).)*?</tr>", re.S)
_TEAMS_RE = re.compile(r'class="in-match"><span>([^<]*)</span>\s*-\s*<span>([^<]*)</span>')
_ODDS_RE = re.compile(r'data-odd="([\d.]+)"')
_TODAY_RE = re.compile(r"Today's match")


class BetExplorerError(RuntimeError):
    pass


@dataclass
class MatchOdds:
    home: str
    away: str
    odds: tuple[float, float, float]  # (1, X, 2), gemiddelde over de getoonde boeken
    is_today: bool
    when: str = ""       # het label zoals BetExplorer het toont, bv. "Today 12:30" of "16.08. 14:30"
    bookmakers: int = 0  # aantal boeken achter het gemiddelde; 0 = niet gevonden


_FIX_ROW_RE = re.compile(r"<tr[^>]*>(?:(?!</tr>).)*?</tr>", re.S)
_WHEN_RE = re.compile(r'class="table-main__datetime"[^>]*>([^<]*)<')
_BOOKS_RE = re.compile(r'class="table-main__bs"[^>]*>(\d+)<')


def fetch_league_fixtures(url: str) -> list[MatchOdds]:
    """1X2-odds voor **alle** aankomende wedstrijden, via de /fixtures/-pagina.

    Waarom dit naast `fetch_league_odds` bestaat (15 aug 2026). De "Next matches"-tabel op de
    competitiepagina toont maximaal vijf à zes duels. Op een volle zaterdag is dat te weinig:
    de Championship had er die dag acht, dus drie wedstrijden zouden zonder 1X2 blijven. De
    /fixtures/-pagina van dezelfde competitie geeft ze wél allemaal — gemeten op 15 aug 2026:
    551 teamparen en odds voor de eerstvolgende negentien duels, met alle acht van die dag erbij.

    `url` mag de competitiepagina zijn of de fixtures-pagina zelf; "fixtures/" wordt zo nodig
    aangeplakt.

    LET OP, twee dingen die de prijzen betekenis geven:

    1. Dit is het **gemiddelde** over de getoonde boeken, niet de beste prijs, en de bookmaker is
       niet herleidbaar (zie de kop van dit bestand). Een edge die je hiertegen meet is dus
       systematisch lager dan een edge tegen de beste prijs. Vergelijk daarom nooit een 1X2 uit
       deze bron met een handicap uit The Odds API alsof ze op dezelfde schaal staan —
       `_shared-rules.md` §1a legt uit hoe dat wél moet.
    2. De tijd in `when` is **UK-tijd**, net als elders op BetExplorer: "Today 12:30" hoort bij een
       aftrap van 13:30 Nederlandse tijd. Gebruik voor de aftrap dus Fotmob en niet dit label; het
       label is er om op de juiste speeldag te filteren, niet om de tijd te rapporteren.
    """
    if not url.rstrip("/").endswith("fixtures"):
        url = url.rstrip("/") + "/fixtures/"
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=TIMEOUT).read()
    except urllib.error.HTTPError as exc:
        raise BetExplorerError(f"HTTP {exc.code} op {url}") from exc
    text = raw.decode(errors="replace")

    matches: list[MatchOdds] = []
    carried = ""
    for row in _FIX_ROW_RE.finditer(text):
        row_html = row.group(0)
        teams = _TEAMS_RE.search(row_html)
        odds = _ODDS_RE.findall(row_html)
        if not (teams and len(odds) >= 3):
            continue
        when = _WHEN_RE.search(row_html)
        books = _BOOKS_RE.search(row_html)
        # BetExplorer laat de tijd weg zodra een wedstrijd op hetzelfde moment begint als de rij
        # erboven; die cel bevat dan alleen &nbsp;. Zonder doorschuiven raak je precies de dagen
        # kwijt waarop het druk is: op 15 aug 2026 hadden zes van de acht Championship-duels om
        # 15:00 UK een lege cel, en een filter op "Today" hield er dan drie over in plaats van acht.
        label = (when.group(1).strip() if when else "")
        if label.replace("&nbsp;", "").strip():
            carried = label
        else:
            label = carried
        matches.append(MatchOdds(
            home=teams.group(1).strip(),
            away=teams.group(2).strip(),
            odds=(float(odds[0]), float(odds[1]), float(odds[2])),
            is_today=label.lower().startswith("today"),
            when=label,
            bookmakers=int(books.group(1)) if books else 0,
        ))
    return matches


def fetch_league_odds(url: str) -> list[MatchOdds]:
    """1X2-odds uit de 'Next matches'-tabel van een BetExplorer-competitiepagina.

    `url` is de competitiepagina, bv. "https://www.betexplorer.com/football/netherlands/eredivisie/".
    Geeft alleen de aankomende wedstrijden terug (de tabel onder "Next matches"), niet de
    resultatenlijst eronder.
    """
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=TIMEOUT).read()
    except urllib.error.HTTPError as exc:
        raise BetExplorerError(f"HTTP {exc.code} op {url}") from exc
    text = html.decode(errors="replace")

    segment = text.split("Next matches", 1)[-1].split("componentHeader", 1)[0]
    matches = []
    for row in _ROW_RE.finditer(segment):
        row_html = row.group(0)
        teams = _TEAMS_RE.search(row_html)
        odds = _ODDS_RE.findall(row_html)
        if teams and len(odds) >= 3:
            matches.append(MatchOdds(
                home=teams.group(1).strip(),
                away=teams.group(2).strip(),
                odds=(float(odds[0]), float(odds[1]), float(odds[2])),
                is_today=bool(_TODAY_RE.search(row_html)),
            ))
    return matches


# Bekende URL's, bevestigd werkend op 8 aug 2026. Vul aan zodra een nieuwe competitie is
# nagetrokken — verzin geen slug, want een verkeerde geeft een lege lijst zonder foutmelding.
KNOWN_LEAGUE_URLS: dict[str, str] = {
    "Eredivisie (NED)": "https://www.betexplorer.com/football/netherlands/eredivisie/",
    "Liga Portugal (POR)": "https://www.betexplorer.com/football/portugal/liga-portugal/",
    "Belgian Pro League (BEL)": "https://www.betexplorer.com/football/belgium/jupiler-pro-league/",
    "Ekstraklasa (POL)": "https://www.betexplorer.com/football/poland/ekstraklasa/",
    "Scottish Premiership (SCO)": "https://www.betexplorer.com/football/scotland/premiership/",
    "Coppa Italia (ITA)": "https://www.betexplorer.com/football/italy/coppa-italia/",
    "League Cup (ENG)": "https://www.betexplorer.com/football/england/efl-cup/",
    # 10 aug 2026: 'denmark/superliga' werkt, 'denmark/superligaen' geeft HTTP 200 met 0 rijen.
    "Danish Superliga (DEN)": "https://www.betexplorer.com/football/denmark/superliga/",
    # Bevestigd tijdens Run B van 9 aug 2026:
    "Czech First League (CZE)": "https://www.betexplorer.com/football/czech-republic/chance-liga/",
    "Romanian SuperLiga (ROU)": "https://www.betexplorer.com/football/romania/superliga/",
    "Croatian HNL (CRO)": "https://www.betexplorer.com/football/croatia/hnl/",
    "Hungarian NB I (HUN)": "https://www.betexplorer.com/football/hungary/nb-i/",
    "Keuken Kampioen Divisie (NED)": "https://www.betexplorer.com/football/netherlands/eerste-divisie/",
    # Bevestigd tijdens Run B van 10 aug 2026:
    "Allsvenskan (SWE)": "https://www.betexplorer.com/football/sweden/allsvenskan/",
    # Bevestigd op 11 aug 2026: The Odds API heeft GEEN sportkey voor de UEFA Super Cup, dus dit
    # is voor dat duel de enige oddsbron. 'europe/super-cup' en 'world/uefa-super-cup' geven de
    # stille faalmodus (HTTP 200, 0 rijen); alleen deze slug werkt.
    "UEFA Super Cup": "https://www.betexplorer.com/football/europe/uefa-super-cup/",
    # Bevestigd op 12 aug 2026: dit is de enige oddsbron voor de Conference League-voorrondes —
    # soccer_uefa_europa_conference_league staat bij The Odds API op active=false zolang het
    # hoofdtoernooi niet loopt. De slug dekt ook de kwalificatierondes (5 rijen op 12 aug, met de
    # drie Q3-returns van die dag erin). 'europe/uefa-conference-league',
    # 'europe/europa-conference-league' en 'europe/conference-league-qualification' geven alle
    # drie de stille faalmodus (HTTP 200, 0 rijen).
    "UEFA Conference League": "https://www.betexplorer.com/football/europe/conference-league/",
    # Bevestigd op 14 aug 2026 (Run A), alle drie 5 rijen in "Next matches":
    "Championship (ENG)": "https://www.betexplorer.com/football/england/championship/",
    "Süper Lig (TUR)": "https://www.betexplorer.com/football/turkey/super-lig/",
    # Dekt ook de kwalificatierondes — nodig zolang soccer_uefa_europa_league bij The Odds API
    # op active=false staat (dat volgt het hoofdtoernooi, niet de voorronde).
    "UEFA Europa League": "https://www.betexplorer.com/football/europe/europa-league/",
    # Toegevoegd 15 aug 2026, toen 1X2 van The Odds API naar deze bron verhuisde om credits te
    # sparen (zie _shared-rules.md §1a). Alle vijf nagetrokken met fetch_league_fixtures; let op
    # dat Spanje 'laliga' is en niet 'primera-division', dat de stille faalmodus geeft.
    "La Liga (ESP)": "https://www.betexplorer.com/football/spain/laliga/",
    "Premier League (ENG)": "https://www.betexplorer.com/football/england/premier-league/",
    "Serie A (ITA)": "https://www.betexplorer.com/football/italy/serie-a/",
    "Bundesliga (GER)": "https://www.betexplorer.com/football/germany/bundesliga/",
    "Ligue 1 (FRA)": "https://www.betexplorer.com/football/france/ligue-1/",
}


if __name__ == "__main__":
    # Zelftest: haalt de Eredivisie op. Let op: "Next matches" toont alleen wedstrijden die nog
    # niet zijn afgetrapt, dus welke specifieke wedstrijden erin zitten hangt af van het moment
    # van draaien — controleer daarom de vorm van de respons, niet één vaste wedstrijd.
    matches = fetch_league_odds(KNOWN_LEAGUE_URLS["Eredivisie (NED)"])
    print(f"'Next matches': {len(matches)} wedstrijden gevonden")
    for m in matches:
        print(f"  {'*' if m.is_today else ' '} {m.home} - {m.away}  {m.odds}")
    assert matches, "geen wedstrijden gevonden — pagina-structuur kan gewijzigd zijn"
    assert all(m.home and m.away and len(m.odds) == 3 for m in matches), "onvolledige rij geparsed"
    assert all(1.0 < o < 100 for m in matches for o in m.odds), "odds buiten plausibel bereik"

    fixtures = fetch_league_fixtures(KNOWN_LEAGUE_URLS["Championship (ENG)"])
    print(f"\n/fixtures/: {len(fixtures)} wedstrijden, waarvan {sum(f.is_today for f in fixtures)} vandaag")
    assert len(fixtures) > len(matches), \
        "de fixtures-pagina hoort méér duels te geven dan 'Next matches' — anders is de reden weg " \
        "waarom fetch_league_fixtures bestaat"
    assert all(f.when for f in fixtures), \
        "lege tijdcel: het doorschuiven van het tijdstip werkt niet meer, en dan verdwijnen op een " \
        "drukke speeldag stilzwijgend de wedstrijden die gelijk beginnen (zie 15 aug 2026)"
    assert all(1.0 < o < 100 for f in fixtures for o in f.odds), "odds buiten plausibel bereik"
    print("Zelftest geslaagd.")
