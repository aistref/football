"""Poort 9 — vraagt een Under op FULL-data méér voordeel, omdat die kant meetbaar scheef staat.

Ingevoerd 11 oktober 2026, op besluit van de gebruiker. Hij koos uit vier mogelijkheden (a: de
vormfout in `score_grid` repareren, b: deze rem, c: beide, d: niets) voor **c** — dus eerst deze
rem, en de reparatie van de oorzaak daarna. Dit bestand is de rem; de oorzaak staat in
`_shared-rules.md` §6g en is met deze poort **niet** weggenomen.

## Waarom hij er is

Aanleiding: AIK – Brommapojkarna (10 okt 2026, Under 3,5 @1,55, uitslag **5–6**) en het feit dat
er op 11 oktober opnieuw vier Unders op de lijst stonden. Nagerekend bleken er **twee fouten op
elkaar** te staan, allebei gemeten op **uitkomsten** en dus vrij van het circulariteitsbezwaar
van §2:

1. **Een vormfout in het scoregrid, aanwezig in de hele populatie.** Over 1076 doorgerekende duels
   klopt het *gemiddelde* aantal doelpunten (voorspeld 3,061 / werkelijk 3,040, z = −0,40) maar de
   *verdeling* niet: 2,0 pp te veel massa op 2 doelpunten en 4,0 pp te weinig op 4 en 5 samen.
   Daardoor staat P(Under 2.5) structureel **2,4 pp** te hoog en P(Under 3/3.5) **1,6 pp** — bij
   élk duel, vóór er iets gekozen is.
2. **Het selectie-effect eroverheen.** In de duels waarin werkelijk een Under is gespeeld vallen
   er **+0,68 doelpunt per duel méér** dan de eigen lambda zei: n = 49, **z = +2,91**, en
   z = +1,96 zonder de twee grootste uitschieters. Op de Over-kant gebeurt dat niet (n = 38,
   z = −0,54).

## Waar de +2,0 pp vandaan komt, en de fout die daarbij eerst is gemaakt

**Lees dit voordat je aan `UNDER_EXTRA` komt, want de eerste onderbouwing was vervuild.** De
eerste poging mat alle 76 afgewikkelde Under-picks samen en vond "het teken draait om bij een lat
van 10,0" (−12,8% → +3,6%). Dat was de val die §6e in zijn zuiverste vorm beschrijft: **een sterk
ogend verband dat alleen bestaat doordat je de verkeerde populatie neemt.** Uitgesplitst per
datatier:

| | n | rendement |
|---|---|---|
| Under op **FULL** | 66 | **−28,2%** |
| Under op **LIGHT** | 10 | +60,6% |

Die tien LIGHT-picks trokken de gepoolde reeks in de plus. Op FULL alleen draait **geen enkele
lat** het teken om — lat 8,0 geeft −24,4%, lat 10,0 −10,4%, lat 12,0 −8,4%. Dat is dezelfde
conclusie als §1g over het hele logboek: er is geen drempel die geld oplevert, alleen een keuze
tussen weinig en veel verlies.

**Wat de 10,0 dan wél doet: hij haalt precies de slechtste band weg.** FULL-Unders per edge-band,
niet cumulatief:

| edge | n | trefkans | rendement |
|---|---|---|---|
| 0–8 pp | 26 | 34,6% | −34,1% |
| **8–10 pp** | **15** | **26,7%** | **−47,7%** |
| 10–12 pp | 9 | 44,4% | −14,0% |
| 12–14 pp | 9 | 55,6% | +4,9% |
| 14+ pp | 7 | 42,9% | −25,4% |

De band van 8 tot 10 procentpunt is **de slechtste van de hele reeks** — slechter dan de band die
de drempel van §0 al wegvangt — met vier winnaars op vijftien. AIK – Brommapojkarna staat er met
+9,28 pp precies in, en zo ook Reading – Mansfield (+9,21), AEK – Aris (+9,93) en
Middlesbrough – West Brom (+9,85). Een lat van 10,0 haalt die vijftien weg en brengt de reeks van
−24,4% naar −10,4%. Daarboven is de curve vlak (−8,7% bij 11, −8,4% bij 12) en vanaf 14 stort hij
in op n = 7, 4 en 1 — de niet-monotone staart die §0 bij de 8,0 ook als ruis aanmerkt.

**`UNDER_EXTRA` is dus +2,0 pp, en dat is "de grens van de slechtste band", geen optimum en geen
belofte van winst.** Het blijft in-sample gekozen — hetzelfde bezwaar dat §0 bij de 8,0 maakt —
maar er ligt een onafhankelijk gemeten mechanisme onder (de vormfout) dat zegt dat juist deze kant
meer marge nodig heeft, en de slechtste band is één samenhangend blok en niet één uitschieter.

## Waarom LIGHT er NIET bij hoort

**De poort raakt alleen `FULL`.** Op LIGHT staan tien afgewikkelde Under-picks, samen +60,6%, en
dat is te weinig om iets te zeggen (§6d eist ~30) én het wijst de andere kant op. Een gemeten rem
uitbreiden naar een populatie waar de meting hem niet steunt, is precies wat §1c en §4 verbieden —
en de LIGHT-lat staat met 16,0 al op het dubbele. Het 2:1-verband tussen de twee drempels, waar
`model.DATA_WEIGHT` van afhangt, blijft daarmee ook ongemoeid.

Gevolg, en het is het vermelden waard: Lillestrøm – Molde van 11 oktober (Under 3,5, +17,66 pp op
LIGHT) zou door deze poort **niet** zijn tegengehouden, terwijl LASK – Rapid Wien (+9,12 pp op
FULL) dat wél zou zijn. Dat is geen inconsequentie maar het verschil tussen een gemeten en een
ongemeten populatie.

## Wat de poort verder NIET dekt

**BTTS "nee" valt erbuiten.** Zelfde richting ("weinig doelpunten") en vermoedelijk dezelfde
oorzaak, maar er liggen maar 15 afgewikkelde BTTS-picks (beide richtingen samen, +29,1%) — niets
gemeten, dus geen rem. Dit is het eerste wat opnieuw bekeken hoort te worden zodra die reeks ~30
gevallen haalt. Op 11 oktober stond er één BTTS-nee op de lijst (Palmeiras – Corinthians,
+7,94 pp) die deze poort niet raakt.

**Over/Under "Over" valt erbuiten.** Die kant staat op +10,6% over 62 gevallen; er is geen enkele
grond voor een rem daar — en volgens §6g betáált die kant juist mee aan dezelfde vormfout.

## Hoe hij werkt

Zoals poort 8: hij **houdt alleen tegen**, stelt `my_prob` niet bij en laat nooit iets extra door.
Elke tegengehouden kandidaat gaat met `failed_gate = "doelpunten_onder"` naar `data/shadow.jsonl`
en wordt daar net zo afgerekend als elke andere kandidaat (§6d), zodat over enkele weken met
cijfers te zeggen is of deze poort geld bespaart of alleen bets kost. Lees die reeks niet onder
~30 afgewikkelde gevallen, en pas hem niet aan op één dag.

**Geef `today` mee met de rundag.** De poort bindt vanaf `BINDS_FROM` (12 okt 2026) en niet eerder:
de run van 11 oktober was al gepubliceerd en verstuurd toen dit besluit viel, en §4 zegt sinds
9 oktober dat een al gepubliceerde run niet met terugwerkende kracht wordt aangevuld — anders geeft
een herberekening van die dag een andere uitkomst dan de dag zelf gaf. Zonder `today` krijgt zo'n
herberekening stil de poort van vandaag. Zelfde constructie als `sides.LAPSED_FROM`.

**En hij is bedoeld om te verdwijnen.** Zodra de vormfout in `score_grid` is gerepareerd (keuze
**a**, nog te doen) hoort deze poort opnieuw gemeten en vermoedelijk verlaagd of geschrapt — net
als bij poort 8, waar de herijking van §1g de rem deels overbodig maakte. Een rem op een symptoom
die blijft staan nadat de oorzaak weg is, kost alleen nog bets.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

#: Hoeveel procentpunt een Under op FULL-data bovenop de drempel van §0 moet halen. Gemeten op de
#: 66 afgewikkelde FULL-Under-picks; zie "Waar de +2,0 pp vandaan komt" in de module-docstring.
UNDER_EXTRA = 2.0

#: Alleen deze datatiers krijgen de verzwaarde lat. LIGHT staat er met opzet niet bij — zie
#: "Waarom LIGHT er NIET bij hoort".
TIERS = ("FULL",)

#: De drempels van §0 waarop `UNDER_EXTRA` wordt opgeteld. Bewust een eigen kopie in plaats van een
#: import uit een runscript, zodat Run A, B en C dezelfde lat gebruiken.
THRESHOLD = {"FULL": 8.0, "LIGHT": 16.0}

#: Eerste dag waarop de poort bindt. Zie de docstring: 11 okt 2026 was al gepubliceerd.
BINDS_FROM = date(2026, 10, 12)


@dataclass
class UnderCheck:
    passed: bool
    reason: str
    required: float | None = None
    #: Wat de poort zou hebben gedaan, ook als hij op die dag nog niet bond. Zelfde rol als
    #: `sides.SideCheck.would_block`: het enige spoor van een poort die nog niet werkt.
    would_block: bool = False


def is_under(market: str | None, selection: str | None) -> bool:
    """Is dit een Over/Under-selectie op de Under-kant?

    Bewust streng op de markt: een handicap of een BTTS valt hier niet onder, ook niet als de
    selectietekst het woord "under" bevat. Zie "Wat de poort verder NIET dekt".
    """
    if (market or "").strip() != "Over/Under":
        return False
    return str(selection or "").strip().lower().startswith("under")


def covers(tier: str | None) -> bool:
    return str(tier or "").upper() in TIERS


def required_edge(tier: str | None) -> float:
    """De lat voor een Under bij deze datatier."""
    base = THRESHOLD.get(str(tier or "").upper(), 8.0)
    return base + UNDER_EXTRA if covers(tier) else base


def binds(today: date | None = None) -> bool:
    return (today or date.today()) >= BINDS_FROM


def check(market: str | None, selection: str | None, edge_pp: float | None,
          tier: str | None, today: date | None = None) -> UnderCheck:
    """Mag deze selectie gepubliceerd worden, gegeven de scheefstand op de Under-kant?

    `edge_pp` is de **herijkte** edge in procentpunten (§1g), dezelfde grootheid waarop de
    edge-afkapping van §5b meet. `today` is de rundatum — geef hem altijd mee.
    """
    if not is_under(market, selection):
        return UnderCheck(True, "geen Under — poort 9 raakt alleen Over/Under op de Under-kant")
    if not covers(tier):
        return UnderCheck(True, f"Under op {tier} — poort 9 geldt alleen voor "
                                f"{'/'.join(TIERS)} (op LIGHT is de scheefstand niet gemeten)")
    lat = required_edge(tier)
    if not isinstance(edge_pp, (int, float)):
        return UnderCheck(True, "geen edge bekend — poort 9 houdt niets tegen zonder meting", lat)
    # ALLEEN DE BAND TUSSEN DE TWEE LATTEN, en dat is geen detail maar de hele meetbaarheid van
    # deze poort. Een Under die de gewone drempel van §0 al niet haalt, wordt door `edge`
    # tegengehouden en niet hierdoor; zou poort 9 die ook claimen, dan loopt de reeks
    # `doelpunten_onder` vol met kandidaten die nooit een bet konden worden en meet ze niets meer
    # — exact de "twee populaties"-fout die §1e bij `underdog_ruw` en §5b bij `lijstlengte`
    # benoemt. Op de 42 duels van 11 okt 2026 ging het om 44 gemarkeerde selecties zonder deze
    # regel en om 4 mét: de rest zat tot -10 pp onder de lat.
    if edge_pp < THRESHOLD["FULL"]:
        return UnderCheck(True, f"Under met {edge_pp:+.2f} pp — onder de gewone drempel van "
                                f"{THRESHOLD['FULL']:.1f} pp, dus `edge` is de bindende poort en "
                                f"niet poort 9", lat)
    if edge_pp >= lat:
        return UnderCheck(True, f"Under met {edge_pp:+.2f} pp, boven de verzwaarde lat van "
                                f"{lat:.1f} pp (poort 9)", lat)
    blocked = (f"Under onder de verzwaarde lat — {edge_pp:+.2f} pp tegen {lat:.1f} pp "
               f"({THRESHOLD['FULL']:.1f} + {UNDER_EXTRA:.1f} voor de gemeten scheefstand op "
               f"deze kant; de band 8–10 pp staat op −47,7% over 15 gevallen, §6g)")
    if not binds(today):
        return UnderCheck(True, f"{blocked}; poort 9 bindt pas vanaf {BINDS_FROM} en hield hem "
                                f"op die dag niet tegen", lat, would_block=True)
    return UnderCheck(False, blocked, lat, would_block=True)
