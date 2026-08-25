#!/usr/bin/env python3
"""football-data.co.uk: uitslagen en schoten over meerdere divisies, zonder sleutel.

Bestaansreden (21 aug 2026). Op die dag vielen **vijf van de veertien** wedstrijden van Run B af op
`data_tier = NONE`, geen van alle op de analyse: Rudes, LR Vicenza, Girona, FC Volendam en
Skenderbeu speelden vorig seizoen in een andere divisie, en Fotmob geeft per competitie alleen de
stand van díe competitie. Een promovendus staat dus nergens in de tabel waaruit het model zijn
teamsterkte haalt, en dan is er geen onafhankelijke kansinput meer (§2) en geen bet.

Dat is geen incidentele pech maar het seizoensmoment: eind augustus is elke Europese competitie net
begonnen met een verse lichting promovendi en degradanten, terwijl er van het lopende seizoen nog te
weinig gespeeld is om op te rekenen.

Deze bron lost dat niet in één klap op — ook hier staat Girona in SP1 en niet in SP2 (nagetrokken op
21 aug 2026). Wat hij wél geeft, en Fotmob niet, is **beide divisies in één consistent formaat over
vijftien seizoenen**. Daarmee is te meten hoeveel een divisie werkelijk scheelt, en kan de sterkte
van een promovendus uit de divisie eronder worden omgerekend naar de divisie erboven. Zie
`division_gap()` en `convert_strength()`.

    python3 scripts/footballdata.py              # zelftest tegen echte, actuele data

Wat de bron levert:

- **Hoofdbestanden** `mmz4281/{seizoen}/{div}.csv` — uitslagen **plus schoten en schoten op doel**
  (`HS`, `AS`, `HST`, `AST`). Schoten en SOT zijn een categorie-1-input onder `_shared-rules.md` §4,
  dus dit is meer dan alleen doelpunten.
- **Extra bestanden** `new/{land}.csv` — uitslagen zonder schoten, maar wél voor competities die de
  hoofdbestanden niet hebben (Zweden, Noorwegen, Oostenrijk, Zwitserland, Roemenië, Denemarken,
  Polen, Finland, Ierland), t/m het lopende seizoen.

**LET OP — anti-circulariteit (§2).** Beide bestandssoorten bevatten óók bookmakerkoersen (`B365H`,
`PSH`, `AvgH`, …). Uitslagen en schoten mogen als onafhankelijke kansinput dienen, die koersen
**niet**. Dit script gooit de oddskolommen daarom bij het inlezen weg, zodat ze niet per ongeluk in
een `prob_sources` belanden.

**LET OP — de stille faalmodus.** Een bestand dat nog niet bestaat geeft **HTTP 300 Multiple
Choices**, niet 404: de server draait `mod_speling` en biedt gelijkende namen aan. Gemeten op
21 aug 2026 gaven `I1`, `I2` en `G1` voor seizoen 2627 alle drie een 300, terwijl `SP2`, `E2`, `E3`,
`D2` en `N1` gewoon 200 gaven — Serie A/B en Griekenland waren simpelweg nog niet gepubliceerd.
`fetch_division` vertaalt die 300 daarom naar `NotPublished`, een aparte fout die de aanroeper kan
opvangen als "nog niet beschikbaar" in plaats van als storing.

Alleen de standaardbibliotheek — deze repo heeft geen installatiestap.
"""

from __future__ import annotations

import csv
import io
import json
import re
import statistics
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache" / "footballdata"
BASE = "https://www.football-data.co.uk"
TIMEOUT = 45
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


class FootballDataError(RuntimeError):
    pass


class NotPublished(FootballDataError):
    """Het bestand bestaat (nog) niet — de server gaf HTTP 300 met gelijkende namen.

    Dit is een normale toestand aan het begin van een seizoen, geen storing. Behandel hem als
    "deze competitie heeft nog geen bestand", niet als een omgevallen bron.
    """


# --------------------------------------------------------------------------- divisies
#
# `tier` maakt het verschil tussen de divisies van hetzelfde land expliciet: 1 is de hoogste.
# `division_gap()` gebruikt precies dat om aangrenzende divisies te koppelen.

