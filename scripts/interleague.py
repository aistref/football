"""Krachtsverschil tussen nationale competities, gemeten op Europese uitslagen.

WAAROM DIT BESTAAT. `model.analyze_match` normaliseert elke ploeg op het gemiddelde van zijn
**eigen** competitie. Bij een binnenlands duel is dat precies goed; bij een Europees duel staan de
twee sterktes op onvergelijkbare schalen en kent het model het niveauverschil tussen die twee
competities niet. Doorrekenen levert dan geen kansschatting op maar dat ontbrekende niveauverschil,
verkleed als edge — gemeten op 19 aug 2026 bij Atlético – Málaga: zeventien procentpunt op één
uitwinst. Daarom stonden alle kruis-grensduels van 18 aug t/m 8 sep 2026 op `data_tier = NONE`.

Voor divisies BINNEN één land is dat gat gemeten (`promotion.MEASURED_TIER2_GAP`) omdat ploegen
daar fysiek tussen bewegen: Burnley speelde vorig seizoen Premier League en dit seizoen
Championship. Tussen twee landen gebeurt dat niet. De enige brug is de Europese wedstrijd zelf, en
dat is precies waarop deze factoren zijn gemeten.

HET MODEL. Voor een Europees duel tussen thuisploeg i (competitie A) en uitploeg j (competitie B):

    lambda_thuis = H * (att_i * A_A) * (dfn_j * D_B)
    lambda_uit   = W * (att_j * A_B) * (dfn_i * D_A)

`att` en `dfn` zijn de aanval- en verdedigingsverhouding tegenover het gemiddelde van de eigen
competitie in het vorige afgeronde seizoen, met dezelfde `shrink` als `model.team_strength`.
`A_L` en `D_L` zijn de twee onbekenden per competitie. Dit is exact de vorm van
`model.match_lambdas` met één extra factor per ploeg, en daarom kan het resultaat als een
OMREKENING worden toegepast — net als `promotion.convert` — zonder dat er aan het model iets
verandert.

DE METING. Poisson-MLE met multiplicatieve updates op **2111 kruis-grensduels** uit UCL, UEL en
UECL, seizoenen 2021/2022 t/m 2025/2026, alle uitslagen van Fotmob. Knock-outduels die in
verlenging of op strafschoppen zijn beslist staan er NIET in (61 stuks): `status.scoreStr` is de
eindstand en §6d rekent af op 90 minuten. Regularisatie met een pseudo-waarneming die naar 1
trekt, sterkte 5 "pseudo-doelpunten", uit-steekproef gekozen.

UIT-STEEKPROEF GECONTROLEERD. Gefit op 2021/2022 t/m 2024/2025 (1622 duels) en getest op
2025/2026 (489 duels, die bij het fitten geen enkele rol speelden):

| 1X2-Brier op 2025/2026 | |
|---|---|
| zonder competitiefactor (wat het model tot 8 sep 2026 deed) | 0.66249 |
| met competitiefactor | **0.56869** |
| ter ijking: 1/3-1/3-1/3 gokken | 0.66667 |

Lees die derde regel. **Zonder deze factoren was het model op kruis-grensduels niet te
onderscheiden van blind gokken** — dat is de kwantitatieve rechtvaardiging achter de NONE-regel
van 18 augustus, en tegelijk de reden dat deze correctie zoveel oplevert. De winst houdt stand in
elke deelgroep: league phase −0.103, knock-out en voorrondes −0.065, UCL −0.089, UEL −0.102,
UECL −0.090.

WAT DIT **NIET** IS. Het model is hiermee niet beter dan de bookmaker op Europese duels. Op de zes
Champions League-duels van 8 sep 2026 week het na omrekening gemiddeld 11.9 procentpunt af van de
de-vigde marktkans (bereik 2.2 tot 20.4). Deze factoren repareren de competitieschaal; ze
repareren niet dat de teamsterkte uit doelpunten van vorig seizoen komt. Daarom:

* een omgerekende ploeg is **nooit** `FULL` — zelfde regel als bij `promotion.convert`, en om
  dezelfde reden: de omrekening haalt de systematische fout eruit, niet de onzekerheid;
* `LIGHT` betekent `EDGE_THRESHOLD_LIGHT` = 16.0 procentpunt, en daar bovenop gaat nog de
  herijking van §1g. Bets op Europese duels blijven dus zeldzaam, en dat hoort zo.

RECENCY IS GEPROBEERD EN AFGEWEZEN. Of recentere seizoenen zwaarder moeten wegen is nagemeten met
een exponentiële halfwaardetijd over dezelfde rollende oorsprong. Halfwaardetijd 5 jaar gaf 0.58614
tegen 0.58630 voor vlakke gewichten — verwaarloosbaar — en een halfwaardetijd van 1 jaar was
duidelijk SLECHTER (0.58727). Dezelfde les als bij de afgewezen rollende xG in §4 van
_shared-rules.md: meer waarnemingen verslaan hier de slimmere bewerking. Dus vlakke gewichten.

TE HERZIEN. De factoren zijn gemeten op de seizoenen t/m 2025/2026 en drift is echt: over
2021-2023 tegen 2024-2026 verschuift Nederland van 1.25 naar 0.87 en Frankrijk van 1.35 naar 1.64
(Spearman +0.87 tussen beide perioden voor competities met >= 40 duels in allebei, mediane
afwijking een factor 1.19). Hermeten na afloop van het Europese seizoen 2026/2027.
"""
from __future__ import annotations

