#!/usr/bin/env python3
"""Welke bekertoernooien staan vandaag op de runlijst? Stage 2 van `_shared-rules.md`.

**Waarom dit bestaat (18 nov 2026, op besluit van de gebruiker; op 19 nov uitgebreid met de
League Cup).** Tot deze datum stonden de bekers het hele seizoen op de runlijst. De gebruiker:

> *"Copa del Rey, DFB Pokal, FA Cup, Coppa Italia en KNVB Beker wil ik vanaf nu alleen pas in de
> tweede helft van het seizoen. Dus activeer deze competities pas vanaf 2027 (en volgend seizoen
> pas in de tweede helft van het seizoen)."*

Dat besluit kwam op dezelfde dag dat de **Copa del Rey** aan de Run A-runlijst is toegevoegd, en
die twee horen bij elkaar: de beker is toegevoegd mét deze grens, niet eerst toegevoegd en daarna
beperkt. Hij speelde op 18 november zes duels terwijl alle eenentwintig andere competities van
Run A leeg waren, en dat was de aanleiding om hem erbij te vragen.

**Waarom dit een goede grens is en niet alleen een voorkeur.** De vroege rondes van een beker
zetten clubs uit de hoogste divisie tegenover ploegen uit de regionale en amateurdivisies. Daar is
per ontwerp geen bruikbare kansinput voor — de ploeg onderaan staat in geen enkele tabel die het
model kent — en §4 laat dan niets anders toe dan `data_tier = NONE`. Dat is in deze reeks ook
precies wat er gebeurde: de FA Cup-rondes van begin november leverden over meerdere dagen uitsluitend
`NONE`-duels op, en op 9 november was het enige duel in het hele inzetvenster van Run A een
FA Cup-duel dat op `NONE` uitkwam. In de tweede seizoenshelft zijn de amateurclubs eruit en staan
er clubs tegenover elkaar die het model allebei kent.

**Wat de tweede seizoenshelft hier betekent: 1 januari t/m 30 juni.** Het Europese clubseizoen
loopt van augustus tot mei, dus de jaarwissel is de natuurlijke knip, en hij is met een
kalenderdatum te bepalen zonder per competitie te weten hoeveel speelronden er zijn. Juni staat
erbij omdat de bekerfinales soms in de laatste week van mei of begin juni liggen; juli valt er
buiten en daar speelt geen van de vijf. Deze grens herhaalt zich dus elk seizoen vanzelf — dat is
wat *"volgend seizoen pas in de tweede helft"* vraagt, en het is de reden dat het een functie van
de datum is en geen vlag die iemand jaarlijks moet omzetten.

**Deze module houdt alleen tegen; hij voegt nooit iets toe.** Een competitie die niet in
`SECOND_HALF_ONLY` staat, gaat er onveranderd doorheen. Dat is dezelfde vorm als de poorten 7, 8
en 9 in §1.

DE LEAGUE CUP IS ER OP 19 NOVEMBER 2026 BIJ GEKOMEN, EN HIJ BINDT EEN DAG LATER DAN DE ANDERE VIJF.
Op 18 november viel hij er met opzet buiten — de gebruiker noemde vijf bekers en deze was daar niet
een van — terwijl hij wél op de Run A-runlijst stond en net zo goed lage-divisierondes kent. Die
vraag is als besluitpunt in het dagrapport van 18 én 19 november aan de gebruiker voorgelegd, zoals
§1a/§1e voorschrijven voor een keuze die een run niet op eigen initiatief maakt, en het antwoord op
19 november was *"League Cup ook"*. Het zijn er daarmee zes.

Zijn ingangsdatum staat op **20 november 2026** in `BINDS_FROM_PER_COMPETITION` en niet op de 19e.
Run A van 19 november had op het moment van het besluit al gedraaid met de League Cup op de
runlijst; hem met terugwerkende kracht eraf halen zou een herberekening van die dag een andere
runlijst geven dan die dag zelf gaf. Zijn eerstvolgende ronde was 15 december 2026 en valt nu
buiten de lijst, dus het kost geen enkele wedstrijd.

    python3 scripts/cups.py selftest      # geen netwerk, geen repo nodig
"""

from __future__ import annotations

import sys
from datetime import date

