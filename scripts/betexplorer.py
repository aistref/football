#!/usr/bin/env python3
"""BetExplorer-ophaalcode: gratis 1X2-odds, server-side in de HTML.

Stond tot 8 aug 2026 als `js_only` in data/source-health.json — dat was gemeten op de
wedstrijdpagina, die inderdaad leeg is. De "Next matches"-tabel op een competitiepagina levert
1X2 wél server-side, in `data-odd` (gemiddelde) en `data-odd-max` (beste prijs). Alleen 1X2 —
de ou/bts/ah-ajax-endpoints gaven 404 bij het natrekken.

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
}


if __name__ == "__main__":
    # Zelftest: haalt de Eredivisie op. Let op: "Next matches" toont alleen wedstrijden die nog
    # niet zijn afgetrapt, dus welke specifieke wedstrijden erin zitten hangt af van het moment
    # van draaien — controleer daarom de vorm van de respons, niet één vaste wedstrijd.
    matches = fetch_league_odds(KNOWN_LEAGUE_URLS["Eredivisie (NED)"])
    print(f"{len(matches)} wedstrijden gevonden")
    for m in matches:
        print(f"  {'*' if m.is_today else ' '} {m.home} - {m.away}  {m.odds}")
    assert matches, "geen wedstrijden gevonden — pagina-structuur kan gewijzigd zijn"
    assert all(m.home and m.away and len(m.odds) == 3 for m in matches), "onvolledige rij geparsed"
    assert all(1.0 < o < 100 for m in matches for o in m.odds), "odds buiten plausibel bereik"
    print("Zelftest geslaagd.")
