"""Hoe vaak ging deze markt eerder op? Doelpunten- en BTTS-frequenties per ploeg.

**Waarom deze module bestaat (17 okt 2026, op verzoek van de gebruiker).** De runrapporten
noemden bij een Over/Under- of BTTS-bet wél de doelverwachting van het model en wél de vorm als
`WWDLW`, maar nooit **hoe vaak het werkelijk gebeurde**: in hoeveel van de laatste vijf duels van
deze ploeg vielen er meer dan 2,5 doelpunten, hoe vaak scoorden beide ploegen. De gebruiker:

> *"Wat mij opvalt is dat je nooit in de beschrijving van de bets meeneemt hoevaak een ploeg
> bijvoorbeeld o/u 2,5 of BTS heeft gehad (in de laatste 5 wedstrijden bijvoorbeeld, of over een
> heel seizoen) als je dat tipt. Je zet alleen wedstrijdvorm (WWVDW) volgens mij."*

Dat klopte, en het was ook niet stil wél bekeken: er stond nergens in `scripts/` een telling van
dit soort frequenties. Het model rekent met team-xG en met thuis/uit-doelpuntensplits — dus met
**gemiddelden** — en een gemiddelde zegt niets over de verdeling. Juist die verdeling is de
grootheid waarvan §6g heeft gemeten dat het model haar fout heeft: er staat te weinig massa op 4
en 5 doelpunten, waardoor `P(Under)` bij élk duel ruim twee procentpunt te hoog staat. Een telling
van wat er werkelijk gebeurde is dus geen versiering naast het model maar precies de waarneming
waartegen de zwakste aanname van het model te toetsen is.

**Wat deze module WEL en NIET doet.** Ze **telt** en ze **beschrijft**; ze raakt `my_prob` niet
aan. Een frequentie met een gewicht in de kansschatting stoppen zou een getal verzinnen waarvoor
geen meting bestaat, en dat is wat §2 en §4 verbieden — dezelfde reden dat poort 7 een rem is en
geen bijstelling (§1c). Wat ze wél mag en moet: in de onderbouwing van elke gepubliceerde bet
staan, en naast de modelkans worden gelegd zodat zichtbaar is of de twee hetzelfde zeggen.

**Het kost geen enkel extra verzoek.** `fotmob.fetch_league_stats` haalt
`api/data/leagues?id=..&season=..` op voor de stand en gooit het veld `fixtures.allMatches` weg —
en daar staan alle duels van het seizoen in met `status.scoreStr` en `status.finished`. Deze
module haalt diezelfde URL op met een eigen dagcache, dus één verzoek per competitie-seizoen per
dag, en nul credits (Fotmob rekent niet af per verzoek).

**Twee valkuilen die hier zijn afgedekt.**

1. **Een promovendus staat niet in de stand van vorig seizoen.** Zeventien van de 47 duels van
   17 oktober hadden een omgerekende ploeg (§4), en voor die ploegen levert "vorig seizoen in deze
   divisie" per definitie nul duels op. `team_form` geeft dan `n = 0` en `found = False`, en
   `describe` schrijft dat op in plaats van "0 van 0". Een telling van nul die als een gemeten nul
   leest, is dezelfde stille faalvorm als de `measure_gap`-val van 9 oktober.
2. **De `teamForm`-reeks van Fotmob is níet hetzelfde als de laatste vijf competitieduels.** Die
   reeks (`WWDLW`, wat de runrapporten tot nu toe toonden) bevat ook beker- en Europese duels. Deze
   module telt uitsluitend **competitieduels**, zodat de frequenties op dezelfde populatie staan
   als het model, dat op het competitiegemiddelde is genormaliseerd. Wie de twee naast elkaar legt
   en ze niet gelijk ziet: dat is geen fout maar dit verschil.
3. **Namen worden met `teamnames.norm` gekoppeld en niet met `fotmob._fold`.** Die tweede laat de
   Poolse **ł** staan, want NFKD ontleedt een streepletter niet: "Śląsk Wrocław" vouwt daar naar
   `slaskwrocław` en "Slask Wroclaw" naar `slaskwroclaw`. Dat is dezelfde faalvorm als de
   æ-ligatuur van 13 september, en hij zou hier stil `found = False` hebben opgeleverd voor een
   ploeg die op 17 oktober een gepubliceerde bet is. De zelftest dekt dat geval af.
"""
from __future__ import annotations

