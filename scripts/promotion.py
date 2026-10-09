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
    # Toegevoegd 1 sep 2026 (Run B). League One stond hier nog niet, terwijl E2/E3 wél gemeten in
    # footballdata.MEASURED_GAPS staat (n=43, het grootste van de acht paren). Drie van de zeven
    # League One-duels van die dag hadden een promovendus uit League Two aan boord (Bromley,
    # Cambridge United, Notts County); zonder deze regel was dat drie keer NONE geweest op een
    # ontbrekende aanroep, niet op een ontbrekende meting.
    "League One (ENG)":           Tier2(109, "League Two (ENG)",          ("E2", "E3")),
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
    # Toegevoegd 2 sep 2026 (Run B). Beide id's zijn niet geraden maar uit de Fotmob-daglijsten
    # van 27 aug t/m 7 sep 2026 gehaald en op naam én ccode gecontroleerd: CZE 253 "FNL" en
    # SUI 163 "Challenge League". Aanleiding: die dag stond er in allebei de competities één duel
    # met een promovendus (FC Zbrojovka Brno bij Czech, FC Vaduz bij Swiss), en zonder deze regels
    # was dat twee keer NONE geweest op een ontbrekende aanroep in plaats van op een ontbrekende
    # meting — precies wat §4 van _shared-rules.md verbiedt.
    #
    # LET OP: allebei zonder `fd_pair` én zonder eigen meting in MEASURED_TIER2_GAP, dus
    # `gap_and_range` valt hier terug op POOLED_GAP. Meld dat in het runrapport; `GapResult.direction`
    # zegt het zelf ("gepoold — ... niet apart gemeten"). Wie hier tijd in wil steken: `measure_gap`
    # over 2016/2017-2024/2025 doet voor deze twee wat de meting van 31 aug voor NED/DEN/POR/BEL/
    # TUR/POL deed.
    "Czech First League (CZE)":   Tier2(253, "FNL (CZE)"),
    "Swiss Super League (SUI)":   Tier2(163, "Challenge League (SUI)"),
    # Toegevoegd 5 sep 2026 (Run B), op dezelfde grond als de twee regels hierboven. Beide id's
    # komen uit de Fotmob-daglijst van 5 sep 2026 en zijn op naam én ccode gecontroleerd (NOR 203
    # "1. Divisjon", SWE 168 "Superettan"), en daarna nog eens op de stand zelf: 16 ploegen per
    # competitie, met Lillestrøm in de Noorse en Västerås SK in de Zweedse — precies de twee
    # promovendi die die dag op `NONE` uitkwamen omdat er geen tweede divisie bekend was.
    #
    # LET OP, hetzelfde voorbehoud als bij CZE en SUI: geen `fd_pair` en geen eigen meting in
    # MEASURED_TIER2_GAP, dus `gap_and_range` valt hier terug op POOLED_GAP. Dat is de factor die
    # op 30 aug de grootste schijnedge van de run opleverde (ADO Den Haag +23.6 pp), dus meld hem
    # in het runrapport — `GapResult.direction` zegt zelf dat hij gepoold is. Wie hier tijd in wil
    # steken: `measure_gap` over 2016/2017-2024/2025 doet voor NOR en SWE wat de meting van
    # 31 aug voor NED/DEN/POR/BEL/TUR/POL deed. Kalenderjaarcompetities, dus seizoen "2025" en
    # niet "2025/2026".
    "Eliteserien (NOR)":          Tier2(203, "1. Divisjon (NOR)"),
    "Allsvenskan (SWE)":          Tier2(168, "Superettan (SWE)"),

    # Toegevoegd 5 okt 2026, op besluit van de gebruiker, en met een EIGEN METING in
    # MEASURED_TIER2_GAP — dus geen gepoolde factor (zie daar).
    #
    # Waarom dit er moest komen: vier runs op rij kostte het een duel. Een promovendus uit de
    # Primera Federación kwam op `data_tier = NONE` uit omdat er geen Spaans paar
    # LaLiga2/Primera Federación bestond — 2 en 3 okt 2026 Sabadell, 4 okt Celta Fortuna, 5 okt
    # Tenerife, drie verschillende ploegen en één gat. De foutmelding noemde alleen de TIER1-tak
    # ("staat niet in de stand van La Liga"), wat de oorzaak makkelijk verkeerd laat lezen.
    #
    # LET OP: DEZE DIVISIE SPEELT IN TWEE PARALLELLE GROEPEN van twintig ploegen, en dat is geen
    # administratief detail. `fotmob.fetch_league_stats` zonder `group` levert de eerste van de
    # twee en zegt niet welke; een ploeg uit de andere groep "staat niet in de stand", en een
    # ploeg die er toevallig wél in staat wordt genormaliseerd op een gemiddelde van een groep
    # waarin hij niet speelde. Die gemiddeldes lopen meetbaar uiteen: 1.366 thuis / 1.058 uit in
    # Group 1 tegen 1.316 / 0.937 in Group 2 (2025/2026). `lower_table()` kiest daarom de groep
    # waarin de ploeg werkelijk staat, en `measure_gap` meet per groep tegen diens eigen
    # gemiddelde. Verwijder die twee niet zonder de meting opnieuw te doen.
    "LaLiga2 (ESP)":              Tier2(8968, "Primera Federación (ESP)"),

    # Toegevoegd 9 okt 2026 (Run B), op besluit van de gebruiker, en met een EIGEN METING in
    # MEASURED_TIER2_GAP — dus geen gepoolde factor (zie daar).
    #
    # Waarom dit er moest komen: op 9 okt 2026 kostte het de HELE Roemeense speelronde. Zowel
    # Corvinul Hunedoara – FC Voluntari (beide ploegen promovendus) als Sepsi OSK – Dinamo
    # București (Sepsi promovendus) kwam op `data_tier = NONE` uit met de melding "geen divisie
    # boven of onder 'Romanian SuperLiga (ROU)' bekend" — niet omdat de analyse iets vond, maar
    # omdat deze tabel geen Roemeense ingang had. Dat is de situatie die §4 van
    # _shared-rules.md expliciet verbiedt: eerst omrekenen, dan pas NONE.
    #
    # Het id is niet geraden. `https://www.fotmob.com/api/data/allLeagues` geeft onder ccode ROU
    # precies vijf competities — Liga I (189), **Liga II (9113)**, Cupa României (190),
    # Supercupa (192) en Liga I Qualification (9587) — en Liga II stond op 10 en 11 oktober 2026
    # ook met acht respectievelijk twee duels in de Fotmob-daglijst, onder diezelfde ccode. De
    # stand gaat terug tot 2010/2011 en heeft thuis/uit-splits in elk gemeten seizoen.
    #
    # LET OP: Liga II heeft een KAMPIOENS-/DEGRADATIESPLITSING ('Promotion Group',
    # 'Relegation Group A', 'Relegation Group B') náást de volledige stand, net als de Deense
    # 1. Division. Dat is géén parallelle opdeling: de groepen overlappen met de hele stand.
    # `_season_tables` gebruikt daarom `fotmob.partitioned_groups` en niet `league_groups` —
    # zie de docstring daar, want tot 9 okt 2026 stond dat fout en telde het elke ploeg dubbel.
    "Romanian SuperLiga (ROU)":   Tier2(9113, "Liga II (ROU)"),

    # GEEN REGEL VOOR KROATIË, en dat is een bronbevinding en geen vergeten regel (9 okt 2026).
    # Het duel HNK Gorica – Rudeš kwam die dag op NONE uit omdat Rudeš promovendus is, en de
    # opdracht was om er — net als voor Roemenië — een gemeten factor voor te maken. Dat kan
    # niet: **Fotmob heeft de Kroatische tweede divisie niet.** `api/data/allLeagues` geeft onder
    # ccode CRO precies drie competities, en geen daarvan is een divisie: HNL (252), Croatian Cup
    # (275) en Super Cup (276). Ook in veertien opeenvolgende daglijsten (9 t/m 22 okt 2026) komt
    # er geen tweede Kroatische competitie voorbij behalve de beker.
    #
    # Er is dus geen stand van de Prva NL om een relatieve sterkte uit te halen, en zonder die
    # invoer is er niets te meten — niet "nog niet gemeten" maar "niet meetbaar op deze bron".
    # Een gepoolde factor erop zetten zou het gat wél dichten en is precies wat §2 en §4
    # verbieden: dan draait een Kroatische promovendus op een getal dat uit zes andere landen
    # komt, en §4 zegt sinds 31 aug 2026 dat geen enkele competitie uit de runlijst nog op een
    # gepoolde factor draait. Een Kroatische promovendus blijft daarom NONE, en dat is de
    # eerlijke uitkomst. Wie dit ooit wil oplossen heeft een andere bron voor de Prva NL nodig,
    # geen regel hier.
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
#:
#: **LaLiga2 (ESP) / Primera Federación is er op 5 okt 2026 bij gekomen, op besluit van de
#: gebruiker.** Zelfde methode, zelfde `measure_gap`, maar met twee dingen die het vermelden
#: waard zijn voordat iemand eraan sleutelt.
#:
#: 1. **De divisie is twee keer van vorm veranderd en de factor niet.** Fotmob-id 8968 dekt de
#:    hele Spaanse derde divisie, maar in 2016/17-2019/20 was dat Segunda B met VIER groepen, in
#:    2020/21 en 2021/22 heeft dat id helemaal geen stand, en vanaf 2022/23 is het de Primera
#:    Federación met TWEE groepen. Apart gemeten geven die twee tijdperken bijna hetzelfde
#:    antwoord: Primera Federación 0.719 / 1.544 (n=12) tegen Segunda B 0.695 / 1.637 (n=16).
#:    Dat ze zo dicht bij elkaar liggen is de reden dat ze hier samen één factor vormen over
#:    n=28 — niet het verlangen naar een hoger getal voor n. Wijken ze ooit wél uiteen, dan
#:    hoort alleen het Primera Federación-tijdperk te blijven.
#: 2. **Het gat is op de AANVALSKANT KLEINER dan de gepoolde factor aannam** (0.716 tegen
#:    0.605), en dat is dezelfde soort correctie als bij Denemarken, nu de andere kant op: de
#:    gepoolde factor was hier te streng. Een Spaanse promovendus houdt méér van zijn aanval
#:    over dan de pool suggereerde. Verdediging 1.581 tegen 1.513 gepoold, wat nauwelijks
#:    scheelt.
#:
#: De twaalf promovendi van het Primera Federación-tijdperk, voor wie het wil narekenen:
#: Alcorcón, Eldense, Racing de Ferrol en SD Amorebieta (2022), Castellón, Córdoba, Deportivo A
#: Coruña en Málaga (2023), AD Ceuta FC, Cultural Leonesa, FC Andorra en Real Sociedad B (2024).
#:
#: Wat het bereik hier tegenhoudt, en dat is geen bijzaak: **Celta Fortuna valt erbuiten.** Zijn
#: relatieve verdediging in 2025/2026 is 1.042 tegen een gemeten maximum van 0.925, dus
#: `conversion_in_range` weigert en de ploeg blijft `NONE`. Dat is correct gedrag en precies de
#: Coventry-val waarvoor die poort bestaat — een beloftenelftal dat promoveerde met een
#: verdediging zwakker dan alles wat ooit gemeten is, is geen geval om op te extrapoleren. Van
#: de drie ploegen die deze lacune in oktober 2026 zichtbaar maakten worden er dus twee
#: opgelost (Tenerife, Sabadell) en wordt de derde met reden geweigerd.
#:
#: Narekenen:
#:     PYTHONPATH=. python3 -c "from scripts import promotion as P; \
#:         print(P.measure_gap('LaLiga2 (ESP)', 140, range(2016, 2025)).summary())"
MEASURED_TIER2_GAP: dict[str, tuple[float, float, int, float, float, float, float]] = {
    "Eredivisie (NED)":         (0.614, 1.564, 23, 0.941, 1.775, 0.407, 0.979),
    "Danish Superliga (DEN)":   (0.624, 1.807, 18, 0.989, 1.747, 0.462, 0.989),
    "Primeira Liga (POR)":      (0.615, 1.504, 22, 1.093, 1.717, 0.457, 0.950),
    "Belgian Pro League (BEL)": (0.696, 1.604, 13, 0.759, 1.691, 0.462, 1.109),
    "Süper Lig (TUR)":          (0.708, 1.497, 27, 0.979, 1.912, 0.497, 1.124),
    "Ekstraklasa (POL)":        (0.680, 1.743, 24, 1.069, 1.516, 0.505, 0.929),
    # Gemeten 5 okt 2026, niet 31 aug — zie `MEASURED_GAP_DATE` hieronder.
    "LaLiga2 (ESP)":            (0.716, 1.581, 28, 1.019, 1.905, 0.498, 0.925),
    # Gemeten 9 okt 2026 (Run B), op besluit van de gebruiker — zie de toelichting hieronder.
    "Romanian SuperLiga (ROU)": (0.541, 1.811, 16, 0.888, 1.740, 0.285, 1.250),
}

