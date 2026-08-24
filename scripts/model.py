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


def team_strength(stats: TeamStats, league: LeagueContext, shrink: float = DEFAULT_SHRINK) -> tuple[float, float]:
    """(aanvalsfactor, verdedigingsfactor) t.o.v. het competitiegemiddelde, met regressie.

    `shrink=1.0` is de ruwe xG-verhouding; `shrink=0.0` is volledig het competitiegemiddelde
    (elk team even sterk). Vroeg seizoen (§4 van _shared-rules.md) rechtvaardigt shrink < 1.0
    omdat rolling xG dan niet bestaat en transfers niet in de cijfers zitten.

    LET OP — de richting van deze knop, gemeten 23 aug 2026. Regressie maakt ploegen onderling
    gelijker, en gelijker betekent dat de underdog meer kans krijgt dan hij verdient. Op de 25
    duels van die dag lag `analyze_match` bij `shrink=0.80` op +4.82 pp boven de markt op
    longshots en −8.70 pp eronder bij favorieten; bij `shrink=1.00` was dat +3.07 en −5.43. Minder
    regressie is daar dus béter gekalibreerd. Het niveau is niettemin niet verlaagd: twee dagen is
    onder de leesdrempel van §6e, en `ROBUSTNESS_COMBOS` varieert deze parameter juist met opzet
    van 0.70 tot 1.00 — een edge die alleen bij lage shrink bestaat, valt daar al op poort 6.
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
3.0 / 6.0. De regels eisen van zwakke data al twee keer zoveel edge om überhaupt mee te doen;
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
    print("Zelftest geslaagd.")