from dataclasses import dataclass

from scripts.model import DEFAULT_SHRINK, LeagueContext, TeamSplits, TeamStats

# Het Europese doelpuntenniveau uit dezelfde fit: thuis- en uitdoelpunten per duel voor twee
# ploegen die na omrekening allebei exact gemiddeld zijn.
EURO_HOME_GOALS = 1.5722
EURO_AWAY_GOALS = 1.1790

# De shrink waarmee de factoren zijn gefit. Moet gelijk zijn aan `model.DEFAULT_SHRINK`; staat hier
# apart omdat de omrekening hem moet terugrekenen (zie `_deshrink`).
FIT_SHRINK = 0.80

# Minimaal aantal Europese duels waarin ploegen uit een competitie zijn waargenomen. Onder deze
# grens is de factor vrijwel volledig door de regularisatie bepaald en dus geen meting maar een
# aanname: die competities blijven `NONE`. Bij >= 40 duels is de factor stabiel over de tijd
# (Spearman +0.87, mediane afwijking factor 1.19); bij minder loopt dat op naar 1.36.
MIN_MATCHES = 40

# Bereik waarbinnen de omgerekende aanval en verdediging in de meting daadwerkelijk zijn
# waargenomen (1e tot 99e percentiel over alle 4222 ploegwaarnemingen). Buiten dit bereik is er
# geen meting en dus geen bet — dit is de kruis-grensversie van `promotion.conversion_in_range`,
# en hij is er om dezelfde reden: extrapoleren levert schijn-edge op die alle andere poorten haalt.
ATTACK_RANGE = (0.585, 2.432)
DEFENCE_RANGE = (0.388, 1.446)