@dataclass(frozen=True)
class Division:
    slug: str
    country: str
    tier: int
    name: str


MAIN_DIVISIONS: dict[str, Division] = {d.slug: d for d in [
    Division("E0", "England", 1, "Premier League (ENG)"),
    Division("E1", "England", 2, "Championship (ENG)"),
    Division("E2", "England", 3, "English League One (ENG)"),
    Division("E3", "England", 4, "English League Two (ENG)"),
    Division("SP1", "Spain", 1, "La Liga (ESP)"),
    Division("SP2", "Spain", 2, "Segunda División (ESP)"),
    Division("D1", "Germany", 1, "Bundesliga (GER)"),
    Division("D2", "Germany", 2, "2. Bundesliga (GER)"),
    Division("I1", "Italy", 1, "Serie A (ITA)"),
    Division("I2", "Italy", 2, "Serie B (ITA)"),
    Division("F1", "France", 1, "Ligue 1 (FRA)"),
    Division("F2", "France", 2, "Ligue 2 (FRA)"),
    Division("SC0", "Scotland", 1, "Scottish Premiership (SCO)"),
    Division("SC1", "Scotland", 2, "Scottish Championship (SCO)"),
    Division("N1", "Netherlands", 1, "Eredivisie (NED)"),
    Division("B1", "Belgium", 1, "Belgian Pro League (BEL)"),
    Division("P1", "Portugal", 1, "Liga Portugal (POR)"),
    Division("T1", "Turkey", 1, "Süper Lig (TUR)"),
    Division("G1", "Greece", 1, "Greek Super League (GRE)"),
]}

#: `new/{bestand}.csv` — competities buiten de hoofdbestanden. Waarde is de landcode in het bestand.
EXTRA_FILES: dict[str, str] = {
    "SWE": "Sweden", "NOR": "Norway", "AUT": "Austria", "SWZ": "Switzerland",
    "DNK": "Denmark", "POL": "Poland", "ROU": "Romania", "FIN": "Finland",
    "IRL": "Ireland", "RUS": "Russia", "MEX": "Mexico", "USA": "USA",
    "JPN": "Japan", "BRA": "Brazil", "CHN": "China", "ARG": "Argentina",
}

#: Competitienaam uit de runlijsten -> waar hij hier vandaan komt.
#: `("main", slug)` of `("extra", bestand, competitienaam-in-het-bestand)`.
KNOWN_COMPETITIONS: dict[str, tuple] = {
    "Premier League (ENG)": ("main", "E0"),
    "Championship (ENG)": ("main", "E1"),
    "English League One (ENG)": ("main", "E2"),
    "English League Two (ENG)": ("main", "E3"),
    "La Liga (ESP)": ("main", "SP1"),
    "Segunda División (ESP)": ("main", "SP2"),
    "Bundesliga (GER)": ("main", "D1"),
    "2. Bundesliga (GER)": ("main", "D2"),
    "Serie A (ITA)": ("main", "I1"),
    "Serie B (ITA)": ("main", "I2"),
    "Ligue 1 (FRA)": ("main", "F1"),
    "Eredivisie (NED)": ("main", "N1"),
    "Belgian Pro League (BEL)": ("main", "B1"),
    "Liga Portugal (POR)": ("main", "P1"),
    "Süper Lig (TUR)": ("main", "T1"),
    "Greek Super League (GRE)": ("main", "G1"),
    "Scottish Premiership (SCO)": ("main", "SC0"),
    "Allsvenskan (SWE)": ("extra", "SWE", "Allsvenskan"),
    "Eliteserien (NOR)": ("extra", "NOR", "Eliteserien"),
    "Austrian Bundesliga (AUT)": ("extra", "AUT", "Bundesliga"),
    "Swiss Super League (SUI)": ("extra", "SWZ", "Super League"),
    "Danish Superliga (DEN)": ("extra", "DNK", "Superliga"),
    "Ekstraklasa (POL)": ("extra", "POL", "Ekstraklasa"),
    "Romanian SuperLiga (ROU)": ("extra", "ROU", "Superliga"),
}

