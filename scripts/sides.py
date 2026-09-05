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

Deze poort staat in `scripts/` en niet in de run-scripts, om dezelfde reden als
`scripts/settling.py`: zodra Run A en Run B er elk hun eigen versie van hebben, lopen ze uiteen.

## Verlicht op 5 september 2026, op verzoek van de gebruiker

De poort blokkeerde tot die datum **elke** selectie op de underdog-kant. Dat is nagerekend en het
bleek te grof, om twee redenen die allebei op uitslagen zijn gemeten:

1. **Het geldverlies op die kant is niet significant.** −17.7% over 89 gevallen klinkt hard, maar
   staat op t = −1.39. De gemeten kalibratiefout (z = −3.14) is wél hard; het *rendement* is dat
   niet. De halve markt dichtzetten op een resultaat dat ruis kan zijn, is niet proportioneel.
2. **De vergelijkingsgroep deugde niet.** De "+1.2% van alle overige picks" waarmee de underdogs
   werden afgezet, bestaat voor driekwart uit doelpuntenmarkten. De écht gespeelde favorietenkant
   telt maar 21 gevallen en verliest óók — 10.9%. De +6.28u voor de favorietenkant in de
   oorspronkelijke onderbouwing is een **spiegelberekening met geschatte koersen**, geen waarneming.

Wat wél standhoudt, is dat de schade niet gelijkmatig over de underdogs verdeeld ligt. Uitgesplitst
naar de marktkans van de gespeelde selectie zelf:

| marktkans van de selectie | n | trefkans | rendement |
|---|---|---|---|
| < 25% (zware outsider) | 11 | 18.2% | −10.2% |
| **25–35%** | **18** | **16.7%** | **−44.4%** |
| 35–45% | 9 | 33.3% | −7.8% |
| 45–55% (bijna gelijk) | 38 | 44.7% | −12.1% |
| ≥ 55% | 13 | 53.8% | −10.5% |

Daarom blokkeert de poort vanaf nu alleen nog de underdog-kant **onder `UNDERDOG_FLOOR`**. Dat
houdt 29 van de 89 gevallen tegen — precies de groep die −31.4% deed — en laat de zestig
overgebleven underdogs door, die op −11.1% staan en daarmee niet meer uit de toon vallen bij de
favorietenkant (−10.9%).

**Twee dingen die je hierbij moet weten en die niet moeten wegvallen.** De niet-monotonie in de
tabel hierboven (de bak onder 25% doet het *beter* dan die van 25–35%) is bij deze aantallen ruis;
de grens is dus "ongeveer waar het misgaat", geen scherp getal. En de belangrijkste reden dat deze
poort lichter kán, staat elders: sinds 5 sep loopt `my_prob` door `scripts/recalibrate.py`, dat de
scheefstand van bijna tien procentpunt er op uitslagen af haalt. Die correctie pakt de oorzaak aan
waar deze poort een symptoom van afdekte. Wie de herijking ooit uitzet, moet deze poort weer
zwaarder maken.

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

# Onder deze marktkans wordt er niet op de underdog-kant gespeeld. Boven deze grens gaat de poort
# open: daar is het gemeten rendement van de underdog-kant (−11.1%) niet te onderscheiden van dat
# van de favorietenkant (−10.9%), en dan is er geen grond om één van beide af te sluiten.
UNDERDOG_FLOOR = 0.35


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
        if mine < UNDERDOG_FLOOR:
            return SideCheck(False, f"underdog-kant onder de ondergrens — de markt geeft deze "
                                    f"ploeg {mine:.1%} tegen {theirs:.1%} voor de tegenstander, "
                                    f"onder de {UNDERDOG_FLOOR:.0%} waar poort 8 (§1) dichtgaat",
                             probs)
        return SideCheck(True, f"underdog-kant, maar boven de ondergrens ({mine:.1%} om "
                               f"{theirs:.1%}; poort 8 sluit onder {UNDERDOG_FLOOR:.0%})", probs)
    return SideCheck(True, f"favorietenkant ({mine:.1%} om {theirs:.1%})", probs)