# ccode -> (A = aanval, D = verdediging, n = Europese duels in de meting).
# A hoog = ploegen uit deze competitie scoren meer dan hun binnenlandse cijfers doen vermoeden;
# D hoog = ze krijgen meer tegen. De sterkte-index A/D staat in de tabel hieronder ter illustratie
# en wordt nergens in de code gebruikt — het model rekent met A en D apart.
#
#   cc     A       D      n     A/D            cc     A       D      n     A/D
#   ENG  1.623   0.609   400   2.67           SUI  0.831   1.335    97   0.62
#   GER  1.389   0.745   359   1.86           GRE  0.795   1.308   128   0.61
#   ITA  1.279   0.722   357   1.77           SCO  0.768   1.469   108   0.52
#   ESP  1.400   0.802   364   1.75           AUT  0.669   1.306   122   0.51
#   FRA  1.254   0.798   286   1.57           CYP  0.604   1.207    74   0.50
#   POR  1.038   0.970   205   1.07           SWE  0.657   1.324    65   0.50
#   NED  1.095   1.079   220   1.02           ISR  0.677   1.398    57   0.48
#   DEN  1.010   1.074    97   0.94           ROU  0.602   1.262    44   0.48
#   BEL  0.942   1.006   181   0.94           UKR  0.639   1.408    85   0.45
#   POL  0.872   1.021    79   0.85           AZE  0.711   1.748    42   0.41
#   TUR  0.989   1.201   137   0.82           SRB  0.624   1.761    73   0.35
#   NOR  0.904   1.113    85   0.81           BUL  0.489   1.487    45   0.33
#   CRO  0.802   1.198    48   0.67
#   HUN  0.809   1.268    44   0.64
#   CZE  0.794   1.265   132   0.63
FACTORS: dict[str, tuple[float, float, int]] = {
    "ENG": (1.6225, 0.6089, 400), "GER": (1.3889, 0.7454, 359),
    "ITA": (1.2790, 0.7220, 357), "ESP": (1.4002, 0.8016, 364),
    "FRA": (1.2535, 0.7984, 286), "POR": (1.0384, 0.9698, 205),
    "NED": (1.0953, 1.0787, 220), "DEN": (1.0101, 1.0741,  97),
    "BEL": (0.9424, 1.0058, 181), "POL": (0.8723, 1.0205,  79),
    "TUR": (0.9888, 1.2005, 137), "NOR": (0.9044, 1.1130,  85),
    "CRO": (0.8023, 1.1984,  48), "HUN": (0.8092, 1.2675,  44),
    "CZE": (0.7941, 1.2649, 132), "SUI": (0.8313, 1.3347,  97),
    "GRE": (0.7950, 1.3077, 128), "SCO": (0.7678, 1.4690, 108),
    "AUT": (0.6694, 1.3058, 122), "CYP": (0.6044, 1.2070,  74),
    "SWE": (0.6573, 1.3235,  65), "ISR": (0.6774, 1.3981,  57),
    "ROU": (0.6019, 1.2615,  44), "UKR": (0.6389, 1.4080,  85),
    "AZE": (0.7112, 1.7483,  42), "SRB": (0.6243, 1.7614,  73),
    "BUL": (0.4892, 1.4866,  45),
}


# ccode -> Fotmob-id van de HOOGSTE divisie van dat land. Dit is een controle, geen lijst om uit
# te kiezen: `details.primaryLeagueId` van een ploeg moet hiermee overeenkomen, anders speelt hij
# niet in de competitie waarop de factor van dat land is gemeten (bijvoorbeeld een bekerwinnaar
# uit de tweede divisie) en is er geen geldige omrekening.
TOP_DIVISION_ID: dict[str, int] = {
    "ENG": 47, "GER": 54, "ITA": 55, "ESP": 87, "FRA": 53, "POR": 61, "NED": 57, "DEN": 46,
    "BEL": 40, "POL": 196, "TUR": 71, "NOR": 59, "CRO": 252, "HUN": 212, "CZE": 122, "SUI": 69,
    "GRE": 135, "SCO": 64, "AUT": 38, "CYP": 136, "SWE": 67, "ISR": 127, "ROU": 189, "UKR": 441,
    "AZE": 262, "SRB": 182, "BUL": 270,
}


class InterLeagueError(RuntimeError):
    """Geen gemeten factor voor deze competitie — de aanroeper hoort `NONE` te zetten."""


@dataclass(frozen=True)
class Converted:
    """Een ploeg, omgerekend naar de Europese schaal."""
    stats: TeamStats
    splits: TeamSplits | None
    attack: float          # omgerekende aanvalsverhouding (1.0 = Europees gemiddeld)
    defence: float         # omgerekende verdedigingsverhouding (lager = beter)
    in_range: bool
    note: str


def reference_league() -> LeagueContext:
    """De `LeagueContext` waarin twee omgerekende ploegen tegen elkaar gezet mogen worden."""
    return LeagueContext(home_goals_per_match=EURO_HOME_GOALS,
                         away_goals_per_match=EURO_AWAY_GOALS,
                         avg_xg_per_match=(EURO_HOME_GOALS + EURO_AWAY_GOALS) / 2)


