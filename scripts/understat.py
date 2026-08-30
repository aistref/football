#!/usr/bin/env python3
"""Understat: team-xG per wedstrijd, gratis en zonder sleutel — de tweede kansbron.

Bestaansreden (31 aug 2026). Tot vandaag kwam **alle** onafhankelijke kansinput van Fotmob: xG,
opstellingen, blessures, vorm, rust en transfers. Dat werkt al weken foutloos, maar het is één
onofficiële bron zonder contract. Valt hij om, dan heeft de routine geen enkele kansinput meer,
faalt de anti-circulariteitsregel (§2) voor élke wedstrijd en levert elke run nul bets tot iemand
ingrijpt. Understat neemt dat risico weg voor de vijf competities waar het meeste geld omgaat.

**De bron is veranderd en de oude aanpak werkt niet meer.** `data/coverage.json` noemt nog
`https://understat.com/league/{code}/{season}` met de data als `var teamsData = JSON.parse('...')`
in de HTML. Op 31 aug 2026 nagetrokken: die pagina is nog maar 18 kB en bevat geen enkele
`JSON.parse` meer — de data komt nu client-side binnen. Zo'n pagina is voor een fetch-only tool
onbruikbaar (vergelijk `js_only` bij oddsportal en flashscore in `source-health.json`).

Wat wél werkt is het endpoint dat de pagina zelf aanroept, te vinden in `js/league.min.js`:

    GET https://understat.com/getLeagueData/{code}/{season}      # gzip, ~95 kB, JSON

Dat is geen omzeiling van een blokkade — er is geen blokkade. Het is hetzelfde verzoek dat de
pagina in de browser doet, met dezelfde headers. Understat zet geen Cloudflare-challenge en geen
robots-verbod op dit pad; vergelijk §3 van `_shared-rules.md`, dat het omzeilen van sites die zich
bewust afsluiten verbiedt. Hier sluit niets zich af.

Wat het oplevert, en waarom het meer is dan een kopie van Fotmob:

- **xG en xGA per wedstrijd**, niet als seizoenstotaal. Daarmee zijn thuis/uit-splits op xG te
  maken (Fotmob geeft splits alleen op doelpunten) en is een rollende vorm over de laatste 5-8
  duels te berekenen — de categorie-1-input die §4 noemt en die tot nu toe nergens vandaan kwam.
- **npxG**, dus zonder strafschoppen.
- Een **tweede, onafhankelijke meting** van dezelfde grootheid. Waar Fotmob en Understat over
  dezelfde ploeg hetzelfde zeggen, hangt een bet niet aan één leverancier.

Dekking: vijf competities uit de Run A-runlijst. Understat heeft geen tweede divisies, dus voor
promovendi blijft `scripts/promotion.py` op Fotmob leunen.

    python3 scripts/understat.py        # zelftest tegen echte, actuele data

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import gzip
import json
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

TIMEOUT = 35
BASE = "https://understat.com/getLeagueData"
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache" / "understat"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"),
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip",
}

#: Competitie uit de runlijst -> de code die Understat gebruikt. Alle vijf op 31 aug 2026
#: nagetrokken: 20, 20, 20, 18 en 18 ploegen, elk 34 of 38 duels per ploeg.
LEAGUES: dict[str, str] = {
    "Premier League (ENG)": "EPL",
    "La Liga (ESP)": "La_liga",
    "Bundesliga (GER)": "Bundesliga",
    "Serie A (ITA)": "Serie_A",
    "Ligue 1 (FRA)": "Ligue_1",
}

#: Understat noemt het seizoen naar het startjaar: "2025" is 2025/2026.
def season_code(fotmob_season: str) -> str:
    """"2025/2026" -> "2025"."""
    return fotmob_season.split("/")[0]


class UnderstatError(RuntimeError):
    pass


def _cache_path(code: str, season: str) -> Path:
    return CACHE_DIR / f"{code}_{season}.json"


def fetch_league(code: str, season: str, *, use_cache: bool = True) -> dict:
    """Ruwe respons van het league-endpoint: `{"teams": ..., "players": ..., "dates": ...}`."""
    cache_file = _cache_path(code, season)
    if use_cache and cache_file.exists():
        cached = json.loads(cache_file.read_text())
        if cached.get("_fetched_on") == date.today().isoformat():
            return cached
    url = f"{BASE}/{code}/{season}"
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS),
                                     timeout=TIMEOUT).read()
    except urllib.error.HTTPError as exc:
        raise UnderstatError(f"HTTP {exc.code} op {url}") from exc
    except Exception as exc:
        raise UnderstatError(f"{type(exc).__name__} op {url}: {exc}") from exc
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UnderstatError(f"geen JSON terug van {url} ({len(raw)} bytes)") from exc
    if not isinstance(data, dict) or "teams" not in data:
        raise UnderstatError(f"onverwachte vorm van {url}: {list(data)[:5]}")
    data["_fetched_on"] = date.today().isoformat()
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(data, ensure_ascii=False))
    return data


def team_stats(data: dict) -> dict:
    """Zet de respons om naar dezelfde vorm als `fotmob.fetch_league_stats()["teams"]`.

    Per ploeg: `xg`, `xga`, `npxg`, `mp`, `gf`, `ga`, `played`, en `home`/`away` met dezelfde
    velden plus xG — dat laatste heeft Fotmob niet, want daar zijn de splits alleen op doelpunten.
    """
    out: dict[str, dict] = {}
    for team in data["teams"].values():
        rows = team.get("history") or []
        rec = {"xg": 0.0, "xga": 0.0, "npxg": 0.0, "mp": 0, "gf": 0, "ga": 0, "played": 0,
               "home": {"xg": 0.0, "xga": 0.0, "gf": 0, "ga": 0, "played": 0},
               "away": {"xg": 0.0, "xga": 0.0, "gf": 0, "ga": 0, "played": 0}}
        for r in rows:
            side = "home" if r.get("h_a") == "h" else "away"
            xg, xga = float(r.get("xG", 0) or 0), float(r.get("xGA", 0) or 0)
            gf, ga = int(r.get("scored", 0) or 0), int(r.get("missed", 0) or 0)
            rec["xg"] += xg
            rec["xga"] += xga
            rec["npxg"] += float(r.get("npxG", 0) or 0)
            rec["gf"] += gf
            rec["ga"] += ga
            rec["mp"] += 1
            rec["played"] += 1
            s = rec[side]
            s["xg"] += xg
            s["xga"] += xga
            s["gf"] += gf
            s["ga"] += ga
            s["played"] += 1
        out[team["title"]] = rec
    return out


def league_context(teams: dict) -> dict:
    """Competitiebasis uit deze standen: dezelfde drie getallen die `model.LeagueContext` wil."""
    hg = sum(t["home"]["gf"] for t in teams.values())
    hp = sum(t["home"]["played"] for t in teams.values())
    ag = sum(t["away"]["gf"] for t in teams.values())
    ap = sum(t["away"]["played"] for t in teams.values())
    mp = sum(t["mp"] for t in teams.values())
    xg = sum(t["xg"] for t in teams.values())
    return {"home_goals_per_match": hg / hp if hp else None,
            "away_goals_per_match": ag / ap if ap else None,
            "avg_xg_per_match": xg / mp if mp else None}


def rolling_xg(data: dict, team_title: str, last: int = 8) -> tuple[float, float, int] | None:
    """(xG, xGA) per duel over de laatste `last` wedstrijden, en hoeveel duels dat waren.

    Dit is de "rolling xG-trend (laatste 5-8)" uit §4 van `_shared-rules.md`. Die stond daar vanaf
    het begin als categorie-1-input, maar er was geen bron voor: Fotmob geeft alleen seizoenstotalen.
    """
    for team in data["teams"].values():
        if team["title"] != team_title:
            continue
        rows = sorted(team.get("history") or [], key=lambda r: r.get("date", ""))[-last:]
        if not rows:
            return None
        n = len(rows)
        return (sum(float(r.get("xG", 0) or 0) for r in rows) / n,
                sum(float(r.get("xGA", 0) or 0) for r in rows) / n, n)
    return None


def _selftest() -> int:
    """Haalt alle vijf competities op en legt ze naast Fotmob."""
    try:
        from scripts import fotmob
    except ImportError:
        fotmob = None
    FOTMOB_ID = {"Premier League (ENG)": 47, "La Liga (ESP)": 87, "Bundesliga (GER)": 54,
                 "Serie A (ITA)": 55, "Ligue 1 (FRA)": 53}
    fouten = 0
    for comp, code in LEAGUES.items():
        try:
            data = fetch_league(code, "2025")
            teams = team_stats(data)
            ctx = league_context(teams)
        except UnderstatError as exc:
            print(f"{comp:24} FOUT: {exc}")
            fouten += 1
            continue
        print(f"\n{comp:24} {len(teams)} ploegen · {ctx['avg_xg_per_match']:.3f} xG/duel "
              f"· thuis {ctx['home_goals_per_match']:.3f} uit {ctx['away_goals_per_match']:.3f}")
        if fotmob is None:
            continue
        fm = fotmob.fetch_league_stats(FOTMOB_ID[comp], "2025/2026")
        print(f"{'':24} Fotmob: {fm['avg_xg_per_match']:.3f} xG/duel "
              f"· thuis {fm['home_goals_per_match']:.3f} uit {fm['away_goals_per_match']:.3f}")
        # per ploeg vergelijken op naam die in beide voorkomt
        paren = [(n, teams[n]["xg"] / teams[n]["mp"], fm["teams"][n]["xg"] / fm["teams"][n]["mp"])
                 for n in teams if n in fm["teams"] and fm["teams"][n].get("mp")]
        if paren:
            diffs = [abs(a - b) for _, a, b in paren]
            grootste = max(paren, key=lambda p: abs(p[1] - p[2]))
            print(f"{'':24} {len(paren)} ploegen op naam gematcht · gem. verschil in xG/duel "
                  f"{sum(diffs) / len(diffs):.3f} · grootste: {grootste[0]} "
                  f"{grootste[1]:.2f} vs {grootste[2]:.2f}")
        else:
            print(f"{'':24} geen enkele ploegnaam gematcht — namen verschillen per bron")
    print(f"\n{'ALLES OK' if not fouten else str(fouten) + ' PROBLEEM(EN)'}")
    return 1 if fouten else 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