import json
import urllib.parse
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from pathlib import Path

from scripts import fotmob, teamnames

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache" / "marketform"

#: De lijnen waarop geteld wordt. 2.5 is de markt waar de gebruiker naar vroeg; 1.5 en 3.5 staan
#: erbij omdat de routine ook op die lijnen publiceert (17 okt: drie van de vijf regels op 3.5).
LINES = (1.5, 2.5, 3.5)

#: Hoeveel recente duels "recent" is. Vijf is wat de gebruiker noemde en wat Fotmob zelf toont.
RECENT = 5


class MarketFormError(RuntimeError):
    pass


# --------------------------------------------------------------------- de bron

def _cache_path(league_id: int, season: str) -> Path:
    veilig = season.replace("/", "-")
    return CACHE_DIR / f"{league_id}-{veilig}.json"


def season_results(league_id: int, season: str, *, use_cache: bool = True) -> list[dict]:
    """Alle AFGELOPEN competitieduels van één seizoen, als platte rijen.

    Eén verzoek per competitie-seizoen per dag; daarna uit de cache. Retourneert rijen
    `{"utc", "home", "away", "hg", "ag", "round"}`, oplopend op aftrap.
    """
    cache_file = _cache_path(league_id, season)
    if use_cache and cache_file.exists():
        cached = json.loads(cache_file.read_text())
        if cached.get("_fetched_on") == date.today().isoformat():
            return cached["results"]

    encoded = urllib.parse.quote(season, safe="")
    raw = fotmob._get_json(
        f"https://www.fotmob.com/api/data/leagues?id={league_id}&season={encoded}")
    alle = (raw.get("fixtures") or {}).get("allMatches") or []

    rijen = []
    for m in alle:
        st = m.get("status") or {}
        if not st.get("finished") or st.get("cancelled") or st.get("awarded"):
            continue
        score = (st.get("scoreStr") or "").replace(" ", "")
        if "-" not in score:
            continue
        try:
            hg, ag = (int(x) for x in score.split("-", 1))
        except ValueError:
            continue
        rijen.append({
            "utc": st.get("utcTime") or "",
            "home": ((m.get("home") or {}).get("name") or "").strip(),
            "away": ((m.get("away") or {}).get("name") or "").strip(),
            "hg": hg, "ag": ag, "round": m.get("round"),
        })
    rijen.sort(key=lambda r: r["utc"])

    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(
            {"_fetched_on": date.today().isoformat(), "_league_id": league_id,
             "_season": season, "results": rijen}, ensure_ascii=False, indent=1))
    return rijen


# --------------------------------------------------------------------- de telling

@dataclass
class MarketForm:
    """De doelpunten- en BTTS-frequenties van één ploeg over één reeks duels."""
    team: str
    season: str
    scope: str                              #: "seizoen" | "laatste 5" | "thuis" | "uit"
    n: int = 0
    found: bool = True                      #: False = deze ploeg speelde niet in deze divisie
    goals_for: int = 0
    goals_against: int = 0
    over: dict = field(default_factory=dict)   #: lijn (als str) -> aantal duels erboven
    btts: int = 0
    clean_sheets: int = 0
    failed_to_score: int = 0
    scores: list = field(default_factory=list)  #: "2-1" per duel, oudste eerst

    @property
    def goals_per_match(self) -> float | None:
        return (self.goals_for + self.goals_against) / self.n if self.n else None

    @property
    def btts_pct(self) -> float | None:
        return 100.0 * self.btts / self.n if self.n else None

    def over_pct(self, line: float) -> float | None:
        return 100.0 * self.over[str(line)] / self.n if self.n else None

    def as_dict(self) -> dict:
        d = asdict(self)
        d["goals_per_match"] = self.goals_per_match
        d["btts_pct"] = self.btts_pct
        return d