def _deshrink(target: float, shrink: float = DEFAULT_SHRINK) -> float:
    """De waarde die in `TeamStats` moet staan zodat `team_strength` er `target` van maakt.

    `model.team_strength` rekent `1 + shrink * (ratio - 1)` en wordt dus ná deze omrekening nog
    een keer over het resultaat gehaald. De factoren zijn gefit op de ratio ná die shrink, dus
    zonder deze terugrekening zou de competitiecorrectie er een tweede keer doorheen gedrukt
    worden en verdwijnt vier vijfde van het effect.

    Let op wat dit betekent voor poort 6: `robustness_check` varieert `shrink` van 0.70 tot 1.00
    en verandert daarmee hoe sterk de competitieverschillen doorwerken. Dat is precies wat die
    poort hoort te doen — een edge die alleen bestaat wanneer het competitieverschil maximaal
    meetelt, hoort daar te sneuvelen.
    """
    return 1 + (target - 1) / shrink


def convert(ccode: str, gf: int, ga: int, played: int,
            domestic_goals_per_team_per_match: float,
            *, home: dict | None = None, away: dict | None = None,
            shrink: float = DEFAULT_SHRINK) -> Converted:
    """Reken één ploeg om van zijn eigen competitie naar de Europese schaal.

    `gf`, `ga`, `played` en `domestic_goals_per_team_per_match` komen uit de stand van het laatst
    afgeronde binnenlandse seizoen — dezelfde bron waarop de factoren zijn gemeten. `home` en
    `away` zijn de thuis/uit-rijen van diezelfde stand ({"played","gf","ga"}), voor de tweede
    methode van §1; laat ze weg als die er niet zijn.

    Gooit `InterLeagueError` als er geen gemeten factor is. Dat is met opzet luidruchtig: stil
    terugvallen op factor 1.0 is precies hoe een kruis-grensduel als gewone wedstrijd zou
    doorglippen, en dat is de fout die deze module moet wegnemen.
    """
    entry = FACTORS.get((ccode or "").upper())
    if entry is None:
        raise InterLeagueError(
            f"geen gemeten competitiefactor voor {ccode!r} — minder dan {MIN_MATCHES} Europese "
            f"duels in de meting, of een competitie die er niet in zit")
    A, D, n = entry
    if not played or not domestic_goals_per_team_per_match:
        raise InterLeagueError(f"{ccode}: geen bruikbare binnenlandse stand (played={played})")

    raw_attack = (gf / played) / domestic_goals_per_team_per_match
    raw_defence = (ga / played) / domestic_goals_per_team_per_match
    # Eerst dezelfde shrink als de fit, dan de competitiefactor. De volgorde is niet vrij: de
    # factoren zijn op precies deze samenstelling gemeten.
    attack = (1 + FIT_SHRINK * (raw_attack - 1)) * A
    defence = (1 + FIT_SHRINK * (raw_defence - 1)) * D

    in_range = (ATTACK_RANGE[0] <= attack <= ATTACK_RANGE[1]
                and DEFENCE_RANGE[0] <= defence <= DEFENCE_RANGE[1])
    problems = []
    if not ATTACK_RANGE[0] <= attack <= ATTACK_RANGE[1]:
        problems.append(f"aanval {attack:.3f} buiten {ATTACK_RANGE[0]}-{ATTACK_RANGE[1]}")
    if not DEFENCE_RANGE[0] <= defence <= DEFENCE_RANGE[1]:
        problems.append(f"verdediging {defence:.3f} buiten {DEFENCE_RANGE[0]}-{DEFENCE_RANGE[1]}")

    level = reference_league().avg_xg_per_match
    stats = TeamStats(xg=_deshrink(attack, shrink) * level * played,
                      xga=_deshrink(defence, shrink) * level * played,
                      matches_played=played)

    splits = None
    if home and away and home.get("played") and away.get("played"):
        # Zelfde bewerking op de thuis/uit-helften: eerst de verhouding in de eigen competitie,
        # dan de competitiefactor, dan het Europese niveau.
        def side(row: dict, factor: float, rate: float) -> int:
            r = (row["gf"] / row["played"]) / domestic_goals_per_team_per_match
            return max(0, round((1 + FIT_SHRINK * (r - 1)) * factor * rate * row["played"]))

        def conceded(row: dict, factor: float, rate: float) -> int:
            r = (row["ga"] / row["played"]) / domestic_goals_per_team_per_match
            return max(0, round((1 + FIT_SHRINK * (r - 1)) * factor * rate * row["played"]))

        splits = TeamSplits(
            home_gf=side(home, A, EURO_HOME_GOALS),
            home_ga=conceded(home, D, EURO_AWAY_GOALS),
            home_played=home["played"],
            away_gf=side(away, A, EURO_AWAY_GOALS),
            away_ga=conceded(away, D, EURO_HOME_GOALS),
            away_played=away["played"])

    note = (f"{ccode}: binnenlandse verhouding aanval {raw_attack:.3f} / verdediging "
            f"{raw_defence:.3f} over {played} duels, omgerekend met de gemeten Europese "
            f"competitiefactor x{A:.3f}/{D:.3f} (n={n} Europese duels) naar {attack:.3f}/"
            f"{defence:.3f}"
            + ("; " + ", ".join(problems) if problems else "; binnen het gemeten bereik"))
    return Converted(stats=stats, splits=splits, attack=attack, defence=defence,
                     in_range=in_range, note=note)


