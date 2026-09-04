"""Naamkoppeling tussen de Fotmob-daglijst en de Fotmob-standtabel.

Beide komen van Fotmob, maar de daglijst gebruikt de korte weergavenaam ("Wigan", "Cádiz")
en de tabel de volledige ("Wigan Athletic", "Cadiz"). Zonder koppeling leest dat als
"ploeg zonder historie in deze divisie" en dus als tier NONE — op 30 aug 2026 gebeurde dat
bij 12 van de 18 vermeende NONE-duels, allemaal ten onrechte.
"""
import re, unicodedata

_DROP = {"fc", "afc", "cf", "sc", "ac", "as", "sv", "vfl", "vfb", "tsv", "bsc", "se", "if", "ff",
         "town", "city", "united", "utd", "athletic", "wanderers", "rovers", "county", "argyle",
         "albion", "kf", "ks", "cd", "ad", "ca", "ud", "sd", "us", "club", "calcio", "1905"}

ALIASES = {  # daglijstnaam -> tabelnaam, alleen waar geen enkele token overlapt
    "hamkam": "hamarkameratene",
    # 1 sep 2026: de Engelse daglijst kort af tot een deel dat na _DROP niets overhoudt dat
    # met de tabelnaam overlapt. Zonder deze drie leest een ploeg die gewoon in de stand
    # staat als "geen historie in deze divisie" en gaat hij ten onrechte de omrekening in.
    "sheff utd": "sheffield united",
    "wolves": "wolverhampton wanderers",
    "west ham": "west ham united",
    # 2 sep 2026: dezelfde val, twee nieuwe gevallen. "QPR" is een initiaalwoord en deelt geen
    # enkel token met "Queens Park Rangers"; bij "West Brom" valt "albion" weg in _DROP, zodat
    # "brom" en "bromwich" overblijven — verschillende tokens. Beide ploegen staan gewoon in de
    # Championship-stand van 2025/2026 en gingen zonder deze twee regels ten onrechte de
    # promovendi-omrekening in.
    "qpr": "queens park rangers",
    "west brom": "west bromwich albion",
    # 3 sep 2026: derde geval van dezelfde soort. De daglijst schrijft "Hearts", de
    # Premiership-stand "Heart of Midlothian" — enkelvoud tegen meervoud, dus geen enkel
    # gedeeld token. Hearts stond gewoon in de stand van 2025/2026 en ging zonder deze regel
    # ten onrechte de promovendi-omrekening in (en daarmee van FULL naar LIGHT).
    "hearts": "heart of midlothian",
    # 4 sep 2026: vierde geval van dezelfde soort, en het duurste tot nu toe. De daglijst
    # schrijft "PSG", de Ligue 1-stand "Paris Saint-Germain" — een initiaalwoord deelt geen
    # enkel token met de voluitnaam. PSG stond gewoon in de stand van 2025/2026 en ging zonder
    # deze regel ten onrechte de promovendi-omrekening in, die voor een ploeg uit de hoogste
    # divisie niets kán opleveren (er is geen divisie boven Ligue 1) en dus op NONE uitkomt.
    "psg": "paris saint germain",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("Ø", "o").replace("ł", "l").replace("đ", "d").replace("ß", "ss")
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()


def tokens(s: str) -> frozenset:
    return frozenset(t for t in norm(s).split() if t not in _DROP) or frozenset(norm(s).split())


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
    tn = tokens(name)
    hits = [k for k in table if tokens(k) <= tn or tn <= tokens(k)]
    if len(hits) == 1:
        return hits[0]
    return None


import difflib


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def best_pair(home: str, away: str, rows: list, key_home, key_away, floor: float = 0.62):
    """Vind de rij die bij (home, away) hoort, op naamgelijkenis over het hele paar.

    Nodig omdat BetExplorer en The Odds API elk hun eigen korte clubnaam gebruiken: op
    30 aug 2026 heette Györi ETO bij BetExplorer 'Gyor', en dat kost zonder deze koppeling
    de enige 1X2-prijs van die wedstrijd.
    """
    scored = []
    for r in rows:
        s = (similarity(home, key_home(r)) + similarity(away, key_away(r))) / 2
        scored.append((s, r))
    scored.sort(key=lambda t: -t[0])
    if not scored or scored[0][0] < floor:
        return None
    if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.05:
        return None                     # te dicht bij elkaar: liever geen prijs dan de verkeerde
    return scored[0][1]


def side_of(outcome: str, home: str, away: str) -> str | None:
    """Bij welke ploeg hoort deze uitkomstnaam uit een spreads-respons?"""
    sh, sa = similarity(outcome, home), similarity(outcome, away)
    if abs(sh - sa) < 0.08:
        return None
    return "home" if sh > sa else "away"