#: De bekers die alleen in de tweede seizoenshelft meedoen. Namen exact zoals ze in de
#: runlijsten en in `data/coverage.json` staan — wie hier een naam anders spelt, zet de grens stil
#: uit voor dat toernooi, en dat is precies de stille faalvorm waar `idcheck.py` voor bestaat.
#:
#: Het waren er vijf; de `League Cup (ENG)` is er op 19 nov 2026 bij gekomen — zie
#: `BINDS_FROM_PER_COMPETITION` hieronder, want hij bindt een dag later dan de andere vijf.
SECOND_HALF_ONLY: frozenset[str] = frozenset({
    "Copa del Rey (ESP)",
    "DFB Pokal (GER)",
    "FA Cup (ENG)",
    "Coppa Italia (ITA)",
    "KNVB Beker (NED)",
    "League Cup (ENG)",
})

#: De maanden die als tweede seizoenshelft gelden: januari t/m juni.
SECOND_HALF_MONTHS: frozenset[int] = frozenset({1, 2, 3, 4, 5, 6})

#: Vanaf deze dag bindt de regel. Vóór die datum stonden de bekers het hele seizoen op de lijst,
#: en een herberekening van een eerdere rundag moet dezelfde runlijst geven als die dag zelf gaf —
#: dezelfde eis als bij `sides.LAPSED_FROM` (§1e) en `model.LEVEL_SCALE_BINDS_FROM` (§6g).
BINDS_FROM = date(2026, 11, 19)

#: Per beker de dag waarop de grens bindt. Staat een naam hier niet in, dan geldt `BINDS_FROM`.
#:
#: **Waarom de League Cup een eigen datum heeft, en waarom dat geen detail is.** De gebruiker heeft
#: hem op 19 nov 2026 aan deze lijst toegevoegd, nadat Run A van die ochtend de vraag had
#: voorgelegd die `prompts/run-a.md` punt 4 ervoor openhield. Run A van 19 november had op dat
#: moment al gedraaid **met** de League Cup op de runlijst, en hem als `GEEN WEDSTRIJD` in zijn
#: dekkingstabel gezet. Zou hij op 19 november binden, dan gaf een herberekening van die dag een
#: andere runlijst dan die dag zelf gaf — precies wat `sides.LAPSED_FROM` (§1e) en
#: `ranking.SHORTLIST_LEGACY` (§0) met zoveel woorden voorkomen. Hij bindt daarom vanaf **20 nov
#: 2026**. Dat kost niets: zijn eerstvolgende ronde is 15 december.
BINDS_FROM_PER_COMPETITION: dict[str, date] = {
    "League Cup (ENG)": date(2026, 11, 20),
}


def binds_from(competition: str) -> date:
    """Vanaf welke dag bindt de grens voor deze beker?"""
    return BINDS_FROM_PER_COMPETITION.get(competition, BINDS_FROM)


def in_second_half(day: date) -> bool:
    """Valt `day` in de tweede helft van het seizoen (1 januari t/m 30 juni)?"""
    return day.month in SECOND_HALF_MONTHS


def active(competition: str, day: date) -> bool:
    """Staat `competition` op `day` op de runlijst?

    True voor alles wat niet in `SECOND_HALF_ONLY` staat, en voor de bekers die er wél in staan
    alleen in de tweede seizoenshelft. Vóór de ingangsdatum van die beker staat hij gewoon aan;
    die datum is per beker te zetten, zie `binds_from`.
    """
    if competition not in SECOND_HALF_ONLY:
        return True
    if day < binds_from(competition):
        return True
    return in_second_half(day)


def reason(competition: str, day: date) -> str | None:
    """De regel voor de dekkingstabel, of None als het toernooi gewoon meedoet.

    Dit is met opzet geen `GEEN WEDSTRIJD`: er wordt wél gespeeld, het staat alleen niet op de
    runlijst. Een toernooi dat buiten de lijst valt als "niets op de kalender" opschrijven zou
    hetzelfde zijn als een stille truncatie in Stage 4 (§3).
    """
    if active(competition, day):
        return None
    besluit = ("19 nov 2026" if competition in BINDS_FROM_PER_COMPETITION else "18 nov 2026")
    return (f"BUITEN DE RUNLIJST — besluit van de gebruiker van {besluit}: deze beker doet "
            "alleen mee in de tweede seizoenshelft (1 jan t/m 30 jun), omdat de vroege rondes "
            "lage-divisieploegen bevatten waarvoor geen kansinput bestaat en die dus toch op "
            "`data_tier = NONE` uitkomen. Eerstvolgende keer dat hij meedoet: "
            f"1 januari {day.year + (0 if day.month <= 6 else 1)}.")


def filter_runlist(runlist: dict[str, int], day: date) -> tuple[dict[str, int], dict[str, str]]:
    """Splits een runlijst in (wat meedoet, wat buiten de lijst valt met de reden erbij)."""
    mee = {k: v for k, v in runlist.items() if active(k, day)}
    buiten = {k: reason(k, day) or "" for k in runlist if not active(k, day)}
    return mee, buiten