def covered(ccode: str) -> bool:
    """Heeft deze competitie een gemeten factor? Zo nee: `NONE`, geen bet."""
    return (ccode or "").upper() in FACTORS


# --------------------------------------------------------------------------------------------
# Opzoeking: van een Fotmob-ploeg-id naar een omgerekende ploeg. Dit staat hier en niet in het
# dagscript omdat het de plek is waar de poorten zitten — een dagscript dat dit zelf naschrijft
# kan er stilzwijgend eentje overslaan.
# --------------------------------------------------------------------------------------------

def team_country(team_id: int | str) -> tuple[str | None, int | None, str | None]:
    """(ccode, primaryLeagueId, competitienaam) van een ploeg, uit Fotmob.

    Eén verzoek per ploeg, en het alternatief is 27 competitiestanden aflopen. `country` is het
    land van de CLUB en `primaryLeagueId` de competitie waarin hij speelt; die tweede is nodig om
    een ploeg uit een lagere divisie te herkennen.
    """
    from scripts import fotmob
    data = fotmob._get_json(f"https://www.fotmob.com/api/data/teams?id={team_id}")
    det = data.get("details") or {}
    return det.get("country"), det.get("primaryLeagueId"), det.get("primaryLeagueName")


def convert_team(team_id: int | str, team_name: str, season: str,
                 *, shrink: float = DEFAULT_SHRINK) -> Converted:
    """Zoek de binnenlandse competitie van een ploeg op en reken hem om naar de Europese schaal.

    `season` is het laatst AFGERONDE binnenlandse seizoen in Fotmob-vorm ("2025/2026" of "2025").
    `team_name` is nodig omdat `fotmob.fetch_league_stats` zijn stand op NAAM sleutelt en niet op
    id; de koppeling gaat via `promotion.find_team`, dus exact of genormaliseerd-exact en nooit
    een gok.

    Gooit `InterLeagueError` zodra een van de poorten dichtgaat — geen competitie bekend, geen
    gemeten factor, ploeg speelt niet in de hoogste divisie, of geen bruikbare stand. De aanroeper
    hoort daarop `data_tier = NONE` te zetten.
    """
    from scripts import fotmob, promotion
    ccode, league_id, league_name = team_country(team_id)
    if not ccode:
        raise InterLeagueError(f"Fotmob geeft geen land voor ploeg {team_id}")
    ccode = ccode.upper()
    if not covered(ccode):
        raise InterLeagueError(
            f"{ccode}: geen gemeten competitiefactor (minder dan {MIN_MATCHES} Europese duels "
            f"in de meting, of niet in de meting opgenomen)")
    expected = TOP_DIVISION_ID.get(ccode)
    if expected and league_id and int(league_id) != expected:
        raise InterLeagueError(
            f"{ccode}: ploeg speelt in {league_name!r} (id {league_id}), niet in de hoogste "
            f"divisie (id {expected}) waarop de factor is gemeten")

    stats = fotmob.fetch_league_stats(expected or int(league_id), season)
    # Eerst op id — dat is exact. Naamkoppeling is de terugval voor een gecachte stand van vóór
    # de dag waarop `_id` werd toegevoegd; die valt vanzelf weg zodra de cache ververst.
    key = next((n for n, t in stats["teams"].items() if str(t.get("_id")) == str(team_id)), None)
    if key is None:
        key = promotion.find_team(stats["teams"], team_name)
    if key is None:
        raise InterLeagueError(
            f"{team_name!r} staat niet in de stand van {ccode} {season} — gepromoveerd, of de "
            f"naamkoppeling faalt")
    row = stats["teams"][key]
    if not row.get("played"):
        raise InterLeagueError(f"{team_name!r} heeft nul gespeelde duels in {ccode} {season}")
    home_rate = stats.get("home_goals_per_match") or 0.0
    away_rate = stats.get("away_goals_per_match") or 0.0
    avg = (home_rate + away_rate) / 2
    return convert(ccode, row["gf"], row["ga"], row["played"], avg,
                   home=row.get("home"), away=row.get("away"), shrink=shrink)