def team_form(results: list[dict], team: str, season: str, *, last: int | None = None,
              venue: str | None = None) -> MarketForm:
    """Tel de frequenties van één ploeg uit `season_results`.

    `last` beperkt tot de laatste N duels (oudste eerst gesorteerd, dus de staart);
    `venue` tot "home" of "away". `found=False` als de ploeg in deze reeks niet voorkomt —
    dat is het geval bij een promovendus in de stand van vorig seizoen, en dat moet een
    expliciete uitkomst zijn in plaats van een nul.
    """
    naam = teamnames.norm(team)
    eigen = [r for r in results
             if teamnames.norm(r["home"]) == naam or teamnames.norm(r["away"]) == naam]
    scope = "seizoen" if last is None and venue is None else (
        venue if venue else f"laatste {last}")
    if not eigen:
        return MarketForm(team=team, season=season, scope=scope, n=0, found=False,
                          over={str(l): 0 for l in LINES})

    if venue == "home":
        eigen = [r for r in eigen if teamnames.norm(r["home"]) == naam]
    elif venue == "away":
        eigen = [r for r in eigen if teamnames.norm(r["away"]) == naam]
    if last is not None:
        eigen = eigen[-last:]

    mf = MarketForm(team=team, season=season, scope=scope, n=len(eigen),
                    over={str(l): 0 for l in LINES})
    for r in eigen:
        thuis = teamnames.norm(r["home"]) == naam
        gf, ga = (r["hg"], r["ag"]) if thuis else (r["ag"], r["hg"])
        mf.goals_for += gf
        mf.goals_against += ga
        totaal = r["hg"] + r["ag"]
        for l in LINES:
            if totaal > l:
                mf.over[str(l)] += 1
        if r["hg"] > 0 and r["ag"] > 0:
            mf.btts += 1
        if ga == 0:
            mf.clean_sheets += 1
        if gf == 0:
            mf.failed_to_score += 1
        mf.scores.append(f"{gf}-{ga}")
    return mf


# --------------------------------------------------------------------- de beschrijving

def _tel(aantal: int, n: int) -> str:
    return f"{aantal} van de {n}" + (f" ({100.0 * aantal / n:.0f}%)" if n else "")


def describe(mf: MarketForm, line: float | None = None, *, market: str = "OU") -> str:
    """Eén regel gewone taal over deze reeks, voor het dagrapport (§6c: geen jargon)."""
    if not mf.found:
        return (f"{mf.team}: speelde {mf.season} niet in deze divisie, dus hierover is niets te "
                f"tellen (promovendus of degradant — zie de omrekening van §4).")
    if not mf.n:
        return f"{mf.team}: nog geen afgelopen duels in {mf.season}."
    kern = []
    if market == "BTTS" or line is None:
        kern.append(f"beide ploegen scoorden in {_tel(mf.btts, mf.n)} duels")
    if line is not None:
        kern.append(f"meer dan {line:g} doelpunten in {_tel(mf.over[str(line)], mf.n)} duels")
    kern.append(f"gemiddeld {mf.goals_per_match:.2f} doelpunten per duel")
    return f"{mf.team} ({mf.scope}, {mf.season}): " + "; ".join(kern) + "."


def match_block(league_id: int, season_cur: str, season_prev: str, home: str, away: str,
                *, lines: tuple[float, ...] = LINES) -> dict:
    """Het volledige blok voor één wedstrijd, klaar om in `data/run-state/` te zetten.

    Per ploeg drie reeksen: het lopende seizoen, de laatste `RECENT` duels daarin, en het vorige
    seizoen. Plus de thuis/uit-reeks van de kant waarop de ploeg nu speelt, want dat is de
    splitsing waar het model zelf ook mee rekent (§1d).
    """
    uit: dict = {"league_id": league_id, "season_cur": season_cur, "season_prev": season_prev,
                 "lines": [str(l) for l in lines], "recent": RECENT, "teams": {}}
    cur = season_results(league_id, season_cur)
    prev = season_results(league_id, season_prev)
    uit["n_duels_cur"] = len(cur)
    uit["n_duels_prev"] = len(prev)
    for rol, team, venue in (("home", home, "home"), ("away", away, "away")):
        uit["teams"][rol] = {
            "team": team,
            "lopend": team_form(cur, team, season_cur).as_dict(),
            "lopend_recent": team_form(cur, team, season_cur, last=RECENT).as_dict(),
            "lopend_kant": team_form(cur, team, season_cur, venue=venue).as_dict(),
            "vorig": team_form(prev, team, season_prev).as_dict(),
        }
    return uit


# --------------------------------------------------------------------- zelftest

