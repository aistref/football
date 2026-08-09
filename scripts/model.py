#!/usr/bin/env python3
"""Kansmodel: Poisson met Dixon-Coles-correctie op xG-gebaseerde team­sterktes.

Dit is de rekenkern die tijdens de Run A-diagnose van 8 aug 2026 per wedstrijd met de hand in
bash werd herschreven. Het overhandtypen was zelf een groot deel van de tijd die één diepe
analyse kostte — dit bestand bestaat om dat weg te nemen: dezelfde wiskunde, nu één keer
geschreven en per wedstrijd aan te roepen.

    from scripts.model import analyze_match, robustness_check

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

DEFAULT_SHRINK = 0.80
DEFAULT_RHO = -0.05
MAX_GOALS = 12

# Parametercombinaties voor de robuustheidstest — zie _shared-rules.md en de Run A-diagnose van
# 8 aug 2026: een edge die alleen bij één (shrink, rho)-paar boven de drempel komt is een
# artefact van die keuze, geen edge.
ROBUSTNESS_COMBOS: list[tuple[float, float]] = [
    (0.70, -0.05), (0.80, -0.05), (0.90, -0.05), (1.00, -0.05),
    (0.80, 0.00), (0.80, -0.10),
]


@dataclass
class TeamStats:
    """Eén team-seizoen. xg/xga zijn totalen over het seizoen, niet per duel."""
    xg: float
    xga: float
    matches_played: int

    @property
    def xg_per_match(self) -> float:
        return self.xg / self.matches_played

    @property
    def xga_per_match(self) -> float:
        return self.xga / self.matches_played


@dataclass
class LeagueContext:
    """Competitiebasis: nodig om team-xG te normaliseren en thuisvoordeel mee te nemen."""
    home_goals_per_match: float
    away_goals_per_match: float
    avg_xg_per_match: float


@dataclass
class MatchProbabilities:
    lambda_home: float
    lambda_away: float
    home: float
    draw: float
    away: float
    over_2_5: float
    btts: float

    @property
    def under_2_5(self) -> float:
        return 1 - self.over_2_5


def _poisson(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def _dixon_coles_tau(x: int, y: int, lambda_home: float, lambda_away: float, rho: float) -> float:
    if x == 0 and y == 0:
        return 1 - lambda_home * lambda_away * rho
    if x == 0 and y == 1:
        return 1 + lambda_home * rho
    if x == 1 and y == 0:
        return 1 + lambda_away * rho
    if x == 1 and y == 1:
        return 1 - rho
    return 1.0


def score_grid(lambda_home: float, lambda_away: float, rho: float = DEFAULT_RHO,
               max_goals: int = MAX_GOALS) -> list[list[float]]:
    """Kansverdeling over exacte uitslagen 0..max_goals x 0..max_goals, genormaliseerd."""
    grid = [
        [_poisson(i, lambda_home) * _poisson(j, lambda_away)
         * _dixon_coles_tau(i, j, lambda_home, lambda_away, rho)
         for j in range(max_goals + 1)]
        for i in range(max_goals + 1)
    ]
    total = sum(sum(row) for row in grid)
    return [[v / total for v in row] for row in grid]


def team_strength(stats: TeamStats, league: LeagueContext, shrink: float = DEFAULT_SHRINK) -> tuple[float, float]:
    """(aanvalsfactor, verdedigingsfactor) t.o.v. het competitiegemiddelde, met regressie.

    `shrink=1.0` is de ruwe xG-verhouding; `shrink=0.0` is volledig het competitiegemiddelde
    (elk team even sterk). Vroeg seizoen (§4 van _shared-rules.md) rechtvaardigt shrink < 1.0
    omdat rolling xG dan niet bestaat en transfers niet in de cijfers zitten.
    """
    attack = 1 + shrink * (stats.xg_per_match / league.avg_xg_per_match - 1)
    defense = 1 + shrink * (stats.xga_per_match / league.avg_xg_per_match - 1)
    return attack, defense


def match_lambdas(home: TeamStats, away: TeamStats, league: LeagueContext,
                   shrink: float = DEFAULT_SHRINK) -> tuple[float, float]:
    home_attack, home_defense = team_strength(home, league, shrink)
    away_attack, away_defense = team_strength(away, league, shrink)
    lambda_home = league.home_goals_per_match * home_attack * away_defense
    lambda_away = league.away_goals_per_match * away_attack * home_defense
    return lambda_home, lambda_away


def analyze_match(home: TeamStats, away: TeamStats, league: LeagueContext,
                   shrink: float = DEFAULT_SHRINK, rho: float = DEFAULT_RHO) -> MatchProbabilities:
    lambda_home, lambda_away = match_lambdas(home, away, league, shrink)
    grid = score_grid(lambda_home, lambda_away, rho)
    home_p = sum(grid[i][j] for i in range(MAX_GOALS + 1) for j in range(MAX_GOALS + 1) if i > j)
    draw_p = sum(grid[i][i] for i in range(MAX_GOALS + 1))
    away_p = 1 - home_p - draw_p
    over_p = sum(grid[i][j] for i in range(MAX_GOALS + 1) for j in range(MAX_GOALS + 1) if i + j > 2)
    btts_p = sum(grid[i][j] for i in range(1, MAX_GOALS + 1) for j in range(1, MAX_GOALS + 1))
    return MatchProbabilities(lambda_home, lambda_away, home_p, draw_p, away_p, over_p, btts_p)


def edge_pp(my_prob: float, odds: float) -> float:
    """Edge in procentpunten: (my_prob - implied_prob) * 100."""
    return (my_prob - 1 / odds) * 100


@dataclass
class RobustnessResult:
    edges: dict[tuple[float, float], float] = field(default_factory=dict)

    @property
    def min_edge(self) -> float:
        return min(self.edges.values())

    @property
    def max_edge(self) -> float:
        return max(self.edges.values())

    def is_robust(self, threshold: float) -> bool:
        return self.min_edge >= threshold


def robustness_check(home: TeamStats, away: TeamStats, league: LeagueContext,
                      select: "callable[[MatchProbabilities], float]", odds: float,
                      combos: list[tuple[float, float]] | None = None) -> RobustnessResult:
    """Herhaal `analyze_match` over een grid van (shrink, rho) en geef de edge per combinatie.

    `select` haalt de relevante kans uit een MatchProbabilities, bv. `lambda r: r.home` voor de
    1X2-thuiszege of `lambda r: r.under_2_5` voor Under 2.5. Een bet die hier bij één combinatie
    boven de drempel komt en bij een andere eronder zakt, is een artefact van die parameterkeuze
    — zie de Run A-diagnose van 8 aug 2026, waar dit drie kandidaten met een op zich voldoende
    nominale edge alsnog heeft afgevoerd.
    """
    result = RobustnessResult()
    for shrink, rho in combos or ROBUSTNESS_COMBOS:
        probs = analyze_match(home, away, league, shrink, rho)
        result.edges[(shrink, rho)] = edge_pp(select(probs), odds)
    return result


EARLY_SEASON_PRIOR = 8.0
"""Sterkte van de prior in speeldagen, voor `early_season_uplift`. Bij 8 gespeelde speeldagen
telt de waarneming van dit seizoen even zwaar als de aanname 'geen effect'. Vooraf vastgezet en
niet op de markt bijgesteld — zie de anti-circulariteitsregel in _shared-rules.md §2."""


def early_season_uplift(observations: list[tuple[float, float, int]],
                        prior_matchdays: float = EARLY_SEASON_PRIOR) -> tuple[float, float, int]:
    """Hoeveel hoger ligt het scoreniveau nu dan het seizoensgemiddelde waarop het model rekent?

    Reden van bestaan (gemeten in runs/2026-08-09-run-a.md): met teamsterktes uit vorig seizoen
    schat het model structureel te weinig doelpunten — over 17 wedstrijden gemiddeld 3.0
    procentpunt onder de markt op P(Over 2.5), tien van de zeventien keer dezelfde kant op.
    Het mechanisme is niet dat de teamsterktes fout staan, maar dat het **niveau** fout staat:
    begin seizoen wordt er meer gescoord dan het gemiddelde over een heel seizoen, en het model
    haalt zijn niveau uit de eindstand van vorig jaar.

    `observations` is per competitie `(avg_xg vorig seizoen, avg_xg dit seizoen, speeldagen)`.
    Eén competitie na één speeldag is ruis; zes competities samen zijn dat veel minder, en het
    effect zelf is competitie-overstijgend. Daarom wordt er over competities gepoold, gewogen
    naar speeldagen, en daarna teruggetrokken naar 1.0 met `prior_matchdays` als prior.

    Geeft `(schaalfactor, ruwe gepoolde verhouding, totaal aantal speeldagen)` terug. De
    correctie dooft vanzelf uit: naarmate het seizoen vordert nadert `avg_xg dit seizoen` het
    seizoensgemiddelde en gaat de verhouding naar 1.0.

    **Let op — dit mag nooit op de markt worden gefit.** De correctie komt volledig uit
    xG-waarnemingen (Fotmob) en gebruikt geen enkele bookmakerprijs. Zou je `prior_matchdays`
    afregelen tot de afwijking tegenover de markt nul is, dan is `my_prob` alsnog van de odds
    afgeleid en meet de edge niets meer.
    """
    usable = [(base, cur, md) for base, cur, md in observations if base > 0 and cur > 0 and md > 0]
    if not usable:
        return 1.0, 1.0, 0
    total_md = sum(md for _, _, md in usable)
    pooled = sum((cur / base) * md for base, cur, md in usable) / total_md
    weight = total_md / (total_md + prior_matchdays)
    return 1.0 + weight * (pooled - 1.0), pooled, total_md


def scale_level(league: LeagueContext, factor: float) -> LeagueContext:
    """Schaal het doelpuntenniveau van een competitie, zonder de teamsterktes aan te raken.

    Alleen `home_goals_per_match` en `away_goals_per_match` bewegen: die zetten het niveau.
    `avg_xg_per_match` blijft staan, want dat is de noemer waartegen de teamsterktes uit
    hetzelfde seizoen genormaliseerd zijn — die meeschalen zou de correctie weer wegdelen.
    """
    return LeagueContext(
        home_goals_per_match=league.home_goals_per_match * factor,
        away_goals_per_match=league.away_goals_per_match * factor,
        avg_xg_per_match=league.avg_xg_per_match,
    )


@dataclass
class TeamSplits:
    """Wat een ploeg thuis en uit werkelijk scoorde en incasseerde. Geen xG."""
    home_gf: int
    home_ga: int
    home_played: int
    away_gf: int
    away_ga: int
    away_played: int


def analyze_match_from_splits(home: TeamSplits, away: TeamSplits,
                              rho: float = DEFAULT_RHO) -> MatchProbabilities:
    """Tweede kansschatting, op echte doelpunten in plaats van op xG.

    Dit is met opzet een andere doorsnede van dezelfde data: `analyze_match` normaliseert
    teamsterkte op het competitiegemiddelde en rekent met kansenkwaliteit, deze rekent recht­toe
    met wat de thuisploeg thuis deed en de uitploeg uit. Waar beide methodes hetzelfde zeggen,
    hangt een edge niet aan één modelkeuze.

    Nut, concreet: op 9 aug 2026 gaf het xG-model Gil Vicente – Rio Ave +10.3 pp — nominaal de op
    één na grootste edge van die dag — terwijl deze methode op +2.7 pp uitkwam, onder de drempel.
    Groningen en Anderlecht werden door beide bevestigd en zijn wel gepubliceerd.
    """
    lambda_home = (home.home_gf / home.home_played + away.away_ga / away.away_played) / 2
    lambda_away = (away.away_gf / away.away_played + home.home_ga / home.home_played) / 2
    grid = score_grid(lambda_home, lambda_away, rho)
    home_p = sum(grid[i][j] for i in range(MAX_GOALS + 1) for j in range(MAX_GOALS + 1) if i > j)
    draw_p = sum(grid[i][i] for i in range(MAX_GOALS + 1))
    over_p = sum(grid[i][j] for i in range(MAX_GOALS + 1) for j in range(MAX_GOALS + 1) if i + j > 2)
    btts_p = sum(grid[i][j] for i in range(1, MAX_GOALS + 1) for j in range(1, MAX_GOALS + 1))
    return MatchProbabilities(lambda_home, lambda_away, home_p, draw_p,
                              1 - home_p - draw_p, over_p, btts_p)


def splits_from_fotmob(team: dict) -> TeamSplits:
    """`TeamSplits` uit één teamrij van `fotmob.fetch_league_stats`."""
    return TeamSplits(
        home_gf=team["home"]["gf"], home_ga=team["home"]["ga"], home_played=team["home"]["played"],
        away_gf=team["away"]["gf"], away_ga=team["away"]["ga"], away_played=team["away"]["played"],
    )


def league_context_from_table(all_rows: list[dict], home_rows: list[dict], away_rows: list[dict],
                               teams_with_xg: dict[str, TeamStats]) -> LeagueContext:
    """Bouw de competitiebasis uit Fotmob-achtige standrijen (zie scripts/fotmob.py).

    Elke rij heeft minimaal `played` en `scoresStr` ("GF-GA"). `home_rows`/`away_rows` zijn de
    thuis- resp. uitsplitsing van dezelfde stand.
    """
    def goals_per_match(rows: list[dict]) -> float:
        goals = sum(int(r["scoresStr"].split("-")[0]) for r in rows)
        played = sum(r["played"] for r in rows)
        return goals / played

    avg_xg = sum(t.xg_per_match for t in teams_with_xg.values()) / len(teams_with_xg)
    return LeagueContext(
        home_goals_per_match=goals_per_match(home_rows),
        away_goals_per_match=goals_per_match(away_rows),
        avg_xg_per_match=avg_xg,
    )


if __name__ == "__main__":
    # Zelftest: reproduceert de Cercle Brugge – Standard Luik-bet uit runs/2026-08-08-run-a-2.md
    # (my_prob 41.8%, implied 35.1%, edge +6.7 pp bij shrink 0.80 / rho -0.05).
    league = LeagueContext(home_goals_per_match=1.387, away_goals_per_match=1.229, avg_xg_per_match=1.460)
    standard = TeamStats(xg=47.9, xga=63.3, matches_played=40)
    cercle = TeamStats(xg=59.9, xga=54.9, matches_played=36)
    probs = analyze_match(standard, cercle, league)
    print(f"Standard {probs.home * 100:.1f}%  Gelijk {probs.draw * 100:.1f}%  Cercle {probs.away * 100:.1f}%")
    assert abs(probs.away - 0.418) < 0.002, f"verwacht ~41.8%, kreeg {probs.away * 100:.1f}%"
    print(f"Edge op Cercle @2.85: {edge_pp(probs.away, 2.85):+.1f} pp (verwacht +6.7 pp)")

    # Vroeg-seizoenscorrectie, met de zes competitiemetingen van 9 aug 2026 als vaste invoer.
    obs = [(1.579, 1.820, 1), (1.316, 1.350, 1), (1.460, 1.875, 1),
           (1.394, 1.550, 2), (1.535, 1.562, 3), (1.406, 1.607, 3)]
    factor, pooled, total_md = early_season_uplift(obs)
    print(f"\nVroeg seizoen: gepoold {pooled:.4f} over {total_md} speeldagen "
          f"-> schaalfactor {factor:.4f}")
    assert abs(pooled - 1.1063) < 0.001, f"verwacht ~1.1063, kreeg {pooled:.4f}"
    assert abs(factor - 1.0615) < 0.001, f"verwacht ~1.0615, kreeg {factor:.4f}"
    # Uitdoven: bij een half seizoen zonder verschil moet er niets meer gecorrigeerd worden.
    assert abs(early_season_uplift([(1.5, 1.5, 17)])[0] - 1.0) < 1e-9
    assert early_season_uplift([])[0] == 1.0

    ered = LeagueContext(home_goals_per_match=1.801, away_goals_per_match=1.376,
                         avg_xg_per_match=1.579)
    groningen = TeamStats(xg=61.9, xga=49.0, matches_played=34)
    utrecht = TeamStats(xg=52.4, xga=46.6, matches_played=34)
    voor = analyze_match(groningen, utrecht, ered).over_2_5
    na = analyze_match(groningen, utrecht, scale_level(ered, factor)).over_2_5
    print(f"P(Over 2.5) Groningen-Utrecht: {voor * 100:.1f}% -> {na * 100:.1f}% na correctie")
    assert na > voor, "de correctie hoort het doelpuntenniveau omhoog te brengen"

    # Tweede methode: reproduceert de kruisproef uit runs/2026-08-09-run-a.md.
    g = TeamSplits(home_gf=27, home_ga=18, home_played=17, away_gf=22, away_ga=27, away_played=17)
    u = TeamSplits(home_gf=31, home_ga=13, home_played=17, away_gf=24, away_ga=29, away_played=17)
    split = analyze_match_from_splits(g, u)
    print(f"Tweede methode Groningen-Utrecht: thuiszege {split.home * 100:.1f}% "
          f"(verwacht ~46.4%), edge @2.48 {edge_pp(split.home, 2.48):+.1f} pp")
    assert abs(split.home - 0.464) < 0.005, f"verwacht ~46.4%, kreeg {split.home * 100:.1f}%"
    print("Zelftest geslaagd.")
