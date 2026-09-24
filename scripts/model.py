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

# Hoeveel de xG-verhouding van een ploeg naar het competitiegemiddelde wordt getrokken.
# Op 19 sep 2026 van 0.80 naar 1.00 (= geen regressie), op UITSLAGEN gemeten over de 782
# wedstrijden die de routine zelf heeft doorgerekend. Zie `team_strength` voor de cijfers en
# `tmp-run/shrink_outcome_test.py` om ze na te rekenen. De vorige waarde was gekozen op een
# backtest over álle duels in vijf grote competities (`blend_seasons`); die meting blijft
# staan voor díe populatie, maar ze gold niet voor wat deze routine werkelijk doorrekent.
DEFAULT_SHRINK = 1.00
# Wat de routine t/m 18 sep 2026 gebruikte. Alleen nog nodig als vergelijkingsarm in het
# kalibratieblok (§6e), zodat de reeks "wat doet shrink" niet afbreekt bij de overstap.
LEGACY_SHRINK = 0.80
DEFAULT_RHO = -0.05
MAX_GOALS = 12

# Hoeveel duels van het lópende seizoen nodig zijn voordat dat seizoen even zwaar weegt als het
# vorige. Op uitslagen gemeten (zie `blend_seasons`); op 5 sep 2026 op verzoek van de gebruiker
# van 16 naar 8 gezet — sneller meebewegen met het lopende seizoen, tegen een gemeten prijs die
# in de docstring staat.
CREDIBILITY_K = 8.0