# --------------------------------------------------------------------------------------------
# Zelftest tegen echte, actuele data — zelfde vorm als de andere modules in scripts/.
#   python3 scripts/interleague.py
# --------------------------------------------------------------------------------------------

def _selftest() -> int:
    from scripts.model import match_lambdas

    fails = []

    # 1. De omrekening moet precies de gefitte lambda's teruggeven. Twee ploegen die in hun eigen
    #    competitie exact gemiddeld zijn (ratio 1.0) leveren H * A_thuis * D_uit op.
    lg = reference_league()
    home = convert("ENG", 38, 38, 38, 1.0)
    away = convert("ESP", 38, 38, 38, 1.0)
    lh, la = match_lambdas(home.stats, away.stats, lg)
    A_h, D_h, _ = FACTORS["ENG"]
    A_a, D_a, _ = FACTORS["ESP"]
    want_h, want_a = EURO_HOME_GOALS * A_h * D_a, EURO_AWAY_GOALS * A_a * D_h
    if abs(lh - want_h) > 1e-9 or abs(la - want_a) > 1e-9:
        fails.append(f"lambda's kloppen niet: {lh:.6f}/{la:.6f} tegen {want_h:.6f}/{want_a:.6f} — "
                     f"dit betekent dat `_deshrink` niet meer aansluit op model.team_strength")
    else:
        print(f"  ok  omrekening reproduceert de gefitte lambda's ({lh:.4f} / {la:.4f})")

    # 2. Een competitie zonder gemeten factor moet luidruchtig weigeren, niet stil doorgaan.
    try:
        convert("SVK", 30, 30, 30, 1.0)
        fails.append("SVK werd geaccepteerd terwijl er geen gemeten factor is")
    except InterLeagueError:
        print("  ok  competitie zonder gemeten factor wordt geweigerd")

    # 3. De bereikpoort moet dichtgaan op een ploeg buiten het gemeten bereik.
    extreme = convert("ENG", 120, 5, 38, 1.0)
    if extreme.in_range:
        fails.append(f"bereikpoort ging niet dicht op aanval {extreme.attack:.3f}")
    else:
        print(f"  ok  bereikpoort sluit buiten het gemeten bereik ({extreme.note.split(';')[-1].strip()})")

    # 4. Live: een echte ploeg omrekenen via Fotmob.
    try:
        c = convert_team(8633, "Real Madrid", "2025/2026")
        print(f"  ok  live omrekening Real Madrid: aanval {c.attack:.3f}, "
              f"verdediging {c.defence:.3f}, binnen bereik: {c.in_range}")
    except Exception as exc:      # netwerk mag geen harde fout zijn in een zelftest
        print(f"  -   live omrekening overgeslagen ({type(exc).__name__}: {exc})")

    print(f"\n{len(FACTORS)} competities met een gemeten factor, drempel {MIN_MATCHES} Europese duels.")
    for f in fails:
        print(f"  FOUT {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
