"""Naamkoppeling tussen de Fotmob-daglijst en de Fotmob-standtabel.

Beide komen van Fotmob, maar de daglijst gebruikt de korte weergavenaam ("Wigan", "Cádiz")
en de tabel de volledige ("Wigan Athletic", "Cadiz"). Zonder koppeling leest dat als
"ploeg zonder historie in deze divisie" en dus als tier NONE — op 30 aug 2026 gebeurde dat
bij 12 van de 18 vermeende NONE-duels, allemaal ten onrechte.

**De tabel zelf staat sinds 5 okt 2026 in `scripts/teamnames.py` en niet meer hier.** Reden:
een module in `scripts/` kan niet uit `tmp-run/` importeren, dus `scripts/settling.py` had zijn
eigen, veel simpelere koppeling en liet 47 wedstrijden onafgewikkeld in het kalibratielogboek —
het logboek waaruit de herijking van §1g wordt gefit. Zie de kop van dat bestand. Hier blijven
de functies staan die alleen de runscripts gebruiken (`resolve`, `best_pair`, `side_of`), zodat
er één aliastabel is en niet twee die uiteenlopen.
"""
from scripts.teamnames import (ALIASES, _DROP, norm, tokens,  # noqa: F401  (doorgegeven)
                               is_abbreviation, ordered_tokens)


def resolve(name: str, table: dict) -> str | None:
    """Geef de sleutel in `table` die bij `name` hoort, of None."""
    if name in table:
        return name
    by_norm = {norm(k): k for k in table}
    n = norm(name)
    if n in by_norm:
        return by_norm[n]
    if ALIASES.get(n) in by_norm:
        return by_norm[ALIASES[n]]
    # De aliastabel moet BEIDE kanten op worden gelezen, en tot 9 okt 2026 gebeurde dat maar
    # één kant op: de regel hierboven zoekt de GEVRAAGDE naam op in ALIASES, maar niet de
    # sleutel in `table`. Staat de afkorting in de tabel en de volledige naam in de vraag, dan
    # mist de koppeling — ALIASES heeft `qpr -> queens park rangers`, en dat helpt alleen als de
    # vraag "QPR" is. Gevonden op West Ham United – Queens Park Rangers (Run A, 9 okt 2026):
    # BetExplorer noteert de Championship-rij als "West Ham - QPR", `resolve` koppelde de
    # thuisploeg wel en de uitploeg niet, en `best_pair` viel daarna terug op 0.273 gelijkenis
    # (onder de vloer van 0.62). Dat kostte geen bet — het duel haalde zijn LIGHT-drempel niet —
    # maar wel twee dingen die §6e en §1e nodig hebben: het kalibratieblok van deze wedstrijd
    # bleef leeg (1 van de 12 waarnemingen van de dag) en poort 8 kwam uit op "geen 1X2-prijzen,
    # geen marktoordeel over wie de mindere is" en stond dus OPEN zonder te zijn getoetst.
    # Dezelfde soort stille faalstand als de `is_today`-filter die op 7 oktober is gerepareerd,
    # nu aan de naamkant. Deze lus leest de tabelsleutels óók door ALIASES heen.
    by_alias = {}
    for k in table:
        by_alias.setdefault(ALIASES.get(norm(k), norm(k)), k)
    if n in by_alias:
        return by_alias[n]
    # 27 okt 2026 — hier stond `tokens(k) <= tn or tn <= tokens(k)`, een DEELVERZAMELING, en die
    # koppelde FC Eindhoven aan PSV Eindhoven (zie `teamnames.is_abbreviation` voor het geval en
    # wat het kostte). Een afkorting laat de staart weg en niet de kop, dus de eis is nu een
    # voorvoegsel op woordniveau — dezelfde eis die §4 al aan `promotion.find_team` stelt.
    hits = [k for k in table if is_abbreviation(name, k)]
    if len(hits) == 1:
        return hits[0]
    return None