def _selftest() -> int:
    d = date
    # Niet-bekers gaan er altijd doorheen, ook midden in het eerste seizoenshelft.
    assert active("Premier League (ENG)", d(2026, 11, 19))
    assert active("UEFA Champions League", d(2026, 12, 9))

    # De League Cup is er op 19 nov 2026 bij gekomen en bindt een dag later dan de andere vijf.
    # Dit is de kern van die uitzondering: op 19 november stond hij nog gewoon op de runlijst,
    # want Run A van die ochtend had toen al met hem gedraaid.
    assert active("League Cup (ENG)", d(2026, 11, 19)), "19 nov stond hij nog op de lijst"
    assert not active("League Cup (ENG)", d(2026, 11, 20)), "vanaf 20 nov bindt hij"
    assert not active("League Cup (ENG)", d(2026, 12, 15)), "zijn ronde van 15 dec valt eruit"
    assert active("League Cup (ENG)", d(2027, 1, 1)), "vanaf januari doet hij weer mee"
    assert binds_from("League Cup (ENG)") == d(2026, 11, 20)
    assert binds_from("FA Cup (ENG)") == BINDS_FROM == d(2026, 11, 19)

    # De bekers: uit in de eerste seizoenshelft vanaf hun eigen ingangsdatum.
    for naam in SECOND_HALF_ONLY:
        assert not active(naam, d(2026, 11, 20)), naam
        assert not active(naam, d(2026, 12, 1)), naam
        assert active(naam, d(2027, 1, 1)), naam
        assert active(naam, d(2027, 3, 15)), naam
        assert active(naam, d(2027, 6, 30)), naam
        # En volgend seizoen opnieuw uit — dit herhaalt zich zonder dat iemand iets omzet.
        assert not active(naam, d(2027, 8, 15)), naam
        assert not active(naam, d(2027, 11, 1)), naam
        assert active(naam, d(2028, 2, 1)), naam

    # Juli valt buiten de tweede helft; daar speelt geen van de vijf.
    assert not in_second_half(d(2027, 7, 10))
    assert in_second_half(d(2027, 6, 30)) and not in_second_half(d(2027, 12, 31))

    # Vóór de ingangsdatum staat alles aan, zodat een herberekening van een oudere rundag
    # dezelfde runlijst geeft als die dag zelf gaf.
    assert active("FA Cup (ENG)", d(2026, 11, 18))
    assert active("KNVB Beker (NED)", d(2026, 11, 8))
    assert active("League Cup (ENG)", d(2026, 11, 19))

    # De reden is geen `GEEN WEDSTRIJD` en noemt wanneer hij terugkomt.
    r = reason("FA Cup (ENG)", d(2026, 12, 4))
    assert r and "BUITEN DE RUNLIJST" in r and "1 januari 2027" in r, r
    assert reason("FA Cup (ENG)", d(2027, 2, 1)) is None
    r2 = reason("Coppa Italia (ITA)", d(2027, 11, 20))
    assert r2 and "1 januari 2028" in r2, r2
    # De League Cup draagt de datum van zijn eigen besluit, niet die van de andere vijf.
    r3 = reason("League Cup (ENG)", d(2026, 12, 15))
    assert r3 and "19 nov 2026" in r3, r3
    assert reason("FA Cup (ENG)", d(2026, 12, 4)).count("18 nov 2026") == 1

    # filter_runlist splitst en laat niets vallen.
    rl = {"Premier League (ENG)": 47, "FA Cup (ENG)": 132, "Copa del Rey (ESP)": 138}
    mee, buiten = filter_runlist(rl, d(2026, 12, 4))
    assert set(mee) == {"Premier League (ENG)"}, mee
    assert set(buiten) == {"FA Cup (ENG)", "Copa del Rey (ESP)"}, buiten
    assert len(mee) + len(buiten) == len(rl)
    mee2, buiten2 = filter_runlist(rl, d(2027, 2, 4))
    assert len(mee2) == 3 and not buiten2

    print("Zelftest geslaagd — 6 bekers x 8 datums plus 22 losse controles.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        raise SystemExit(_selftest())
    vandaag = date.today()
    print(f"Stand op {vandaag} (tweede seizoenshelft: {in_second_half(vandaag)})")
    for naam in sorted(SECOND_HALF_ONLY):
        print(f"  {'MEE ' if active(naam, vandaag) else 'UIT '} {naam}")