#: Competities uit de twee runlijsten die deze bron NIET heeft. Expliciet, zodat een run niet
#: elke keer opnieuw gaat zoeken. Nagetrokken 21 aug 2026.
NOT_COVERED = (
    "Czech First League (CZE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
    "Keuken Kampioen Divisie (NED)", "Kategoria Superiore (ALB)", "Kosovo Superleague (KOS)",
)

_ODDS_COL = re.compile(
    r"^(B365|BF|BFD|BFE|BFEC|BMGM|BV|BW|CL|GB|IW|LB|PS|PSC|SB|SJ|SO|SY|VC|WH|Max|Avg|P)"
    r"(C?)(H|D|A|>2\.5|<2\.5|AHH|AHA)?", re.I)


def _is_odds_column(name: str) -> bool:
    """Koerskolommen eruit filteren — zie de anti-circulariteitswaarschuwing bovenaan."""
    keep = {"HomeTeam", "AwayTeam", "Home", "Away", "Date", "Time", "Div", "Country",
            "League", "Season", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
            "HG", "AG", "Res", "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC",
            "HY", "AY", "HR", "AR", "Attendance", "Referee"}
    if name in keep:
        return False
    return bool(_ODDS_COL.match(name)) or "AH" in name or name.startswith(("MaxC", "AvgC"))


@dataclass
class Match:
    """Eén wedstrijd. `shots`/`sot` zijn None in de extra bestanden — die hebben ze niet."""
    date: str
    home: str
    away: str
    hg: int
    ag: int
    competition: str
    season: str
    shots: tuple[int, int] | None = None
    sot: tuple[int, int] | None = None


def _get(url: str, *, cache_key: str, permanent: bool) -> str:
    """Haal een CSV op, met cache. Afgelopen seizoenen veranderen nooit meer en worden daarom
    **permanent** gecached; het lopende seizoen krijgt hetzelfde dagelijkse regime als Fotmob."""
    path = CACHE_DIR / f"{cache_key}.json"
    if path.exists():
        blob = json.loads(path.read_text())
        if permanent or blob.get("_fetched_on") == date.today().isoformat():
            return blob["text"]
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=TIMEOUT).read()
    except urllib.error.HTTPError as exc:
        if exc.code == 300:
            raise NotPublished(f"{url} bestaat nog niet (HTTP 300, mod_speling)") from exc
        raise FootballDataError(f"HTTP {exc.code} op {url}") from exc
    except Exception as exc:
        raise FootballDataError(f"{type(exc).__name__} op {url}: {exc}") from exc
    text = raw.decode("utf-8-sig", "replace")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"text": text, "_fetched_on": date.today().isoformat()}))
    return text


def season_code(start_year: int) -> str:
    """2025 -> '2526'. De bestandsnaam gebruikt de twee jaartallen zonder eeuw."""
    return f"{start_year % 100:02d}{(start_year + 1) % 100:02d}"


def fetch_division(slug: str, start_year: int, *, permanent: bool | None = None) -> list[Match]:
    """Alle wedstrijden van één divisie in één seizoen uit de hoofdbestanden.

    `start_year` is het kalenderjaar waarin het seizoen begint (2025 = 2025/2026). Werpt
    `NotPublished` als het bestand er nog niet is — dat is aan het begin van een seizoen normaal.
    """
    if slug not in MAIN_DIVISIONS:
        raise FootballDataError(f"onbekende divisie {slug!r}; bekend: {sorted(MAIN_DIVISIONS)}")
    code = season_code(start_year)
    if permanent is None:
        permanent = start_year < date.today().year - (0 if date.today().month >= 7 else 1)
    text = _get(f"{BASE}/mmz4281/{code}/{slug}.csv", cache_key=f"{slug}_{code}", permanent=permanent)
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        if not row.get("HomeTeam") or row.get("FTHG") in (None, ""):
            continue
        def num(k):
            v = row.get(k, "")
            try:
                return int(float(v))
            except (TypeError, ValueError):
                return None
        hs, aws, hst, ast = num("HS"), num("AS"), num("HST"), num("AST")
        out.append(Match(
            date=row.get("Date", ""), home=row["HomeTeam"].strip(), away=row["AwayTeam"].strip(),
            hg=num("FTHG"), ag=num("FTAG"),
            competition=MAIN_DIVISIONS[slug].name, season=code,
            shots=(hs, aws) if hs is not None and aws is not None else None,
            sot=(hst, ast) if hst is not None and ast is not None else None))
    return out