import difflib


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def _prefix_pair(a: str, b: str) -> bool:
    """Is de ene naam op woordniveau een leidend voorvoegsel van de andere, na `_DROP`?

    `['roda']` tegen `['roda', 'kerkrade']`, `['jong', 'az']` tegen `['jong', 'az', 'alkmaar']`.
    Dit is met opzet zwakker dan `teamnames.is_abbreviation` (die gelijkheid eist) en het mag
    hier alleen bestaan omdat `best_pair` het op een PAAR toepast en op precies één rij — zie
    daar.
    """
    ta, tb = ordered_tokens(a), ordered_tokens(b)
    if not ta or not tb:
        return False
    short, long = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return long[:len(short)] == short


# Ploegen waarvan de ONDERSCHEIDENDE kop vooraan staat: een reserveploeg heet "Jong PSV" en de
# hoofdmacht "PSV", dus daar is de kop juist het hele verschil. `_affix_pair` mag de staartrichting
# daarom nooit op zo'n naam toepassen — zie de docstring daar.
_RESERVE = frozenset({"jong", "ii", "2", "b", "u19", "u20", "u21", "u23", "reserves", "res",
                      "amateurs", "castilla", "atletic", "atletico b"})


def _affix_pair(a: str, b: str) -> bool:
    """Is de ene naam op woordniveau een AANSLUITENDE kop OF staart van de andere, na `_DROP`?

    Dit verruimt `_prefix_pair` met de staartrichting, en de aanleiding is gemeten op
    27 nov 2026 (Run B). `Jong AZ Alkmaar – TOP Oss` stond bij BetExplorer als `Jong AZ – Oss`.
    De paarscore is (0.636 + 0.600) / 2 = **0.618**, twee duizendsten onder de vloer van 0.62, en
    de kopterugval van 30 oktober redde alleen de thuisploeg: `['jong', 'az']` is een kop van
    `['jong', 'az', 'alkmaar']`, maar `['oss']` is géén kop van `['top', 'oss']` — het is de
    staart. Het duel kwam daardoor de analyse binnen met **nul prijzen in alle zes de markten**
    en werd gerapporteerd als `GEEN BET — geen prijzen gevonden voor deze wedstrijd`, terwijl de
    prijzen op precies de pagina stonden die de run al had opgehaald. Dat is dezelfde stille
    faalstand als `la galaxy` (17 okt), `red bull new york` (30 sep) en `Roda – Jong AZ`
    (30 okt), nu in de andere richting.

    **De staartrichting is gevaarlijker dan de kop en krijgt daarom een eigen rem.** `['psv']` is
    een staart van `['jong', 'psv']`, en MVV Maastricht – Jong PSV stond diezelfde ochtend op de
    runlijst. Een koppeling van Jong PSV aan een rij die PSV noemt is precies de verkeerde prijs
    waar §4 en `teamnames.is_abbreviation` voor waarschuwen. Daarom geldt: de woorden die in de
    staartrichting wegvallen mogen géén reserveaanduiding bevatten (`_RESERVE`). Bij `TOP Oss`
    valt `top` weg en dat is er geen; bij `Jong PSV` valt `jong` weg en dat is er wel.

    De drie eisen van `best_pair` blijven er bovendien onverkort bovenop staan: de fuzzy score
    moet eerst hebben gefaald, BEIDE ploegen van het paar moeten op woordniveau koppelen, en er
    moet precies ÉÉN rij overblijven. Liever geen prijs dan de verkeerde.
    """
    ta, tb = ordered_tokens(a), ordered_tokens(b)
    if not ta or not tb:
        return False
    short, long = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if long[:len(short)] == short:                      # kop — de regel van 30 okt 2026
        return True
    if long[len(long) - len(short):] == short:          # staart — nieuw op 27 nov 2026
        weggevallen = set(long[:len(long) - len(short)])
        return not (weggevallen & _RESERVE)
    return False