#: **Romanian SuperLiga (ROU) / Liga II is er op 9 okt 2026 bij gekomen, op besluit van de
#: gebruiker.** Zelfde methode en dezelfde `measure_gap` als de zeven paren hierboven, maar er
#: zijn drie dingen die erbij horen voordat iemand dit getal gebruikt of eraan sleutelt.
#:
#: 1. **Het gat is op de AANVALSKANT het grootste dat tot nu toe is gemeten: 0.541.** Alle zeven
#:    andere paren liggen tussen 0.614 (NED) en 0.716 (ESP), en de gepoolde factor staat op
#:    0.605. Een Roemeense promovendus houdt dus mínder van zijn aanval over dan waar ook —
#:    ruwweg de helft in plaats van tweederde. De verdedigingskant (1.811) ligt vlak bij
#:    Denemarken (1.807) en duidelijk boven de gepoolde 1.513. Had deze competitie op de
#:    gepoolde factor gedraaid, dan was een Roemeense promovendus systematisch te sterk
#:    ingeschat op beide kanten tegelijk — precies de fout die op 30 aug 2026 ADO Den Haag
#:    +23.6 pp schijnedge gaf. Dat is de opbrengst van deze meting, en ze is groter dan het
#:    dichten van het gat zelf.
#:
#: 2. **n=16 over zes seizoenen en niet negen, en dat is een echte beperking.** Fotmob-id 9113
#:    heeft voor 2016/2017 en 2017/2018 geen bruikbare stand; de meting loopt daarom over de
#:    promovendi van 2018/2019 t/m 2024/2025. Zestien is het tweede kleinste aantal van de acht
#:    paren (alleen BEL is kleiner met 13). Het is een mediaan over zestien, dus één ingestorte
#:    promovendus verschuift hem niet — maar lees hem als "ongeveer waar het ligt" en niet als
#:    een scherp getal, net als bij de andere zeven.
#:
#: 3. **Liga II heeft een kampioens-/degradatiesplitsing, en die telde mee tot vandaag.** Zie de
#:    docstring van `_season_tables`: die functie vroeg `league_groups` in plaats van
#:    `partitioned_groups` en behandelde de 'Promotion Group' en de twee 'Relegation Groups' als
#:    parallelle groepen. Daardoor kwam elke ploeg twee keer in de meting en werd de helft van de
#:    rijen genormaliseerd op het gemiddelde van zes of zeven ploegen in plaats van op dat van de
#:    competitie. Dat is op 9 okt 2026 gerepareerd vóórdat deze meting is gedaan, en de reparatie
#:    is getoetst door alle zeven bestaande paren opnieuw te meten: ze reproduceren alle zeven
#:    exact de waarde in deze tabel.
#:
#: De zestien gemeten promovendi, voor wie het wil narekenen: FC Argeș Pitesti en UTA Arad
#: (2019), CS Mioveni, Rapid București en U Craiova 1948 (2020), Hermannstadt, Petrolul Ploiești
#: en Universitatea Cluj (2021), CSM Politehnica Iași, Dinamo București en Oțelul Galați (2022),
#: FC Gloria Buzău en FC Unirea Slobozia (2023), Csikszereda Miercurea Ciuc, FC Argeș Pitesti en
#: FC Metaloglobus București (2024).
#:
#: Narekenen:
#:     PYTHONPATH=. python3 -c "from scripts import promotion as P; \
#:         print(P.measure_gap('Romanian SuperLiga (ROU)', 189, range(2016, 2025)).summary())"
#:
#: **En er is met opzet GEEN Kroatische ingang bijgekomen**, hoewel die op 9 oktober in dezelfde
#: opdracht zat. Fotmob heeft de Kroatische tweede divisie niet — `api/data/allLeagues` geeft
#: onder ccode CRO alleen HNL, beker en supercup. Zonder stand van de Prva NL is er geen
#: invoersterkte en dus niets te meten: niet "nog niet gemeten" maar niet meetbaar op deze bron.
#: Zie de opmerking bij `TIER2` hierboven.

