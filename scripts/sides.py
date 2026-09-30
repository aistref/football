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

## Teruggezet op 30 september 2026, op verzoek van de gebruiker

**De poort werkt weer.** Hij heeft van 25 t/m 30 september 2026 stilgestaan en houdt sinds
1 oktober opnieuw de underdog-kant onder `UNDERDOG_FLOOR` tegen. De reden staat hieronder onder
"Waarom hij terug is"; de twee alinea's daaronder beschrijven het vervallen en blijven staan omdat
het venster in de code blijft bestaan.

**In dezelfde vorm als vóór het vervallen**, dus de lichte versie met `UNDERDOG_FLOOR = 0.35` en
niet de zware versie van vóór 5 september die élke underdog-kant blokkeerde. Dat is een keuze en
ze hoort uitgelegd, want §1e zegt letterlijk *"zet de herijking ooit uit, dan moet deze poort weer
zwaarder"* en je zou kunnen vinden dat dat hier van toepassing is:

* Die zin is geschreven toen het alternatief was dat de herijking van ~10 procentpunt zou worden
  uitgezet. Dat is niet wat er gebeurd is. De herijking staat aan; ze corrigeert alleen bijna
  niets meer, doordat ze op 20 september op de **ongeselecteerde** ijksteekproef is gezet en het
  ruwe model daarop al goed gekalibreerd blijkt.
* De scheefstand die overblijft is dus niet ~10 procentpunt maar **+1.9 pp op longshots en
  −3.7 pp op favorieten** (3549 uitkomsten, gemeten 30 sep 2026). De zware versie was op een
  scheefstand van die grootte al te grof bevonden: op 5 september leverde ze 311 doorgerekende
  selecties en **nul** bets op.
* De lichte versie mikt precies op de groep waar de schade op uitkomsten zat: de 29 gevallen
  onder de ondergrens deden −31.4%, de zestig erboven −11.1% — niet te onderscheiden van de
  −10.9% van de favorietenkant.

Wordt de herijking ooit écht uitgezet (niet: naar de identiteit gemeten, maar niet meer
toegepast), dan geldt die zin uit §1e onverkort en moet de ondergrens omhoog.

## Waarom hij terug is (30 september 2026)

De onderbouwing van het vervallen is op 30 september onhoudbaar gebleken, en dat is aan de
gebruiker voorgelegd. De keten:

1. Het vervallen is verantwoord met één argument, hieronder vetgedrukt: de herijking van §1g haalt
   ~10 procentpunt van elke te optimistische schatting af en pakt daarmee de oorzaak aan waar deze
   poort een symptoom afdekte.
2. Maar op 20 september is de bron van die herijking veranderd — van `picks.jsonl` + `shadow.jsonl`
   (de geselecteerde groep, met de winner's curse erin) naar `data/calibration.jsonl` (de
   ongeselecteerde ijksteekproef). Dat was een verbetering en ze blijft staan: de oude correctie
   maakte de voorspelling méétbaar slechter.
3. Het gevolg is niemand opgevallen. Op de nieuwe steekproef is de fit ongeveer de identiteit — op
   30 september gemeten `a = 1.0001`, `b = 0.0000` over 3243 waarnemingen, wat nergens meer dan
   één procentpunt van een schatting afhaalt. De correctie waar punt 1 zich op beroept bestaat dus
   sinds 20 september niet meer.
4. Daarmee stond er vanaf 25 september geen enkele rem op deze kant, terwijl de scheefstand zelf
   nog meetbaar aanwezig is.

De gebruiker heeft op 30 september gekozen de poort terug te zetten vóór 9 oktober, de eerste dag
waarop Run A weer wedstrijden heeft. Dat is zijn keuze om te maken — het gaat over
risicobereidheid en niet over de data, dezelfde redenering als bij `selection_score` (§1a) en bij
het vervallen zelf.

**Wat dit kost, en dat hoort er net zo eerlijk bij als bij het vervallen.** De poort houdt bets
tegen die hadden kunnen winnen: de `underdog`-reeks in het schaduwlogboek staat op **+15.8% over
20 afgewikkelde gevallen** (55% trefkans). Dat is precies de reeks die het vervallen moest
beantwoorden, en hij staat positief. Twee dingen die dat relativeren, maar het niet wegnemen:
§6d eist ~30 gevallen voordat zo'n reeks gelezen mag worden en het zijn er 20, en de tegenhanger
`underdog_ruw` staat op **−8.8% over 17 gevallen** — die twee mogen volgens §1e nooit bij elkaar
worden opgeteld, want het zijn twee populaties. Er is dus geen cijfer dat zegt dat terugzetten
goed is; er is een gemeten kalibratiefout die zegt dat de kant scheef staat, en een keuze van de
gebruiker om daar een rem op te houden.

