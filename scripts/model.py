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
    print("Zelftest geslaagd.")