# Parametercombinaties voor de robuustheidstest — zie _shared-rules.md en de Run A-diagnose van
# 8 aug 2026: een edge die alleen bij één (shrink, rho)-paar boven de drempel komt is een
# artefact van die keuze, geen edge.
# De rho-arm staat op de STANDAARD-shrink, anders varieert hij twee dingen tegelijk; hij is
# daarom op 19 sep 2026 van 0.80 naar 1.00 meeverhuisd. De shrink-arm blijft met opzet van 0.70
# tot 1.00 lopen: de standaard staat nu aan de bovenkant van dat bereik, dus poort 6 toetst of
# een edge ook overleeft wanneer ploegen onderling gelijker worden gemaakt. Dat is de strengere
# kant op — een edge op de zwakkere ploeg wordt bij lagere shrink juist groter en zakt dus niet
# door de poort, maar een edge op de favoriet wel, en dat is precies de kant waar deze
# parameterwijziging de routine naartoe beweegt.
ROBUSTNESS_COMBOS: list[tuple[float, float]] = [
    (0.70, -0.05), (0.80, -0.05), (0.90, -0.05), (1.00, -0.05),
    (1.00, 0.00), (1.00, -0.10),
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
    level_factor: float = 1.0
    """Met welke factor `scale_level` het doelpuntenniveau al heeft opgeschroefd (1.0 = niet).

    Alleen `analyze_match_from_splits` heeft dit nodig, en wel om de reden die in de docstring
    van `scale_level` staat: die functie houdt `avg_xg_per_match` met opzet op de ongeschaalde
    waarde, omdat dat de **noemer** is waartegen teamsterktes uit hetzelfde seizoen genormaliseerd
    zijn. De splitsmethode heeft zo'n apart noemerveld niet — die gebruikt
    `home_goals_per_match` tegelijk als noemer én als niveau. Zonder dit veld deelt hij de
    correctie dus niet alleen weg maar **keert hij hem om**: gemeten op 24 aug 2026 gaf een
    niveaucorrectie van +10% een splitsmethode die 9% mínder doelpunten voorspelde. Zie
    `analyze_match_from_splits`."""


@dataclass
class MatchProbabilities:
    lambda_home: float
    lambda_away: float
    home: float
    draw: float
    away: float
    over_2_5: float
    btts: float
    grid: list[list[float]] | None = None
    """Het volledige scoregrid. Nodig voor elke markt die niet met een los veld is af te lezen —
    Asian Handicap, Draw No Bet, andere O/U-lijnen dan 2.5. Toegevoegd op 14 aug 2026; zie de
    toelichting bij `asian_prob` waarom die velden er eerst niet waren en dat dat scheef liep."""

    @property
    def under_2_5(self) -> float:
        return 1 - self.over_2_5

    @property
    def dc_1x(self) -> float:
        return self.home + self.draw

    @property
    def dc_x2(self) -> float:
        return self.draw + self.away

    @property
    def dc_12(self) -> float:
        return self.home + self.away


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


def blend_seasons(prior: TeamStats, current: TeamStats | None,
                  k: float = CREDIBILITY_K) -> TeamStats:
    """Weeg het lopende seizoen mee met het vorige, naar rato van wat er al gespeeld is.

    Reden van bestaan (verzoek van de gebruiker, 3 sep 2026): tot die datum kwamen de
    teamsterktes **uitsluitend** uit het vorige seizoen, en werden ze nooit ververst. De
    routine wist in mei dus precies evenveel over een club als in augustus. Het lopende
    seizoen kwam alleen binnen als competitiebreed doelpuntenniveau (`early_season_uplift`),
    en dat is een correctie die juist uitdooft — kennis die verdwijnt, niet die groeit.

        gewicht_nu = n / (n + k)
        tarief     = gewicht_nu * tarief_dit_seizoen + (1 - gewicht_nu) * tarief_vorig_seizoen

    Met k = 8 weegt het lopende seizoen na 8 duels even zwaar als het hele vorige, na 4 duels
    voor eenderde, en op speeldag 1 helemaal niet. De routine wordt daarmee vanzelf beter
    naarmate het seizoen vordert, zonder dat er iets aan de knoppen hoeft.

    **k stond van 3 t/m 5 sep 2026 op 16 en is op verzoek van de gebruiker naar 8 gezet.** Dat is
    een stap wég van het gemeten optimum, en dat hoort er eerlijk bij te staan. Exact nagemeten op
    dezelfde backtest, dezelfde 1263 wedstrijden:

    | | alleen vorig seizoen | k = 16 (optimum) | **k = 8 (nu)** |
    |---|---|---|---|
    | Brier | .61761 | **.61269** | .61331 |
    | log loss | 1.03057 | 1.02334 | 1.02422 |

    k = 8 houdt daarmee **87%** van de winst die blenden überhaupt oplevert (.00430 van .00492).
    De prijs is dus reëel maar klein, en er staat iets tegenover dat de backtest niet kan meten:
    die draait op één testseizoen in vijf grote competities met stabiele selecties. Bij een ploeg
    die in de zomer half is omgebouwd — en daar zitten de promovendi en de kleinere competities
    vol mee — is "reageer sneller op wat je dit seizoen ziet" een verdediging die niet in deze
    cijfers zit. Wie k terugzet naar 16 heeft de meting aan zijn kant; wie hem op 8 laat, kiest
    voor sneller bijleren tegen 13% van de blendwinst. Beide zijn verdedigbaar, geen van beide is
    gratis.

    **k is op uitslagen gemeten, niet gekozen.** Backtest over vijf competities bij Understat
    (EPL, La Liga, Bundesliga, Serie A, Ligue 1), elke wedstrijd gescoord met alleen wat er
    vóór die wedstrijd bekend was — geen enkele wedstrijd ziet zijn eigen uitslag, en er komt
    geen bookmakerprijs aan te pas (§2). Multiclass Brier op 1X2, lager is beter:

    | k | 40 | 30 | 22 | **16** | 12 | 9 | **8** | 5 | 0 | alleen vorig |
    |---|---|---|---|---|---|---|---|---|---|---|
    | Brier | .61338 | .61301 | .61276 | **.61269** | .61283 | .61314 | **.61331** | .61424 | .62396 | .61761 |

    Twee dingen die daaruit volgen en die je niet moet vergeten als je hieraan komt te sleutelen:

    1. **Blenden, niet omschakelen.** k = 0 (alleen het lopende seizoen) is met .62396 *slechter*
       dan alleen het vorige seizoen. De winst zit in het wegen; wie het lopende seizoen als
       vervanging gebruikt, maakt de analyse aantoonbaar slechter. Het dal rond k = 12–22 is vlak,
       dus 16 is "ongeveer waar het optimum ligt", geen scherp getal.
    2. **De winst groeit mee met het seizoen, en dat is het hele punt.** Per speeldagbak, met de
       uit-steekproefcontrole ernaast:

       | speeldagen gespeeld | winst 2025/26 (in-steekproef) | winst 2024/25 (uit-steekproef) |
       |---|---|---|
       | 1–5   | +0.00276 | +0.00230 |
       | 6–12  | +0.00109 | +0.00525 |
       | 13–24 | +0.00328 | −0.00046 |
       | 25+   | **+0.01155** | **+0.01117** |

    **Uit-steekproef gecontroleerd**, juist omdat §0 bij `EDGE_THRESHOLD_FULL` terecht klaagt dat
    die in-sample is gekozen. k = 16 is bepaald op 2025/2026 (n=1263, verschil +0.00491, t=+2.11)
    en daarna ongewijzigd toegepast op 2024/2025 met prior 2023/2024 — een seizoen dat bij de
    keuze geen rol speelde: n=1297, verschil +0.00424, t=+1.71. Het effect krimpt dus nauwelijks
    (86% van de in-steekproefwaarde), wat betekent dat k niet op ruis is gefit. Het is wél een
    bescheiden effect: de blend is beter in 51% van de wedstrijden, niet in 60%.

    **Wat dit níet is.** Geen regressie naar het competitiegemiddelde — dat is geprobeerd en het
    werkte averechts (§1d). Dit weegt twee steekproeven van dezelfde ploeg tegen elkaar, en dat
    is een andere bewerking: het trekt een ploeg niet naar het midden maar naar zijn eigen
    recentere cijfers.

    Terzijde, ook gemeten: `shrink` hoeft níet af te lopen naarmate het seizoen vordert.
    `shrink=0.8` verslaat `shrink=1.0` bij elke waarde van k (bij k=16: .61269 tegen .61488).

    LET OP — die laatste regel gold voor DEZE backtest en niet voor de routine. Hier stond tot
    19 sep 2026 bij dat de openstaande vraag van §6e daarmee beantwoord was ("laten staan"). Dat
    is die dag omgedraaid: op de 782 wedstrijden die de routine zelf doorrekent is `shrink=1.0`
    beter gekalibreerd én wint hij de tekentoets (z=+3.22), en de standaard staat sindsdien op
    1.00. Zie de docstring van `team_strength`. De backtest hierboven is niet ingetrokken — hij
    meet een andere populatie (alle duels in vijf grote competities, één seizoen) en een andere
    grootheid (gemiddelde Brier in plaats van kalibratie in de staarten).

    `current=None` of nul gespeelde duels geeft `prior` onveranderd terug — speeldag 1 en een
    competitie zonder lopende-seizoensdata veranderen dus niets.
    """
    if current is None or current.matches_played <= 0 or prior.matches_played <= 0:
        return prior
    n = current.matches_played
    w = n / (n + k)
    xg = w * current.xg_per_match + (1 - w) * prior.xg_per_match
    xga = w * current.xga_per_match + (1 - w) * prior.xga_per_match
    # matches_played=1 maakt xg/xga meteen het tarief per duel; TeamStats bewaart totalen.
    return TeamStats(xg=xg, xga=xga, matches_played=1)


def blend_weight(matches_played: int, k: float = CREDIBILITY_K) -> float:
    """Hoe zwaar het lopende seizoen meeweegt, voor in het runrapport."""
    if matches_played <= 0:
        return 0.0
    return matches_played / (matches_played + k)


def team_strength(stats: TeamStats, league: LeagueContext, shrink: float = DEFAULT_SHRINK) -> tuple[float, float]:
    """(aanvalsfactor, verdedigingsfactor) t.o.v. het competitiegemiddelde, met regressie.

    `shrink=1.0` is de ruwe xG-verhouding; `shrink=0.0` is volledig het competitiegemiddelde
    (elk team even sterk). Vroeg seizoen (§4 van _shared-rules.md) rechtvaardigt shrink < 1.0
    omdat rolling xG dan niet bestaat en transfers niet in de cijfers zitten.

    DE RICHTING VAN DEZE KNOP. Regressie maakt ploegen onderling gelijker, en gelijker betekent
    dat de underdog meer kans krijgt dan hij verdient. Dat stond hier sinds 23 aug 2026 als
    vermoeden, gemeten tegen de markt op 25 duels, met de aantekening dat twee dagen onder de
    leesdrempel van §6e ligt en het niveau daarom niet werd verlaagd.

    OP 19 SEP 2026 IS HET OP UITSLAGEN GEMETEN EN IS DE WAARDE OP 1.00 GEZET. Aanleiding: de
    gebruiker merkte op dat de schaduwlijst dag na dag uit dezelfde soort bet bestaat. Vier
    andere verklaringen zijn eerst getoetst en alle vier verworpen — oneenigheid tussen de twee
    methodes, `min(edge_xg, edge_split)`, `edge_robust_min` en de koersband gaven geen van alle
    een monotoon verband met de uitkomst. Deze wel.

    De meting gebruikt het kalibratielogboek, dat per doorgerekende wedstrijd zowel `p_xg`
    (standaard-shrink) als `p_xg_noshrink` (1.00) bewaart, en legt daar de werkelijke uitslag
    naast. 782 wedstrijden, 29 rundagen:

        marktbak     n   werkelijk   shrink 0.8   shrink 1.0
        <15%       145        5.5%        15.7%        12.9%
        15-25%     552       20.8%        23.3%        21.8%
        25-35%     823       28.7%        28.7%        28.3%
        35-50%     478       40.0%        41.5%        42.2%
        50-65%     248       58.9%        52.9%        55.9%
        >=65%      100       86.0%        64.9%        69.8%

    Gewogen gemiddelde kalibratiefout 3.08 pp -> 2.28 pp. De scheefstand op longshots zakt van
    +4.11 naar +2.34 pp en die op favorieten van -10.32 naar -6.81 pp: precies de compressie die
    de underdog te sterk maakt, en ze wordt ongeveer gehalveerd. De marktkans bepaalt hier alleen
    de BAK; er wordt niets op de markt afgeregeld (§2, §6e "controleren, niet fitten").

    Twee cijfers die er eerlijk bij horen. De tekentoets is hard — `shrink=1.0` is beter in
    436 van de 782 duels, z=+3.22, en het teken houdt stand in beide helften van de periode
    (z=+3.17 en +1.49) en op beide datatiers. De gepaarde Brier-toets is dat niet: +0.00234 met
    t=+1.44. `shrink=1.0` wint dus vaker, maar als 0.8 wint, wint hij groter. Dat is het
    normale beeld bij een schatter die in de staarten beter is gekalibreerd, en het is de reden
    om dit als een kalibratieverbetering te lezen en niet als een nauwkeurigheidssprong.

    WAAROM DIT DE BACKTEST VAN 3 SEP NIET TEGENSPREEKT. Die mat `shrink=0.8` als beter over álle
    duels in vijf grote competities in één seizoen (zie `blend_seasons`). Deze routine rekent iets
    anders door: 21 competities, veel omgerekende promovendi en degradanten, vroeg seizoen, en ze
    kiest juist de staart waar ze het verst van de markt af zit. Een parameter kan gemiddeld beter
    zijn en in de staart slechter. Belangrijk: `shrink` is nooit op déze 782 wedstrijden gefit,
    dus dit is voor die keuze een echte uit-steekproefmeting.

    Narekenen: `PYTHONPATH=. python3 tmp-run/shrink_outcome_test.py`.
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
    return MatchProbabilities(lambda_home, lambda_away, home_p, draw_p, away_p, over_p, btts_p, grid)


# Hoe zwaar de xG-methode weegt in `my_prob` ten opzichte van de splitsmethode. Op uitslagen
# gemeten, zie `combine_probs`.
XG_WEIGHT = 0.80


def combine_probs(p_xg: float, p_split: float, weight: float = XG_WEIGHT) -> float:
    """Combineer de twee methodes van §1 tot één kans: `weight` op xG, de rest op de splits.

    **Tot 5 sep 2026 was dit het ongewogen gemiddelde**, en dat was nooit ergens op gebaseerd —
    het stond zo in de eerste versie van de opdracht en is daarna nooit tegen uitkomsten gelegd.
    §1d en §6e wezen de splitsmethode al aan als de scheefste van de twee, maar dat was gemeten
    tegen de **markt** en mag daarom hooguit een diagnose heten (§2).

    Nu wél op uitslagen gemeten, over 392 afgerekende gevallen — 155 gespeelde picks plus 237
    kandidaten die een poort tegenhield, samen precies de groep waar de routine iets van vond.
    Brier tegen de werkelijke uitkomst, lager is beter:

    | gewicht xG | 0.0 | 0.3 | 0.5 (oud) | 0.7 | **0.8** | 0.9 | 1.0 |
    |---|---|---|---|---|---|---|---|
    | Brier | .24415 | .23934 | .23737 | .23638 | **.23625** | .23637 | .23674 |

    Drie dingen die hierbij horen:

    1. **De curve is vlak tussen 0.7 en 1.0.** 0.80 is "ongeveer waar het optimum ligt", geen
       scherp getal; alles van 0.7 tot 0.9 is praktisch gelijkwaardig. Ga hier niet op fijnregelen.
    2. **De splitsmethode voegt als kansbron vrijwel niets toe** — alleen xG (1.0) is met .23674
       nauwelijks slechter dan de beste mix. Ze blijft wél staan als **veto**: poort 5 eist dat
       beide methodes de markt dezelfde kant op verslaan, en die poort houdt aantoonbaar slechte
       bets tegen (§6d). Meerekenen voor een vijfde, meebeslissen over ja/nee: dat is de rol.
    3. **Dit maakt het model beter, niet goed.** Ook bij het beste gewicht schat de markt nog
       altijd scherper (.22374). Zie `recalibrate.py` voor wat daar nog wél aan te doen is en waar
       de grens ligt.
    """
    return weight * p_xg + (1 - weight) * p_split


def edge_pp(my_prob: float, odds: float) -> float:
    """Edge in procentpunten: (my_prob - implied_prob) * 100."""
    return (my_prob - 1 / odds) * 100


# --------------------------------------------------------------------------- markten
#
# Waarom dit bestaat (14 aug 2026). `_shared-rules.md` §1 schrijft voor: "Ga alle markten langs —
# 1X2, Double Chance, Draw No Bet, Asian Handicap, Over/Under, BTTS — en publiceer alleen de
# sterkste." Dat gebeurde niet, en de reden zat hier: `MatchProbabilities` had velden voor 1X2,
# Over/Under **2.5** en BTTS en verder niets. Asian Handicap en Draw No Bet waren met geen
# mogelijkheid uit te rekenen, andere O/U-lijnen dan 2.5 evenmin. Het gevolg is te tellen in
# `data/picks.jsonl`: van de eerste 15 picks waren er 11 een 1X2, 3 een Over/Under 2.5 en 1 een
# Double Chance — nul Asian Handicap, nul BTTS, nul Draw No Bet. De routine zocht dus niet "de
# sterkste markt" maar "de sterkste van de twee markten die toevallig geïmplementeerd waren".
#
# Alles hieronder rekent op hetzelfde scoregrid, zodat één modelaanroep alle markten bedient en een
# extra markt niets extra's kost aan ophalen.

def _payout_probs(grid: list[list[float]], line: float, side: str,
                   totals: bool = False) -> tuple[float, float, float]:
    """(kans op winst, kans op push, kans op verlies) voor één hele of halve lijn.

    `side` is "home"/"away" bij een handicap, of "over"/"under" bij een totaal. De marge is bij een
    handicap het doelsaldo plus de lijn, bij een totaal het aantal doelpunten min de lijn.
    """
    win = push = lose = 0.0
    n = len(grid)
    for i in range(n):
        for j in range(n):
            p = grid[i][j]
            if totals:
                margin = (i + j) - line
                if side == "under":
                    margin = -margin
            else:
                margin = (i - j) + line if side == "home" else (j - i) + line
            if margin > 0:
                win += p
            elif margin == 0:
                push += p
            else:
                lose += p
    return win, push, lose


def _split_line(line: float) -> list[tuple[float, float]]:
    """Een kwartlijn (±0.25, ±0.75, ...) is twee halve inzetten op de twee buurlijnen.

    -0.75 is dus een halve inzet op -0.5 en een halve op -1.0. Hele en halve lijnen komen er
    ongewijzigd uit, met gewicht 1.
    """
    if abs(line * 2 - round(line * 2)) < 1e-9:      # hele of halve lijn
        return [(line, 1.0)]
    return [(line - 0.25, 0.5), (line + 0.25, 0.5)]


def expected_return(grid: list[list[float]], line: float, side: str, odds: float,
                     totals: bool = False) -> float:
    """Verwachte uitbetaling per ingezette eenheid, inclusief de inzet zelf.

    Winst betaalt `odds`, push betaalt 1 (inzet terug), verlies 0. Bij een kwartlijn wordt dat over
    de twee halve inzetten gemiddeld. `> 1` betekent positieve verwachtingswaarde.
    """
    total = 0.0
    for component, weight in _split_line(line):
        win, push, lose = _payout_probs(grid, component, side, totals)
        total += weight * (win * odds + push * 1.0 + lose * 0.0)
    return total


def asian_prob(grid: list[list[float]], line: float, side: str, odds: float,
                totals: bool = False) -> float:
    """De kans waarmee deze bet zich als een gewone binaire bet gedraagt.

    Een handicap of totaal met push (hele lijn) of halve inzet (kwartlijn) is niet zomaar met een
    kans te beschrijven: bij een push krijg je je geld terug in plaats van te verliezen. Daarom
    wordt hier de kans teruggegeven die bij deze koers **dezelfde verwachtingswaarde** oplevert:
    `p = E[uitbetaling] / odds`. Voor een halve lijn zonder push valt dat exact samen met de gewone
    winkans, zodat `edge_pp(asian_prob(...), odds)` overal op dezelfde schaal staat als de 1X2-edge
    en de vijf poorten van §1 er zonder uitzondering op werken.
    """
    return expected_return(grid, line, side, odds, totals) / odds


def dnb_prob(grid: list[list[float]], side: str, odds: float) -> float:
    """Draw No Bet is de Aziatische handicap op 0.0: bij gelijkspel komt de inzet terug."""
    return asian_prob(grid, 0.0, side, odds)


def totals_prob(grid: list[list[float]], line: float, side: str, odds: float) -> float:
    """Over/Under op een willekeurige lijn (1.5, 2.5, 3.0, 3.25, ...), niet alleen 2.5."""
    return asian_prob(grid, line, side, odds, totals=True)


DATA_WEIGHT = {"FULL": 1.0, "LIGHT": 0.5}
"""Het gewicht van `data_tier` in `selection_score`.

0.5 voor LIGHT is niet gekozen maar afgeleid: `EDGE_THRESHOLD_FULL / EDGE_THRESHOLD_LIGHT` =
8.0 / 16.0 (tot 31 aug 2026: 3.0 / 6.0; de verhouding 2:1 is bij die verhoging bewust
intact gelaten, juist omdat dit gewicht eraan hangt). De regels eisen van zwakke data al twee keer zoveel edge om überhaupt mee te doen;
dezelfde verhouding gebruiken bij het rangschikken houdt die twee met elkaar in de pas. `NONE`
staat er niet in — die wedstrijden leveren per §2 geen bet op.
"""


def selection_score(edge_pp_value: float, my_prob: float, data_tier: str = "FULL") -> float:
    """`Edge × Probability × Data-betrouwbaarheid` uit _shared-rules.md §1 en §5, als één getal.

    Vastgesteld op 14 aug 2026, op verzoek van de gebruiker, uit vier lezingen die niet dezelfde
    kant op wezen. De aanleiding: dezelfde inschatting levert op vier tot zeven markten tegelijk
    een edge op, en dan bepaalt de weegregel welke daarvan je publiceert. Op Viborg – AGF gaven de
    vier lezingen twee verschillende antwoorden:

        1X2 AGF wint  @3.55  kans 45.8%  edge +17.6 pp  ->  score  8.05
        AH +0.5 AGF   @1.87  kans 69.0%  edge +15.5 pp  ->  score 10.71   <- wint

    Rangschikken op edge alleen koos hier de 1X2; deze regel kiest de handicap. Dat is een keuze
    over risicobereidheid, geen uitkomst van de data — een selectie met een hogere trefkans krijgt
    de voorkeur boven een selectie met een paar procentpunt meer edge.

    Er is één inhoudelijk argument dat dezelfde kant op wijst: de bekende zwakte van dit model
    (het kent geen competitiesterkte, zie de runrapporten van 13 en 14 aug) verschuift kansmassa
    tussen *winst* en *gelijkspel*. Een 1X2 is daar maximaal gevoelig voor, want het gelijkspel is
    dan puur verlies; een handicap +0.5 of een Draw No Bet is er ongevoelig voor, want daar wordt
    een gelijkspel gewonnen of teruggegeven. Zolang die fout niet gerepareerd is, ligt het
    zwaartepunt van deze regel dus ook op de minst blootgestelde uitdrukking van dezelfde mening.

    `my_prob` moet voor elke markt op dezelfde schaal staan; gebruik daarom `asian_prob` /
    `dnb_prob` / `totals_prob` voor markten met push, niet de kale winkans.
    """
    try:
        weight = DATA_WEIGHT[data_tier]
    except KeyError:
        raise ValueError(f"data_tier moet FULL of LIGHT zijn, kreeg {data_tier!r}") from None
    return edge_pp_value * my_prob * weight


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
        level_factor=league.level_factor * factor,
    )


SEASON_MATURE_SHARE = 0.5
"""Vanaf welk deel van zijn speeldagen een lopend seizoen zijn eigen niveau mag zetten.

**Dit getal is niet gefit, en dat staat er met opzet bij.** Wat wél vastligt is het mechanisme
eronder, en dat is met cijfers beschreven in `league_level`. De 0.5 is "ongeveer waar het omslaat",
in dezelfde geest als `sides.UNDERDOG_FLOOR` en de gewichten van `ranking.data_richness`: hij
scheidt een competitie die net begonnen is van een die halverwege is, en tussen die twee zit geen
scherpe grens. Wat de keuze wél meetbaar maakt: `league_level` geeft per competitie terug welke
route hij nam, dus over een paar weken is met het kalibratielogboek na te gaan of de
lopend-seizoensroute beter gekalibreerd is dan de uplift-route. Herzie hem op die meting, niet op
een nieuwe redenering."""


def matchdays_played(teams: dict[str, dict]) -> int:
    """Hoeveel speeldagen er in dit seizoen al zijn gespeeld, uit de stand van `fetch_league_stats`.

    Het maximum en niet het gemiddelde: bij een uitgestelde wedstrijd lopen ploegen een duel uit
    elkaar, en dan is de verst gevorderde ploeg de speeldag waar de competitie op staat.
    """
    return max((t.get("played") or 0) for t in teams.values()) if teams else 0


def season_length(prev_teams: dict[str, dict]) -> int | None:
    """Hoeveel speeldagen een volledig seizoen in deze competitie heeft — **gemeten, niet geraden**.

    Het vorige seizoen is afgelopen, dus zijn eigen speeldagental is het antwoord: MLS 2025 staat op
    34, Eliteserien 2025 op 30, Serie B 2025/2026 op 38. Dat is beter dan het uit het aantal ploegen
    afleiden, want `2 x (n - 1)` klopt precies niet voor de competitie waar het hier om begon: MLS
    heeft dertig ploegen en **34** speeldagen, niet 58, omdat het schema per conference loopt. Het is
    ook beter dan een tabel in de repo: die veroudert stil zodra een competitie van formaat
    verandert.

    Geeft `None` als de stand van vorig seizoen leeg is of op 0 staat. De aanroeper hoort dat te
    behandelen als "seizoenslengte onbekend" en niet als "seizoen nog niet begonnen" — zie
    `season_is_mature`, die bij `None` de veilige kant kiest.
    """
    n = matchdays_played(prev_teams)
    return n or None


def season_is_mature(played: int, length: int | None,
                     share: float = SEASON_MATURE_SHARE) -> bool:
    """Heeft dit seizoen genoeg speeldagen achter zich om zijn eigen niveau te zetten?

    Bij een onbekende seizoenslengte is het antwoord **False**: dan blijft de bestaande route staan
    (vorig seizoen plus de vroeg-seizoenscorrectie), en dat is de conservatieve kant — de correctie
    is klein en dooft uit, terwijl een onterecht "volwassen" seizoen het niveau op een handvol
    speeldagen zou baseren.
    """
    if not length or length <= 0 or played <= 0:
        return False
    return played / length >= share


@dataclass
class LevelChoice:
    """Het competitieniveau dat een run gebruikt, plus waarom het dat is.

    Leg dit blok per competitie vast in `data/run-state/` onder `niveau`. Zonder `source` en
    `share` erbij is achteraf niet na te gaan met welk niveau een pick is gepubliceerd, en dan is
    de meting waar `SEASON_MATURE_SHARE` op herzien moet worden niet te doen.
    """
    league: LeagueContext
    source: str
    """`"lopend"` of `"vorig+uplift"`."""
    played: int
    length: int | None
    share: float | None
    ratio: float | None
    """`avg_xg` lopend / `avg_xg` vorig — de verhouding waar de uplift op rekent."""
    uplift_factor: float
    """De factor die `early_season_uplift` gaf. Bij `source == "lopend"` is hij **niet toegepast**;
    hij staat er om te kunnen zien wat de andere route zou hebben gedaan."""
    blend_weight: float
    """Het gewicht waarmee het lopende seizoen in de noemer meeweegt — hetzelfde gewicht dat
    `blend_seasons` aan de teamsterktes geeft, want dat is waar de noemer bij hoort."""
    xg_available: bool
    reason: str

    def as_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "league"}
        d["home_goals_per_match"] = self.league.home_goals_per_match
        d["away_goals_per_match"] = self.league.away_goals_per_match
        d["avg_xg_per_match"] = self.league.avg_xg_per_match
        d["level_factor"] = self.league.level_factor
        return d


def _level(stats: dict) -> tuple[float, float]:
    return stats["home_goals_per_match"], stats["away_goals_per_match"]


def _denominator(stats: dict) -> float:
    """De noemer waartegen teamsterktes genormaliseerd worden: `avg_xg_per_match`.

    Zes van de zeventien Run B-competities hebben geen xG bij Fotmob. Dan is het doelpuntgemiddelde
    de sterktemaat, en dus ook de noemer. Die terugval stond tot 24 sep 2026 in elk runscript apart
    overgetypt (`rb20_analyze.py`, `b_analyze.py`); hier staat hij één keer.
    """
    avg = stats.get("avg_xg_per_match")
    if avg:
        return avg
    home, away = _level(stats)
    return (home + away) / 2


def league_level(prev: dict, cur: dict | None = None, *, uplift_factor: float = 1.0,
                 length: int | None = None, k: float = CREDIBILITY_K,
                 share: float = SEASON_MATURE_SHARE) -> LevelChoice:
    """Het `LeagueContext` waarmee een run rekent, langs de route die bij het seizoen past.

    `prev` en `cur` zijn de antwoorden van `fotmob.fetch_league_stats` voor het vorige en het
    lopende seizoen. Twee routes, en welke het wordt hangt alleen af van hoeveel er van het lopende
    seizoen is gespeeld:

    | route | wanneer | niveau |
    |---|---|---|
    | `vorig+uplift` | lopend seizoen jonger dan `share` van zijn speeldagen | vorig seizoen x `uplift_factor` |
    | `lopend` | lopend seizoen op of boven `share` | het lopende seizoen zelf, ongeschaald |

    **Waarom de tweede route moest bestaan (Run B, 20 en 24 sep 2026).** `early_season_uplift`
    beantwoordt de vraag "er wordt nu meer gescoord dan het seizoensgemiddelde waarop mijn
    teamsterktes staan — hoeveel?". Hij doet dat door de verhouding lopend/vorig te poolen over alle
    competities van de dag en die dan met `EARLY_SEASON_PRIOR` naar 1.0 terug te trekken. Beide
    stappen zijn goed vroeg in het seizoen, waar één competitie na één speeldag ruis is, en beide
    zijn fout zodra een seizoen halverwege is:

    - **De verhouding meet dan iets anders.** Bij 27 van de 34 gespeelde speeldagen is
      `avg_xg` van het lopende seizoen een nette schatting van het volledige seizoensgemiddelde, en
      is `lopend / vorig` dus geen tijdseffect binnen een seizoen maar een **echt niveauverschil
      tussen twee seizoenen**. Terugtrekken naar 1.0 gooit dat verschil gedeeltelijk weg. Voor MLS
      op 24 sep 2026: gemeten verhouding 1.0301, uplift-factor 1.0232 — 0,7% te laag, en dat gat
      groeit met de rest van het seizoen mee.
    - **Het poolen loopt andersom.** Omdat de pool competitie-overstijgend is, drukt een
      halverwege lopende competitie haar eigen niveauverschil in de factor van álle andere. Dat is
      op 20 sep 2026 gebeurd: Eliteserien (21 speeldagen) en Allsvenskan (22) tilden de gepoolde
      factor over zeven competities naar 1.0600, en drie van de vijf bets van die dag stonden in die
      twee competities. Gebruik daarom `uplift_observations` om de pool te vullen; die laat precies
      de competities weg die hier op de `lopend`-route uitkomen.

    **Wat de `lopend`-route óók repareert, en dat is nieuw op 24 sep 2026: de noemer.**
    `avg_xg_per_match` is niet het niveau maar de **noemer** waartegen `team_strength` de
    teamsterktes normaliseert (zie `scale_level`, die hem daarom met opzet laat staan). Die
    teamsterktes komen sinds 3 sep uit `blend_seasons`, dus uit een **weging** van beide seizoenen
    met gewicht `n / (n + k)`. De noemer hoort diezelfde weging te krijgen, en die kreeg hij niet:
    elk runscript gaf tot nu toe het `avg_xg` van één seizoen mee. Voor MLS op 24 sep was dat het
    lopende (1.537) bij een blendgewicht van 0.758, waar 0.758 x 1.537 + 0.242 x 1.492 = 1.526
    hoort. Een noemer die 0,7% te hoog staat gaat in aanval **en** verdediging mee, dus in `lambda`
    kwadratisch: ongeveer 1,4% te weinig doelpunten. Klein, maar het is een fout die in elke
    wedstrijd van elke run zat, en hij hoort niet nog eens overgetypt te worden.

    `level_factor` blijft betekenen wat hij in `analyze_match_from_splits` betekent: de factor
    tussen het niveau dat hier wordt teruggegeven en het niveau waarin de splits zijn geméten. Op de
    `lopend`-route is dat `niveau lopend / niveau vorig`, want de splitsmethode leest de
    thuis/uit-reeksen van beide seizoenen samen en normaliseert op vorig seizoen. Zonder dat veld
    zou de splitsmethode de niveaukeuze **omgekeerd** verwerken — dezelfde fout die op 24 aug 2026
    bij de uplift is gevonden en gerepareerd.

    `cur=None`, een leeg lopend seizoen of nul gespeelde speeldagen geeft de `vorig+uplift`-route
    met het gedrag van vóór deze wijziging: bij `uplift_factor=1.0` is dat letterlijk het vorige
    seizoen.
    """
    prev_teams = prev.get("teams") or {}
    cur_teams = (cur or {}).get("teams") or {}
    played = matchdays_played(cur_teams)
    length = length if length is not None else season_length(prev_teams)
    avg_prev = _denominator(prev)
    xg_available = bool(prev.get("avg_xg_per_match"))

    if not cur_teams or played <= 0:
        home, away = _level(prev)
        league = scale_level(LeagueContext(home_goals_per_match=home, away_goals_per_match=away,
                                          avg_xg_per_match=avg_prev), uplift_factor)
        return LevelChoice(league=league, source="vorig+uplift", played=played, length=length,
                           share=None, ratio=None, uplift_factor=uplift_factor, blend_weight=0.0,
                           xg_available=xg_available,
                           reason="geen bruikbare stand van het lopende seizoen — niveau uit vorig "
                                  f"seizoen met de vroeg-seizoenscorrectie ({uplift_factor:.4f})")

    avg_cur = _denominator(cur)
    weight = blend_weight(played, k)
    denominator = weight * avg_cur + (1 - weight) * avg_prev
    ratio = (avg_cur / avg_prev) if avg_prev else None
    mature = season_is_mature(played, length, share)
    part = (played / length) if length else None

    if mature:
        home_cur, away_cur = _level(cur)
        home_prev, away_prev = _level(prev)
        prev_total = home_prev + away_prev
        factor = ((home_cur + away_cur) / prev_total) if prev_total else 1.0
        league = LeagueContext(home_goals_per_match=home_cur, away_goals_per_match=away_cur,
                               avg_xg_per_match=denominator, level_factor=factor)
        reason = (f"lopend seizoen op {played} van {length} speeldagen ({part:.0%}) — niveau "
                  f"rechtstreeks uit het lopende seizoen; de vroeg-seizoenscorrectie "
                  f"({uplift_factor:.4f}) is NIET toegepast, want bij deze stand meet "
                  f"lopend/vorig ({ratio:.4f}) een echt niveauverschil en geen tijdseffect")
        return LevelChoice(league=league, source="lopend", played=played, length=length,
                           share=part, ratio=ratio, uplift_factor=uplift_factor,
                           blend_weight=weight, xg_available=xg_available, reason=reason)

    home, away = _level(prev)
    league = scale_level(LeagueContext(home_goals_per_match=home, away_goals_per_match=away,
                                       avg_xg_per_match=denominator), uplift_factor)
    deel = f"{part:.0%}" if part is not None else "onbekend deel"
    reason = (f"lopend seizoen op {played} speeldagen van "
              f"{length if length else 'onbekend'} ({deel}) — onder {share:.0%}, dus niveau uit "
              f"vorig seizoen met de vroeg-seizoenscorrectie ({uplift_factor:.4f})")
    return LevelChoice(league=league, source="vorig+uplift", played=played, length=length,
                       share=part, ratio=ratio, uplift_factor=uplift_factor, blend_weight=weight,
                       xg_available=xg_available, reason=reason)


def uplift_observations(seasons: dict[str, tuple[dict, dict | None]], *,
                        share: float = SEASON_MATURE_SHARE,
                        ) -> tuple[list[tuple[float, float, int]], dict[str, str]]:
    """De waarnemingen voor `early_season_uplift`, zonder de competities die er niet in horen.

    Geeft `(observaties, overgeslagen)` terug; `overgeslagen` is `{competitie: reden}` en hoort in
    het runrapport, want een stil weggelaten waarneming is hetzelfde probleem als een stille
    truncatie in Stage 4.

    Twee redenen om een competitie weg te laten:

    1. **Halverwege haar seizoen** (op of boven `share`). Dat is de pooling-fout uit
       `league_level`: haar verhouding lopend/vorig is een niveauverschil tussen seizoenen, en die
       in de pool leggen tilt de factor van alle andere competities op. Op 20 sep 2026 deden
       Eliteserien en Allsvenskan dat, met een gepoolde factor van 1.0600 als gevolg.
    2. **Geen bruikbare xG in een van beide seizoenen.** `early_season_uplift` filtert die zelf al
       weg, maar dan zonder te zeggen welke; hier komt de reden mee.
    """
    observations: list[tuple[float, float, int]] = []
    skipped: dict[str, str] = {}
    for comp, (prev, cur) in seasons.items():
        if not prev or not cur:
            skipped[comp] = "geen stand van beide seizoenen"
            continue
        base, now = prev.get("avg_xg_per_match"), cur.get("avg_xg_per_match")
        played = matchdays_played(cur.get("teams") or {})
        if not base or not now:
            skipped[comp] = "geen xG in vorig of lopend seizoen"
            continue
        if played <= 0:
            skipped[comp] = "lopend seizoen nog niet begonnen"
            continue
        length = season_length(prev.get("teams") or {})
        if season_is_mature(played, length, share):
            skipped[comp] = (f"halverwege het seizoen ({played} van {length} speeldagen) — "
                             f"niveau komt uit het lopende seizoen, niet uit de gepoolde correctie")
            continue
        observations.append((base, now, played))
    return observations, skipped


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
                              rho: float = DEFAULT_RHO,
                              league: LeagueContext | None = None) -> MatchProbabilities:
    """Tweede kansschatting, op echte doelpunten in plaats van op xG.

    Dit is met opzet een andere doorsnede van dezelfde data: `analyze_match` normaliseert
    teamsterkte op het competitiegemiddelde en rekent met kansenkwaliteit, deze rekent met wat de
    thuisploeg thuis deed en de uitploeg uit. Waar beide methodes hetzelfde zeggen, hangt een edge
    niet aan één modelkeuze.

    Nut, concreet: op 9 aug 2026 gaf het xG-model Gil Vicente – Rio Ave +10.3 pp — nominaal de op
    één na grootste edge van die dag — terwijl deze methode op +2.7 pp uitkwam, onder de drempel.
    Groningen en Anderlecht werden door beide bevestigd en zijn wel gepubliceerd.

    **MULTIPLICATIEF SINDS 23 AUG 2026 — lees dit voordat je `league` weglaat.**

    Tot die datum deed deze functie `lambda_home = (aanval_thuis + verdediging_uit) / 2`: twee
    doelpuntgemiddeldes optellen en door twee delen. Dat is geen sterktemodel maar een gemiddelde,
    en middelen trekt naar het midden. Het gevolg was over 165 waarnemingen (22–23 aug) te meten:
    deze methode gaf longshots **+6.61 pp** meer kans dan de markt en favorieten **−11.86 pp**
    minder, terwijl `analyze_match` op dezelfde duels veel vlakker lag. Omdat `my_prob` het
    ongewogen gemiddelde van de twee is, sloeg die samendrukking door in elke gepubliceerde kans —
    en in de picks: **89% van alle picks die een ploeg speelden, speelde de zwakkere kant**, met
    een ROI van −29.7% tegen −14.4% voor de markten zonder kant.

    Geef je `league` mee, dan rekent deze functie net als `analyze_match` met verhoudingen:

        aanval_thuis   = (thuisdoelpunten per duel)   / competitiegemiddelde thuis
        verdediging_uit = (uitgoals tegen per duel)   / competitiegemiddelde thuis
        lambda_home     = competitiegemiddelde thuis x aanval_thuis x verdediging_uit

    Vermenigvuldigen behoudt de spreiding die middelen wegdrukt, en zet beide schatters van §1 op
    dezelfde grootheid — precies wat _shared-rules.md §6e als remedie aanwees.

    `league=None` houdt het oude additieve gedrag, alleen nog voor de historische ankers in de
    zelftest hieronder. Gebruik het niet in een run.

    **DE VROEG-SEIZOENSCORRECTIE WERKTE HIER OMGEKEERD — gerepareerd 24 aug 2026 (Run B).**
    De verhoudingen hierboven delen door het competitieniveau en vermenigvuldigen er daarna weer
    mee, zodat `lambda_home` netto op `(gf/duel) x (ga/duel) / niveau` uitkomt: **omgekeerd
    evenredig** met het niveau. Werd `league` door `scale_level` opgeschroefd, dan voorspelde deze
    methode dus mínder doelpunten in plaats van meer. Gemeten op een niveaucorrectie van +10%:
    lambda-som 2.683 -> 2.439, oftewel 9% omlaag waar 10% omhoog bedoeld was.

    Dat is geen detail dat alleen de doelpuntenmarkten raakt. Omdat §1 `my_prob` als het ongewogen
    gemiddelde van deze methode en `analyze_match` neemt, en die twee sinds Stage 5 tegengesteld op
    de correctie reageerden, **hief de correctie zichzelf grotendeels op in elke gepubliceerde
    kans**. Dat verklaart waarom het effect van de correctie tegenover de markt in de runrapporten
    van 22 en 23 aug 2026 steeds "marginaal" heette (4.83 -> 4.78 pp gemiddelde absolute fout),
    terwijl de gemeten factor die dagen 1.069 resp. 1.084 was.

    De reparatie deelt door het **ongeschaalde** niveau (`LeagueContext.level_factor`) en
    vermenigvuldigt met het geschaalde, waarna `lambda` net als bij `analyze_match` recht evenredig
    met de factor meebeweegt. Bij `level_factor = 1.0` — elke aanroep zonder `scale_level` — is er
    geen verschil met het gedrag van vóór deze datum.

    **WAT HIER NIET IN ZIT, EN WAAROM — een negatief resultaat, om herhaling te voorkomen.**
    Bij het bouwen hiervan lag het voor de hand om de verhoudingen óók te regresseren naar het
    competitiegemiddelde, naar rato van de steekproef: een thuisreeks van 11 duels (Denemarken na
    de kampioenssplitsing) is nu eenmaal ruiziger dan een van 19. Twee varianten zijn gebouwd en
    gemeten op de 25 duels van 23 aug 2026, tegen de de-vigde marktkans:

    | variant | longshots | favorieten | gem. abs. fout |
    |---|---|---|---|
    | additief (t/m 22 aug) | +6.02 | −11.02 | 6.23 |
    | **multiplicatief, geen regressie** | **+4.09** | **−7.38** | **5.61** |
    | multiplicatief + `n/(n+9.5)` | +5.53 | −10.09 | 5.87 |
    | multiplicatief + gemeten Bühlmann-credibiliteit | +6.09 | −11.11 | 6.10 |

    Beide regressievarianten maken het dus **slechter**, en de netjes uit de competitiespreiding
    gemeten credibiliteit het slechtst van de drie — die kwam op Z = 0.36 tot 0.76 uit en drukte
    daarmee precies de spreiding weg die het probleem was. Regressie naar het gemiddelde ís de
    samendrukking: hij duwt elke wedstrijd richting "de ploegen ontlopen elkaar niet veel", en
    tegen een markt die favoriet en underdog wél scheidt, komt dat er als schijnedge op de zwakke
    kant uit. Ruis in de invoer is een echt probleem, maar regresseren is er niet het antwoord op.
    """
    if league is None:
        lambda_home = (home.home_gf / home.home_played + away.away_ga / away.away_played) / 2
        lambda_away = (away.away_gf / away.away_played + home.home_ga / home.home_played) / 2
    else:
        base_home = league.home_goals_per_match
        base_away = league.away_goals_per_match
        # De noemer is het niveau waarin de splits zelf gemeten zijn — dus vóór de
        # vroeg-seizoenscorrectie. Zie `LeagueContext.level_factor`: met de geschaalde waarde als
        # noemer werkt de correctie omgekeerd, omdat lambda dan met 1/factor gaat in plaats van
        # met factor. Bij level_factor 1.0 verandert er niets aan het gedrag van vóór 24 aug 2026.
        norm_home = base_home / league.level_factor
        norm_away = base_away / league.level_factor

        # Elke verhouding krijgt de regressie die bij háár eigen steekproef hoort. Een thuis/uit-
        # split gaat over de helft van een seizoen, en na een kampioenssplitsing (Denemarken,
        # België) over nog minder: 11 duels op 23 aug 2026. Zonder deze weging telde zo'n reeks
        # van 11 even zwaar als een van 19, en dat gaf op die dag de grootste geclaimde edge van
        # de run (Sønderjyske, +31 pp op de splitsmethode alleen) — op de dunste data van de dag.
        attack_home = (home.home_gf / home.home_played) / norm_home
        defence_away = (away.away_ga / away.away_played) / norm_home
        attack_away = (away.away_gf / away.away_played) / norm_away
        defence_home = (home.home_ga / home.home_played) / norm_away
        lambda_home = base_home * attack_home * defence_away
        lambda_away = base_away * attack_away * defence_home
    grid = score_grid(lambda_home, lambda_away, rho)
    home_p = sum(grid[i][j] for i in range(MAX_GOALS + 1) for j in range(MAX_GOALS + 1) if i > j)
    draw_p = sum(grid[i][i] for i in range(MAX_GOALS + 1))
    over_p = sum(grid[i][j] for i in range(MAX_GOALS + 1) for j in range(MAX_GOALS + 1) if i + j > 2)
    btts_p = sum(grid[i][j] for i in range(1, MAX_GOALS + 1) for j in range(1, MAX_GOALS + 1))
    return MatchProbabilities(lambda_home, lambda_away, home_p, draw_p,
                              1 - home_p - draw_p, over_p, btts_p, grid)


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
    # LET OP — dit anker is expliciet op shrink 0.80 en niet op de standaard. Dat was het tot
    # 19 sep 2026 wel, en toen `DEFAULT_SHRINK` die dag van 0.80 naar 1.00 ging, is dit anker
    # meeverschoven naar 44.3% en ging deze assert kapot. Gevolg: `python3 scripts/model.py`
    # brak op regel 1 van de zelftest en ALLES eronder heeft vijf dagen niet gedraaid — ook de
    # weegregelankers, waarvan hieronder staat dat ze bestaan omdat een stille verschuiving daar
    # elke topselectie verschuift. Gevonden op 24 sep 2026. Een historisch anker hoort zijn eigen
    # parameters mee te nemen in plaats van de standaard te volgen, want anders meet hij de
    # standaard en niet de wedstrijd.
    probs08 = analyze_match(standard, cercle, league, shrink=0.80)
    probs = analyze_match(standard, cercle, league)
    print(f"Standard {probs.home * 100:.1f}%  Gelijk {probs.draw * 100:.1f}%  Cercle {probs.away * 100:.1f}%"
          f"   (shrink 0.80, het anker van 8 aug: Cercle {probs08.away * 100:.1f}%)")
    assert abs(probs08.away - 0.418) < 0.002, f"verwacht ~41.8% bij shrink 0.80, kreeg {probs08.away * 100:.1f}%"
    # En de huidige standaard, zodat een volgende wijziging van DEFAULT_SHRINK hier opvalt in
    # plaats van de hele zelftest om te leggen.
    assert abs(probs.away - 0.443) < 0.002, f"verwacht ~44.3% bij shrink {DEFAULT_SHRINK}, kreeg {probs.away * 100:.1f}%"
    print(f"Edge op Cercle @2.85: {edge_pp(probs08.away, 2.85):+.1f} pp bij shrink 0.80 "
          f"(verwacht +6.7 pp) · {edge_pp(probs.away, 2.85):+.1f} pp bij de standaard {DEFAULT_SHRINK}")

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

    # Markten (toegevoegd 14 aug 2026). Deze acht controles zijn er omdat een handicap of totaal
    # met push niet zomaar een kans is: bij een push krijg je je inzet terug in plaats van te
    # verliezen, en bij een kwartlijn staat er maar de helft op elke lijn. De ankers hieronder
    # leggen vast dat de nieuwe rekenweg op de bekende gevallen exact samenvalt met de oude.
    probs = analyze_match(standard, cercle, league)
    grid = probs.grid

    # 1-2. Een halve lijn kent geen push, dus AH -0.5 is exact de thuiszege en AH +0.5 exact 1X.
    assert abs(asian_prob(grid, -0.5, "home", 2.0) - probs.home) < 1e-9
    assert abs(asian_prob(grid, 0.5, "home", 2.0) - probs.dc_1x) < 1e-9
    # 3. Uit op de spiegellijn is het complement: samen precies 1.
    assert abs(asian_prob(grid, -0.5, "home", 2.0) + asian_prob(grid, 0.5, "away", 2.0) - 1) < 1e-9
    # 4-5. De generieke totalenweg moet het bestaande veld reproduceren.
    assert abs(totals_prob(grid, 2.5, "over", 2.0) - probs.over_2_5) < 1e-9
    assert abs(totals_prob(grid, 2.5, "under", 2.0) - probs.under_2_5) < 1e-9
    # 6. Hele lijn: winst, push en verlies vormen samen de hele kansmassa.
    win, push, lose = _payout_probs(grid, 0.0, "home")
    assert abs(win + push + lose - 1) < 1e-9
    # 7. Draw No Bet moet nul edge geven op zijn eigen eerlijke koers, (1 - P(X)) / P(1).
    fair = (1 - probs.draw) / probs.home
    assert abs(edge_pp(dnb_prob(grid, "home", fair), fair)) < 1e-9
    # 8. Een kwartlijn is per definitie het gemiddelde van zijn twee buurlijnen.
    assert abs(asian_prob(grid, -0.25, "home", 2.1)
               - (asian_prob(grid, -0.5, "home", 2.1) + asian_prob(grid, 0.0, "home", 2.1)) / 2) < 1e-12
    # Weegregel (vastgesteld 14 aug 2026). Verankerd op de wedstrijden van die dag, want dit is de
    # regel die bepaalt wélke van vijf even geldige uitdrukkingen van dezelfde mening wordt
    # gepubliceerd. Verschuift hij ongemerkt, dan verschuift daarmee elke topselectie.
    viborg = [("1X2 AGF wint", 17.59, 0.4576), ("AH +0.5 AGF", 15.52, 0.690),
              ("DNB AGF", 15.16, 0.550), ("DC AGF of gelijk", 12.18, 0.690),
              ("AH +1.0 AGF", 8.76, 0.807)]
    beste = max(viborg, key=lambda r: selection_score(r[1], r[2]))
    assert beste[0] == "AH +0.5 AGF", f"verwacht de handicap, kreeg {beste[0]}"
    assert abs(selection_score(17.59, 0.4576) - 8.05) < 0.01     # 1X2, tweede
    assert abs(selection_score(15.52, 0.690) - 10.71) < 0.01     # AH +0.5, eerste
    # Telstar - Sparta: daar wijst de regel wél naar de 1X2, dus hij kiest niet blind een handicap.
    telstar = [("1X2 Telstar", 5.67, 0.4877), ("Over 2.5", 3.55, 0.649), ("AH -1.0", 3.05, 0.344)]
    assert max(telstar, key=lambda r: selection_score(r[1], r[2]))[0] == "1X2 Telstar"
    # LIGHT weegt half zo zwaar, precies de verhouding van de twee edge-drempels.
    assert abs(selection_score(10.0, 0.5, "LIGHT") - selection_score(10.0, 0.5, "FULL") / 2) < 1e-12
    print(f"Weegregel: AH +0.5 AGF {selection_score(15.52, 0.690):.2f} verslaat "
          f"1X2 AGF {selection_score(17.59, 0.4576):.2f}")

    print(f"Markten: AH -0.5 thuis {asian_prob(grid, -0.5, 'home', 2.0) * 100:.1f}%  "
          f"DNB thuis @2.34 {dnb_prob(grid, 'home', 2.34) * 100:.1f}%  "
          f"Over 3.5 {totals_prob(grid, 3.5, 'over', 2.0) * 100:.1f}%  "
          f"BTTS {probs.btts * 100:.1f}%")

    # Niveaukeuze (toegevoegd 24 sep 2026). Verankerd op MLS 2025/2026, de competitie waarop de
    # regel is ontstaan, met de cijfers zoals `fetch_league_stats` ze die dag gaf.
    _mls_prev = {"avg_xg_per_match": 1.4921296296296294, "home_goals_per_match": 1.6392156862745098,
                 "away_goals_per_match": 1.3607843137254902,
                 "teams": {f"t{i}": {"played": 34} for i in range(30)}}
    _mls_cur = {"avg_xg_per_match": 1.5370179948586125, "home_goals_per_match": 1.8195876288659794,
                "away_goals_per_match": 1.3891752577319587,
                "teams": {f"t{i}": {"played": 27} for i in range(30)}}
    assert season_length(_mls_prev["teams"]) == 34
    assert matchdays_played(_mls_cur["teams"]) == 27
    # MLS heeft 30 ploegen en 34 speeldagen: 2 x (n - 1) = 58 zou hier fout zijn, en dat is precies
    # waarom `season_length` meet in plaats van rekent.
    assert season_length(_mls_prev["teams"]) != 2 * (30 - 1)

    _keuze = league_level(_mls_prev, _mls_cur, uplift_factor=1.0232)
    assert _keuze.source == "lopend", _keuze.source
    # Het niveau is dat van het lopende seizoen, niet vorig seizoen x de correctie.
    assert abs(_keuze.league.home_goals_per_match - 1.8195876288659794) < 1e-12
    # De noemer is de BLEND, niet één van de twee seizoenen. Dat is de stille fout van vóór 24 sep.
    _w = blend_weight(27, CREDIBILITY_K)
    assert abs(_keuze.league.avg_xg_per_match
               - (_w * 1.5370179948586125 + (1 - _w) * 1.4921296296296294)) < 1e-12
    assert _keuze.league.avg_xg_per_match < 1.5370179948586125   # lager dan het lopende alleen
    assert _keuze.league.avg_xg_per_match > 1.4921296296296294   # hoger dan het vorige alleen
    # `level_factor` moet de verhouding tussen het teruggegeven niveau en dat van vorig seizoen
    # zijn, want de splitsmethode normaliseert op het seizoen waarin de splits zijn gemeten.
    assert abs(_keuze.league.level_factor
               - (1.8195876288659794 + 1.3891752577319587)
               / (1.6392156862745098 + 1.3607843137254902)) < 1e-12
    # En hij mag niet 1.0 zijn: dan zou `analyze_match_from_splits` de niveaukeuze omgekeerd
    # verwerken, dezelfde fout die op 24 aug 2026 bij de uplift is gevonden.
    assert _keuze.league.level_factor > 1.0

    # Een jong seizoen houdt de oude route, inclusief de correctie.
    _jong = {**_mls_cur, "teams": {f"t{i}": {"played": 6} for i in range(30)}}
    _k2 = league_level(_mls_prev, _jong, uplift_factor=1.0600)
    assert _k2.source == "vorig+uplift", _k2.source
    assert abs(_k2.league.home_goals_per_match - 1.6392156862745098 * 1.0600) < 1e-12
    assert abs(_k2.league.level_factor - 1.0600) < 1e-12
    # Zonder lopend seizoen is het letterlijk vorig seizoen bij factor 1.0.
    _k3 = league_level(_mls_prev, None)
    assert _k3.source == "vorig+uplift" and _k3.blend_weight == 0.0
    assert abs(_k3.league.avg_xg_per_match - 1.4921296296296294) < 1e-12
    assert abs(_k3.league.level_factor - 1.0) < 1e-12
    # Onbekende seizoenslengte kiest de veilige kant: de oude route.
    assert league_level({**_mls_prev, "teams": {}}, _mls_cur).source == "vorig+uplift"
    # Geen xG: dan is het doelpuntgemiddelde de noemer, en die terugval hoort hier en niet in een
    # runscript. Zes van de zeventien Run B-competities zitten in dit geval.
    _geen_xg = {"avg_xg_per_match": None, "home_goals_per_match": 1.4, "away_goals_per_match": 1.2,
                "teams": {f"t{i}": {"played": 30} for i in range(16)}}
    _k4 = league_level(_geen_xg, None)
    assert abs(_k4.league.avg_xg_per_match - 1.3) < 1e-12 and _k4.xg_available is False

    # De pool laat een halverwege lopende competitie weg. Cijfers van 20 sep 2026, de dag waarop
    # Eliteserien (21 speeldagen) en Allsvenskan (22) de gepoolde factor naar 1.0600 tilden.
    _eli_prev = {"avg_xg_per_match": 1.5425, "teams": {f"t{i}": {"played": 30} for i in range(16)}}
    _eli_cur = {"avg_xg_per_match": 1.6831288343558284,
                "teams": {f"t{i}": {"played": 21} for i in range(16)}}
    _gre_prev = {"avg_xg_per_match": 1.3063559322033897,
                 "teams": {f"t{i}": {"played": 26} for i in range(14)}}
    _gre_cur = {"avg_xg_per_match": 1.33, "teams": {f"t{i}": {"played": 5} for i in range(14)}}
    _obs, _weg = uplift_observations({"Eliteserien (NOR)": (_eli_prev, _eli_cur),
                                     "Greek Super League (GRE)": (_gre_prev, _gre_cur)})
    assert [o[2] for o in _obs] == [5], _obs
    assert "Eliteserien (NOR)" in _weg and "Greek Super League (GRE)" not in _weg
    assert "halverwege" in _weg["Eliteserien (NOR)"]

    print(f"Niveaukeuze: MLS 27/34 speeldagen -> route '{_keuze.source}', niveau "
          f"{_keuze.league.home_goals_per_match:.3f}/{_keuze.league.away_goals_per_match:.3f}, "
          f"noemer {_keuze.league.avg_xg_per_match:.4f} (blendgewicht {_keuze.blend_weight:.3f}), "
          f"level_factor {_keuze.league.level_factor:.4f}")
    print("Zelftest geslaagd.")