def _selftest() -> int:
    """Geen netwerk, geen repo: tien gevallen op een verzonnen reeks."""
    R = [
        {"utc": "2026-08-01", "home": "Alfa", "away": "Beta", "hg": 2, "ag": 1},   # 3, btts
        {"utc": "2026-08-08", "home": "Gamma", "away": "Alfa", "hg": 0, "ag": 0},  # 0
        {"utc": "2026-08-15", "home": "Alfa", "away": "Gamma", "hg": 4, "ag": 2},  # 6, btts
        {"utc": "2026-08-22", "home": "Beta", "away": "Alfa", "hg": 1, "ag": 0},   # 1
        {"utc": "2026-08-29", "home": "Alfa", "away": "Beta", "hg": 3, "ag": 0},   # 3
        {"utc": "2026-09-05", "home": "Gamma", "away": "Alfa", "hg": 2, "ag": 2},  # 4, btts
    ]
    fouten = []

    def eis(naam, gekregen, verwacht):
        if gekregen != verwacht:
            fouten.append(f"{naam}: {gekregen!r} != {verwacht!r}")

    a = team_form(R, "Alfa", "2026/2027")
    eis("alfa n", a.n, 6)
    eis("alfa doelpunten voor", a.goals_for, 2 + 0 + 4 + 0 + 3 + 2)
    eis("alfa doelpunten tegen", a.goals_against, 1 + 0 + 2 + 1 + 0 + 2)
    eis("alfa over 2.5", a.over["2.5"], 4)          # 3, 6, 3, 4
    eis("alfa over 3.5", a.over["3.5"], 2)          # 6, 4
    eis("alfa btts", a.btts, 3)
    eis("alfa clean sheets", a.clean_sheets, 2)     # 0-0 en 3-0
    eis("alfa niet gescoord", a.failed_to_score, 2) # 0-0 en 0-1

    # Laatste 3: 1-0 tegen (0-1 voor Alfa), 3-0, 2-2  -> totalen 1, 3, 4
    a3 = team_form(R, "Alfa", "2026/2027", last=3)
    eis("alfa laatste 3 n", a3.n, 3)
    eis("alfa laatste 3 over 2.5", a3.over["2.5"], 2)
    eis("alfa laatste 3 btts", a3.btts, 1)

    # Alleen thuis: 2-1, 4-2, 3-0 -> totalen 3, 6, 3
    ah = team_form(R, "Alfa", "2026/2027", venue="home")
    eis("alfa thuis n", ah.n, 3)
    eis("alfa thuis over 2.5", ah.over["2.5"], 3)
    eis("alfa thuis btts", ah.btts, 2)

    # Een ploeg die er niet in staat is `found=False` en NIET een gemeten nul.
    weg = team_form(R, "Delta", "2025/2026")
    eis("delta found", weg.found, False)
    eis("delta n", weg.n, 0)
    eis("delta btts_pct", weg.btts_pct, None)
    if "speelde 2025/2026 niet in deze divisie" not in describe(weg, 2.5):
        fouten.append("describe() meldt een ontbrekende ploeg niet als zodanig")

    # Accentongevoelig koppelen via `teamnames.norm` en NIET via `fotmob._fold`: die laatste
    # laat de Poolse ł staan (NFKD ontleedt zo'n streepletter niet), dus "Śląsk Wrocław" en
    # "Slask Wroclaw" vouwen daar naar twee verschillende sleutels. Dat is geen theoretisch
    # punt: Śląsk Wrocław is op 17 okt 2026 een gepubliceerde bet, en met `_fold` kwam de
    # telling stil op `found=False` uit — precies de faalvorm van de æ-ligatuur (13 sep).
    R2 = R + [{"utc": "2026-09-12", "home": "Sląsk Wroclaw", "away": "Alfa", "hg": 1, "ag": 1}]
    eis("accent", team_form(R2, "Śląsk Wrocław", "2026/2027").n, 1)

    # Percentages
    eis("alfa over 2.5 pct", round(a.over_pct(2.5), 1), 66.7)
    eis("alfa btts pct", round(a.btts_pct, 1), 50.0)

    for f in fouten:
        print("FOUT:", f)
    print(f"{14 - len(fouten)} van 14 controles goed.")
    return 1 if fouten else 0


if __name__ == "__main__":
    import sys
    if "selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
