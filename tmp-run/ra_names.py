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
from scripts.teamnames import ALIASES, _DROP, norm, tokens  # noqa: F401  (hier doorgegeven)


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
