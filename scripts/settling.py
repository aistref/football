#!/usr/bin/env python3
"""Wanneer is een pick afwikkelbaar? Eén antwoord voor `ledger.py` en `shadow.py`.

De regel is sinds 3 sep 2026: **een wedstrijd is afwikkelbaar zodra de bron hem als
afgelopen meldt** (`status.finished` bij Fotmob), niet zodra er een aantal uur sinds de
aftrap verstreken is. De klok is alleen nog een terugval voor het geval de bron niets
zegt — geen netwerk, wedstrijd niet gevonden, veld ontbreekt.

Waarom dit is veranderd, en waarom het hier staat en niet twee keer los:

- De oude regel (`SETTLE_AFTER_HOURS = 12`, gemeten vanaf de **aftrap**) is nooit
  onderbouwd. Hij stond in de eerste commit van de repo en de parametertabel gaf alleen
  een beschrijving, geen reden — anders dan bij `EDGE_THRESHOLD_FULL`, waar een halve
  pagina uitlegt waarop de 8 gemeten is.
- Hij mat bovendien het verkeerde. Een wedstrijd duurt met rust en blessuretijd ongeveer
  twee uur, dus de feitelijke marge ná het laatste fluitsignaal was ~10 uur.
- En hij viel systematisch verkeerd uit. Run A draait rond 04:10 en avondwedstrijden
  trappen af tussen 20:00 en 21:00 CEST; die staan dan op 7 à 8 uur, vallen dus élke keer
  net buiten de grens, en werden pas door de vólgende run afgewikkeld — na ~24 uur in
  plaats van na 12. Gemeten over de eerste 246 afgewikkelde picks: mediaan 9,7 uur, met
  een kwart in de staart van 12 tot 18 uur. Dat is precies die groep.
- `shadow.py` had helemaal geen leeftijdsfilter: de docstring adverteerde `--hours 12`,
  maar `cmd_open` filterde alleen op `result == pending` en die vlag bestond niet eens.
  Op 2 sep 2026 leverde dat een runrapport op waarin wél stond wat de tegengehouden
  kandidaten deden en niet wat de gespeelde bets van dezelfde wedstrijden deden.

Die laatste is de reden dat deze module bestaat in plaats van twee keer dezelfde regel:
zolang beide scripts hun eigen versie hebben, lopen ze uiteen.

Wat de marge moest voorkomen blijft gelden — een uitslag noteren van een duel dat is
uitgesteld, gestaakt, of waar nog verlenging loopt — maar `finished` is dáár het directe
antwoord op, waar een klok er een schatting van was.

LET OP bij bekerduels: `status.scoreStr` van Fotmob is de **eind**stand, dus inclusief
verlenging en strafschoppen. `_shared-rules.md` §6d eist afrekenen op de stand na 90
minuten. `finished` zegt dus wanneer je mág afwikkelen, niet wélke stand je gebruikt —
zoek bij een knock-outduel de doelpuntminuten op en tel zelf tot 90'.

LET OP bij de terugval: `settleable` bepaalt alleen wat er in `open` op de lijst komt, niet
wat er wordt weggeschreven. De terugval van twee uur is dus geen toestemming om een uitslag
te noteren van een duel dat nog loopt — hij zorgt er alleen voor dat een pick niet
onzichtbaar blijft als de bron even niets zegt. Wie afwikkelt heeft hoe dan ook een stand
nodig, en die komt uit dezelfde bron die anders ook `finished` had gegeven.

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, timedelta, timezone

try:                        # als pakket: `from scripts import settling`
    from . import fotmob
except ImportError:         # als los script: `python3 scripts/ledger.py`
    import fotmob           # type: ignore[no-redef]

# Terugvalmarge in uren sinds de aftrap, voor het geval de bron niets zegt. Twee uur is
# de speelduur inclusief rust en blessuretijd; het is met opzet krap, want dit geldt
# alleen als er géén `finished` te krijgen was en een run anders opnieuw een dag wacht.
FALLBACK_HOURS = 2.0


def norm(s: str) -> str:
    """Clubnaam tot vergelijkbare kern. Zelfde bewerking als de settle-scripts gebruikten."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


