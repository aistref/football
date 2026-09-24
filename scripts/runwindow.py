#!/usr/bin/env python3
"""Welke wedstrijden horen bij de run van vandaag? Stage 1 van _shared-rules.md.

**Waarom dit bestaat (Run B, 24 sep 2026).** Stage 1 zei tot die datum "werk uitsluitend met
wedstrijden van **vandaag**", en elke run las dat als "wedstrijden waarvan de UTC-datum de rundag
is". Voor de vijftien Europese competities op de Run B-lijst klopt dat: die trappen af tussen 12:30
en 21:00 NL-tijd en vallen dus altijd binnen hun eigen UTC-dag. Voor MLS en Série A klopt het niet,
en `prompts/run-b.md` waarschuwde daar al voor zonder er een regel aan te verbinden.

Wat er op 24 september gebeurde, en waarom het geen randgeval is:

- De daglijst van 24 sep gaf precies één duel uit de Run B-runlijst: **Seattle Sounders FC – Real
  Salt Lake**, aftrap `2026-09-24T01:40Z`, oftewel **03:40 NL-tijd**.
- Run B begint om ~05:15 en moet om 06:30 klaar zijn, want de gebruiker zet tussen 07:00 en 08:00
  in (§0). Het duel stond bij het eerste verzoek van die run al op **89'** met 2–0.
- Het duel was dus onspeelbaar bij aankomst — en de run van 23 september had het zien komen en
  opgeschreven als "hoort bij de run van morgen". Dat was precies verkeerd om: het hoorde bij de
  run van 23 september, niet bij die van de 24e.
- Vandaag kostte dat één wedstrijd. Op een volle MLS-speelronde (tien tot veertien duels op
  zaterdag en woensdag) kost het de hele ronde, en het runrapport ziet er dan volkomen normaal uit
  met een nette nul erin. Dat is het gevaarlijke deel.

**De regel die dit oplost is één regel en heeft geen lijst met uitzonderingen nodig.** Niet "MLS en
Série A een dag vooruit lezen", maar:

> Een wedstrijd hoort bij de run wiens **inzetvenster** hem nog kan bedienen, en dat venster loopt
> van het einde van de inzetperiode op de rundag tot het einde van de inzetperiode een dag later.

Oftewel `[08:00 NL op dag d, 08:00 NL op dag d+1)`. De gebruiker zet tussen 07:00 en 08:00 in, dus
08:00 is het laatste moment waarop hij een koers kan aannemen; alles wat daarna afgetrapt wordt is
voor hem speelbaar, alles ervoor niet. Wat die ene regel doet met de drie gevallen hierboven:

| aftrap | oude regel (UTC-dag) | dit venster | speelbaar? |
|---|---|---|---|
| 24 sep 20:00 NL (Europees) | run van 24 sep | run van 24 sep | ja, ongewijzigd |
| 25 sep 03:30 NL (MLS) | run van **25** sep — dan al gespeeld | run van **24** sep | ja, gerepareerd |
| 24 sep 03:40 NL (MLS, het duel hierboven) | run van 24 sep — dan al gespeeld | run van **23** sep | ja, gerepareerd |

Er zit dus geen competitielijst in en geen tijdzone-vlag per competitie. Een Europese avondwedstrijd
verschuift niet, want die valt hoe dan ook binnen zijn eigen venster; alleen de band van 00:00 tot
08:00 NL schuift een dag naar voren, en dat is exact de band die onspeelbaar bij de run aankwam.
**Dat maakt de regel ook goed voor Run A en Run C** — een CONCACAF- of Asian-Games-duel om 02:00 NL
heeft hetzelfde probleem, en Run C heeft die duels wél op de lijst.

**Let op bij de overstap, want hier valt een gat.** Zolang de vorige run nog op de oude regel draaide,
is de band `[00:00, 08:00)` NL van de eigen rundag door niemand bekeken: de oude regel gaf hem aan de
run van vandaag (die hem te laat kreeg) en dit venster geeft hem aan de run van gisteren (die hem niet
zocht). De eerste run die deze module gebruikt, moet daarom `include_carry_over=True` meegeven. Dan
begint het venster op 00:00 NL in plaats van op 08:00 NL en wordt die band één keer ingehaald — met de
kanttekening dat de duels erin al zijn afgetrapt en dus niet speelbaar zijn. Ze horen dan in het
runrapport als `GEEN BET` met de aftraptijd erbij, niet als bet.

**Wat deze module niet doet.** Ze haalt niets op. `fetch_fixtures` blijft de bron, en `days_needed`
zegt welke daglijsten je nodig hebt — twee in plaats van één, en de tweede haalden de runs toch al op
om precies deze reden ("de daglijst van morgen is er ook bij gehaald, juist voor MLS en Série A").
Ze kost dus geen extra verzoek.

    from scripts.runwindow import days_needed, matches_for_run

    fixtures = {d: fotmob.fetch_fixtures(d) for d in days_needed(DAY)}
    per_comp = matches_for_run(DAY, fixtures, RUNLIST_IDS)

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

try:                                       # pragma: no cover - afhankelijk van de tzdata op de host
    from zoneinfo import ZoneInfo
    NL = ZoneInfo("Europe/Amsterdam")
except Exception:                          # pragma: no cover
    NL = timezone(timedelta(hours=2))
    """Terugval als de host geen tzdata heeft. LET OP: die vaste +02:00 is CEST en klopt dus niet
    na de laatste zondag van oktober. De rest van de repo rekent nog wél met een hardgecodeerde
    +02:00 (o.a. de `kickoff_nl`-velden in de runscripts), en dat is een eigen openstaand punt —
    hier staat het goed zolang `zoneinfo` beschikbaar is, en op deze container is dat zo
    (nagetrokken op 24 sep 2026: een aftrap in november komt correct op +01:00 uit)."""

#: Het laatste moment waarop de gebruiker een koers kan aannemen, in NL-tijd. §0: het rapport staat
#: om 06:30 klaar en hij zet tussen 07:00 en 08:00 in. Dit is dus geen schatting van zijn gedrag
#: maar de afspraak die in §0 staat; verandert die afspraak, dan verandert dit getal mee.
BET_WINDOW_END = time(8, 0)


class RunWindowError(ValueError):
    pass


def window(day: date, *, include_carry_over: bool = False) -> tuple[datetime, datetime]:
    """`[begin, eind)` van het inzetvenster van de run van `day`, in UTC.

    `include_carry_over=True` trekt het begin terug naar 00:00 NL van `day`, voor de eenmalige
    overstap die in de kop van deze module staat. Gebruik het niet standaard: dan pakt elke run de
    band op die de vorige run al heeft gehad, en staat dezelfde wedstrijd twee runrapporten in.
    """
    start_time = time(0, 0) if include_carry_over else BET_WINDOW_END
    start = datetime.combine(day, start_time, tzinfo=NL)
    end = datetime.combine(day + timedelta(days=1), BET_WINDOW_END, tzinfo=NL)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def days_needed(day: date, *, include_carry_over: bool = False) -> list[date]:
    """Welke Fotmob-daglijsten dit venster kan raken.

    Altijd `day` en `day + 1`: het venster loopt over middernacht UTC heen, dus een duel erin kan
    op beide daglijsten staan. Meer dan twee zijn er niet nodig — het venster is 24 uur lang en
    begint na 00:00 UTC, dus het raakt precies twee UTC-dagen.
    """
    return [day, day + timedelta(days=1)]


def parse_kickoff(value: str | datetime) -> datetime:
    """De `utcTime` van Fotmob als bewust-UTC `datetime`.

    Fotmob levert `2026-09-24T01:40:00.000Z`. `fromisoformat` slikt die `Z` pas vanaf Python 3.11,
    en een naïeve `datetime` vergelijken met een bewuste gooit een `TypeError` op een plek waar
    niemand hem verwacht — vandaar deze ene functie in plaats van dezelfde drie regels per run.
    """
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError as exc:
            raise RunWindowError(f"onleesbare aftraptijd: {value!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def kickoff_nl(value: str | datetime) -> str:
    """De aftrap als `HH:MM` in NL-tijd. §5 eist NL-tijd in het rapport, met zomertijd."""
    return parse_kickoff(value).astimezone(NL).strftime("%H:%M")


def belongs_to_run(kickoff: str | datetime, day: date, *,
                   include_carry_over: bool = False) -> bool:
    """Valt deze aftrap in het inzetvenster van de run van `day`?"""
    start, end = window(day, include_carry_over=include_carry_over)
    return start <= parse_kickoff(kickoff) < end


def playable(kickoff: str | datetime, *, now: datetime | None = None) -> bool:
    """Kan de gebruiker hier nog op inzetten?

    Los van het venster, want een run kan te laat draaien of een duel kan zijn verschoven. De
    vergelijking is met het einde van de inzetperiode van de dag waarop de run draait, niet met de
    klok van dit moment: een run die om 05:22 klaar is, wordt om 07:00 gelezen.
    """
    now = now or datetime.now(timezone.utc)
    deadline = datetime.combine(now.astimezone(NL).date(), BET_WINDOW_END,
                                tzinfo=NL).astimezone(timezone.utc)
    return parse_kickoff(kickoff) >= deadline


@dataclass
class RunMatch:
    """Eén wedstrijd zoals Stage 1 hem aan Stage 2 doorgeeft."""
    competition: str
    league_id: int
    match_id: int | None
    home: str
    away: str
    home_id: int | None
    away_id: int | None
    kickoff_utc: str
    kickoff_nl: str
    source_day: date
    """Op welke Fotmob-daglijst hij stond. Staat hij op `day + 1`, dan is dit een duel dat de oude
    UTC-dagregel aan de run van morgen zou hebben gegeven — en morgen is het te laat. Noem dat in
    het runrapport, anders leest de lijst als een gewone speeldag."""
    playable: bool
    """False = al afgetrapt voordat de gebruiker kon inzetten. Alleen mogelijk met
    `include_carry_over=True` of bij een run die veel te laat draait; zo'n duel hoort in het
    rapport als `GEEN BET` met de aftraptijd als reden, niet als bet."""

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["source_day"] = self.source_day.isoformat()
        return d


def _leagues_by_id(fixtures: dict) -> dict[int, dict]:
    out = {}
    for league in fixtures.get("leagues", []) or []:
        lid = league.get("primaryId") or league.get("id")
        if lid is not None:
            out[int(lid)] = league
    return out


def matches_for_run(day: date, fixtures: dict[date, dict], leagues: dict[str, int], *,
                    include_carry_over: bool = False,
                    now: datetime | None = None) -> dict[str, list[RunMatch]]:
    """Per competitie uit `leagues` de wedstrijden die bij de run van `day` horen.

    `fixtures` is `{dag: antwoord van fotmob.fetch_fixtures(dag)}` voor de dagen uit
    `days_needed(day)`; ontbreekt een dag, dan wordt hij overgeslagen en niet geraden.
    `leagues` is `{runlijstnaam: Fotmob primaryId}` — **matchen gaat op id en nooit op naam**, om
    dezelfde reden die `coverage.json` drie keer noteert: de Tsjechische beker heeft `ccode = CZE`
    en de Braziliaanse Série B heet bijna hetzelfde als Série A.

    Afgelaste duels (`status.cancelled`) vallen eruit. Een duel zonder `utcTime` ook, want zonder
    aftraptijd is niet te zeggen bij welke run het hoort — dat is een gat om te melden, geen duel om
    te raden.

    Duels staan op meer dan één daglijst als hun UTC-tijd dicht bij middernacht ligt; ze worden op
    `match_id` ontdubbeld, met de daglijst van `day` zelf als voorkeur.
    """
    if not isinstance(day, date):
        raise RunWindowError(f"`day` moet een date zijn, niet {type(day).__name__}")
    per_day = {d: _leagues_by_id(fx) for d, fx in fixtures.items() if fx}
    out: dict[str, list[RunMatch]] = {name: [] for name in leagues}
    seen: dict[str, set] = {name: set() for name in leagues}

    for source_day in days_needed(day, include_carry_over=include_carry_over):
        by_id = per_day.get(source_day)
        if by_id is None:
            continue
        for name, lid in leagues.items():
            league = by_id.get(int(lid))
            if not league:
                continue
            for m in league.get("matches", []) or []:
                status = m.get("status") or {}
                if status.get("cancelled"):
                    continue
                utc = status.get("utcTime")
                if not utc:
                    continue
                if not belongs_to_run(utc, day, include_carry_over=include_carry_over):
                    continue
                key = m.get("id") or (m.get("home", {}).get("name"), utc)
                if key in seen[name]:
                    continue
                seen[name].add(key)
                out[name].append(RunMatch(
                    competition=name, league_id=int(lid), match_id=m.get("id"),
                    home=(m.get("home") or {}).get("name"),
                    away=(m.get("away") or {}).get("name"),
                    home_id=(m.get("home") or {}).get("id"),
                    away_id=(m.get("away") or {}).get("id"),
                    kickoff_utc=utc, kickoff_nl=kickoff_nl(utc), source_day=source_day,
                    playable=playable(utc, now=now)))

    for name in out:
        out[name].sort(key=lambda r: parse_kickoff(r.kickoff_utc))
    return out


if __name__ == "__main__":
    # Zelftest op de drie gevallen uit de kop van deze module, plus de wintertijdcontrole. Geen
    # netwerk: de daglijsten zijn nagemaakt met de velden die `matches_for_run` werkelijk leest.
    from datetime import date as _date

    DAY = _date(2026, 9, 24)

    def _fx(*matches):
        return {"leagues": [{"primaryId": 130, "ccode": "USA", "name": "Major League Soccer",
                             "matches": list(matches)}]}

    def _m(mid, utc, home="Seattle Sounders FC", away="Real Salt Lake"):
        return {"id": mid, "home": {"name": home, "id": 1}, "away": {"name": away, "id": 2},
                "status": {"utcTime": utc}}

    start, end = window(DAY)
    assert start.isoformat() == "2026-09-24T06:00:00+00:00", start
    assert end.isoformat() == "2026-09-25T06:00:00+00:00", end

    # 1. Het duel van 24 sep 01:40Z (03:40 NL) hoort NIET bij de run van 24 sep maar bij die van 23.
    assert not belongs_to_run("2026-09-24T01:40:00.000Z", DAY)
    assert belongs_to_run("2026-09-24T01:40:00.000Z", _date(2026, 9, 23))
    # 2. Een MLS-duel van 25 sep 01:30Z hoort bij de run van 24 sep, niet bij die van 25.
    assert belongs_to_run("2026-09-25T01:30:00.000Z", DAY)
    assert not belongs_to_run("2026-09-25T01:30:00.000Z", _date(2026, 9, 25))
    # 3. Een Europese avondwedstrijd verschuift niet.
    assert belongs_to_run("2026-09-24T18:30:00.000Z", DAY)

    # De carry-over haalt de band van 00:00-08:00 NL eenmalig in, met playable=False.
    got = matches_for_run(DAY, {DAY: _fx(_m(1, "2026-09-24T01:40:00.000Z")),
                                DAY + timedelta(days=1): _fx(_m(2, "2026-09-25T01:30:00.000Z"))},
                          {"MLS (USA)": 130})
    assert [m.match_id for m in got["MLS (USA)"]] == [2], got
    assert got["MLS (USA)"][0].source_day == DAY + timedelta(days=1)
    assert got["MLS (USA)"][0].kickoff_nl == "03:30"

    got2 = matches_for_run(DAY, {DAY: _fx(_m(1, "2026-09-24T01:40:00.000Z")),
                                 DAY + timedelta(days=1): _fx(_m(2, "2026-09-25T01:30:00.000Z"))},
                           {"MLS (USA)": 130}, include_carry_over=True,
                           now=datetime(2026, 9, 24, 3, 22, tzinfo=timezone.utc))
    assert [m.match_id for m in got2["MLS (USA)"]] == [1, 2], got2
    assert got2["MLS (USA)"][0].playable is False
    assert got2["MLS (USA)"][1].playable is True

    # Ontdubbelen: hetzelfde duel op beide daglijsten levert één rij.
    dupe = matches_for_run(DAY, {DAY: _fx(_m(2, "2026-09-25T01:30:00.000Z")),
                                 DAY + timedelta(days=1): _fx(_m(2, "2026-09-25T01:30:00.000Z"))},
                           {"MLS (USA)": 130})
    assert len(dupe["MLS (USA)"]) == 1, dupe

    # Afgelast en zonder aftraptijd vallen eruit, niet om.
    odd = _fx({"id": 9, "home": {"name": "A"}, "away": {"name": "B"},
               "status": {"utcTime": "2026-09-24T18:00:00.000Z", "cancelled": True}},
              {"id": 10, "home": {"name": "C"}, "away": {"name": "D"}, "status": {}})
    assert matches_for_run(DAY, {DAY: odd}, {"MLS (USA)": 130})["MLS (USA)"] == []

    # Wintertijd: 20 nov 01:40Z is 02:40 NL, niet 03:40.
    assert kickoff_nl("2026-11-20T01:40:00.000Z") == "02:40"

    # Een competitie zonder wedstrijden komt terug als lege lijst, niet als ontbrekende sleutel —
    # Stage 2 heeft dat verschil nodig om `GEEN WEDSTRIJD` van "niet gezocht" te scheiden.
    assert matches_for_run(DAY, {DAY: _fx()}, {"MLS (USA)": 130, "Serie B (ITA)": 56}) == {
        "MLS (USA)": [], "Serie B (ITA)": []}

    print("runwindow: alle zelftests geslaagd")
    for d in (_date(2026, 9, 23), DAY, _date(2026, 9, 25)):
        s, e = window(d)
        print(f"  venster run {d}: {s:%Y-%m-%d %H:%M}Z t/m {e:%Y-%m-%d %H:%M}Z")