def fetch_extra(file_key: str, league: str | None = None,
                season: str | None = None) -> list[Match]:
    """Wedstrijden uit `new/{file_key}.csv`, optioneel gefilterd op competitie en seizoen.

    Deze bestanden bevatten **alle seizoenen tegelijk** (sinds 2012) en worden bij elke
    speelronde bijgewerkt, dus ze staan altijd op het dagelijkse cacheregime.
    """
    if file_key not in EXTRA_FILES:
        raise FootballDataError(f"onbekend extra bestand {file_key!r}; bekend: {sorted(EXTRA_FILES)}")
    text = _get(f"{BASE}/new/{file_key}.csv", cache_key=f"extra_{file_key}", permanent=False)
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        if not row.get("Home") or row.get("HG") in (None, ""):
            continue
        if league and row.get("League", "").strip() != league:
            continue
        if season and row.get("Season", "").strip() != season:
            continue
        try:
            hg, ag = int(float(row["HG"])), int(float(row["AG"]))
        except (TypeError, ValueError):
            continue
        out.append(Match(date=row.get("Date", ""), home=row["Home"].strip(),
                         away=row["Away"].strip(), hg=hg, ag=ag,
                         competition=f"{row.get('Country','').strip()} {row.get('League','').strip()}".strip(),
                         season=row.get("Season", "").strip()))
    return out


# --------------------------------------------------------------------------- standen

@dataclass
class TeamSeason:
    """Wat één ploeg in één divisie-seizoen deed. Alles per wedstrijd, zodat halve seizoenen
    en competities met een ander aantal speeldagen vergelijkbaar blijven."""
    team: str
    played: int = 0
    gf: int = 0
    ga: int = 0
    home_gf: int = 0
    home_ga: int = 0
    home_played: int = 0
    away_gf: int = 0
    away_ga: int = 0
    away_played: int = 0
    shots_for: int = 0
    shots_against: int = 0
    sot_for: int = 0
    sot_against: int = 0
    shot_matches: int = 0

    @property
    def gf_per_match(self) -> float:
        return self.gf / self.played if self.played else 0.0

    @property
    def ga_per_match(self) -> float:
        return self.ga / self.played if self.played else 0.0


def season_table(matches: list[Match]) -> dict[str, TeamSeason]:
    """Aggregeer wedstrijden tot een stand per ploeg, inclusief thuis/uit-splits."""
    table: dict[str, TeamSeason] = {}
    for m in matches:
        h = table.setdefault(m.home, TeamSeason(m.home))
        a = table.setdefault(m.away, TeamSeason(m.away))
        h.played += 1; a.played += 1
        h.gf += m.hg; h.ga += m.ag
        a.gf += m.ag; a.ga += m.hg
        h.home_played += 1; h.home_gf += m.hg; h.home_ga += m.ag
        a.away_played += 1; a.away_gf += m.ag; a.away_ga += m.hg
        if m.shots:
            h.shots_for += m.shots[0]; h.shots_against += m.shots[1]
            a.shots_for += m.shots[1]; a.shots_against += m.shots[0]
            h.shot_matches += 1; a.shot_matches += 1
        if m.sot:
            h.sot_for += m.sot[0]; h.sot_against += m.sot[1]
            a.sot_for += m.sot[1]; a.sot_against += m.sot[0]
    return table


def league_goals_per_match(table: dict[str, TeamSeason]) -> float:
    """Gemiddeld aantal doelpunten dat één ploeg per wedstrijd maakt in deze competitie."""
    played = sum(t.played for t in table.values())
    return sum(t.gf for t in table.values()) / played if played else 0.0