def best_pair(home: str, away: str, rows: list, key_home, key_away, floor: float = 0.62):
    """Vind de rij die bij (home, away) hoort, op naamgelijkenis over het hele paar.

    Nodig omdat BetExplorer en The Odds API elk hun eigen korte clubnaam gebruiken: op
    30 aug 2026 heette Györi ETO bij BetExplorer 'Gyor', en dat kost zonder deze koppeling
    de enige 1X2-prijs van die wedstrijd.

    **Terugval op woordniveau, toegevoegd 30 okt 2026 (Run B).** De fuzzy score alleen is te
    krap als BEIDE namen een staart missen die `_DROP` niet kent. Gemeten geval van die ochtend:
    de Keuken Kampioen Divisie gaf `Roda JC Kerkrade – Jong AZ Alkmaar` in de daglijst en
    `Roda – Jong AZ` bij BetExplorer. De paarscore is dan (0.400 + 0.636) / 2 = **0.518**, onder
    de vloer van 0.62, en het duel kwam de analyse binnen met **nul prijzen in alle zes de
    markten** — als `GEEN BET` met reden "geen prijzen gevonden voor deze wedstrijd". De drie
    andere KKD-duels van dezelfde pagina koppelden wél, dus van buitenaf zag de dag er normaal
    uit met één duel zonder prijzen erin. Dezelfde stille faalstand als `la galaxy` op 17 okt en
    `red bull new york` op 30 sep, nu niet op één ploeg maar op twee tegelijk.

    **Waarom dit niet in `ALIASES` hoort.** Die tabel zegt in zijn eigen kop *"alleen waar geen
    enkele token overlapt"*, en hier overlappen ze juist allemaal: `roda` staat in beide namen.
    Een regel per stad erin zetten is bovendien eindeloos — elke competitie heeft ze.

    **En waarom een voorvoegsel hier mag en in `resolve` niet.** `teamnames.is_abbreviation`
    heeft de voorvoegselregel op 27 okt 2026 juist afgewezen, omdat `Excelsior` dan aan
    `Excelsior '31` koppelt; het onderscheidende deel van een clubnaam kan in de staart zitten.
    Dat bezwaar staat, en daarom geldt deze terugval alleen onder drie eisen tegelijk:

    1. de fuzzy score heeft **gefaald** (niets boven de vloer, of twee rijen te dicht bijeen);
    2. **beide** ploegen van het paar moeten op woordniveau een voorvoegsel zijn — een
       toevallige Excelsior-koppeling moet dus óók bij de tegenstander kloppen;
    3. er is precies **één** rij die daaraan voldoet.

    Dat is een veel sterkere eis dan `resolve` kan stellen: die koppelt één naam tegen een hele
    standtabel, deze koppelt een paar tegen de speellijst van één competitiedag. Blijft er meer
    dan één rij over, dan is het antwoord nog steeds `None` — liever geen prijs dan de verkeerde.
    """
    scored = []
    for r in rows:
        s = (similarity(home, key_home(r)) + similarity(away, key_away(r))) / 2
        scored.append((s, r))
    scored.sort(key=lambda t: -t[0])
    ok = bool(scored) and scored[0][0] >= floor and not (
        len(scored) > 1 and scored[0][0] - scored[1][0] < 0.05)
    if ok:
        return scored[0][1]
    hits = [r for r in rows
            if _affix_pair(home, key_home(r)) and _affix_pair(away, key_away(r))]
    if len(hits) == 1:
        return hits[0]
    return None


def side_of(outcome: str, home: str, away: str) -> str | None:
    """Bij welke ploeg hoort deze uitkomstnaam uit een spreads-respons?"""
    sh, sa = similarity(outcome, home), similarity(outcome, away)
    if abs(sh - sa) < 0.08:
        return None
    return "home" if sh > sa else "away"