## Het vervallen van 25 t/m 30 september 2026 (keuze van de gebruiker, 18 september 2026)

De poort is ingevoerd met een herzieningsdatum van 25 september en met één voorwaarde erbij: *lees
het schaduwlogboek pas bij ~30 afgewikkelde gevallen, daaronder is elk verschil ruis*. Die twee
zijn niet samen te halen. Op 18 september stonden de twee reeksen op **8** afgewikkelde
`underdog`-rijen (+12.9%) en **9** `underdog_ruw`-rijen (−34.0%), en ze groeien met ongeveer één
rij per dag: op 25 september zijn het er vijftien à twintig, niet dertig.

De gebruiker is die keuze op 18 september voorgelegd — wachten tot er dertig zijn (A), op
25 september beslissen op de cijfers die er dan liggen (B), of de poort op 25 september laten
vervallen zonder meting (C) — en heeft **C** gekozen. Vanaf `LAPSES_ON` laat `check()` dus élke
kant door.

**Wat dat kost, eerlijk opgeschreven, want het is geen neutrale keuze.** De groep die deze poort
tegenhoudt — de underdog-kant onder 35% marktkans — is de enige groep waarvan op uitkomsten is
gemeten dat de routine er structureel naast zit: over 89 gevallen verwachtte het model 47.1
winnaars, de markt 38.0, en het werden er 33.0 (z = −3.14). De 29 gevallen onder de ondergrens
deden −31.4%. Dat de reeks sinds 5 september nauwelijks groeit, bewijst niet dat het probleem weg
is; het komt doordat de herijking van §1g diezelfde kandidaten nu al bij de edge-poort afvangt
(§1e, "de poort wordt op twee schalen geboekt"). Die herijking is daarmee de enige bescherming die
overblijft — **wie haar ooit uitzet, zet deze poort terug.**

> **Precies dat is gebeurd, en niemand heeft het gezien.** De herijking is op 20 september niet
> uitgezet maar wél tot bijna niets teruggebracht, en voor deze poort komt dat op hetzelfde neer.
> Zie "Waarom hij terug is" bovenaan: de poort is op 30 september 2026 teruggezet en bindt weer
> vanaf 1 oktober. Deze alinea beschrijft dus een venster van zes dagen dat voorbij is, en niet de
> huidige stand.

**Wat er blijft meten.** `check()` geeft na het vervallen `would_block=True` op precies de
gevallen die hij eerder zou hebben tegengehouden. Leg dat per selectie vast in `data/run-state/`,
en wordt zo'n selectie een gepubliceerde bet, noteer dan in de pick dat poort 8 hem vóór
25 september had geblokkeerd. Dan is over enkele maanden alsnog op uitslagen te beantwoorden wat
deze keuze heeft gekost of opgeleverd — met echte bets in plaats van schaduwpicks, wat een betere
meting is dan de reeks die we niet hebben kunnen afmaken.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# Onder dit verschil in de-vigde marktkans noemt de markt geen van beide ploegen de mindere, en
# gaat de poort open. 3 procentpunt is niet gemeten maar gekozen: het is ruwweg de spreiding tussen
# bookmakers op dezelfde wedstrijd, dus kleiner dan dat is geen marktoordeel maar ruis.
PICKEM_TOLERANCE = 0.03

# Onder deze marktkans wordt er niet op de underdog-kant gespeeld. Boven deze grens gaat de poort
# open: daar is het gemeten rendement van de underdog-kant (−11.1%) niet te onderscheiden van dat
# van de favorietenkant (−10.9%), en dan is er geen grond om één van beide af te sluiten.
UNDERDOG_FLOOR = 0.35