def relative_strength(team: TeamSeason, table: dict[str, TeamSeason]) -> tuple[float, float]:
    """(aanval, verdediging) van een ploeg t.o.v. het competitiegemiddelde. 1.0 = gemiddeld.

    Dit is dezelfde normalisatie die `model.team_strength` op xG toepast, en dat is met opzet:
    daardoor is een relatieve sterkte uit deze bron rechtstreeks bruikbaar als invoer voor
    `model.TeamStats` zodra hij met `convert_strength` naar de juiste divisie is omgerekend.
    """
    avg = league_goals_per_match(table)
    if not avg or not team.played:
        return 1.0, 1.0
    return team.gf_per_match / avg, team.ga_per_match / avg


# --------------------------------------------------------------------------- het divisieverschil

@dataclass
class GapResult:
    """Uitkomst van `division_gap`. `attack`/`defence` zijn de factoren waarmee de relatieve
    sterkte van een ploeg meegaat naar de andere divisie."""
    attack: float
    defence: float
    n: int
    direction: str
    attack_spread: tuple[float, float] = (0.0, 0.0)
    defence_spread: tuple[float, float] = (0.0, 0.0)
    samples: list[tuple] = field(default_factory=list)

    def summary(self) -> str:
        return (f"{self.direction}: aanval x{self.attack:.3f}, verdediging x{self.defence:.3f} "
                f"(n={self.n})")


def division_gap(higher: str, lower: str, years: range, *,
                 direction: str = "up", min_played: int = 10) -> GapResult:
    """Meet hoeveel een divisie scheelt, aan ploegen die er zelf tussen zijn verhuisd.

    `direction="up"`: promovendi — ploegen die in seizoen S in `lower` speelden en in S+1 in
    `higher`. `direction="down"`: degradanten, de andere kant op.

    De meting is per ploeg **relatief aan zijn eigen competitie in dat seizoen**, niet in absolute
    doelpunten. Anders meet je het verschil in scoreniveau tussen twee competities mee in plaats van
    het verschil in sterkte, en dat zijn twee verschillende dingen.

    Geeft de mediaan terug, niet het gemiddelde: één gepromoveerde ploeg die in de divisie erboven
    volledig instort (relatieve aanval naar 0.3) trekt een gemiddelde ver mee, en bij deze
    steekproefgroottes is dat het verschil tussen een bruikbare en een misleidende factor.
    """
    if direction not in ("up", "down"):
        raise FootballDataError("direction moet 'up' of 'down' zijn")
    att, dfn, samples = [], [], []
    for y in years:
        try:
            t_from = season_table(fetch_division(lower if direction == "up" else higher, y))
            t_to = season_table(fetch_division(higher if direction == "up" else lower, y + 1))
        except NotPublished:
            continue
        for name, before in t_from.items():
            after = t_to.get(name)
            if after is None or before.played < min_played or after.played < min_played:
                continue
            a_before, d_before = relative_strength(before, t_from)
            a_after, d_after = relative_strength(after, t_to)
            if a_before <= 0 or d_before <= 0:
                continue
            att.append(a_after / a_before)
            dfn.append(d_after / d_before)
            samples.append((name, y, round(a_after / a_before, 3), round(d_after / d_before, 3)))
    if not att:
        return GapResult(1.0, 1.0, 0, direction)

    def spread(xs):
        xs = sorted(xs)
        return (statistics.quantiles(xs, n=4)[0], statistics.quantiles(xs, n=4)[2]) if len(xs) >= 4 \
            else (xs[0], xs[-1])

    return GapResult(statistics.median(att), statistics.median(dfn), len(att), direction,
                     spread(att), spread(dfn), samples)


def convert_strength(attack: float, defence: float, gap: GapResult) -> tuple[float, float]:
    """Reken een relatieve sterkte uit de ene divisie om naar de andere.

    Een promovendus met relatieve aanval 1.40 in de divisie eronder komt met `gap.attack = 0.75`
    uit op 1.05 in de divisie erboven: nog steeds bovengemiddeld, maar niet meer de kampioen.
    """
    return attack * gap.attack, defence * gap.defence