def selftest() -> None:
    """Rekencontroles bij de terugval op woordniveau in `best_pair` (30 okt 2026).

    Geen netwerk nodig. De eerste vier zijn het gemeten geval van die ochtend (Keuken Kampioen
    Divisie, vier duels van één BetExplorer-pagina); de rest zijn de tegenproeven op de val die
    `teamnames.is_abbreviation` op 27 okt 2026 juist heeft afgewezen.
    """
    kh, ka = (lambda r: r["home"]), (lambda r: r["away"])
    kkd = [{"home": "FC Volendam", "away": "De Graafschap"},
           {"home": "Helmond", "away": "Eindhoven FC"},
           {"home": "Roda", "away": "Jong AZ"},
           {"home": "Waalwijk", "away": "Almere City"}]
    # de volledige BetExplorer-pagina van de Keuken Kampioen Divisie van 27 nov 2026, zeven
    # duels, zoals `rb_nov27_odds.py` haar ophaalde
    kkd27 = [{"home": "Jong AZ", "away": "Oss"},
             {"home": "Dordrecht", "away": "Vitesse"},
             {"home": "Jong Ajax", "away": "Heracles"},
             {"home": "Jong Utrecht", "away": "Almere City"},
             {"home": "Maastricht", "away": "Jong PSV"},
             {"home": "NAC Breda", "away": "Den Bosch"},
             {"home": "Venlo", "away": "Waalwijk"}]
    rou27 = [{"home": "U. Cluj", "away": "Sepsi Sf. Gheorghe"},
             {"home": "Petrolul", "away": "FC Arges"}]
    cases = [
        # het geval van 30 okt: paarscore 0.518, onder de vloer — de terugval moet hem vangen
        (("Roda JC Kerkrade", "Jong AZ Alkmaar", kkd), ("Roda", "Jong AZ")),
        # de drie die de fuzzy score al koppelde: die mogen niet veranderen
        (("Helmond Sport", "FC Eindhoven", kkd), ("Helmond", "Eindhoven FC")),
        (("RKC Waalwijk", "Almere City FC", kkd), ("Waalwijk", "Almere City")),
        (("FC Volendam", "De Graafschap", kkd), ("FC Volendam", "De Graafschap")),
        # Excelsior '31 tegen Excelsior: twee kandidaten, en de fuzzy score kiest de juiste
        (("Excelsior", "Katwijk", [{"home": "Excelsior '31", "away": "Katwijk"},
                                   {"home": "Excelsior", "away": "Katwijk"}]),
         ("Excelsior", "Katwijk")),
        # dezelfde val met één rij: de TEGENSTANDER is hier de borg, en die klopt niet
        (("Excelsior", "Katwijk", [{"home": "Excelsior '31", "away": "Rijnsburgse Boys"}]), None),
        # Jong AZ tegen AZ: de gevaarlijkste ambiguïteit van dit geval, fuzzy beslist goed
        (("Jong AZ Alkmaar", "Roda JC Kerkrade", [{"home": "Jong AZ", "away": "Roda"},
                                                  {"home": "AZ", "away": "Roda"}]),
         ("Jong AZ", "Roda")),
        # FC Eindhoven tegen PSV: GEEN voorvoegsel op woordniveau, dus geen koppeling
        (("FC Eindhoven", "Ajax", [{"home": "PSV", "away": "Ajax"}]), None),
        # --- de staartrichting, nieuw op 27 nov 2026 (Run B) ---
        # het gemeten geval: paarscore 0.618, twee duizendsten onder de vloer, en `Oss` is de
        # STAART van `TOP Oss`. Zonder deze richting kwam dit duel met nul prijzen binnen.
        (("Jong AZ Alkmaar", "TOP Oss", kkd27), ("Jong AZ", "Oss")),
        # de zes andere duels van diezelfde pagina mogen niet veranderen
        (("FC Dordrecht", "Vitesse", kkd27), ("Dordrecht", "Vitesse")),
        (("MVV Maastricht", "Jong PSV", kkd27), ("Maastricht", "Jong PSV")),
        (("NAC Breda", "FC Den Bosch", kkd27), ("NAC Breda", "Den Bosch")),
        (("VVV-Venlo", "RKC Waalwijk", kkd27), ("Venlo", "Waalwijk")),
        (("Jong Ajax", "Heracles", kkd27), ("Jong Ajax", "Heracles")),
        (("Jong FC Utrecht", "Almere City FC", kkd27), ("Jong Utrecht", "Almere City")),
        # `az` is in `jong az alkmaar` het MIDDELSTE woord en dus geen kop en geen staart: de
        # terugval koppelt Jong AZ Alkmaar niet aan een rij die de hoofdmacht noemt, ook niet
        # als de tegenstander wél klopt. Liever geen prijs dan de verkeerde.
        (("Jong AZ Alkmaar", "Oss", [{"home": "AZ", "away": "Oss"}]), None),
        # en dezelfde rem in de andere richting: de kopregel van 30 okt blijft wél gelden
        (("Jong AZ Alkmaar", "TOP Oss", [{"home": "Jong AZ", "away": "Oss"}]), ("Jong AZ", "Oss")),
        # Universitatea Cluj – Sepsi OSK, óók van 27 nov 2026: dit blijft met opzet ONGEKOPPELD.
        # `U. Cluj` is een AFKORTING (geen kop en geen staart van `Universitatea Cluj`) en
        # `Sepsi OSK` deelt met `Sepsi Sf. Gheorghe` alleen het eerste woord. Koppelen op één
        # gedeeld woord is exact de Excelsior-val van 27 okt 2026.
        (("Universitatea Cluj", "Sepsi OSK", rou27), None),
    ]
    # Losse controles op `_affix_pair` zelf. Via `best_pair` zijn ze niet te isoleren: de fuzzy
    # score beslist daar vaak al, en die laag is met deze reparatie niet veranderd.
    affix_cases = [
        # de kopregel van 30 okt 2026, ongewijzigd
        (("Jong AZ Alkmaar", "Jong AZ"), True),
        (("Roda JC Kerkrade", "Roda"), True),
        # de staartregel van 27 nov 2026
        (("TOP Oss", "Oss"), True),
        # DE REM: `psv` is een staart van `jong psv`, maar `jong` is een reserveaanduiding, dus
        # de staartrichting mag hier niet. Zonder `_RESERVE` zou dit True geven en zou een
        # reserveploeg aan de prijs van de hoofdmacht kunnen koppelen.
        (("Jong PSV", "PSV"), False),
        (("Jong AZ Alkmaar", "AZ Alkmaar"), False),
        # een afkorting is geen kop en geen staart, en blijft dus buiten deze terugval
        (("Universitatea Cluj", "U. Cluj"), False),
        (("Sepsi OSK", "Sepsi Sf. Gheorghe"), False),
        # de Excelsior-val van 27 okt 2026: op woordniveau is dit wél een kop, en daarom staan
        # de drie eisen van `best_pair` eromheen in plaats van in deze functie
        (("Excelsior '31", "Excelsior"), True),
    ]
    fails = 0
    for (a, b), want in affix_cases:
        got = _affix_pair(a, b)
        ok = got is want
        fails += not ok
        print(f"  {'OK  ' if ok else 'FOUT'} _affix_pair({a!r}, {b!r}) -> {got}"
              + ("" if ok else f"   verwacht {want}"))
    for (home, away, rows), want in cases:
        got = best_pair(home, away, rows, kh, ka)
        got_t = (got["home"], got["away"]) if got else None
        ok = got_t == want
        fails += not ok
        print(f"  {'OK  ' if ok else 'FOUT'} {home} – {away} -> {got_t}"
              + ("" if ok else f"   verwacht {want}"))
    totaal = len(cases) + len(affix_cases)
    print(f"\n{totaal - fails} van {totaal} controles geslaagd.")
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    selftest()
