#!/usr/bin/env python3
"""Promovendi: teamsterkte uit de divisie eronder, via Fotmob.

Bestaansreden (30 aug 2026). `scripts/footballdata.py` rekent een promovendus om naar de divisie
erboven, maar football-data.co.uk dekt maar acht divisieparen. Op 30 aug kostte dat **vier
wedstrijden**: Feyenoord - ADO Den Haag, Willem II - SC Heerenveen en Cambuur - FC Twente (alle
drie een promovendus uit de Eerste Divisie) en Lyngby - OB (Deense 1. Division). Alle vier kregen
`data_tier = NONE` en zijn niet doorgerekend, niet omdat de analyse iets vond maar omdat de bron
die divisie niet heeft.

Nagetrokken op diezelfde dag: **Fotmob heeft die divisies wel.** De Eerste Divisie (id 111) geeft
20 ploegen met doelpunten voor en tegen plus thuis/uit-splits, de Deense 1. Division (id 85) geeft
er 12, en alle vier de promovendi van die dag staan erin (ADO Den Haag 90-37 in 38 duels, Cambuur
75-48, Willem II 59-42, Lyngby 49-25 in 22). Geen xG - `has_xg` is `False` voor beide - maar dat is
ook niet nodig: `footballdata.convert_strength` rekent op **relatieve doelpuntsterkte**, en die
staat er wel.

Dit is dus geen tweede bron naast football-data.co.uk maar een bredere ingang op dezelfde methode:

    Fotmob  ->  relatieve sterkte in de lagere divisie
                -> footballdata.gap_for(...)      (gemeten paar, of de gepoolde factor)
                -> footballdata.convert_strength(...)
                -> model.TeamStats op het niveau van de hogere divisie

**Een omgerekende ploeg is altijd `LIGHT`, nooit `FULL`.** De correctie haalt de systematische
fout eruit, niet de onzekerheid - `footballdata.RESIDUAL_SPREAD` houdt na correctie nog ~0.16
relatieve sterkte over, bijna een vijfde van een competitiegemiddelde.

**En hij is alleen geldig binnen het gemeten bereik.** `conversion_in_range` is geen formaliteit:
zie de Coventry-val in de docstring van die functie, waar een kampioen buiten het bereik +21.6 pp
schijnedge opleverde die alle andere poorten haalde. Valt een ploeg erbuiten, dan hoort hij op
`NONE` en niet op `LIGHT`.

    python3 scripts/promotion.py        # zelftest tegen echte, actuele data

Alleen de standaardbibliotheek plus scripts/fotmob.py en scripts/footballdata.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts import fotmob, footballdata as fd
from scripts.model import TeamStats, TeamSplits, LeagueContext


@dataclass(frozen=True)
class Tier2:
    """De divisie onder een competitie uit de runlijst.

    `fd_pair` is het divisiepaar waarmee `footballdata.gap_for` een **gemeten** factor kan
    opzoeken. Staat er `None`, dan valt `gap_for` terug op `POOLED_GAP` - de mediaan over de acht
    gemeten paren - en dat zegt hij zelf ook in `GapResult.direction`. Neem die tekst over in het
    runrapport, zodat zichtbaar is welke ploegen op een gepoolde factor draaien.
    """
    fotmob_id: int
    name: str
    fd_pair: tuple[str, str] | None = None


#: Competitie uit de runlijst -> de divisie eronder. Alle twaalf `fotmob_id`s zijn op 30 aug 2026
#: opgehaald en op naam en land geverifieerd; een geraden id geeft een andere competitie terug en
#: dat merk je niet aan de cijfers, alleen aan de namen.
TIER2: dict[str, Tier2] = {
    "Premier League (ENG)":       Tier2(48,  "Championship (ENG)",        ("E0", "E1")),
    "Championship (ENG)":         Tier2(108, "League One (ENG)",          ("E1", "E2")),
    "La Liga (ESP)":              Tier2(140, "LaLiga2 (ESP)",             ("SP1", "SP2")),
    "Bundesliga (GER)":           Tier2(146, "2. Bundesliga (GER)",       ("D1", "D2")),
    "Serie A (ITA)":              Tier2(86,  "Serie B (ITA)",             ("I1", "I2")),
    "Ligue 1 (FRA)":              Tier2(110, "Ligue 2 (FRA)",             ("F1", "F2")),
    "Scottish Premiership (SCO)": Tier2(123, "Championship (SCO)",        ("SC0", "SC1")),
    # Hieronder heeft football-data.co.uk geen tweede divisie, dus gaat gap_for gepoold:
    "Eredivisie (NED)":           Tier2(111, "Eerste Divisie (NED)"),
    "Danish Superliga (DEN)":     Tier2(85,  "1. Division (DEN)"),
    "Primeira Liga (POR)":        Tier2(185, "Liga Portugal 2 (POR)"),
    "Belgian Pro League (BEL)":   Tier2(264, "First Division B (BEL)"),
    "Süper Lig (TUR)":            Tier2(165, "1. Lig (TUR)"),
    "Ekstraklasa (POL)":          Tier2(197, "I Liga (POL)"),
}


#: Gemeten divisiegat voor de zes paren die football-data.co.uk niet heeft. Gemeten op
#: **31 aug 2026** met `measure_gap(...)` over de seizoenen 2016/2017 t/m 2024/2025, op Fotmob,
#: aan ploegen die daadwerkelijk promoveerden. Mediaan, niet gemiddelde — één ingestorte
#: promovendus trekt bij deze aantallen een gemiddelde ver mee.
#:
#: Waarde: `(aanvalsfactor, verdedigingsfactor, n, inv_aanval_min, inv_aanval_max,
#: inv_verdediging_min, inv_verdediging_max)`. De laatste vier zijn het bereik van de
#: **invoersterkte** van de gemeten ploegen — daarbuiten is er geen meting en hoort de omrekening
#: te weigeren, precies zoals `footballdata.CONVERSION_RANGE` dat voor de andere acht paren doet.
#:
#: Waarom dit moest (aanleiding: 30 aug 2026). Tot deze meting draaiden alle zes op `POOLED_GAP`
#: (0.605 / 1.513), en dat leverde die dag de grootste edge van de run op — ADO Den Haag +2.5 bij
#: Feyenoord, +23.6 pp. De meting bevestigt de gepoolde factor voor Nederland grotendeels
#: (0.614 / 1.564) maar corrigeert Denemarken duidelijk: de verdedigingsfactor is daar **1.807**
#: tegen 1.513 gepoold, oftewel een Deense promovendus incasseert fors meer dan de gepoolde factor
#: aannam. Voor Polen geldt hetzelfde in mindere mate (1.743).
MEASURED_TIER2_GAP: dict[str, tuple[float, float, int, float, float, float, float]] = {
    "Eredivisie (NED)":         (0.614, 1.564, 23, 0.941, 1.775, 0.407, 0.979),
    "Danish Superliga (DEN)":   (0.624, 1.807, 18, 0.989, 1.747, 0.462, 0.989),
    "Primeira Liga (POR)":      (0.615, 1.504, 22, 1.093, 1.717, 0.457, 0.950),
    "Belgian Pro League (BEL)": (0.696, 1.604, 13, 0.759, 1.691, 0.462, 1.109),
    "Süper Lig (TUR)":          (0.708, 1.497, 27, 0.979, 1.912, 0.497, 1.124),
    "Ekstraklasa (POL)":        (0.680, 1.743, 24, 1.069, 1.516, 0.505, 0.929),
}


def gap_and_range(top_competition: str, t2: "Tier2", attack: float, defence: float):
    """De factor voor dit divisiepaar plus de controle of de ploeg binnen het gemeten bereik valt.

    Drie bronnen, in deze volgorde: het gemeten paar bij football-data.co.uk, de eigen meting uit
    `MEASURED_TIER2_GAP`, en pas als laatste de gepoolde factor.
    """
    if t2.fd_pair:
        hi, lo = t2.fd_pair
        return fd.gap_for(hi, lo, "up"), *fd.conversion_in_range(hi, lo, "up", attack, defence)
    m = MEASURED_TIER2_GAP.get(top_competition)
    if m is None:
        hi, lo = top_competition, t2.name
        return fd.gap_for(hi, lo, "up"), *fd.conversion_in_range(hi, lo, "up", attack, defence)
    a, d, n, a_min, a_max, d_min, d_max = m
    gap = fd.GapResult(a, d, n, f"up (gemeten 31 aug 2026 op Fotmob, {top_competition}/{t2.name})")
    buiten = []
    if not a_min <= attack <= a_max:
        buiten.append(f"aanval {attack:.3f} buiten {a_min:.3f}-{a_max:.3f}")
    if not d_min <= defence <= d_max:
        buiten.append(f"verdediging {defence:.3f} buiten {d_min:.3f}-{d_max:.3f}")
    label = f"{top_competition}/{t2.name} up (eigen meting, n={n})"
    if buiten:
        return gap, False, f"{label}: " + "; ".join(buiten)
    return gap, True, (f"{label}: aanval {attack:.3f} in {a_min:.3f}-{a_max:.3f}, "
                       f"verdediging {defence:.3f} in {d_min:.3f}-{d_max:.3f}")


class PromotionError(RuntimeError):
    pass


@dataclass
class Converted:
    """Een promovendus, omgerekend naar de divisie erboven."""
    team: str
    stats: TeamStats
    splits: TeamSplits
    in_range: bool
    note: str

    @property
    def tier(self) -> str:
        """`LIGHT` binnen het gemeten bereik, `NONE` erbuiten - nooit `FULL`."""
        return "LIGHT" if self.in_range else "NONE"


def _rates(table: dict) -> tuple[float, float]:
    """(thuisdoelpunten, uitdoelpunten) per ploeg per duel in deze divisie."""
    hg = sum(t["home"]["gf"] for t in table.values() if "home" in t)
    hp = sum(t["home"]["played"] for t in table.values() if "home" in t)
    ag = sum(t["away"]["gf"] for t in table.values() if "away" in t)
    ap = sum(t["away"]["played"] for t in table.values() if "away" in t)
    if not hp or not ap:
        raise PromotionError("geen thuis/uit-splits in deze stand")
    return hg / hp, ag / ap


def find_team(table: dict, name: str) -> str | None:
    """De rij van deze ploeg in de stand, of None. Exact of genormaliseerd, nooit een gok."""
    if name in table:
        return name

    def norm(s: str) -> str:
        out = []
        for c in (s or "").lower():
            out.append({"ł": "l", "ø": "o", "æ": "ae", "å": "a", "ß": "ss", "đ": "d"}.get(c, c))
        import unicodedata, re
        s2 = unicodedata.normalize("NFKD", "".join(out)).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]", "", s2)

    target = norm(name)
    for row in table:
        if norm(row) == target:
            return row
    # Afgekorte naam, maar **alleen als voorvoegsel en alleen als hij uniek is**. De daglijst kort
    # namen achteraan af ("Ipswich" waar de stand "Ipswich Town" zegt), en die moeten meekomen.
    #
    # Twee eisen, allebei door schade opgelegd:
    #
    # 1. **Uniek.** Op 30 aug 2026 koppelde een losse deelstringmatch "Deportivo A Coruña" aan
    #    "Deportivo Alaves" — een andere club, en het zou een promovendus stilzwijgend als FULL
    #    hebben doorgelaten.
    # 2. **Voorvoegsel, niet zomaar deelstring.** Op 31 aug 2026 koppelde de uniciteitsregel alléén
    #    "Jong Ajax" aan "Ajax" en "Jong FC Utrecht" aan "FC Utrecht": beloftenelftallen spelen
    #    permanent in de Eerste Divisie en kunnen niet promoveren, maar hun naam bevát die van de
    #    hoofdmacht. In de gapmeting leverde dat "een promovendus behoudt zijn aanval" (factor
    #    1.010) op — onzin, en het zou de omrekening van élke Nederlandse promovendus hebben
    #    bepaald. Met de voorvoegsel-eis valt "Ajax" niet meer op "Jong Ajax" en andersom, terwijl
    #    "Ipswich" op "Ipswich Town" gewoon blijft werken.
    hits = [row for row in table
            if target and (norm(row).startswith(target) or target.startswith(norm(row)))]
    return hits[0] if len(hits) == 1 else None


def convert(top_competition: str, team: str, season: str, top_league: LeagueContext,
            *, use_cache: bool = True) -> Converted:
    """Reken een promovendus om naar `top_competition`, op de cijfers van `season` in de divisie eronder.

    `top_league` is de `LeagueContext` van de hogere divisie **zoals de run hem gebruikt** - dus
    inclusief de vroeg-seizoenscorrectie van `scale_level`, want de omgerekende ploeg moet op
    hetzelfde niveau staan als zijn tegenstander.

    Gooit `PromotionError` als de competitie geen bekende tweede divisie heeft of de ploeg niet in
    die stand staat. Dat is met opzet luidruchtig: stil terugvallen op een gok is precies hoe een
    promovendus als `FULL` zou kunnen doorglippen.
    """
    t2 = TIER2.get(top_competition)
    if t2 is None:
        raise PromotionError(f"geen tweede divisie bekend voor {top_competition!r}")

    lower = fotmob.fetch_league_stats(t2.fotmob_id, season, use_cache=use_cache)
    table = lower["teams"]
    row = find_team(table, team)
    if row is None:
        raise PromotionError(f"{team!r} staat niet in de stand van {t2.name} {season}")

    ts = table[row]
    if "home" not in ts or "away" not in ts:
        raise PromotionError(f"{team!r} heeft geen thuis/uit-splits in {t2.name}")

    low_home, low_away = _rates(table)
    played = ts.get("played") or (ts["home"]["played"] + ts["away"]["played"])
    if not played:
        raise PromotionError(f"{team!r} heeft nul gespeelde duels in {t2.name}")

    # Relatieve sterkte in de lagere divisie, op dezelfde normalisatie als
    # footballdata.relative_strength: doelpunten per duel gedeeld door het competitiegemiddelde.
    low_avg = (low_home + low_away) / 2
    attack = (ts["gf"] / played) / low_avg
    defence = (ts["ga"] / played) / low_avg

    higher_slug, lower_slug = t2.fd_pair or (top_competition, t2.name)
    gap, in_range, range_note = gap_and_range(top_competition, t2, attack, defence)
    new_attack, new_defence = fd.convert_strength(attack, defence, gap)

    # Relatieve sterkte -> xG-totalen op het niveau van de hogere divisie. `team_strength`
    # deelt straks weer door `avg_xg_per_match`, dus dit is de omgekeerde bewerking.
    level = top_league.avg_xg_per_match
    stats = TeamStats(xg=new_attack * level * played,
                      xga=new_defence * level * played,
                      matches_played=played)

    # Splits: eerst de thuis- en uitverhouding in de lagere divisie, dan dezelfde gap-factor, dan
    # het niveau van de hogere divisie. Alleen de gap-factor toepassen zou het niveauverschil
    # tussen de twee divisies laten staan.
    top_home = top_league.home_goals_per_match
    top_away = top_league.away_goals_per_match
    hp, ap = ts["home"]["played"], ts["away"]["played"]

    def scaled(goals: int, played_side: int, low_rate: float, top_rate: float, factor: float) -> int:
        if not played_side or not low_rate:
            return 0
        rate = (goals / played_side) / low_rate * factor * top_rate
        return max(0, round(rate * played_side))

    splits = TeamSplits(
        home_gf=scaled(ts["home"]["gf"], hp, low_home, top_home, gap.attack),
        home_ga=scaled(ts["home"]["ga"], hp, low_away, top_away, gap.defence),
        home_played=hp,
        away_gf=scaled(ts["away"]["gf"], ap, low_away, top_away, gap.attack),
        away_ga=scaled(ts["away"]["ga"], ap, low_home, top_home, gap.defence),
        away_played=ap,
    )

    note = (f"{team}: {t2.name} {season} (Fotmob {t2.fotmob_id}) relatieve aanval {attack:.3f} / "
            f"verdediging {defence:.3f} over {played} duels, omgerekend met "
            f"gap_for({higher_slug},{lower_slug},up) x{gap.attack:.3f}/{gap.defence:.3f} "
            f"[{gap.direction}] naar {new_attack:.3f}/{new_defence:.3f}; "
            f"conversion_in_range: {range_note}")
    return Converted(team=team, stats=stats, splits=splits, in_range=in_range, note=note)


def _selftest() -> int:
    """Reproduceert de vier duels die op 30 aug 2026 op NONE bleven staan."""
    from scripts.model import scale_level

    cases = [
        ("Eredivisie (NED)", 57, ["ADO Den Haag", "Cambuur", "Willem II"]),
        ("Danish Superliga (DEN)", 46, ["Lyngby"]),
    ]
    fouten = 0
    for comp, top_id, teams in cases:
        top = fotmob.fetch_league_stats(top_id, "2025/2026")
        league = scale_level(LeagueContext(top["home_goals_per_match"],
                                           top["away_goals_per_match"],
                                           top["avg_xg_per_match"]), 1.0646)
        print(f"\n=== {comp} (competitiebasis {league.avg_xg_per_match:.3f} xG/duel)")
        for team in teams:
            try:
                c = convert(comp, team, "2025/2026", league)
            except PromotionError as exc:
                print(f"  {team:16} FOUT: {exc}")
                fouten += 1
                continue
            print(f"  {team:16} tier={c.tier}  xG {c.stats.xg_per_match:.2f}/duel  "
                  f"xGA {c.stats.xga_per_match:.2f}/duel  "
                  f"splits thuis {c.splits.home_gf}-{c.splits.home_ga} in {c.splits.home_played}, "
                  f"uit {c.splits.away_gf}-{c.splits.away_ga} in {c.splits.away_played}")
            print(f"                   {c.note}")
            if not (0.2 < c.stats.xg_per_match < 4.0):
                print("                   ^^ ONWAARSCHIJNLIJK, controleer de omrekening")
                fouten += 1
    print(f"\n{'ALLES OK' if not fouten else str(fouten) + ' PROBLEEM(EN)'}")
    return 1 if fouten else 0


if __name__ == "__main__":
    raise SystemExit(_selftest())


# --------------------------------------------------------------------------- het gat meten
#
# `footballdata.MEASURED_GAPS` dekt acht divisieparen; de vijf andere paren in TIER2 draaiden tot
# 31 aug 2026 op `POOLED_GAP` — de mediaan over die acht, uit andere landen. Op 30 aug leverde dat
# de grootste edge van de dag op (ADO Den Haag +2.5 tegen Feyenoord, +23.6 pp) en dat is precies de
# vorm waar `conversion_in_range` voor waarschuwt: een gepoolde factor met een ruime band eronder.
#
# Fotmob heeft beide divisies over tien seizoenen, dus het gat is gewoon te meten — met exact
# dezelfde methode als `footballdata.division_gap()`: per ploeg die daadwerkelijk verhuisde, de
# relatieve sterkte ná gedeeld door die vóór, en dan de mediaan (niet het gemiddelde, want één
# ingestorte promovendus trekt dat bij deze aantallen ver mee).

def _norm_name(s: str) -> str:
    import re, unicodedata
    out = "".join({"ł": "l", "ø": "o", "æ": "ae", "å": "a", "ß": "ss", "đ": "d"}.get(c, c)
                  for c in (s or "").lower())
    return re.sub(r"[^a-z0-9]", "",
                  unicodedata.normalize("NFKD", out).encode("ascii", "ignore").decode())


def _rel(row: dict, table: dict) -> tuple[float, float]:
    """(aanval, verdediging) van een ploeg t.o.v. het competitiegemiddelde in datzelfde seizoen."""
    played = row.get("played") or 0
    if not played:
        return 0.0, 0.0
    tot_g = sum(t.get("gf", 0) for t in table.values())
    tot_p = sum(t.get("played", 0) for t in table.values())
    avg = (tot_g / tot_p) if tot_p else 0.0
    if not avg:
        return 0.0, 0.0
    return (row["gf"] / played) / avg, (row["ga"] / played) / avg


def measure_gap(top_competition: str, top_id: int, years: range, *, direction: str = "up",
                min_played: int = 10) -> "fd.GapResult":
    """Meet het gat tussen een competitie en de divisie eronder, aan ploegen die verhuisden.

    Zelfde definitie als `footballdata.division_gap()`, maar op Fotmob-standen, zodat ook de
    divisieparen meetbaar zijn die football-data.co.uk niet heeft.
    """
    import statistics
    t2 = TIER2[top_competition]
    att, dfn, samples = [], [], []
    for y in years:
        s_from, s_to = f"{y}/{y + 1}", f"{y + 1}/{y + 2}"
        lo, hi = (t2.fotmob_id, top_id) if direction == "up" else (top_id, t2.fotmob_id)
        try:
            t_from = fotmob.fetch_league_stats(lo, s_from)["teams"]
            t_to = fotmob.fetch_league_stats(hi, s_to)["teams"]
        except Exception:
            continue
        for name, before in t_from.items():
            # Exact of genormaliseerd-exact, en verder niets: een ploeg die echt verhuisde houdt
            # bij Fotmob dezelfde naam. Elke soepelere match haalt hier beloftenelftallen binnen
            # (zie find_team) en die verhuizen nooit.
            hit = name if name in t_to else next(
                (r for r in t_to if _norm_name(r) == _norm_name(name)), None)
            after = t_to.get(hit) if hit else None
            if after is None:
                continue
            if (before.get("played") or 0) < min_played or (after.get("played") or 0) < min_played:
                continue
            a0, d0 = _rel(before, t_from)
            a1, d1 = _rel(after, t_to)
            if a0 <= 0 or d0 <= 0:
                continue
            att.append(a1 / a0)
            dfn.append(d1 / d0)
            # ook de INVOERsterkte bewaren: daarop rust het bereik waarbinnen de factor geldig is
            samples.append((name, y, round(a1 / a0, 3), round(d1 / d0, 3),
                            round(a0, 3), round(d0, 3)))
    if not att:
        return fd.GapResult(1.0, 1.0, 0, direction)

    def spread(xs):
        xs = sorted(xs)
        return ((statistics.quantiles(xs, n=4)[0], statistics.quantiles(xs, n=4)[2])
                if len(xs) >= 4 else (xs[0], xs[-1]))

    return fd.GapResult(statistics.median(att), statistics.median(dfn), len(att), direction,
                        spread(att), spread(dfn), samples)