# --------------------------------------------------------------------------- gemeten factoren
#
# `division_gap()` opnieuw draaien kost ~200 bestanden en een paar minuten. De uitkomst hangt niet
# van de dag af, dus hij staat hier vast. Gemeten op 21 aug 2026 over seizoenen 2014/15 t/m
# 2024/25, acht divisieparen, 240 ploeg-overgangen per richting. Draai
# `python3 scripts/footballdata.py --meet` om hem te herhalen.

MEASURED_GAPS: dict[tuple[str, str, str], tuple[float, float, int]] = {
    # (hoger, lager, richting): (aanvalsfactor, verdedigingsfactor, aantal waarnemingen)
    ("E0", "E1", "up"): (0.541, 1.783, 33),   ("E0", "E1", "down"): (1.830, 0.634, 33),
    ("E1", "E2", "up"): (0.673, 1.638, 33),   ("E1", "E2", "down"): (1.559, 0.638, 33),
    ("E2", "E3", "up"): (0.782, 1.375, 43),   ("E2", "E3", "down"): (1.254, 0.814, 43),
    ("SP1", "SP2", "up"): (0.661, 1.498, 33), ("SP1", "SP2", "down"): (1.523, 0.664, 33),
    ("D1", "D2", "up"): (0.549, 1.397, 23),   ("D1", "D2", "down"): (1.777, 0.743, 23),
    ("I1", "I2", "up"): (0.601, 1.528, 33),   ("I1", "I2", "down"): (1.748, 0.641, 32),
    ("F1", "F2", "up"): (0.609, 1.424, 28),   ("F1", "F2", "down"): (1.772, 0.652, 29),
    ("SC0", "SC1", "up"): (0.591, 1.689, 14), ("SC0", "SC1", "down"): (1.525, 0.574, 14),
}

#: Voor een divisiepaar dat hierboven niet is gemeten (Eerste Divisie, Serie C, de Kroatische
#: 1. NL — die staan geen van alle in deze bron). De mediaan over de acht gemeten paren.
POOLED_GAP: dict[str, tuple[float, float, int]] = {
    "up": (0.605, 1.513, 240),
    "down": (1.654, 0.647, 240),
}

#: Hoeveel de omgerekende sterkte er nog naast zit, ná correctie. Leave-one-season-out over
#: dezelfde 480 overgangen (21 aug 2026): de gemiddelde absolute fout in relatieve sterkte daalt
#: van 0.445 naar 0.184 voor de aanval (-59%) en van 0.416 naar 0.190 voor de verdediging (-54%).
#: Wat blijft staan is een spreiding van ~0.16-0.19 — bijna een vijfde van een competitiegemiddelde.
#: Dat is de reden dat een omgerekende ploeg hooguit `LIGHT` kan zijn en nooit `FULL`: de correctie
#: haalt de systematische fout eruit, niet de onzekerheid.
RESIDUAL_SPREAD = {"attack": 0.163, "defence": 0.159, "n": 480}


def gap_for(higher: str, lower: str, direction: str) -> GapResult:
    """De gemeten factor voor een divisiepaar, of de gepoolde als dat paar niet gemeten is.

    Gebruik dit in een run in plaats van `division_gap()` — dat laatste haalt ~200 bestanden op.
    """
    key = (higher, lower, direction)
    if key in MEASURED_GAPS:
        a, d, n = MEASURED_GAPS[key]
        return GapResult(a, d, n, direction)
    a, d, n = POOLED_GAP[direction]
    return GapResult(a, d, n, f"{direction} (gepoold — {higher}/{lower} niet apart gemeten)")


