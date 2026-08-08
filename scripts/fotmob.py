#!/usr/bin/env python3
"""Fotmob-ophaalcode: fixtures en team-xG, met caching per competitie.

Bevestigd werkend op 8 aug 2026 (README "Nog te doen" #4). Vervangt het handmatig herschrijven
van dezelfde urllib/gzip-aanroepen elke run — dat overtypen was zelf een groot deel van de tijd
die één Run A-diagnose kostte.

    from scripts.fotmob import fetch_fixtures, fetch_league_stats, find_league

Caching: `fetch_league_stats` bewaart het resultaat in `data/cache/fotmob/` en hergebruikt het
als het van vandaag is. Team-xG verandert alleen na een gespeelde wedstrijd, dus binnen één
kalenderdag is een nieuwe download nooit nodig — dat scheelt precies het deel van een run dat
niet met matches maar met COMPETITIES schaalt (zie de toelichting bij MAX_DEEP_ANALYSES in
_shared-rules.md §0).

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import gzip
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache" / "fotmob"
TIMEOUT = 45
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


class FotmobError(RuntimeError):
    pass


def _get_json(url: str) -> dict:
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=TIMEOUT).read()
    except urllib.error.HTTPError as exc:
        raise FotmobError(f"HTTP {exc.code} op {url}") from exc
    except Exception as exc:  # netwerk, DNS, TLS
        raise FotmobError(f"{type(exc).__name__} op {url}: {exc}") from exc
    if raw[:2] == b"\x1f\x8b":  # data.fotmob.com geeft gzip terug, ongeacht Accept-Encoding
        raw = gzip.decompress(raw)
    return json.loads(raw)


def fetch_fixtures(day: date) -> dict:
    """Alle wedstrijden van een dag, gegroepeerd per competitie. Stage 1 van _shared-rules.md."""
    return _get_json(f"https://www.fotmob.com/api/data/matches?date={day:%Y%m%d}")


def find_league(fixtures: dict, name: str, ccode: str, aliases: tuple[str, ...] = ()) -> dict | None:
    """Zoek een competitie terug in het antwoord van `fetch_fixtures` op landcode + naam.

    Fotmob gebruikt niet altijd dezelfde naam als onze runlijst (bv. "Primeira Liga (POR)" heet
    bij Fotmob "Liga Portugal", "League Cup (ENG)" heet er "EFL Cup"). Geef bekende afwijkende
    namen mee via `aliases`. Geen match? Geeft `None` terug — de aanroeper moet dat behandelen
    als "niet gevonden, natrekken", nooit als "geen wedstrijden vandaag".
    """
    candidates = {name.lower(), *(a.lower() for a in aliases)}
    for league in fixtures.get("leagues", []):
        if league.get("ccode") == ccode and str(league.get("name", "")).lower() in candidates:
            return league
    return None


def _cache_path(league_id: int, season: str) -> Path:
    safe_season = season.replace("/", "-")
    return CACHE_DIR / f"{league_id}_{safe_season}.json"


def fetch_league_stats(league_id: int, season: str, *, use_cache: bool = True) -> dict:
    """Team-xG, xG-tegen en stand (met thuis/uit-splits) voor één competitie-seizoen.

    `season` in Fotmob-vorm, bv. "2025/2026". Retourneert:
        {"teams": {naam: {"xg":.., "xga":.., "mp":.., "played":.., "gf":.., "ga":.., "pts":..,
                           "home": {...}, "away": {...}}},
         "home_goals_per_match": .., "away_goals_per_match": .., "avg_xg_per_match": ..,
         "has_xg": bool}

    `has_xg=False` betekent: deze competitie heeft geen xG bij Fotmob (bevestigd voor tweede
    divisies als de Eerste Divisie, Liga Portugal 2 en de Scottish Championship op 8 aug 2026).
    Reken dan niet met deze functie — gebruik hooguit de doelpuntengemiddeldes voor een LIGHT-duiding.
    """
    cache_file = _cache_path(league_id, season)
    if use_cache and cache_file.exists():
        cached = json.loads(cache_file.read_text())
        if cached.get("_fetched_on") == date.today().isoformat():
            return cached

    encoded_season = urllib.parse.quote(season, safe="")
    league = _get_json(f"https://www.fotmob.com/api/data/leagues?id={league_id}&season={encoded_season}")
    stat_groups = {g["name"]: g for g in (league.get("stats", {}).get("teams") or []) if isinstance(g, dict)}

    teams: dict[str, dict] = {}
    has_xg = "expected_goals_team" in stat_groups and "expected_goals_conceded_team" in stat_groups
    if has_xg:
        for key, label in (("expected_goals_team", "xg"), ("expected_goals_conceded_team", "xga")):
            data = _get_json(stat_groups[key]["fetchAllUrl"])
            for row in data["TopLists"][0]["StatList"]:
                team = teams.setdefault(row["ParticipantName"], {})
                team[label] = row["StatValue"]
                team["mp"] = row["MatchesPlayed"]

    table = _pick_table(league.get("table", []))
    if table is None:
        raise FotmobError(f"geen bruikbare stand gevonden voor league_id={league_id}, season={season}")

    home_goals = away_goals = home_played = away_played = 0
    for side, key in (("home", "home"), ("away", "away")):
        for row in table[side]:
            gf, ga = (int(x) for x in row["scoresStr"].split("-"))
            teams.setdefault(row["name"], {})[side] = {"played": row["played"], "gf": gf, "ga": ga}
            if side == "home":
                home_goals += gf
                home_played += row["played"]
            else:
                away_goals += gf
                away_played += row["played"]
    for row in table["all"]:
        gf, ga = (int(x) for x in row["scoresStr"].split("-"))
        teams.setdefault(row["name"], {}).update(gf=gf, ga=ga, played=row["played"], pts=row["pts"])

    with_xg = {n: t for n, t in teams.items() if "xg" in t}
    result = {
        "teams": teams,
        "home_goals_per_match": home_goals / home_played if home_played else None,
        "away_goals_per_match": away_goals / away_played if away_played else None,
        "avg_xg_per_match": (sum(t["xg"] for t in with_xg.values()) / sum(t["mp"] for t in with_xg.values())
                              if with_xg else None),
        "has_xg": has_xg,
        "_fetched_on": date.today().isoformat(),
        "_league_id": league_id,
        "_season": season,
    }
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    return result


def _pick_table(table_field: list) -> dict | None:
    """Fotmob geeft `table: [{"data": {"table": {...}}}]` voor een gewone competitie, maar
    `table: [{"data": {"tables": [...meerdere groepen...]}}]` zodra er play-offs of
    degradatiegroepen zijn (bv. Belgian Pro League, Scottish Premiership). Pak dan de grootste
    groep — dat is de hoofdcompetitie, niet de na-seizoen-subgroep."""
    if not table_field:
        return None
    data = table_field[0]["data"]
    if "table" in data:
        return data["table"]
    groups = [t["table"] for t in data.get("tables", []) if isinstance(t.get("table"), dict) and "all" in t["table"]]
    if not groups:
        return None
    return max(groups, key=lambda t: len(t["all"]))


if __name__ == "__main__":
    # Zelftest: reproduceert de xG-cijfers van Standard Luik en Cercle Brugge uit
    # runs/2026-08-08-run-a-2.md (Belgian Pro League, id=40, seizoen 2025/2026).
    stats = fetch_league_stats(40, "2025/2026", use_cache=False)
    standard, cercle = stats["teams"]["Standard Liege"], stats["teams"]["Cercle Brugge"]
    print(f"Standard: xG/duel {standard['xg'] / standard['mp']:.2f}  xGA/duel {standard['xga'] / standard['mp']:.2f}")
    print(f"Cercle:   xG/duel {cercle['xg'] / cercle['mp']:.2f}  xGA/duel {cercle['xga'] / cercle['mp']:.2f}")
    assert abs(standard["xg"] / standard["mp"] - 1.20) < 0.01
    assert abs(cercle["xg"] / cercle["mp"] - 1.66) < 0.01
    print(f"Competitiebasis: thuis {stats['home_goals_per_match']:.3f}  "
          f"uit {stats['away_goals_per_match']:.3f}  gem. xG {stats['avg_xg_per_match']:.3f}")
    print("Zelftest geslaagd.")