#: Wanneer elk paar hierboven is gemeten. Stond tot 5 okt 2026 als "31 aug 2026" hard in de
#: notitie van `gap_and_range`, en dat zou met de eerste latere meting een onwaarheid zijn
#: geworden die in elke pick-notitie en elk runrapport terechtkomt.
MEASURED_GAP_DATE: dict[str, str] = {
    "Eredivisie (NED)": "31 aug 2026", "Danish Superliga (DEN)": "31 aug 2026",
    "Primeira Liga (POR)": "31 aug 2026", "Belgian Pro League (BEL)": "31 aug 2026",
    "Süper Lig (TUR)": "31 aug 2026", "Ekstraklasa (POL)": "31 aug 2026",
    "LaLiga2 (ESP)": "5 okt 2026",
    "Romanian SuperLiga (ROU)": "9 okt 2026",
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
    wanneer = MEASURED_GAP_DATE.get(top_competition, "datum onbekend")
    gap = fd.GapResult(a, d, n, f"up (gemeten {wanneer} op Fotmob, {top_competition}/{t2.name})")
    buiten = []
    if not a_min <= attack <= a_max:
        buiten.append(f"aanval {attack:.3f} buiten {a_min:.3f}-{a_max:.3f}")
    if not d_min <= defence <= d_max:
        buiten.append(f"verdediging {defence:.3f} buiten {d_min:.3f}-{d_max:.3f}")
    label = f"{top_competition}/{t2.name} up (eigen meting {wanneer}, n={n})"
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


#: Dezelfde competitie onder een andere naam. `TIER2` en `TIER1` zijn gevuld met de namen zoals
#: `prompts/run-a.md` ze schrijft; `prompts/run-b.md` schrijft er drie anders, en een dict-lookup
#: die op de spelling afgaat vindt die dan niet.
#:
#: Aanleiding (5 sep 2026, Run B). Op die zaterdag stonden er 11 League One-, 12 League Two- en
#: 5 Segunda-duels op de runlijst. Zestien van de vijfendertig doorgerekende duels kwamen op
#: `NONE` uit omdat een ploeg niet in de stand van vorig seizoen stond — en voor de helft daarvan
#: was de omrekening gewoon aanwezig: Sheffield Wednesday (Championship -> League One), Cambridge,
#: Notts County en MK Dons (League Two -> League One), Port Vale, Rotherham, Exeter en Northampton
#: (League One -> League Two) en Girona (La Liga -> LaLiga2). Alle vier de divisieparen staan
#: **gemeten** in `footballdata.MEASURED_GAPS`. Het was dus geen ontbrekende meting maar een
#: ontbrekende sleutel — precies de fout die de docstring van `convert_relegated` op 1 sep
#: beschreef, één laag hoger.
#:
#: Vertaal daarom altijd via `_resolve` en niet met een rauwe `TIER2.get(naam)`.
COMPETITION_ALIASES: dict[str, str] = {
    "English League One (ENG)": "League One (ENG)",
    "English League Two (ENG)": "League Two (ENG)",
    "Segunda División (ESP)":   "LaLiga2 (ESP)",
}


def _resolve(competition: str) -> str:
    """De naam waaronder `TIER2`/`TIER1` deze competitie kennen."""
    return COMPETITION_ALIASES.get(competition, competition)


def lower_table(t2: "Tier2", season: str, team: str, *, use_cache: bool = True):
    """De stand van de divisie eronder waarin `team` werkelijk staat, plus de groepsnaam.

    **Toegevoegd 5 okt 2026, omdat een divisie in parallelle groepen hier stil misging.** De
    Primera Federación (ESP) speelt in twee groepen van twintig; `fetch_league_stats` zonder
    `group` levert dan de eerste van de twee (zie `fotmob._pick_table`). Een promovendus uit de
    andere groep staat daar niet in, en de foutmelding die eruit komt — "staat niet in de stand" —
    leest als "deze ploeg heeft geen historie" in plaats van "ik heb in de verkeerde groep
    gekeken". Erger nog is het geval dat hij er wél toevallig in staat: dan wordt hij
    genormaliseerd op het gemiddelde van een groep waarin hij niet speelde, en dat gemiddelde
    verschilt meetbaar (1.366/1.058 in Group 1 tegen 1.316/0.937 in Group 2, 2025/2026).

    Geeft `(tabel, groepsnaam_of_None)`. Een ploeg die in twee groepen voorkomt wordt geweigerd —
    liever geen omrekening dan een omrekening op de verkeerde stand.
    """
    # `partitioned_groups` en NIET `league_groups`: alleen een echte opdeling in parallelle
    # groepen hoort hier een rol te spelen. Een kampioens-/degradatiesplitsing gebruikt hetzelfde
    # veld in de respons maar is iets anders — daar overlappen de groepen met de volledige stand
    # en is "de grootste groep" wél het juiste antwoord, precies zoals `_pick_table` het zonder
    # `group` al deed. Dat onderscheid is niet academisch: een eerdere versie van deze functie
    # keek naar alle groepen en liep daarmee vast op Lyngby, dat in de Deense 1. Division zowel in
    # "Promotion Group" als in de volledige stand staat. De zelftest onderaan dit bestand ving dat.
    groups = []
    try:
        import urllib.parse
        enc = urllib.parse.quote(season, safe="")
        meta = fotmob._get_json(
            f"https://www.fotmob.com/api/data/leagues?id={t2.fotmob_id}&season={enc}")
        groups = fotmob.partitioned_groups(meta.get("table", []))
    except Exception:
        groups = []

    # Bij een opdeling wordt de groep EXPLICIET bepaald, ook als de ongesplitste stand de ploeg
    # toevallig zou bevatten: zonder `group` geeft `fetch_league_stats` bij twee gelijke groepen
    # de eerste, dus een ploeg uit Group 1 zou op de juiste stand uitkomen bij geluk in plaats van
    # bij ontwerp — en stil op de verkeerde zodra Fotmob de groepen in een andere volgorde geeft.
    treffers = []
    for g in groups:
        try:
            cand = fotmob.fetch_league_stats(t2.fotmob_id, season, use_cache=use_cache, group=g)
        except Exception:
            continue
        if find_team(cand["teams"], team) is not None:
            treffers.append((g, cand))
    if len(treffers) == 1:
        g, cand = treffers[0]
        return cand, g
    if len(treffers) > 1:
        raise PromotionError(
            f"{team!r} staat in meer dan één groep van {t2.name} {season} "
            f"({', '.join(g for g, _ in treffers)}) — geen omrekening op een onzekere stand")
    # Geen opdeling, of de ploeg staat in geen van de groepen: de ongesplitste stand, en `convert`
    # maakt er een PromotionError van als de ploeg daar ook niet in staat.
    return fotmob.fetch_league_stats(t2.fotmob_id, season, use_cache=use_cache), None


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
    t2 = TIER2.get(_resolve(top_competition))
    if t2 is None:
        raise PromotionError(f"geen tweede divisie bekend voor {top_competition!r}")

    lower, groep = lower_table(t2, season, team, use_cache=use_cache)
    table = lower["teams"]
    row = find_team(table, team)
    if row is None:
        waar = f"{t2.name} {season}" + (f" (groep {groep})" if groep else "")
        raise PromotionError(f"{team!r} staat niet in de stand van {waar}")

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

    groep_noot = f", groep {groep}" if groep else ""
    note = (f"{team}: {t2.name} {season} (Fotmob {t2.fotmob_id}{groep_noot}) relatieve aanval {attack:.3f} / "
            f"verdediging {defence:.3f} over {played} duels, omgerekend met "
            f"gap_for({higher_slug},{lower_slug},up) x{gap.attack:.3f}/{gap.defence:.3f} "
            f"[{gap.direction}] naar {new_attack:.3f}/{new_defence:.3f}; "
            f"conversion_in_range: {range_note}")
    return Converted(team=team, stats=stats, splits=splits, in_range=in_range, note=note)


@dataclass(frozen=True)
class Tier1:
    """De divisie **boven** een competitie uit de runlijst — waar de degradanten vandaan komen.

    Spiegelbeeld van `Tier2`. `fd_pair` is hetzelfde divisiepaar `(hoger, lager)` als daar; alleen
    de richting waarin `footballdata.gap_for` hem opzoekt verschilt (`"down"` in plaats van
    `"up"`).
    """
    fotmob_id: int
    name: str
    fd_pair: tuple[str, str] | None = None


#: Competitie uit de runlijst -> de divisie erboven. Alleen ingevuld waar een run een degradant
#: kan tegenkomen; de `fotmob_id`s zijn dezelfde die `tmp-run/*_stage3.py` voor die competities
#: gebruikt en op naam geverifieerd op 1 sep 2026.
TIER1: dict[str, Tier1] = {
    "Championship (ENG)": Tier1(47, "Premier League (ENG)", ("E0", "E1")),
    "Serie B (ITA)":      Tier1(55, "Serie A (ITA)",        ("I1", "I2")),
    "LaLiga2 (ESP)":      Tier1(87, "La Liga (ESP)",        ("SP1", "SP2")),
    "2. Bundesliga (GER)": Tier1(54, "Bundesliga (GER)",    ("D1", "D2")),
    "Ligue 2 (FRA)":      Tier1(53, "Ligue 1 (FRA)",        ("F1", "F2")),
    # Toegevoegd 1 sep 2026 (Run B), spiegelbeeld van de TIER2-regel hierboven. Op de Run
    # B-runlijst van die dag stonden zeven League One- en twaalf League Two-duels; zeven ploegen
    # waren van boven ingestroomd (Leicester City, Oxford United en Sheffield Wednesday uit de
    # Championship; Exeter City, Northampton Town, Port Vale en Rotherham United uit League One).
    # Beide paren staan gemeten in footballdata.MEASURED_GAPS onder direction="down".
    "League One (ENG)":   Tier1(48,  "Championship (ENG)",  ("E1", "E2")),
    "League Two (ENG)":   Tier1(108, "League One (ENG)",    ("E2", "E3")),
    # Toegevoegd 11 sep 2026 (Run B), op dezelfde grond als de twee regels hierboven: een
    # ontbrekende aanroep, geen ontbrekende meting. De Keuken Kampioen Divisie staat sinds de
    # eerste versie als TIER2 van de Eredivisie in de tabel hierboven (Fotmob 111), maar de
    # omgekeerde richting stond er niet, en die is voor deze competitie juist de drukste: elk
    # seizoen zakken er twee Eredivisieclubs in. Op 11 sep 2026 kostte dat twee van de acht
    # duels — Heracles (Fotmob 9791) en NAC Breda (9761), allebei gedegradeerd uit de
    # Eredivisie 2025/2026 en allebei gewoon in die eindstand te vinden — en dat was `NONE` op
    # een lege dict-lookup, niet op een gat in de data.
    #
    # LET OP, net als bij de Czech/Swiss TIER2-regels: er is geen `fd_pair` (football-data.co.uk
    # dekt de Eerste Divisie niet) en `MEASURED_TIER2_GAP` meet alleen de richting omhóóg, dus
    # `convert_relegated` valt hier terug op POOLED_GAP (x1.654 aanval / x0.647 verdediging,
    # n=240). `GapResult.direction` zegt dat zelf ("gepoold — ... niet apart gemeten"); meld het
    # in het runrapport. Wie hier tijd in wil steken: `measure_gap` over 2016/2017-2024/2025 in
    # de richting "down" doet voor dit paar wat de meting van 31 aug voor de opwaartse richting
    # deed.
    "Keuken Kampioen Divisie (NED)": Tier1(57, "Eredivisie (NED)"),
}


#: Bekercompetitie -> de divisie waarvan de basis (niveau, splits, `TIER1`/`TIER2`-keten) wordt
#: genomen. Een beker heeft zelf geen stand, dus zonder deze tabel is er geen competitiegemiddelde
#: om ploegen op te normaliseren. Stond tot 15 sep 2026 als `PROMO_COMP` in elk analysescript van
#: elke run apart; hij hoort hier, naast `TIER1` en `TIER2` waar hij op wordt opgezocht.
CUP_BASE: dict[str, str] = {
    "Coppa Italia (ITA)": "Serie A (ITA)",
    "DFB Pokal (GER)":    "Bundesliga (GER)",
    "KNVB Beker (NED)":   "Eredivisie (NED)",
    "FA Cup (ENG)":       "Premier League (ENG)",
    "League Cup (ENG)":   "Premier League (ENG)",
}


@dataclass(frozen=True)
class SharedDivision:
    """De divisie waarin **beide** ploegen van een duel staan, lager dan de opgegeven basis."""
    competition: str
    fotmob_id: int
    home_key: str
    away_key: str
    depth: int
    note: str


def shared_lower_division(top_competition: str, home: str, away: str, season: str,
                          *, max_depth: int = 3, use_cache: bool = True) -> SharedDivision | None:
    """De laagste-gemeenschappelijke divisie van twee ploegen die geen van beide in `top_competition` staan.

    **Waarom dit bestaat (15 sep 2026).** Een bekertoernooi heeft zelf geen stand, dus de runs
    hangen de sterktes op aan één vaste basisdivisie (`PROMO_COMP`: de League Cup aan de Premier
    League, de Coppa Italia aan de Serie A, enzovoort). Een ploeg die dáár niet in staat wordt
    omgerekend uit de divisie eronder — één divisie diep, want verder is er geen meting. Twee
    divisies eronder valt de wedstrijd dus op `NONE`.

    Dat is juist zolang de twee ploegen op **verschillende** niveaus spelen: dan is het
    krachtsverschil tussen die niveaus precies wat je moet kennen en niet hebt. Maar spelen ze
    allebei in dezelfde divisie, dan is er niets om te overbruggen. Het duel is gewoon door te
    rekenen in de context van die divisie, net als een competitiewedstrijd daar — dat het in een
    beker wordt gespeeld verandert aan de rekensom niets. De omweg langs de basisdivisie is dan
    een omweg naar een muur die er niet staat.

    Dat kostte op 8 sep 2026 Leyton Orient – Bradford en op 15 sep 2026 Peterborough United –
    Barnsley, beide keren twee League One-ploegen in een League Cup-tie, beide keren `NONE` op een
    omrekening die niet nodig was. Het is een **bronngat noch datagat**: Fotmob heeft xG voor
    League One, en beide ploegen staan gewoon in die stand.

    Wat deze functie **niet** doet, en met opzet: ze lost een duel tussen ploegen uit
    verschillende divisies niet op. Reading – Brentford (League One tegen Premier League) blijft
    `NONE`, want daar is het niveauverschil wél de vraag. Ze zoekt uitsluitend naar de eerste
    divisie in de `TIER2`-keten waarin **beide** namen voorkomen, en geeft anders `None` terug —
    nooit een gok, nooit een gepoolde factor.

    `max_depth` begrenst hoe ver de keten wordt afgelopen (standaard 3: Premier League ->
    Championship -> League One -> League Two). `season` is het laatst afgeronde seizoen, net als
    bij `convert`.
    """
    comp = _resolve(top_competition)
    seen = {comp}
    for depth in range(1, max_depth + 1):
        t2 = TIER2.get(comp)
        if t2 is None:
            return None
        nxt = _resolve(t2.name)
        if nxt in seen:            # kringetje in de keten — nooit voorgekomen, maar goedkoop af te vangen
            return None
        seen.add(nxt)
        try:
            table = fotmob.fetch_league_stats(t2.fotmob_id, season, use_cache=use_cache)["teams"]
        except Exception:
            return None
        hk, ak = find_team(table, home), find_team(table, away)
        if hk and ak:
            return SharedDivision(
                competition=t2.name, fotmob_id=t2.fotmob_id, home_key=hk, away_key=ak,
                depth=depth,
                note=(f"beide ploegen staan in {t2.name} {season} (Fotmob {t2.fotmob_id}), "
                      f"{depth} divisie(s) onder {top_competition} — geen omrekening nodig, "
                      f"het duel is in die divisie doorgerekend"))
        comp = nxt
    return None


def convert_relegated(competition: str, team: str, season: str, league: LeagueContext,
                      *, use_cache: bool = True) -> Converted:
    """Reken een **degradant** om naar `competition`, op zijn cijfers in de divisie erbóven.

    Bestaansreden (1 sep 2026). `convert()` hierboven lost de promovendus op, maar een competitie
    krijgt elk seizoen van twee kanten nieuwe ploegen. Op 1 sep 2026 stonden er acht
    Championship-duels op de Run A-runlijst en waren zes van de vierentwintig ploegen niet in de
    stand van vorig seizoen te vinden: **Lincoln City, Bolton Wanderers en Cardiff City** kwamen
    uit League One (die kon `convert()` al aan) en **West Ham United, Wolverhampton Wanderers en
    Burnley** uit de Premier League (die kon niemand aan). Dat kostte precies één duel volledig —
    West Ham – Wolves, twee degradanten tegen elkaar — plus de helft van de kansinput van elk
    ander duel waarin er een speelde.

    Er was daarvoor geen inhoudelijke reden, alleen een ontbrekende aanroep: de factoren staan al
    **gemeten** in `footballdata.MEASURED_GAPS` onder `direction="down"` (E0/E1: x1.830 aanval,
    x0.634 verdediging, n=33) en het bijbehorende invoerbereik in `CONVERSION_RANGE`. Dit is dus
    dezelfde methode als `convert()`, met de brontabel een divisie hoger en de richting omgekeerd.

    Alles wat voor een promovendus geldt, geldt hier onverkort:

    - **nooit `FULL`** — `RESIDUAL_SPREAD` houdt ook na deze correctie ~0.16 relatieve sterkte
      over, en dat is onzekerheid die de omrekening niet wegneemt;
    - **`conversion_in_range` is een poort, geen aantekening** — buiten het gemeten bereik is er
      geen meting, dus `NONE`. De degradantenkant van dat bereik is even eenzijdig als de
      promovendikant: over alle acht paren kwam geen enkele degradant boven een relatieve aanval
      van 1.089 uit.
    """
    t1 = TIER1.get(_resolve(competition))
    if t1 is None:
        raise PromotionError(f"geen divisie erboven bekend voor {competition!r}")

    higher = fotmob.fetch_league_stats(t1.fotmob_id, season, use_cache=use_cache)
    table = higher["teams"]
    row = find_team(table, team)
    if row is None:
        raise PromotionError(f"{team!r} staat niet in de stand van {t1.name} {season}")

    ts = table[row]
    if "home" not in ts or "away" not in ts:
        raise PromotionError(f"{team!r} heeft geen thuis/uit-splits in {t1.name}")

    high_home, high_away = _rates(table)
    played = ts.get("played") or (ts["home"]["played"] + ts["away"]["played"])
    if not played:
        raise PromotionError(f"{team!r} heeft nul gespeelde duels in {t1.name}")

    high_avg = (high_home + high_away) / 2
    attack = (ts["gf"] / played) / high_avg
    defence = (ts["ga"] / played) / high_avg

    higher_slug, lower_slug = t1.fd_pair or (t1.name, competition)
    gap = fd.gap_for(higher_slug, lower_slug, "down")
    in_range, range_note = fd.conversion_in_range(higher_slug, lower_slug, "down", attack, defence)
    new_attack, new_defence = fd.convert_strength(attack, defence, gap)

    level = league.avg_xg_per_match
    stats = TeamStats(xg=new_attack * level * played,
                      xga=new_defence * level * played,
                      matches_played=played)

    low_home = league.home_goals_per_match
    low_away = league.away_goals_per_match
    hp, ap = ts["home"]["played"], ts["away"]["played"]

    def scaled(goals: int, played_side: int, from_rate: float, to_rate: float, factor: float) -> int:
        if not played_side or not from_rate:
            return 0
        rate = (goals / played_side) / from_rate * factor * to_rate
        return max(0, round(rate * played_side))

    splits = TeamSplits(
        home_gf=scaled(ts["home"]["gf"], hp, high_home, low_home, gap.attack),
        home_ga=scaled(ts["home"]["ga"], hp, high_away, low_away, gap.defence),
        home_played=hp,
        away_gf=scaled(ts["away"]["gf"], ap, high_away, low_away, gap.attack),
        away_ga=scaled(ts["away"]["ga"], ap, high_home, low_home, gap.defence),
        away_played=ap,
    )

    note = (f"{team}: {t1.name} {season} (Fotmob {t1.fotmob_id}) relatieve aanval {attack:.3f} / "
            f"verdediging {defence:.3f} over {played} duels, omgerekend met "
            f"gap_for({higher_slug},{lower_slug},down) x{gap.attack:.3f}/{gap.defence:.3f} "
            f"[{gap.direction}] naar {new_attack:.3f}/{new_defence:.3f}; "
            f"conversion_in_range: {range_note}")
    return Converted(team=team, stats=stats, splits=splits, in_range=in_range, note=note)


def _selftest() -> int:
    """Reproduceert de vier duels die op 30 aug 2026 op NONE bleven staan."""
    from scripts.model import scale_level

    cases = [
        ("Eredivisie (NED)", 57, ["ADO Den Haag", "Cambuur", "Willem II"]),
        # Lyngby staat in de Deense 1. Division zowel in "Promotion Group" als in de volledige
        # stand. Dat is een kampioenssplitsing en géén opdeling in parallelle groepen, dus
        # `lower_table` hoort hier de volledige stand te nemen. Deze regel is op 5 okt 2026 de
        # zelftest die een regressie ving: een versie die naar ALLE groepen keek in plaats van
        # alleen naar een echte opdeling, weigerde hem met "staat in meer dan één groep".
        ("Danish Superliga (DEN)", 46, ["Lyngby"]),
        # Toegevoegd 5 okt 2026 met de meting voor LaLiga2/Primera Federación. Deze drie dekken
        # alle drie de uitkomsten die de groepsafhandeling moet geven, en ze zijn alle drie een
        # echt duel uit oktober 2026:
        #   Tenerife      Group 1, binnen het gemeten bereik           -> LIGHT
        #   Sabadell      Group 2, dus NIET in de ongesplitste stand   -> LIGHT
        #   Celta Fortuna Group 1, verdediging 1.042 buiten het bereik -> NONE (terecht)
        # Verwacht wordt dat de derde op NONE uitkomt; dat is geen fout en de controle hieronder
        # rekent hem dus niet mee.
        ("LaLiga2 (ESP)", 140, ["Tenerife", "Sabadell", "Celta Fortuna"]),
    ]
    verwacht_none = {("LaLiga2 (ESP)", "Celta Fortuna")}
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
            if (comp, team) in verwacht_none and c.tier != "NONE":
                print("                   ^^ VERWACHT NONE (buiten het gemeten bereik) "
                      f"maar kreeg {c.tier} — conversion_in_range laat te veel door")
                fouten += 1
            if (comp, team) not in verwacht_none and c.tier == "NONE":
                print("                   ^^ ONVERWACHT NONE — de omrekening is stukgelopen")
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


def _season_tables(league_id: int, season: str) -> list[tuple[str | None, dict]]:
    """De stand(en) van één competitie-seizoen: [(groepsnaam of None, {naam: rij})].

    Toegevoegd 5 okt 2026. Een competitie die in PARALLELLE groepen is verdeeld heeft geen
    competitiegemiddelde — hij heeft er één per groep, en die lopen uiteen: de Primera Federación
    (ESP) staat in 2025/2026 op 1.366 thuisdoelpunten per duel in Group 1 tegen 1.316 in Group 2,
    en het verschil in uitdoelpunten is groter (1.058 tegen 0.937). `_rel` normaliseert op het
    gemiddelde van de tabel die hij meekrijgt, dus een ploeg hoort tegen de stand van ZIJN EIGEN
    groep te worden afgezet en niet tegen die van de andere.

    Zonder groepen geeft dit precies wat er altijd al gebeurde: één tabel, groepsnaam None.

    **PARTITIONED_GROUPS EN NIET LEAGUE_GROUPS, en dat was hier tot 9 okt 2026 fout** (Run B).
    Deze functie vroeg `fotmob.league_groups`, en die geeft élke groep in het `tables`-veld terug
    — ook de kampioens-/degradatiesplitsing van een competitie die gewoon één stand heeft.
    `fotmob.partitioned_groups` is op diezelfde 5 oktober geschreven om precies dat onderscheid te
    maken, en zegt in zijn eigen docstring waarvoor: *"zodat een aanroeper die op groepen wil
    werken de splitsingscompetities ongemoeid laat."* Deze functie is die aanroeper, en ze riep de
    verkeerde aan.

    Wat dat kostte, gemeten op 9 okt 2026 bij Liga II (ROU) en 1. Division (DEN) — twee divisies
    met zo'n splitsing:

    * **Elke ploeg werd dubbel geteld.** Liga II 2024/2025 gaf 'Promotion Group' (6),
      'Relegation Group A' (7), 'Relegation Group B' (7) EN 'Liga II' (20): veertig rijen voor
      twintig ploegen. De groepen OVERLAPPEN met de volledige stand, dus iedere ploeg kwam twee
      keer in de meting.
    * **En de helft van die rijen werd tegen het verkeerde gemiddelde genormaliseerd** — een
      ploeg uit de 'Promotion Group' tegen het gemiddelde van zes kopploegen in plaats van tegen
      dat van de competitie. Dat is de fout die `_rel` juist moet voorkomen.

    Narekenbaar aan Denemarken, want dat paar is op 31 aug 2026 gemeten toen deze functie nog niet
    bestond: `measure_gap('Danish Superliga (DEN)', 46, range(2016, 2025))` gaf met de kapotte
    versie **0.634 / 1.883 over n=28** tegen de vastgelegde **0.624 / 1.807 over n=18**. De
    opgeslagen waarde is dus de goede en `MEASURED_TIER2_GAP` hoeft niet te worden aangeraakt —
    maar wie de meting na 5 oktober had herhaald, had stil een andere factor gekregen dan er in de
    tabel staat, zonder één foutmelding. Precies de faalstand van het Serie B-id en van
    `calibration.py settle`: een stap die anders uitvalt zonder dat iets klaagt.

    Dit raakt de meting van de Primera Federación (ESP) van 5 oktober NIET: daar zijn 'Group 1' en
    'Group 2' disjunct, dus `partitioned_groups` geeft dezelfde twee namen als `league_groups` en
    de uitkomst is ongewijzigd. Nagerekend op 9 okt: 0.716 / 1.581 over n=28, gelijk aan de tabel.
    """
    try:
        raw = fotmob.fetch_league_stats(league_id, season)
    except Exception:
        return []
    groups = []
    try:
        import urllib.parse
        enc = urllib.parse.quote(season, safe="")
        meta = fotmob._get_json(
            f"https://www.fotmob.com/api/data/leagues?id={league_id}&season={enc}")
        # `partitioned_groups` en niet `league_groups` — zie de docstring hierboven.
        groups = fotmob.partitioned_groups(meta.get("table", []))
    except Exception:
        groups = []
    if not groups:
        return [(None, raw["teams"])]
    out = []
    for g in groups:
        try:
            out.append((g, fotmob.fetch_league_stats(league_id, season, group=g)["teams"]))
        except Exception:
            continue
    return out


def measure_gap(top_competition: str, top_id: int, years: range, *, direction: str = "up",
                min_played: int = 10, calendar_year: bool = False) -> "fd.GapResult":
    """Meet het gat tussen een competitie en de divisie eronder, aan ploegen die verhuisden.

    Zelfde definitie als `footballdata.division_gap()`, maar op Fotmob-standen, zodat ook de
    divisieparen meetbaar zijn die football-data.co.uk niet heeft.

    **Sinds 5 okt 2026 ook voor een divisie die in parallelle groepen speelt** — zie
    `_season_tables`. Elke groep wordt apart tegen zijn eigen gemiddelde genormaliseerd; de
    gemeten verhoudingen gaan daarna op één hoop, want de vraag is wat een promovendus overhoudt
    en niet uit welke groep hij kwam.

    `calendar_year=True` voor een competitie die op het KALENDERJAAR loopt — Eliteserien (NOR),
    Allsvenskan (SWE), MLS (USA), Série A (BRA). Dan is het seizoen `"2025"` en niet
    `"2025/2026"`.

    **Beide toevoegingen zijn van 9 okt 2026 (Run B) en ze repareren samen één stille val.** Deze
    functie bouwde het seizoen altijd als `f"{y}/{y+1}"`, en bij nul waarnemingen gaf ze
    `GapResult(1.0, 1.0, 0, direction)` terug. Voor een kalenderjaarcompetitie bestaat dat seizoen
    niet, dus `fetch_league_stats` wierp bij élk jaar een uitzondering, de lus sloeg elk jaar over
    en het antwoord was **factor 1.000 / 1.000 over n=0** — zonder één foutmelding. Een factor van
    1.0 betekent "er is geen divisiegat", oftewel een promovendus is in de divisie erboven precies
    zo sterk als eronder. Dat is het gevaarlijkste getal dat deze functie kan opleveren en het zag
    eruit als een geldige meting.

    Dat was geen hypothetisch risico: de notitie bij `Eliteserien (NOR)` en `Allsvenskan (SWE)` in
    `TIER2` draagt een volgende run letterlijk op *"`measure_gap` over 2016/2017-2024/2025 doet
    voor NOR en SWE wat de meting van 31 aug voor NED/DEN/POR/BEL/TUR/POL deed"*, en noemt de
    kalenderjaarnotatie wél als valkuil — maar deze functie had er geen knop voor. Wie die
    opdracht uitvoerde kreeg 1.000/1.000 en een aanmoediging om het in de tabel te zetten.

    Daarom weigert ze nu luidruchtig in plaats van een factor van 1.0 te verzinnen: bij nul
    waarnemingen volgt een `PromotionError` die de twee waarschijnlijke oorzaken noemt.
    """
    import statistics
    t2 = TIER2[top_competition]
    att, dfn, samples = [], [], []
    for y in years:
        if calendar_year:
            s_from, s_to = str(y), str(y + 1)
        else:
            s_from, s_to = f"{y}/{y + 1}", f"{y + 1}/{y + 2}"
        lo, hi = (t2.fotmob_id, top_id) if direction == "up" else (top_id, t2.fotmob_id)
        tabellen = _season_tables(lo, s_from)
        try:
            t_to = fotmob.fetch_league_stats(hi, s_to)["teams"]
        except Exception:
            continue
        for groep, t_from in tabellen:
            att_n, dfn_n, samples_n = _gap_rows(t_from, t_to, y, groep, min_played)
            att += att_n
            dfn += dfn_n
            samples += samples_n
    if not att:
        raise PromotionError(
            f"geen enkele verhuisde ploeg gevonden voor {top_competition} / {t2.name} over "
            f"{years.start}-{years.stop - 1}"
            + (" (kalenderjaarnotatie)" if calendar_year else " (seizoensnotatie JJJJ/JJJJ)")
            + ". Twee waarschijnlijke oorzaken: de seizoensnotatie klopt niet voor deze "
              "competitie — probeer calendar_year=True voor NOR, SWE, USA en BRA — of Fotmob "
              "heeft op dit id geen standen voor deze jaren. Dit is met opzet een fout en geen "
              "factor 1.0: dat laatste betekent 'geen divisiegat' en zag er tot 9 okt 2026 uit "
              "als een geldige meting.")

    def spread(xs):
        xs = sorted(xs)
        return ((statistics.quantiles(xs, n=4)[0], statistics.quantiles(xs, n=4)[2])
                if len(xs) >= 4 else (xs[0], xs[-1]))

    return fd.GapResult(statistics.median(att), statistics.median(dfn), len(att), direction,
                        spread(att), spread(dfn), samples)


def _gap_rows(t_from: dict, t_to: dict, y: int, groep: str | None, min_played: int):
    """De verhuisde ploegen van één (groeps)stand, met hun verhouding ná/vóór."""
    att, dfn, samples = [], [], []
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
                        round(a0, 3), round(d0, 3), groep))
    return att, dfn, samples