#: Binnen welke **invoersterktes** de factoren hierboven zijn gemeten. Zelfde meting, zelfde
#: seizoenen (2014/15 t/m 2024/25); dit is de relatieve sterkte die een ploeg had in de divisie
#: waar hij vandáán kwam, vóór de stap.
#:
#: Waarde per sleutel: `(aanval_min, aanval_max, verdediging_min, verdediging_max, n)`.
CONVERSION_RANGE: dict[tuple[str, str, str], tuple[float, float, float, float, int]] = {
    ("E0", "E1", "up"): (0.933, 1.837, 0.284, 1.022, 33),
    ("E0", "E1", "down"): (0.391, 0.941, 0.990, 1.669, 33),
    ("E1", "E2", "up"): (0.939, 1.714, 0.497, 0.965, 33),
    ("E1", "E2", "down"): (0.473, 0.939, 0.918, 1.632, 33),
    ("E2", "E3", "up"): (0.976, 1.547, 0.565, 1.068, 43),
    ("E2", "E3", "down"): (0.526, 1.012, 1.033, 1.861, 43),
    ("SP1", "SP2", "up"): (0.991, 1.651, 0.523, 1.135, 33),
    ("SP1", "SP2", "down"): (0.436, 1.089, 1.078, 1.809, 33),
    ("D1", "D2", "up"): (0.999, 1.673, 0.613, 0.996, 23),
    ("D1", "D2", "down"): (0.481, 1.039, 1.000, 1.668, 23),
    ("I1", "I2", "up"): (1.004, 1.667, 0.565, 1.019, 33),
    ("I1", "I2", "down"): (0.468, 1.001, 1.086, 1.652, 32),
    ("F1", "F2", "up"): (0.899, 1.889, 0.415, 0.997, 28),
    ("F1", "F2", "down"): (0.431, 0.975, 0.929, 1.729, 29),
    ("SC0", "SC1", "up"): (1.157, 1.829, 0.457, 1.053, 14),
    ("SC0", "SC1", "down"): (0.553, 0.935, 1.156, 1.619, 14),
}

#: De omhullende over alle acht paren, voor een divisiepaar dat hierboven niet staat.
POOLED_RANGE: dict[str, tuple[float, float, float, float, int]] = {
    "up": (0.899, 1.889, 0.284, 1.135, 240),
    "down": (0.391, 1.089, 0.918, 1.861, 240),
}


def conversion_in_range(higher: str, lower: str, direction: str,
                        attack: float, defence: float) -> tuple[bool, str]:
    """Valt deze ploeg binnen de sterktes waarop `gap_for` is gemeten?

    **Waarom dit bestaat (gemeten 25 aug 2026, Run A).** De factoren in `MEASURED_GAPS` zijn
    gemeten aan ploegen die daadwerkelijk tussen twee divisies zijn verhuisd, en die groep is per
    definitie **eenzijdig**: `down` is gemeten aan degradanten en `up` aan promovendi. Over alle
    acht divisieparen heen kwam geen enkele degradant boven een relatieve aanval van **1.089** uit
    en geen enkele promovendus onder **0.899**. `convert_strength` is vermenigvuldigend, dus buiten
    dat bereik loopt de omrekening hard uit de hand in plaats van geleidelijk minder nauwkeurig te
    worden.

    Concreet, de aanleiding: Coventry City won in 2025/2026 de Championship met een relatieve
    aanval van **1.619** — 72% boven de hoogste waarneming waarop de `E1->E2 down`-factor rust.
    Vermenigvuldigd met x1.559 kwam Coventry uit op 2.27x het League One-gemiddelde, oftewel 2.96
    xG per duel. Dat leverde in de bekerwedstrijd bij Plymouth Argyle **+21.6 pp** op een handicap
    en +17.5 pp op Over 2.5 op — een schijnedge die alle zes de andere poorten haalde. Dezelfde val
    staat sinds 19 aug 2026 in `data/coverage.json` bij La Liga beschreven, met exact hetzelfde
    getal: "+21.4 pp op een handicap +1.5 die alle andere vijf poorten haalde".

    De correctie haalt de systematische fout eruit (zie `RESIDUAL_SPREAD`), maar alleen op het
    terrein waar hij gemeten is. Buiten dat bereik is er geen meting, en dan is er ook geen
    onafhankelijke kansinput op het niveau waarop het duel gespeeld wordt: `data_tier = NONE`,
    dus geen bet. Vergelijk `_shared-rules.md` §1c — liever een bet te veel tegengehouden dan een
    verzonnen kansbijstelling.

    Geeft `(binnen_bereik, toelichting)` terug. `attack`/`defence` zijn de relatieve sterktes uit
    `relative_strength()`, dus in de divisie waar de ploeg vandáán komt.
    """
    if direction not in ("up", "down"):
        raise FootballDataError("direction moet 'up' of 'down' zijn")
    key = (higher, lower, direction)
    rng = CONVERSION_RANGE.get(key)
    label = f"{higher}/{lower} {direction}"
    if rng is None:
        rng = POOLED_RANGE[direction]
        label = f"gepoold {direction} ({higher}/{lower} niet apart gemeten)"
    a_min, a_max, d_min, d_max, n = rng
    buiten = []
    if not a_min <= attack <= a_max:
        buiten.append(f"aanval {attack:.3f} buiten {a_min:.3f}-{a_max:.3f}")
    if not d_min <= defence <= d_max:
        buiten.append(f"verdediging {defence:.3f} buiten {d_min:.3f}-{d_max:.3f}")
    if buiten:
        return False, f"{label} (n={n}): " + "; ".join(buiten)
    return True, (f"{label} (n={n}): aanval {attack:.3f} in {a_min:.3f}-{a_max:.3f}, "
                  f"verdediging {defence:.3f} in {d_min:.3f}-{d_max:.3f}")