# De poort is op 25 september 2026 vervallen (keuze C van de gebruiker, 18 sep) en op
# 30 september 2026 op zijn verzoek teruggezet, met ingang van 1 oktober. Dat is dus een
# **venster** waarin hij niets deed, en geen einddatum meer. Het venster blijft met opzet in de
# code staan in plaats van te worden weggehaald: `check(..., today=<rundag>)` moet voor een
# herberekening van 25 t/m 30 september hetzelfde antwoord geven als die dagen zelf gaven, anders
# gaat een hermeting van die zes dagen stil over een andere poort dan er toen stond.
#
# WAAROM 1 OKTOBER EN NIET 30 SEPTEMBER, terwijl het besluit op 30 september is genomen: Run B en
# Run C hadden die dag hun analyse al gedraaid en Run C had twee bets gepubliceerd, waarvan
# Seychelles – Sri Lanka (1 @ 3.15) er één is die deze poort zou hebben tegengehouden — de markt
# gaf Seychelles 28.3%, onder de ondergrens. De poort halverwege die dag laten ingaan zou een al
# gepubliceerde en mogelijk al ingezette bet met terugwerkende kracht blokkeren, en zou een
# herberekening van 30 september een andere poort geven dan de drie runs van die dag gebruikten.
# De gebruiker vroeg om de poort "vóór 9 oktober"; 1 oktober is de eerste dag waarop nog geen run
# had gedraaid en haalt dat ruim.
LAPSED_FROM = date(2026, 9, 25)
LAPSED_UNTIL = date(2026, 10, 1)

# Gehouden voor de leesbaarheid van oudere runrapporten en run-state, die naar deze naam verwijzen.
LAPSES_ON = LAPSED_FROM
REINSTATED_ON = LAPSED_UNTIL   # 1 okt 2026: eerste dag waarop de poort weer bindt


@dataclass(frozen=True)
class SideCheck:
    passed: bool
    reason: str
    market_probs: tuple[float, float, float] | None = None
    would_block: bool = False
    """Zou de poort deze selectie hebben tegengehouden als hij nog gold?

    Gelijk aan `not passed` zolang de poort werkt, en ná `LAPSES_ON` het enige spoor dat ervan
    overblijft. Leg hem vast, ook (juist) als `passed` True is.
    """


def has_lapsed(today: date | None = None) -> bool:
    """Stond de poort op deze dag stil? (§1e)

    Waar is dat alleen voor het venster van 25 t/m 30 september 2026. Vóór 25 september werkte de
    poort en vanaf 1 oktober werkt hij weer, dus voor elke dag buiten dat venster is dit False.
    Geef `today` mee met de **rundag** als je een oude dag herberekent; zonder argument geldt
    vandaag, en dan is het antwoord False.
    """
    day = today or date.today()
    return LAPSED_FROM <= day < LAPSED_UNTIL


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


def check(side: str | None, odds_1x2, today: date | None = None) -> SideCheck:
    """Mag er op deze kant gespeeld worden?

    `side` is "home", "away" of None (Over/Under, BTTS, gelijkspel). `odds_1x2` zijn de drie
    1X2-koersen van de wedstrijd, in de volgorde 1 / X / 2. `today` is de **rundatum**: geef hem
    mee zodat een herberekening van een oude dag hetzelfde antwoord geeft als die dag zelf.

    Binnen het venster `LAPSED_FROM` t/m `LAPSED_UNTIL` (25 t/m 30 sep 2026) is `passed` altijd
    True en zegt alleen `would_block` nog wat de poort zou hebben gedaan. Daarbuiten — dus ook
    vandaag — houdt de poort weer tegen. Zie de docstring van de module.
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
            blocked = (f"underdog-kant onder de ondergrens — de markt geeft deze ploeg "
                       f"{mine:.1%} tegen {theirs:.1%} voor de tegenstander, onder de "
                       f"{UNDERDOG_FLOOR:.0%} waar poort 8 (§1) dichtging")
            if has_lapsed(today):
                return SideCheck(True, f"{blocked}; poort 8 stond van {LAPSED_FROM} tot "
                                       f"{LAPSED_UNTIL} stil (keuze van de gebruiker, 18 sep 2026) "
                                       f"en hield hem op die dag niet tegen", probs,
                                       would_block=True)
            return SideCheck(False, blocked.replace("dichtging", "dichtgaat"), probs,
                             would_block=True)
        return SideCheck(True, f"underdog-kant, maar boven de ondergrens ({mine:.1%} om "
                               f"{theirs:.1%}; poort 8 sluit onder {UNDERDOG_FLOOR:.0%})", probs)
    return SideCheck(True, f"favorietenkant ({mine:.1%} om {theirs:.1%})", probs)
