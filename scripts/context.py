#!/usr/bin/env python3
"""Contextfactoren per wedstrijd: blessures, vorm en rust. Uit Fotmob, zonder sleutel.

Bestaansreden (23 aug 2026, op aanwijzing van de gebruiker). Tot vandaag rekende de routine
uitsluitend met xG en doelpuntensplits van vórig seizoen. Alles wat een mens als eerste noemt —
"die zijn drie man kwijt", "die kwamen woensdag pas terug uit Boedapest", "die hebben vijf keer op
rij gewonnen" — zat nergens in `my_prob`, en ook nergens in de administratie. `_shared-rules.md` §4
noemt blessures en vorm nadrukkelijk als geldige categorie-1-input; de code deed er niets mee.

Dat is niet alleen een gat in de onderbouwing, het wijst één kant op. Ontbrekende context is
gemiddeld genomen slecht nieuws voor de ploeg die het treft, en de routine zette in 89% van haar
picks juist op de zwakkere ploeg. Precies daar hakt een geblesseerde spits of een midweekse
Europese uitwedstrijd het hardst in.

Wat deze module wél en niet doet:

- **Wel**: de drie factoren meten en per wedstrijd vastleggen, zodat ze over enkele weken tegen
  uitkomsten te leggen zijn.
- **Wel**: een bet tegenhouden als de gespeelde kant er duidelijk slechter voorstaat dan de
  tegenstander. Dat is een veto, geen coëfficiënt.
- **Niet**: `my_prob` met een verzonnen factor bijstellen. Er is geen enkele meting die zegt
  hoeveel procentpunt een geblesseerde middenvelder waard is, en zo'n getal uit de duim zuigen is
  precies wat §2 en §4 verbieden ("niet gevonden = schrijf niet gevonden, nooit gokken"). De
  drempels in `ContextGate` zijn met opzet grof en staan hieronder als *voorlopig* aangemerkt.

Kosten: één Fotmob-verzoek per wedstrijd, geen credits. Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

TIMEOUT = 45
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

#: Een wedstrijd binnen zoveel dagen vóór of ná dit duel telt als belasting.
CONGESTION_DAYS = 4

#: VOORLOPIGE drempels voor `ContextGate`. Ze zijn niet gefit — er is nog geen enkele afgerekende
#: bet met contextdata. Ze staan op een niveau dat alleen duidelijke gevallen raakt, en ze horen
#: bijgesteld te worden zodra `data/context.jsonl` genoeg regels heeft om ze tegen uitkomsten te
#: leggen. Tot die tijd: liever een bet te veel tegengehouden dan een verzonnen kansbijstelling.
INJURY_GAP = 0.10        #: verschil in uitgevallen marktwaarde-aandeel dat als materieel telt
REST_GAP_DAYS = 2        #: zoveel dagen minder rust dan de tegenstander telt als materieel
SHORT_REST_DAYS = 4      #: ... maar alleen als de eigen rust hier onder zit


class ContextError(RuntimeError):
    pass


def _get_json(url: str) -> dict:
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=TIMEOUT).read()
    except urllib.error.HTTPError as exc:
        raise ContextError(f"HTTP {exc.code} op {url}") from exc
    return json.loads(raw)


@dataclass
class TeamContext:
    """De drie factoren voor één ploeg in één wedstrijd."""
    name: str
    out_count: int = 0
    out_value: float = 0.0            #: marktwaarde van de uitvallers
    squad_value: float = 0.0          #: marktwaarde van de vermoedelijke basiself
    out_names: list[str] = field(default_factory=list)
    form: str = ""                    #: bv. "WWLDW", oudste links
    form_points: int | None = None    #: punten uit de getoonde reeks
    form_matches: int = 0
    rest_days: float | None = None    #: dagen sinds de vorige wedstrijd
    congested: bool = False           #: nog een duel binnen CONGESTION_DAYS ervoor
    note: str = ""

    @property
    def out_share(self) -> float:
        """Aandeel van de basiself-marktwaarde dat niet beschikbaar is.

        Marktwaarde is een grove maat voor hoe belangrijk een speler is, maar het is de enige die
        Fotmob per uitvaller meegeeft, en hij onderscheidt in elk geval een eerste spits van een
        derde keeper. Is er geen selectiewaarde bekend, dan is dit 0.0 en telt de poort niet mee.
        """
        if self.squad_value <= 0:
            return 0.0
        return self.out_value / (self.squad_value + self.out_value)

    def summary(self) -> str:
        bits = []
        if self.out_count:
            bits.append(f"{self.out_count} afwezig ({self.out_share * 100:.0f}% van de "
                        f"selectiewaarde)")
        else:
            bits.append("niemand afwezig gemeld")
        if self.form:
            bits.append(f"vorm {self.form}")
        if self.rest_days is not None:
            bits.append(f"{self.rest_days:.0f} dagen rust" + (" (druk programma)" if self.congested else ""))
        return " · ".join(bits)


@dataclass
class MatchContext:
    home: TeamContext
    away: TeamContext
    source: str = "fotmob"
    lineup_type: str = ""

    def for_side(self, side: str) -> TeamContext:
        return self.home if side == "home" else self.away

    def other(self, side: str) -> TeamContext:
        return self.away if side == "home" else self.home


def _parse_unavailable(team: dict) -> tuple[int, float, list[str]]:
    out = team.get("unavailable") or []
    total, names = 0.0, []
    for p in out:
        mv = p.get("marketValue") or 0
        total += float(mv)
        u = p.get("unavailability") or {}
        kind = u.get("type") or "onbekend"
        names.append(f"{p.get('name', '?')} ({kind}"
                     + (f", terug {u['expectedReturn']}" if u.get("expectedReturn") else "") + ")")
    return len(out), total, names


def _parse_form(entries: list, kickoff: datetime | None) -> tuple[str, int, int, float | None, bool]:
    """Vorm, punten en rust uit één `teamForm`-reeks van Fotmob."""
    letters, points, dates = [], 0, []
    for e in entries or []:
        s = (e.get("resultString") or "").upper()[:1]
        if s in ("W", "D", "L"):
            letters.append(s)
            points += {"W": 3, "D": 1, "L": 0}[s]
        t = ((e.get("date") or {}).get("utcTime")) or ""
        if t:
            try:
                dates.append(datetime.fromisoformat(t.replace("Z", "+00:00")))
            except ValueError:
                pass
    rest, congested = None, False
    if kickoff and dates:
        before = [d for d in dates if d < kickoff]
        if before:
            rest = (kickoff - max(before)).total_seconds() / 86400
            congested = rest < CONGESTION_DAYS
    return "".join(letters), points, len(letters), rest, congested


def fetch_match_context(match_id: int, kickoff_utc: str | None = None) -> MatchContext:
    """Blessures, vorm en rust voor één wedstrijd.

    `kickoff_utc` in ISO-vorm; zonder aftraptijd worden `rest_days` en `congested` niet ingevuld.

    LET OP: vóór de aftrap geeft Fotmob `lineupType = "predicted"`. De blessurelijst is dan al
    gevuld (nagetrokken op vier competities op 23 aug 2026), de opstelling zelf is een voorspelling
    en wordt hier niet gebruikt — alleen `unavailable` en `totalStarterMarketValue`.
    """
    data = _get_json(f"https://www.fotmob.com/api/data/matchDetails?matchId={match_id}")
    content = data.get("content") or {}
    lineup = content.get("lineup") or {}
    facts = content.get("matchFacts") or {}
    forms = facts.get("teamForm") or [[], []]

    ko = None
    if kickoff_utc:
        try:
            ko = datetime.fromisoformat(kickoff_utc.replace("Z", "+00:00"))
        except ValueError:
            ko = None
    if ko is None:
        t = ((facts.get("infoBox") or {}).get("Match Date") or {}).get("utcTime")
        if t:
            try:
                ko = datetime.fromisoformat(t.replace("Z", "+00:00"))
            except ValueError:
                ko = None

    teams = []
    for idx, key in enumerate(("homeTeam", "awayTeam")):
        t = lineup.get(key) or {}
        n, value, names = _parse_unavailable(t)
        letters, pts, played, rest, cong = _parse_form(
            forms[idx] if idx < len(forms) else [], ko)
        teams.append(TeamContext(
            name=t.get("name") or ("thuis" if idx == 0 else "uit"),
            out_count=n, out_value=value, out_names=names,
            squad_value=float(t.get("totalStarterMarketValue") or 0),
            form=letters, form_points=pts if played else None, form_matches=played,
            rest_days=rest, congested=cong,
        ))
    return MatchContext(home=teams[0], away=teams[1],
                        lineup_type=lineup.get("lineupType") or "")


@dataclass
class ContextGate:
    """Uitkomst van de contextpoort (poort 7 in _shared-rules.md §1)."""
    passed: bool
    reason: str = ""
    detail: dict = field(default_factory=dict)


def check(ctx: MatchContext, side: str | None) -> ContextGate:
    """Staat de gespeelde kant er materieel slechter voor dan de tegenstander?

    `side` is "home", "away" of None. Bij None (Over/Under, BTTS, gelijkspel) is er geen kant om
    te benadelen en gaat de poort altijd open — context kan het *totaal* best beïnvloeden, maar in
    welke richting is zonder meting niet te zeggen, en dan is tegenhouden willekeur.

    De poort is bewust asymmetrisch: hij houdt alleen tegen, hij laat nooit iets extra's door.
    Twijfelgevallen (geen selectiewaarde bekend, geen vormreeks) gaan open, want een ontbrekende
    meting is geen bewijs van een probleem.
    """
    if side is None:
        return ContextGate(True, "geen kant om te benadelen")

    mine, theirs = ctx.for_side(side), ctx.other(side)
    detail = {
        "gespeeld": mine.name, "tegenstander": theirs.name,
        "uit_aandeel": round(mine.out_share, 4), "uit_aandeel_tegenstander": round(theirs.out_share, 4),
        "uit_namen": mine.out_names,
        "vorm": mine.form, "vorm_tegenstander": theirs.form,
        "rust": mine.rest_days, "rust_tegenstander": theirs.rest_days,
        "druk_programma": mine.congested,
    }

    gap = mine.out_share - theirs.out_share
    if mine.squad_value > 0 and theirs.squad_value > 0 and gap >= INJURY_GAP:
        return ContextGate(False, (
            f"blessures: {mine.name} mist {mine.out_share * 100:.0f}% van de selectiewaarde tegen "
            f"{theirs.out_share * 100:.0f}% bij {theirs.name} — {', '.join(mine.out_names[:3])}"),
            detail)

    if (mine.rest_days is not None and theirs.rest_days is not None
            and mine.rest_days <= SHORT_REST_DAYS
            and theirs.rest_days - mine.rest_days >= REST_GAP_DAYS):
        return ContextGate(False, (
            f"rust: {mine.name} had {mine.rest_days:.0f} dagen tegen "
            f"{theirs.rest_days:.0f} bij {theirs.name}"), detail)

    return ContextGate(True, "geen materieel nadeel gemeten", detail)


if __name__ == "__main__":
    # Zelftest tegen echte, actuele data: één duel van vandaag met een voorspelde opstelling.
    import sys
    from datetime import date
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    from scripts import fotmob

    fixtures = fotmob.fetch_fixtures(date.today())
    probe = None
    for lg in fixtures.get("leagues", []):
        for m in lg.get("matches", []):
            if not m["status"].get("started"):
                probe = (m["id"], m["status"]["utcTime"], m["home"]["name"], m["away"]["name"])
                break
        if probe:
            break
    if not probe:
        print("Geen wedstrijd meer voor de boeg vandaag; zelftest overgeslagen.")
        raise SystemExit(0)

    mid, ko, h, a = probe
    ctx = fetch_match_context(mid, ko)
    print(f"{h} - {a}  (lineupType={ctx.lineup_type})")
    print(f"  thuis: {ctx.home.summary()}")
    print(f"  uit  : {ctx.away.summary()}")
    for s in ("home", "away", None):
        g = check(ctx, s)
        print(f"  poort {str(s):5}: {'open ' if g.passed else 'DICHT'} — {g.reason}")
    assert ctx.home.name and ctx.away.name, "teamnamen niet gevonden"
    assert check(ctx, None).passed, "zonder kant hoort de poort altijd open te staan"
