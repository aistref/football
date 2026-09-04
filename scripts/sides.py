"""Poort 8 — staat deze selectie op de kant die de markt zwakker vindt?

Ingevoerd 4 september 2026, op verzoek van de gebruiker, na de spiegelanalyse in
`runs/2026-09-04-run-a.md`. De aanleiding in drie zinnen:

* Van de 118 afgewikkelde picks met een kant stond **89 (75%) op de underdog**. Die 89 leverden
  36.0% trefkans en **−15.76u (−17.7%)** op; de overige 118 picks samen **+1.46u (+1.2%)**. Alle
  verlies van de routine zit dus in die ene kant.
* Op diezelfde 89 verwachtte het model **47.1** winnaars, de markt **38.0**, en het werden er
  **33.0** — een afwijking van **z = −3.14** voor het model tegen −1.11 voor de markt. Gemeten op
  uitkomsten, niet tegen de markt, en daarmee vrij van het circulariteitsbezwaar van §2.
* Een hógere edge-drempel op die kant is doorgerekend en **afgewezen**: de ROI daalt met de
  drempel (−26.3% vanaf 8 pp, −46.4% vanaf 12 pp, −64.4% vanaf 20 pp) terwijl hij bij alle andere
  picks juist stijgt (+15.6% vanaf 8 pp, +26.4% vanaf 10 pp). Op de underdog-kant is een grotere
  geclaimde edge geen sterker signaal dat de bet goed is, maar dat het model ernaast zit.

Deze poort is dus geen fijnregeling maar een **rem**: zolang de kansschatting op die kant
aantoonbaar scheef staat, wordt daar niet gespeeld. Hij staat in `scripts/` en niet in de
run-scripts, om dezelfde reden als `scripts/settling.py`: zodra Run A en Run B er elk hun eigen
versie van hebben, lopen ze uiteen.

Drie eigenschappen, met opzet gelijk aan poort 7 (§1c):

* **Hij houdt alleen tegen.** Hij laat nooit iets extra's door en stelt `my_prob` niet bij.
* **Geen kant, geen poort.** Bij Over/Under, BTTS en het gelijkspel is er geen ploeg om te
  benadelen; daar staat hij altijd open.
* **Ontbrekende meting laat hem open.** Zonder 1X2-prijzen is er geen marktoordeel over wie de
  mindere ploeg is, en een meting die er niet is, is geen bewijs van een probleem.

Herzien uiterlijk **25 september 2026** op wat het schaduwlogboek zegt dat hij heeft gekost: elke
tegengehouden kandidaat gaat als `failed_gate = "underdog"` naar `data/shadow.jsonl` en wordt daar
net zo afgerekend als een echte pick. Houdt hij structureel winnaars tegen, dan gaat hij eruit;
staat de kalibratie op die kant weer recht, dan gaat hij ook eruit.
"""
from __future__ import annotations

from dataclasses import dataclass

# Onder dit verschil in de-vigde marktkans noemt de markt geen van beide ploegen de mindere, en
# gaat de poort open. 3 procentpunt is niet gemeten maar gekozen: het is ruwweg de spreiding tussen
# bookmakers op dezelfde wedstrijd, dus kleiner dan dat is geen marktoordeel maar ruis.
PICKEM_TOLERANCE = 0.03


@dataclass(frozen=True)
class SideCheck:
    passed: bool
    reason: str
    market_probs: tuple[float, float, float] | None = None


def devig(odds_1x2) -> tuple[float, float, float] | None:
    """1X2-koersen -> marktkansen die tot 1 sommeren, of None als ze onbruikbaar zijn."""
    try:
        inv = [1.0 / float(o) for o in odds_1x2]
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    total = sum(inv)
    if not total or len(inv) != 3:
        return None
    return tuple(x / total for x in inv)


def market_underdog(odds_1x2) -> str | None:
    """"home" | "away" als de markt een mindere ploeg aanwijst, anders None (pick'em of geen data)."""
    probs = devig(odds_1x2)
    if probs is None:
        return None
    home, _, away = probs
    if abs(home - away) < PICKEM_TOLERANCE:
        return None
    return "away" if home > away else "home"


def check(side: str | None, odds_1x2) -> SideCheck:
    """Mag er op deze kant gespeeld worden?

    `side` is "home", "away" of None (Over/Under, BTTS, gelijkspel). `odds_1x2` zijn de drie
    1X2-koersen van de wedstrijd, in de volgorde 1 / X / 2.
    """
    if side not in ("home", "away"):
        return SideCheck(True, "geen kant om te benadelen")
    probs = devig(odds_1x2)
    if probs is None:
        return SideCheck(True, "geen 1X2-prijzen — geen marktoordeel over wie de mindere is")
    under = market_underdog(odds_1x2)
    home, _, away = probs
    mine, theirs = (home, away) if side == "home" else (away, home)
    if under is None:
        return SideCheck(True, f"pick'em — de markt scheidt de ploegen niet ({mine:.1%} om "
                               f"{theirs:.1%})", probs)
    if under == side:
        return SideCheck(False, f"underdog-kant — de markt geeft deze ploeg {mine:.1%} tegen "
                                f"{theirs:.1%} voor de tegenstander; poort 8 (§1) is dicht zolang "
                                f"de kalibratie daar scheef staat", probs)
    return SideCheck(True, f"favorietenkant ({mine:.1%} om {theirs:.1%})", probs)