class DayIndex:
    """De wedstrijden van één of meer dagen bij Fotmob, opzoekbaar op (thuis, uit).

    Haalt per kalenderdag één keer op en onthoudt het resultaat, zodat een lijst van
    twintig openstaande picks van dezelfde dag niet twintig verzoeken kost.
    """

    def __init__(self) -> None:
        self._days: dict[date, dict] = {}
        self.errors: dict[date, str] = {}

    def _day(self, day: date) -> dict:
        if day in self._days or day in self.errors:
            return self._days.get(day, {})
        index: dict[tuple[str, str], dict] = {}
        try:
            fx = fotmob.fetch_fixtures(day)
        except Exception as exc:  # netwerk, HTTP, JSON — nooit fataal voor de aanroeper
            self.errors[day] = f"{type(exc).__name__}: {exc}"
            return {}
        for lg in fx.get("leagues", []) or []:
            for m in lg.get("matches", []) or []:
                st = m.get("status", {}) or {}
                index[(norm(m["home"]["name"]), norm(m["away"]["name"]))] = {
                    "match_id": m.get("id"), "league": lg.get("name"),
                    "score": st.get("scoreStr"), "finished": bool(st.get("finished")),
                    "cancelled": bool(st.get("cancelled")),
                    "home": m["home"]["name"], "away": m["away"]["name"],
                }
        self._days[day] = index
        return index

    def lookup(self, day: date, home: str, away: str) -> dict | None:
        index = self._day(day)
        if not index:
            return None
        hit = index.get((norm(home), norm(away)))
        if hit:
            return hit
        # Zelfde voorvoegselkoppeling als de losse settle-scripts van 1 en 2 sep, en met
        # dezelfde voorwaarde: alleen accepteren als er precies één kandidaat is. Liever
        # geen uitslag dan de verkeerde.
        nh, na = norm(home)[:6], norm(away)[:6]
        cand = [v for k, v in index.items() if k[0].startswith(nh) and k[1].startswith(na)]
        return cand[0] if len(cand) == 1 else None


def kickoff_of(pick: dict) -> datetime | None:
    """De aftrap uit een pick (`kickoff`) of een schaduwpick (`date`, geen tijd)."""
    raw = pick.get("kickoff")
    if raw:
        try:
            dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    raw = pick.get("date")
    if raw:
        try:  # schaduwpicks kennen alleen de rundatum; neem het eind van die dag
            return datetime.fromisoformat(f"{raw}T23:59:59+00:00")
        except ValueError:
            return None
    return None


def settleable(pick: dict, index: DayIndex | None = None,
               fallback_hours: float = FALLBACK_HOURS,
               now: datetime | None = None) -> tuple[bool, str]:
    """(mag afgewikkeld worden, reden). Reden is altijd ingevuld, ook bij False."""
    now = now or datetime.now(timezone.utc)
    ko = kickoff_of(pick)
    if ko is None:
        return True, "aftrap onbekend — altijd tonen"

    age_h = (now - ko).total_seconds() / 3600
    home, away = pick.get("home"), pick.get("away")
    if not home and pick.get("match") and "–" in pick["match"]:
        home, away = [x.strip() for x in pick["match"].split("–", 1)]

    if index is not None and home and away:
        hit = index.lookup(ko.date(), home, away)
        if hit is not None:
            if hit["cancelled"]:
                return True, f"bron meldt afgelast ({hit['score'] or 'geen stand'})"
            if hit["finished"]:
                return True, f"bron meldt afgelopen — {hit['score'] or 'geen stand'}"
            return False, f"bron meldt nog niet afgelopen ({age_h:.1f}u na aftrap)"

    if age_h >= fallback_hours:
        return True, f"geen bronstatus; terugval op de klok ({age_h:.1f}u ≥ {fallback_hours:g}u)"
    return False, f"geen bronstatus; {age_h:.1f}u na aftrap, terugval eist {fallback_hours:g}u"
