#!/usr/bin/env python3
"""Het wedstrijddossier: alles wat er vóór de aftrap over één duel te weten valt.

Aanleiding (20 sep 2026, op verzoek van de gebruiker). De routine was een poort geworden die
vrijwel altijd nee zegt, en daarmee verdween ook de voetbalinhoud uit het dagrapport. De vraag
was of er Opta-cijfers, oude wedstrijdverslagen en de lezing van andere sites bij konden.

Het antwoord op het eerste deel bleek: **dat zit er al in.** `context.py` haalde per wedstrijd de
volledige Fotmob-respons op (50 KB), gebruikte daarvan alleen de uitvallers en de vorm, en gooide
de rest weg. Die respons draagt `"source": "Opta"` en geeft per speler een `optaId`.

DIT IS GEEN BESPARING EN MOET OOK NIET ZO GELEZEN WORDEN. Bij de bouw is eerst geschreven dat het
"nul extra verzoeken kost", en de gebruiker wees er terecht op dat dat een schaarste suggereert die
er niet is: de 20.000 credits zijn het budget van The Odds API (op 19 sep 2026 werden er 54 van
793 gebruikt) en Fotmob kost helemaal geen credits. Gemeten op 20 sep 2026 duurt een
matchDetails-verzoek mediaan **0,15 seconde**; 57 wedstrijden is negen seconden, en 627 verzoeken —
tien historische duels per wedstrijd erbij — blijft onder de twee minuten, op een run die 14,6
minuten duurde met ruim twee uur tot de deadline van 06:30. Het argument voor dit bestand is dus
niet dat het goedkoop is maar dat de data er is en niet werd gebruikt. Wees navenant ruimhartig in
wat je ophaalt; de enige grens die telt is §0's tijdsgrens, en die is voorlopig niet in zicht.

Wat er vóór de aftrap in zit, en dus in het dossier komt:

| veld | wat het is |
|---|---|
| `h2h` | onderlinge balans en de laatste ontmoetingen met uitslag en competitie |
| `insights` | Fotmob's eigen voorbeschouwingsregels in gewone taal ("Have scored 11 goals in their last 5 matches", "Evanilson is ranked 3 in big chances created") |
| `form` | vorm, punten en rustdagen per ploeg (dezelfde bron als poort 7) |
| `unavailable` | geblesseerden en geschorsten met hun marktwaarde |
| `table` | de stand, voor de competitiecontext |
| `top_players` | de best beoordeelde spelers per ploeg dit seizoen |
| `weather` | temperatuur, wind, neerslag |
| `lineup_type` | of de opstelling voorspeld of bevestigd is |

Wat er pas ná afloop bij komt — en dus alleen voor historische duels te halen is: `stats` per
periode (xG, schoten, passes, duels), `playerStats` voor 40 spelers met `optaId`, `shotmap` met
x/y/minuut per schot, `momentum` en `attackingZones`. Dat is het materiaal waarmee een
spelersvergelijking ("welke linksback tegen welke rechtsbuiten") te bouwen is; `fetch_history`
hieronder haalt het op voor de duels uit de h2h-lijst.

## WAAR DIT WEL EN NIET VOOR IS — lees dit voordat je het aansluit

Het dossier voedt **de lezing**, niet `my_prob`. Dat onderscheid is niet cosmetisch maar de
anti-circulariteitsregel van §2, en hij is hard:

- **Schoon voor `my_prob`:** xG, doelpunten, schoten, opstellingen, blessures, vorm, h2h — alles
  wat uit het spel zelf komt.
- **NIET schoon voor `my_prob`:** de lezing van tipsites, beurskoersen (Betfair, Matchbook),
  "modelkansen" van sites die zelf odds meewegen. Die horen in de lezing en in het marktbeeld, en
  ze mogen nooit in de kansschatting terechtkomen waar `edge_pp` tegen wordt afgezet — anders meet
  de edge alleen nog de afstand tot een getal dat zelf uit de markt komt.

`insights` zit op het randje en staat daarom hieronder apart: het zijn feitelijke waarnemingen uit
de wedstrijddata ("heeft 11 goals in 5 duels"), geen voorspelling en geen marktafgeleide. Bruikbaar
in de lezing; niet als kansinput, want het is een selectie van feiten die Fotmob interessant vindt
en geen volledige beschrijving.

    python3 scripts/dossier.py show --match-id 5795455
    python3 scripts/dossier.py show --match-id 5795455 --json

Alleen de standaardbibliotheek plus `scripts/fotmob.py`.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field, asdict

try:
    from . import fotmob
except ImportError:
    import fotmob          # type: ignore[no-redef]

# Hoeveel onderlinge duels er in het dossier komen. Tien is ruim genoeg om een patroon te zien en
# kort genoeg om leesbaar te blijven; de volledige lijst blijft in de respons beschikbaar.
H2H_LIMIT = 10


@dataclass
class Dossier:
    match_id: int
    home: str = ""
    away: str = ""
    competition: str | None = None
    kickoff_utc: str | None = None
    lineup_type: str | None = None
    h2h_summary: dict = field(default_factory=dict)
    h2h_matches: list = field(default_factory=list)
    insights: list = field(default_factory=list)
    form: dict = field(default_factory=dict)
    unavailable: dict = field(default_factory=dict)
    top_players: dict = field(default_factory=dict)
    table_note: str | None = None
    weather: dict = field(default_factory=dict)
    has_post_match: bool = False
    notes: list = field(default_factory=list)


def _team_names(data: dict) -> tuple[str, str]:
    general = data.get("general") or {}
    return (general.get("homeTeam") or {}).get("name") or "", \
           (general.get("awayTeam") or {}).get("name") or ""


def _h2h(content: dict) -> tuple[dict, list]:
    h = content.get("h2h") or {}
    summary = h.get("summary") or []
    out: list[dict] = []
    for m in (h.get("matches") or []):
        st = m.get("status") or {}
        if not st.get("finished"):
            continue                      # toekomstige ontmoetingen zeggen niets over het verleden
        out.append({"date": (m.get("time") or {}).get("utcTime") or st.get("utcTime"),
                    "competition": (m.get("league") or {}).get("name"),
                    "home": (m.get("home") or {}).get("name"),
                    "away": (m.get("away") or {}).get("name"),
                    "score": st.get("scoreStr"),
                    "match_id": _id_from_url(m.get("matchUrl"))})
    out.sort(key=lambda r: r["date"] or "", reverse=True)
    label = {}
    if len(summary) == 3:
        label = {"thuisploeg_won": summary[0], "gelijk": summary[1], "uitploeg_won": summary[2]}
    return label, out[:H2H_LIMIT]


def _id_from_url(url: str | None) -> int | None:
    if not url or "#" not in url:
        return None
    try:
        return int(url.rsplit("#", 1)[1])
    except ValueError:
        return None


def _insights(facts: dict) -> list[dict]:
    out = []
    for i in (facts.get("insights") or []):
        tekst = i.get("text")
        if not tekst:
            continue
        out.append({"team_id": i.get("teamId"), "speler_id": i.get("playerId"),
                    "tekst": tekst, "soort": i.get("type")})
    return out


def _lineup_side(lineup: dict, key: str) -> dict:
    t = lineup.get(key) or {}
    uit = []
    for p in (t.get("unavailable") or []):
        u = p.get("unavailability") or {}
        uit.append({"naam": p.get("name") or "?",
                    "reden": u.get("type") or "onbekend",
                    "terug": u.get("expectedReturn"),
                    "marktwaarde": p.get("marketValue")})
    return {"ploeg": t.get("name"), "team_id": t.get("id"),
            "selectiewaarde": t.get("totalStarterMarketValue"), "afwezig": uit}


def build(match_id: int, data: dict | None = None) -> Dossier:
    """Het dossier voor één wedstrijd. Hergebruikt de respons die `context.py` toch al ophaalt."""
    data = data if data is not None else fotmob.fetch_match_details(match_id)
    content = data.get("content") or {}
    facts = content.get("matchFacts") or {}
    lineup = content.get("lineup") or {}
    general = data.get("general") or {}
    home, away = _team_names(data)
    summary, matches = _h2h(content)

    forms = facts.get("teamForm") or [[], []]
    vorm = {}
    for idx, kant in enumerate(("thuis", "uit")):
        reeks = forms[idx] if idx < len(forms) else []
        vorm[kant] = [{"tegen": (r.get("teamName") or r.get("opponent")),
                       "uitslag": r.get("resultString") or r.get("result"),
                       "datum": (r.get("date") or {}).get("utcTime") if isinstance(r.get("date"), dict) else r.get("date")}
                      for r in (reeks or [])][:6]

    tp = facts.get("topPlayers") or {}
    top = {}
    for kant, sleutel in (("thuis", "homeTopPlayers"), ("uit", "awayTopPlayers")):
        spelers = tp.get(sleutel) or []
        top[kant] = [{"naam": p.get("name"), "rating": (p.get("value") or p.get("rating")),
                      "opta_id": p.get("optaId") or p.get("id")}
                     for p in spelers[:3]]

    d = Dossier(
        match_id=match_id, home=home, away=away,
        competition=(general.get("leagueName") or general.get("parentLeagueName")),
        kickoff_utc=((facts.get("infoBox") or {}).get("Match Date") or {}).get("utcTime"),
        lineup_type=lineup.get("lineupType"),
        h2h_summary=summary, h2h_matches=matches,
        insights=_insights(facts), form=vorm,
        unavailable={"thuis": _lineup_side(lineup, "homeTeam"),
                     "uit": _lineup_side(lineup, "awayTeam")},
        top_players=top,
        weather=content.get("weather") or {},
        has_post_match=bool(content.get("playerStats")),
    )
    if not d.insights:
        d.notes.append("geen insights in de respons")
    if not d.h2h_matches:
        d.notes.append("geen eerdere onderlinge duels bij Fotmob")
    return d


def fetch_history(d: Dossier, limit: int = 5) -> list[dict]:
    """Per-speler- en schotdata van eerdere onderlinge duels (alleen ná afloop gevuld).

    Dit is het materiaal voor een spelersvergelijking: `playerStats` geeft 40 spelers met hun
    `optaId`, `shotmap` geeft x/y/minuut per schot, en `stats` de volledige wedstrijdstatistiek
    per helft. Eén verzoek per historisch duel, à 0,15 s — bij `limit=10` over 57 wedstrijden is
    dat anderhalve minuut, dus dit kan gewoon in de dagelijkse run mee. Draai het niet krapper dan
    nodig uit zuinigheid; zuinig hoeft hier niet.
    """
    out = []
    for m in d.h2h_matches[:limit]:
        mid = m.get("match_id")
        if not mid:
            continue
        try:
            det = fotmob.fetch_match_details(mid)
        except Exception as exc:
            out.append({**m, "fout": f"{type(exc).__name__}: {exc}"})
            continue
        c = det.get("content") or {}
        spelers = c.get("playerStats") or {}
        out.append({**m,
                    "spelers": len(spelers),
                    "schoten": len((c.get("shotmap") or {}).get("shots") or []),
                    "stats_secties": [s.get("title") for s in
                                      (((c.get("stats") or {}).get("Periods") or {}).get("All") or {}).get("stats", [])]})
    return out


def render(d: Dossier) -> str:
    """Het dossier als leesbare tekst — de basis voor de lezing in het dagrapport."""
    r = [f"{d.home} – {d.away}" + (f"  ·  {d.competition}" if d.competition else "")]
    if d.lineup_type:
        r.append(f"opstelling: {d.lineup_type}")
    if d.h2h_summary:
        s = d.h2h_summary
        r.append(f"onderling: {s.get('thuisploeg_won')}–{s.get('gelijk')}–{s.get('uitploeg_won')} "
                 f"(winst thuisploeg – gelijk – winst uitploeg)")
    for m in d.h2h_matches[:5]:
        r.append(f"   {(m['date'] or '')[:10]}  {m['home']} {m['score']} {m['away']}"
                 f"  ({m['competition']})")
    if d.insights:
        r.append("waarnemingen:")
        for i in d.insights:
            r.append(f"   - {i['tekst']}")
    for kant in ("thuis", "uit"):
        u = d.unavailable.get(kant) or {}
        afw = u.get("afwezig") or []
        if afw:
            namen = ", ".join(f"{p['naam']} ({p['reden']})" for p in afw[:5])
            r.append(f"afwezig {kant} ({u.get('ploeg')}): {namen}")
    if d.weather:
        w = d.weather
        r.append(f"weer: {w.get('temperature')}°C, wind {w.get('windSpeed')} "
                 f"{w.get('windDirectionCardinal') or ''}".rstrip())
    for n in d.notes:
        r.append(f"[{n}]")
    return "\n".join(r)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show", help="dossier van één wedstrijd")
    s.add_argument("--match-id", type=int, required=True)
    s.add_argument("--json", action="store_true")
    s.add_argument("--history", type=int, default=0,
                   help="haal ook per-speler-data van N eerdere onderlinge duels (1 verzoek elk)")
    args = ap.parse_args(argv)

    d = build(args.match_id)
    if args.history:
        hist = fetch_history(d, args.history)
        if args.json:
            print(json.dumps({**asdict(d), "historie": hist}, ensure_ascii=False, indent=1))
            return 0
        print(render(d))
        print("\nhistorische duels met spelersdata:")
        for h in hist:
            print(f"   {(h['date'] or '')[:10]} {h['home']} {h['score']} {h['away']}"
                  f"  -> {h.get('spelers', 0)} spelers, {h.get('schoten', 0)} schoten")
        return 0
    print(json.dumps(asdict(d), ensure_ascii=False, indent=1) if args.json else render(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