if __name__ == "__main__":
    # Zelftest tegen echte, actuele data. Bewust drie dingen: dat de hoofdbestanden schoten
    # bevatten, dat de extra bestanden het lopende seizoen halen, en dat een nog niet gepubliceerd
    # bestand als NotPublished terugkomt in plaats van als storing.
    e1 = fetch_division("E1", 2025)
    print(f"E1 2025/26: {len(e1)} wedstrijden, {sum(1 for m in e1 if m.shots)} met schoten")
    assert len(e1) > 400, "Championship hoort een vol seizoen te zijn"
    assert all(m.shots for m in e1), "schotenkolommen ontbreken — bestandsformaat gewijzigd?"

    table = season_table(e1)
    print(f"  {len(table)} ploegen, {league_goals_per_match(table):.3f} doelpunten per ploeg per duel")
    assert 20 <= len(table) <= 26, "onverwacht aantal ploegen"
    assert 1.0 < league_goals_per_match(table) < 2.0, "doelpuntenniveau buiten plausibel bereik"

    swe = fetch_extra("SWE", "Allsvenskan")
    seasons = sorted({m.season for m in swe})
    print(f"Allsvenskan (extra): {len(swe)} wedstrijden, seizoenen {seasons[0]}–{seasons[-1]}")
    assert seasons[-1] >= "2026", "extra bestand loopt niet door tot het lopende seizoen"

    try:
        fetch_division("I2", 2026)
        print("I2 2026/27: gepubliceerd")
    except NotPublished as exc:
        print(f"I2 2026/27: nog niet gepubliceerd — {exc}")

    gap = division_gap("E1", "E2", range(2015, 2025), direction="up")
    print(gap.summary())
    assert gap.n >= 20, "te weinig promovendi gevonden om iets te zeggen"
    assert 0.5 < gap.attack < 1.0, "een promovendus hoort in de divisie erboven zwakker te worden"

    # De vastgelegde factoren horen intern consistent te zijn: op en neer zijn elkaars omgekeerde,
    # want het is één divisiekloof die twee kanten op wordt gemeten. Wijkt dit af, dan meet
    # `division_gap` iets anders dan de kloof — bijvoorbeeld een verschil in scoreniveau.
    up_a, _, _ = POOLED_GAP["up"]
    down_a, _, _ = POOLED_GAP["down"]
    print(f"gepoolde factoren: op x{up_a:.3f}, neer x{down_a:.3f}, 1/neer = {1/down_a:.3f}")
    assert abs(up_a - 1 / down_a) < 0.05, "op en neer zijn geen omgekeerden — meting verdacht"

    pooled = gap_for("N1", "N2", "down")   # niet gemeten paar -> gepoold
    assert pooled.n == 240 and "gepoold" in pooled.direction
    assert gap_for("SP1", "SP2", "down").attack == 1.523
    print("Zelftest geslaagd.")
