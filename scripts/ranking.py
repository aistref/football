#!/usr/bin/env python3
"""Stage 4: welke wedstrijden krijgen een plek onder `MAX_DEEP_ANALYSES`?

**Waarom dit bestaat (29 aug 2026, op aanwijzing van de gebruiker).** Tot deze datum rangschikte
Stage 4 binnen dezelfde datakwaliteit op één proxy: het aantal speeldagen dat de **competitie**
dit seizoen al gespeeld had. Op 29 aug stonden er 49 duels op de runlijst voor 30 plekken, en die
tie-break gooide precies de vier volwaardige Bundesliga-duels eruit — omdat de Bundesliga pas één
speeldag had gespeeld.

Dat criterium meet bijna niets. De teamsterktes in het model komen bij **alle** competities uit
het volledige seizoen 2025/2026; het aantal speeldagen van dit seizoen gaat alleen de gepoolde
vroeg-seizoenscorrectie in, en die is competitie-overstijgend. Eén Bundesliga-speeldag meer of
minder verandert aan die vier analyses niets.

De vraag die er wél toe doet is: **hoe goed beschrijft wat ik weet deze twee ploegen vandáág?**
Dat is te meten, en het kost geen credits — alles hieronder komt gratis van Fotmob:

| Onderdeel | Punten | Waar het vandaan komt |
|---|---|---|
| selectiecontinuïteit | 0–3 | `scripts/squad.turnover` — transfers sinds 1 juni, op marktwaarde |
| opstelling | 0–2 | `lineupType`: bevestigd (2) boven voorspeld (1) |
| blessures/schorsingen bekend | 0–2 | de `unavailable`-lijst bestaat voor beide ploegen |
| vorm en rust | 0–2 | `matchFacts.teamForm`: reeks van >= 3 duels én rustdagen |
| lopend seizoen | 0–1 | duels die déze twee ploegen dit seizoen al speelden |

Dit is met opzet grof en niet gefit. Er is geen enkele meting die zegt hoeveel een bevestigde
opstelling waard is ten opzichte van een lage transferomzet, en zo'n gewicht verzinnen is precies
wat §2 en §4 verbieden. Wat de score wél doet is de rangschikking baseren op **gemeten
aanwezigheid van actuele informatie** in plaats van op een proxy die met de wedstrijd niets te
maken heeft. Ontbrekende metingen krijgen het middenpunt, nooit nul: een meting die er niet is,
is geen bewijs van een probleem (zelfde regel als poort 7 in §1c).

De datakwaliteit (`FULL` boven `LIGHT` boven `NONE`) blijft de **primaire** sortering; deze score
beslist alleen binnen dezelfde tier, en het aantal beschikbare markten is de laatste tie-break.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

#: `MAX_DEEP_ANALYSES` uit _shared-rules.md §0 — 30 op ma-do, 35 op vr-zo.
#: Verhoogd voor het weekend op 29 aug 2026 op verzoek van de gebruiker: op een zaterdag met
#: elf lopende competities stonden er 49 duels op de runlijst en paste 61% ervan.
DEEP_WEEKDAY = 30
DEEP_WEEKEND = 35

TIER_RANK = {"FULL": 0, "LIGHT": 1, "NONE": 2}


def max_deep_analyses(day: date) -> int:
    """30 op maandag t/m donderdag, 35 op vrijdag t/m zondag."""
    return DEEP_WEEKEND if day.weekday() >= 4 else DEEP_WEEKDAY


def max_shortlist(day: date) -> int:
    """3 op ma-do, 5 op vr-zo — `MAX_SHORTLIST` uit _shared-rules.md §0."""
    return 5 if day.weekday() >= 4 else 3


# --------------------------------------------------------------------- deelscores

def _continuity_points(share: float | None) -> float:
    """0-1.5 per ploeg. `share` = (marktwaarde in + uit) / waarde basisopstelling."""
    if share is None:
        return 0.75                      # niet gemeten -> middenpunt, geen straf en geen beloning
    if share <= 0.25:
        return 1.5
    if share <= 0.50:
        return 1.0
    if share <= 1.00:
        return 0.5
    return 0.0


def _lineup_points(lineup_type: str) -> float:
    kind = (lineup_type or "").lower()
    if kind == "lineup":
        return 2.0                       # bevestigde opstelling
    if kind == "predicted":
        return 1.0
    return 0.0


def _absence_points(squad_value_home: float, squad_value_away: float) -> float:
    """1 punt per ploeg waarvan het opstellingsblok er is.

    Een lege `unavailable`-lijst telt als informatie ("niemand afwezig"), niet als een gat —
    maar alleen als het blok er überhaupt is, en dat is te zien aan een selectiewaarde > 0.
    """
    return (1.0 if squad_value_home > 0 else 0.0) + (1.0 if squad_value_away > 0 else 0.0)


def _form_points(form_home: str, rest_home, form_away: str, rest_away) -> float:
    home = 1.0 if (form_home and len(form_home) >= 3 and rest_home is not None) else 0.0
    away = 1.0 if (form_away and len(form_away) >= 3 and rest_away is not None) else 0.0
    return home + away


def _season_points(matches_home: int, matches_away: int) -> float:
    """0-1, op de duels die déze twee ploegen dit seizoen al speelden (niet de competitie)."""
    return min(1.0, (max(0, matches_home) + max(0, matches_away)) / 6.0)


@dataclass
class Richness:
    """Hoeveel actuele informatie er over dit duel op tafel ligt. Maximaal 10."""
    total: float = 0.0
    parts: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def summary(self) -> str:
        bits = " · ".join(f"{k} {v:.1f}" for k, v in self.parts.items())
        return f"{self.total:.1f}/10 ({bits})"


def data_richness(ctx, turnover_home=None, turnover_away=None,
                  matches_home: int = 0, matches_away: int = 0) -> Richness:
    """De score voor één duel.

    `ctx` is een `context.MatchContext` (of None als de context niet op te halen was — dan telt
    alleen het lopende seizoen mee en krijgt de rest het middenpunt, zodat een bronstoring een
    wedstrijd niet stilletjes achteraan zet).
    """
    r = Richness()
    if ctx is None:
        r.parts = {"continuïteit": 1.5, "opstelling": 1.0, "afwezigen": 1.0, "vorm": 1.0,
                   "seizoen": _season_points(matches_home, matches_away)}
        r.notes.append("context niet opgehaald — middenpunt toegekend, geen straf")
        r.total = sum(r.parts.values())
        return r

    share_h = turnover_home.share if turnover_home is not None else None
    share_a = turnover_away.share if turnover_away is not None else None
    r.parts = {
        "continuïteit": _continuity_points(share_h) + _continuity_points(share_a),
        "opstelling": _lineup_points(ctx.lineup_type),
        "afwezigen": _absence_points(ctx.home.squad_value, ctx.away.squad_value),
        "vorm": _form_points(ctx.home.form, ctx.home.rest_days, ctx.away.form, ctx.away.rest_days),
        "seizoen": _season_points(matches_home, matches_away),
    }
    r.total = round(sum(r.parts.values()), 2)
    if share_h is not None and share_h > 1.0:
        r.notes.append(f"{ctx.home.name}: selectieverloop {share_h * 100:.0f}% van de basiswaarde")
    if share_a is not None and share_a > 1.0:
        r.notes.append(f"{ctx.away.name}: selectieverloop {share_a * 100:.0f}% van de basiswaarde")
    return r


def sort_key(tier: str, richness: float, markets: int, kickoff: str):
    """De volledige Stage 4-sortering, in één sleutel.

    1. datakwaliteit (FULL boven LIGHT boven NONE) — dit blijft de primaire regel uit §5;
    2. datarijkdom (hoog boven laag) — wat we over déze twee ploegen vandaag weten;
    3. aantal beschikbare markten (veel boven weinig) — bij gelijke informatie is een duel waar
       vier markten om de publicatie kunnen strijden een betere besteding van een plek dan een
       duel waar er maar één ligt. Dit is een eigenschap van de *prijs* en niet van de kansinput,
       en staat daarom bewust achteraan en niet in `data_richness`;
    4. aftrap, zodat de volgorde bij volledig gelijke stand reproduceerbaar is.
    """
    return (TIER_RANK.get(tier, 9), -richness, -markets, kickoff)


if __name__ == "__main__":
    from datetime import date as _d
    assert max_deep_analyses(_d(2026, 8, 26)) == 30    # woensdag
    assert max_deep_analyses(_d(2026, 8, 28)) == 35    # vrijdag
    assert max_deep_analyses(_d(2026, 8, 29)) == 35    # zaterdag
    assert max_deep_analyses(_d(2026, 8, 30)) == 35    # zondag
    assert max_deep_analyses(_d(2026, 8, 31)) == 30    # maandag
    assert _continuity_points(None) == 0.75
    assert _continuity_points(0.1) == 1.5 and _continuity_points(2.0) == 0.0
    assert _lineup_points("lineup") > _lineup_points("predicted") > _lineup_points("")
    assert _season_points(3, 3) == 1.0 and _season_points(0, 0) == 0.0
    # een volledig gedocumenteerd duel moet boven een half gedocumenteerd uitkomen
    assert sort_key("FULL", 9.0, 4, "x") < sort_key("FULL", 4.0, 4, "x")
    assert sort_key("FULL", 4.0, 4, "x") < sort_key("LIGHT", 9.0, 4, "x")
    assert sort_key("FULL", 7.0, 4, "x") < sort_key("FULL", 7.0, 2, "x")
    print("Zelftest geslaagd.")
