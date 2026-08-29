#!/usr/bin/env python3
"""Selectieverloop: hoeveel van de ploeg die vorig seizoen die cijfers maakte, staat er nog?

**Waarom dit bestaat (29 aug 2026, op aanwijzing van de gebruiker).** De routine rekende
teamsterktes uit het *vorige* seizoen en rangschikte de wedstrijden voor `MAX_DEEP_ANALYSES`
op één proxy: het aantal speeldagen dat de *competitie* dit seizoen al gespeeld had. Die
tie-break gooide op 29 aug de hele Bundesliga uit de run — vier volwaardige duels — terwijl hij
inhoudelijk vrijwel niets meet: de teamsterktes komen bij álle competities uit 2025/2026, en het
aantal speeldagen van dit seizoen verandert daar niets aan.

Wat er wél toe doet bij de vraag "hoe goed beschrijft vorig seizoen deze ploeg vandaag?" is
of het nog dezelfde ploeg ís. Fotmob geeft dat gratis: per club een transferlijst met
marktwaarde per speler. Deze module maakt daar één getal van.

    from scripts.squad import turnover
    t = turnover(team_id, since="2026-06-01")
    t.share        # marktwaarde in+uit als aandeel van de basisopstelling
    t.summary()

**Marktwaarde en niet transfersom.** Een huurling kost niets en verandert de ploeg net zo goed;
`amountEuroEstimated` is bij de helft van de regels `null`, `marketValue` vrijwel nooit. Het is
een grove maat — dat is het bij `context.py` ook — maar hij onderscheidt een eerste elftalspeler
van een weggestuurde derde keeper, en dat is precies het onderscheid dat telt.

Alleen de standaardbibliotheek. Caching per dag in `data/cache/fotmob/`, net als fotmob.py.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache" / "fotmob"
TIMEOUT = 45
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "application/json",
}

#: Vanaf wanneer een transfer meetelt voor "dit is een andere ploeg dan vorig seizoen".
#: 1 juni is het begin van de zomermarkt in vrijwel elke competitie op de twee runlijsten.
DEFAULT_WINDOW_START = "2026-06-01"


class SquadError(RuntimeError):
    pass


def _get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise SquadError(f"HTTP {exc.code} op {url}") from exc


def _cache_path(team_id: int) -> Path:
    return CACHE_DIR / f"transfers-{team_id}.json"


def fetch_team(team_id: int, *, use_cache: bool = True) -> dict:
    """De ruwe transferlijsten van één club, gecached per dag."""
    cache_file = _cache_path(team_id)
    if use_cache and cache_file.exists():
        cached = json.loads(cache_file.read_text())
        if cached.get("_fetched_on") == date.today().isoformat():
            return cached

    data = _get_json(f"https://www.fotmob.com/api/data/teams?id={team_id}")
    blocks = ((data.get("transfers") or {}).get("data") or {})
    result = {
        "in": blocks.get("Players in") or [],
        "out": blocks.get("Players out") or [],
        "_fetched_on": date.today().isoformat(),
        "_team_id": team_id,
    }
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(result, ensure_ascii=False))
    return result


@dataclass
class Turnover:
    """Hoeveel selectiewaarde er sinds de vensteropening is in- en uitgegaan."""
    team_id: int
    n_in: int = 0
    n_out: int = 0
    value_in: float = 0.0
    value_out: float = 0.0
    squad_value: float = 0.0
    names_in: list[str] = field(default_factory=list)
    names_out: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def share(self) -> float | None:
        """(waarde in + waarde uit) / waarde van de basisopstelling.

        `None` als de basiswaarde onbekend is — een ontbrekende meting is geen nul.
        """
        if not self.squad_value:
            return None
        return (self.value_in + self.value_out) / self.squad_value

    def summary(self) -> str:
        if self.error:
            return f"selectieverloop niet gemeten ({self.error})"
        share = self.share
        deel = f"{share * 100:.0f}% van de basiswaarde" if share is not None else "aandeel onbekend"
        return f"{self.n_in} in / {self.n_out} uit sinds {DEFAULT_WINDOW_START}, {deel}"


def _value(row: dict) -> float:
    for key in ("marketValue", "amountEuroEstimated"):
        v = row.get(key)
        if isinstance(v, (int, float)) and v > 0:
            return float(v)
    return 0.0


def _after(row: dict, since: str) -> bool:
    stamp = row.get("transferDate") or row.get("fromDate") or ""
    return stamp[:10] >= since


def turnover(team_id: int, squad_value: float = 0.0, since: str = DEFAULT_WINDOW_START) -> Turnover:
    """Het selectieverloop van één club sinds `since`.

    `squad_value` is `totalStarterMarketValue` uit `context.fetch_match_context` — geef hem mee,
    anders blijft `share` op None en telt deze ploeg in de rangschikking als "niet gemeten"
    (en dus niet als "geen verloop", want dat zou een aanname zijn).
    """
    result = Turnover(team_id=team_id, squad_value=squad_value)
    try:
        raw = fetch_team(team_id)
    except Exception as exc:                      # bron weg = meting weg, geen run die klapt
        result.error = f"{type(exc).__name__}: {exc}"
        return result

    for row in raw["in"]:
        if row.get("contractExtension") or not _after(row, since):
            continue
        result.n_in += 1
        result.value_in += _value(row)
        result.names_in.append(row.get("name") or "?")
    for row in raw["out"]:
        if row.get("contractExtension") or not _after(row, since):
            continue
        result.n_out += 1
        result.value_out += _value(row)
        result.names_out.append(row.get("name") or "?")
    return result


if __name__ == "__main__":
    # Zelftest op Tottenham (Fotmob team-id 8586): de zomer van 2026 moet transfers laten zien.
    t = turnover(8586, squad_value=312035786)
    print(t.summary())
    print(f"  in : {', '.join(t.names_in[:6])}")
    print(f"  uit: {', '.join(t.names_out[:6])}")
    assert t.n_in or t.n_out, "geen enkele transfer gevonden — respons kan gewijzigd zijn"
    print("Zelftest geslaagd.")
