"""Het materiaal voor een voorbeschouwing: historie, waarnemingen en de week eromheen.

**Aanleiding (17 okt 2026, op verzoek van de gebruiker).** Het dagrapport las als een
rekenverslag. De gebruiker:

> *"Ik vind de verslagen echt niet te lezen. (...) Nu is het allemaal over 'sterkste regel',
> 'drempels', 'procentpunten', extra uitleg over drempels en andere rekeningen en toetsen,
> scheefstand en dan een klein beetje context. Ik wil in de ochtend gewoon een leuke
> voorbeschouwing lezen op basis van wat je hebt gevonden. (...) Het is gewoon interessanter om te
> lezen bij Strasbourg – Paris Saint-Germain alle 5 duels BTS eindigde en bij PSG 4/5 maar dat het
> minder vaak boven de 3,5 uitkwam. Hoe ze tegen elkaar speelden eerder, teamnieuws (vorm,
> blessures, europees gespeeld of europees komende week randzaken)."*

De verhouding moest dus om: de voetbalinhoud vooraan, de rekenkundige verantwoording minimaal en
in het markdown-runrapport. Dit bestand levert de **feiten** die een voorbeschouwing nodig heeft
en die de run tot nu toe niet vastlegde. Drie dingen, en alle drie zijn ze de reden dat de
voorbeschouwing van 17 oktober te schrijven was:

| wat | waarom het moest worden toegevoegd |
|---|---|
| `h2h` | de onderlinge duels mét uitslag, en per duel het doelpuntentotaal en of beide ploegen scoorden. Bij Strasbourg – PSG waren dat 1–2, 3–3, 2–1, 4–2, 1–2: drie van de vijf op exact drie doelpunten en vijf van de vijf met doelpunten aan beide kanten. Dat is de kern van het verhaal en het stond nergens. |
| `insights` | Fotmob's eigen voorbeschouwingsregels, in gewone taal. *"Haven't kept a clean sheet in 20 matches"* bij Strasbourg is één regel die meer zegt dan een kolom cijfers. Let op §4: ze mogen in de **lezing** en nooit in `my_prob`. |
| `week` | wat deze ploeg vóór en ná dit duel speelt, inclusief de Europese toernooien. PSG speelde woensdag 2–4 bij Manchester City en ontvangt dinsdag Barcelona; dat is het soort randzaak waar een voorbeschouwing op draait en dat uit rustdagen alleen niet te zien is. |

**`scripts/dossier.py` haalde h2h en insights al op — maar alleen voor de mens achter de CLI.**
Geen enkele run legde ze in `data/run-state/` vast, dus `report.py` kon ze niet renderen en een
volgende run kon ze niet teruglezen. Dat is dezelfde fout als `teamForm` bij `marketform`: de data
was er en werd weggegooid.

**Wat dit NIET doet.** Niets hier gaat in `my_prob`. Een voorbeschouwing beschrijft; ze rekent
niet. Dat is §2 en §4 en het is geen smaakkwestie — `insights` is per ontwerp een selectie van
feiten die Fotmob interessant vindt, en zoiets als kansinput gebruiken maakt de schatting
afhankelijk van andermans redactie.

**Kosten.** Fotmob rekent niet af per verzoek. Per gepubliceerde bet is dit één matchDetails-
verzoek (mediaan 0,15 s, §4) plus de daglijsten van het venster rond de rundag, die gedeeld worden
over alle bets. Op een dag met vijf bets is dat ruim onder de seconde aan wachttijd.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta, timezone

from scripts import fotmob, teamnames

#: Hoeveel dagen vóór en ná de rundag naar andere duels van deze ploegen wordt gekeken. Zeven
#: dekt de Europese speelronde aan beide kanten (een club speelt di/wo en daarna za/zo) plus de
#: week erna, en dat is precies het venster waarin "drukke week" iets betekent.
WEEK_BEFORE = 7
WEEK_AFTER = 7

#: Toernooien die als "Europees" gelden in het weekoverzicht. De namen komen uit de Fotmob-
#: daglijst, waar het veld `name` per competitie staat.
EUROPEAN = ("Champions League", "Europa League", "Conference League", "Europa Conference League",
            "UEFA Super Cup", "Intercontinental Cup", "Club World Cup")


@dataclass
class Meeting:
    """Één eerdere ontmoeting, met wat een doelpuntenmarkt eruit wil weten."""
    date: str = ""
    home: str = ""
    away: str = ""
    hg: int = 0
    ag: int = 0
    competition: str = ""

    @property
    def total(self) -> int:
        return self.hg + self.ag

    @property
    def btts(self) -> bool:
        return self.hg > 0 and self.ag > 0

    @property
    def score(self) -> str:
        return f"{self.hg}–{self.ag}"


def _int(x) -> int | None:
    try:
        return int(str(x).strip())
    except (TypeError, ValueError):
        return None


def head_to_head(details: dict, *, limit: int = 6) -> dict:
    """De onderlinge balans en de laatste ontmoetingen, met totaal en BTTS per duel.

    De balans komt uit `h2h.summary` ([thuiswinst, gelijk, uitwinst] vanuit het perspectief van
    de thuisploeg van VANDAAG). De duels zelf staan in `h2h.matches`, nieuwste eerst.
    """
    h = ((details.get("content") or {}).get("h2h") or {})
    summary = h.get("summary") or []
    uit = {"balans": list(summary) if len(summary) == 3 else None, "duels": []}
    meetings: list[Meeting] = []
    for m in (h.get("matches") or [])[:limit]:
        st = m.get("status") or {}
        score = (st.get("scoreStr") or "").replace(" ", "")
        if "-" not in score:
            continue
        hg, ag = (_int(x) for x in score.split("-", 1))
        if hg is None or ag is None:
            continue
        meetings.append(Meeting(
            date=(st.get("utcTime") or "")[:10],
            home=((m.get("home") or {}).get("name") or "").strip(),
            away=((m.get("away") or {}).get("name") or "").strip(),
            hg=hg, ag=ag,
            competition=(m.get("tournament") or {}).get("name") or m.get("leagueName") or ""))
    uit["duels"] = [{**asdict(x), "total": x.total, "btts": x.btts, "score": x.score}
                    for x in meetings]
    if meetings:
        uit["samenvatting"] = {
            "n": len(meetings),
            "doelpunten_per_duel": round(sum(x.total for x in meetings) / len(meetings), 2),
            "btts": sum(1 for x in meetings if x.btts),
            "totalen": [x.total for x in meetings],
        }
    return uit


def insights(details: dict) -> dict:
    """Fotmob's eigen voorbeschouwingsregels, GESPLITST PER PLOEG.

    Elke regel draagt een `teamId` en een `type` (`team` of `player`), en met de ploeg-id's uit
    `general` zijn ze dus aan de juiste ploeg toe te wijzen. Dat is geen luxe: de regels komen in
    één vlakke lijst binnen, eerst de thuisploeg en dan de uitploeg, en wie dat op volgorde raadt
    schrijft vroeg of laat "Straatsburg heeft zijn laatste vijf niet verloren" terwijl dat over
    PSG ging. Gemeten op Strasbourg – PSG: drie regels op id 9848 (thuis) en drie op 9847 (uit).

    De tekst is Engels en blijft Engels: dit is een citaat uit de bron, en een vertaalde variant
    is niet meer tegen die bron te controleren. De voorbeschouwing van §6c schrijft hem in gewone
    taal om — dát is de plek voor Nederlands.
    """
    f = ((details.get("content") or {}).get("matchFacts") or {})
    g = details.get("general") or {}
    ids = {str((g.get("homeTeam") or {}).get("id") or ""): "home",
           str((g.get("awayTeam") or {}).get("id") or ""): "away"}
    rijen = f.get("insights") or f.get("previewQAData") or []
    uit: dict = {"regels": [], "home": [], "away": []}
    for r in rijen:
        if isinstance(r, str):
            uit["regels"].append({"tekst": r, "team": None, "soort": None})
            continue
        if not isinstance(r, dict):
            continue
        t = r.get("text") or r.get("title") or r.get("insight")
        if not t:
            continue
        rol = ids.get(str(r.get("teamId") or ""))
        rij = {"tekst": str(t), "team": rol, "soort": r.get("type")}
        uit["regels"].append(rij)
        if rol:
            uit[rol].append(rij)
    return uit


def top_players(details: dict) -> dict:
    """De best beoordeelde spelers per ploeg, voor een naam in de lopende tekst.

    De rating staat in `value` en soms in `rating`; die eerste gaat voor, net als in
    `dossier.py`. **Een rij zonder naam wordt overgeslagen**, en dat is geen defensieve
    overdrijving: bij Strasbourg – PSG bestaat `homeTopPlayers` wél maar zijn de rijen LEEG
    (`{}`). Zonder die controle komt er `{"name": null}` in de run-state en zet een volgende
    voorbeschouwing een speler zonder naam in de tekst. De bron geeft hier dus niets, en dat is
    iets anders dan dat de ploeg geen uitblinkers heeft.
    """
    f = ((details.get("content") or {}).get("matchFacts") or {})
    tp = f.get("topPlayers") or {}
    uit = {}
    for key, rol in (("homeTopPlayers", "home"), ("awayTopPlayers", "away")):
        spelers = []
        for s in (tp.get(key) or [])[:3]:
            if not isinstance(s, dict) or not s.get("name"):
                continue
            r = s.get("value")
            if r is None:
                r = s.get("rating")
            spelers.append({"name": s.get("name"),
                            "rating": (r.get("num") if isinstance(r, dict) else r)})
        if spelers:
            uit[rol] = spelers
    return uit


def weather(details: dict) -> dict:
    """Temperatuur, wind en neerslag.

    LET OP HET PAD: dit staat op `content.weather` en NIET op `content.matchFacts.weather`. De
    eerste versie van dit bestand keek op de tweede plek en gaf stilzwijgend een leeg blok terug —
    geen foutmelding, alleen niets, dezelfde faalvorm die in deze repo al vier keer geld heeft
    gekost. `dossier.py` deed het al goed; dat had de eerste aanwijzing moeten zijn.
    """
    w = (details.get("content") or {}).get("weather") or {}
    velden = ("temperature", "windSpeed", "windDirectionCardinal", "precipitation",
              "precipChance", "cloudCover", "description")
    return {k: w.get(k) for k in velden if w.get(k) is not None}


def week_around(day: date, teams: dict[str, str], *, before: int = WEEK_BEFORE,
                after: int = WEEK_AFTER, fixtures: dict | None = None) -> dict:
    """Wat deze twee ploegen vóór en ná de rundag spelen, met de Europese duels apart.

    `teams` is `{"home": naam, "away": naam}`. `fixtures` mag een al opgehaalde
    `{datum: daglijst}` zijn, zodat meerdere wedstrijden van dezelfde dag die lijsten delen.

    Dit is de enige manier om "drukke week" hard te maken. Rustdagen (§1c) zeggen hoe lang de
    ploeg niet speelde; ze zeggen niet dat het vorige duel een uitwedstrijd in de Champions
    League was, en ze zeggen al helemaal niets over wat er dinsdag wacht.
    """
    gezocht = {rol: teamnames.norm(naam) for rol, naam in teams.items()}
    fixtures = {} if fixtures is None else fixtures
    uit = {rol: {"ervoor": [], "erna": []} for rol in teams}
    for off in range(-before, after + 1):
        if off == 0:
            continue
        d = day + timedelta(days=off)
        if d not in fixtures:
            try:
                fixtures[d] = fotmob.fetch_fixtures(d)
            except Exception:
                fixtures[d] = {}
        for lg in (fixtures[d].get("leagues") or []):
            comp = lg.get("name") or ""
            for m in (lg.get("matches") or []):
                h = ((m.get("home") or {}).get("name") or "").strip()
                a = ((m.get("away") or {}).get("name") or "").strip()
                nh, na = teamnames.norm(h), teamnames.norm(a)
                for rol, naam in gezocht.items():
                    if naam not in (nh, na):
                        continue
                    st = m.get("status") or {}
                    rij = {"date": d.isoformat(), "competition": comp,
                           "home": h, "away": a,
                           "thuis": naam == nh,
                           "score": st.get("scoreStr") if st.get("finished") else None,
                           "kickoff_utc": st.get("utcTime"),
                           "europees": any(e.lower() in comp.lower() for e in EUROPEAN)}
                    uit[rol]["ervoor" if off < 0 else "erna"].append(rij)
    for rol in uit:
        uit[rol]["ervoor"].sort(key=lambda r: r["date"])
        uit[rol]["erna"].sort(key=lambda r: r["date"])
        uit[rol]["europees_ervoor"] = [r for r in uit[rol]["ervoor"] if r["europees"]]
        uit[rol]["europees_erna"] = [r for r in uit[rol]["erna"] if r["europees"]]
    return uit


def match_block(match_id: int, day: date, home: str, away: str, *,
                fixtures: dict | None = None) -> dict:
    """Het volledige voorbeschouwingsblok voor één duel, klaar voor `data/run-state/`."""
    details = fotmob.fetch_match_details(match_id)
    return {
        "match_id": match_id,
        "h2h": head_to_head(details),
        "insights": insights(details),
        "top_players": top_players(details),
        "weather": weather(details),
        "week": week_around(day, {"home": home, "away": away}, fixtures=fixtures),
        "_noot": ("Materiaal voor de voorbeschouwing van §6c. Niets hiervan gaat in my_prob of "
                  "prob_sources (§2, §4): insights is andermans redactie en de rest is historie."),
    }


# --------------------------------------------------------------------- zelftest

def _selftest() -> int:
    """Geen netwerk: de drie parsers op een verzonnen respons."""
    fouten = []

    def eis(naam, gekregen, verwacht):
        if gekregen != verwacht:
            fouten.append(f"{naam}: {gekregen!r} != {verwacht!r}")

    details = {"content": {
        "h2h": {"summary": [2, 5, 12], "matches": [
            {"status": {"utcTime": "2026-02-01T20:00:00Z", "finished": True, "scoreStr": "1 - 2"},
             "home": {"name": "Strasbourg"}, "away": {"name": "Paris Saint-Germain"},
             "tournament": {"name": "Ligue 1"}},
            {"status": {"utcTime": "2025-10-17T19:00:00Z", "finished": True, "scoreStr": "3 - 3"},
             "home": {"name": "Paris Saint-Germain"}, "away": {"name": "Strasbourg"},
             "tournament": {"name": "Ligue 1"}},
            {"status": {"utcTime": "2025-05-03T19:00:00Z", "finished": True, "scoreStr": "2 - 1"},
             "home": {"name": "Strasbourg"}, "away": {"name": "Paris Saint-Germain"},
             "tournament": {"name": "Ligue 1"}},
            # een duel zonder bruikbare stand hoort te worden overgeslagen, niet op 0–0 te komen
            {"status": {"utcTime": "2024-01-01T19:00:00Z", "finished": False, "scoreStr": None},
             "home": {"name": "Strasbourg"}, "away": {"name": "Paris Saint-Germain"}},
        ]},
        "weather": {"temperature": 13, "windSpeed": 3, "windDirectionCardinal": "NNE",
                    "precipitation": 0},
        "matchFacts": {
            "insights": [
                {"teamId": 9848, "type": "team",
                 "text": "Have scored 11 goals in their last 5 matches"},
                {"teamId": 9848, "type": "team",
                 "text": "Haven't kept a clean sheet in 20 matches"},
                {"teamId": 9847, "type": "team", "text": "Haven't lost in 5 matches"},
            ],
            "topPlayers": {"homeTopPlayers": [{"name": "Amo-Ameyaw", "value": {"num": 7.4}}],
                           "awayTopPlayers": [{"name": "Dembélé", "value": 8.1}]},
        },
    }, "general": {"homeTeam": {"id": 9848}, "awayTeam": {"id": 9847}}}

    h = head_to_head(details)
    eis("balans", h["balans"], [2, 5, 12])
    eis("aantal duels", len(h["duels"]), 3)
    eis("totalen", h["samenvatting"]["totalen"], [3, 6, 3])
    eis("btts", h["samenvatting"]["btts"], 3)
    eis("doelpunten per duel", h["samenvatting"]["doelpunten_per_duel"], 4.0)
    eis("score-notatie", h["duels"][0]["score"], "1–2")

    i = insights(details)
    eis("insights n", len(i["regels"]), 3)
    eis("insights dict-vorm gelezen", i["regels"][1]["tekst"],
        "Haven't kept a clean sheet in 20 matches")
    # Splitsen op teamId en NIET op volgorde: id 9848 is thuis, 9847 is uit.
    eis("insights thuis", [r["tekst"] for r in i["home"]],
        ["Have scored 11 goals in their last 5 matches",
         "Haven't kept a clean sheet in 20 matches"])
    eis("insights uit", [r["tekst"] for r in i["away"]], ["Haven't lost in 5 matches"])
    eis("soort meegenomen", i["home"][0]["soort"], "team")

    t = top_players(details)
    eis("topspeler thuis", t["home"][0]["name"], "Amo-Ameyaw")
    eis("rating uit `value`", t["home"][0]["rating"], 7.4)
    eis("rating als getal", t["away"][0]["rating"], 8.1)
    # Een LEGE rij (die de bron bij Strasbourg - PSG werkelijk teruggaf) mag niet als speler
    # zonder naam in de run-state belanden.
    eis("lege rij overgeslagen", top_players(
        {"content": {"matchFacts": {"topPlayers": {"homeTopPlayers": [{}, {}]}}}}), {})

    # `precipitation: 0` HOORT te blijven staan: nul millimeter regen is "het is droog", en dat
    # is informatie. Daarom filtert `weather` op `is not None` en niet op waarheid — met een
    # valsheidstest zou een droge wedstrijd niet te onderscheiden zijn van een ontbrekende meting.
    eis("weer van content.weather", weather(details),
        {"temperature": 13, "windSpeed": 3, "windDirectionCardinal": "NNE", "precipitation": 0})
    eis("weer NIET van matchFacts", weather(
        {"content": {"matchFacts": {"weather": {"temperature": 99}}}}), {})

    # Een leeg blok mag geen uitzondering geven: niet elk duel heeft h2h of insights.
    leeg = {"content": {}}
    eis("leeg h2h", head_to_head(leeg)["duels"], [])
    eis("leeg h2h balans", head_to_head(leeg)["balans"], None)
    eis("leeg insights", insights(leeg)["regels"], [])
    eis("leeg insights per kant", insights(leeg)["home"], [])
    eis("leeg topspelers", top_players(leeg), {})

    # week_around zonder netwerk: lege daglijsten meegeven en kijken of de vorm klopt.
    w = week_around(date(2026, 10, 17), {"home": "Strasbourg", "away": "Paris Saint-Germain"},
                    before=1, after=1,
                    fixtures={date(2026, 10, 16): {}, date(2026, 10, 18): {}})
    eis("week rollen", sorted(w), ["away", "home"])
    eis("week leeg", w["home"]["ervoor"], [])
    eis("europees afgeleid", w["away"]["europees_erna"], [])

    # Een Europees duel in de daglijst hoort als europees te worden gemarkeerd, en een
    # accentverschil in de naam mag de koppeling niet breken (teamnames.norm, niet _fold).
    fx = {date(2026, 10, 14): {"leagues": [{"name": "Champions League", "matches": [
        {"home": {"name": "Manchester City"}, "away": {"name": "Paris Saint-Germain"},
         "status": {"utcTime": "2026-10-14T19:00:00Z", "finished": True, "scoreStr": "2 - 4"}}]}]}}
    w2 = week_around(date(2026, 10, 17), {"away": "Paris Saint-Germain"},
                     before=3, after=0, fixtures={**fx, date(2026, 10, 15): {},
                                                  date(2026, 10, 16): {}})
    eis("europees ervoor gevonden", len(w2["away"]["europees_ervoor"]), 1)
    eis("uitwedstrijd herkend", w2["away"]["ervoor"][0]["thuis"], False)
    eis("uitslag meegenomen", w2["away"]["ervoor"][0]["score"], "2 - 4")

    for f in fouten:
        print("FOUT:", f)
    print(f"{27 - len(fouten)} van 27 controles goed.")
    return 1 if fouten else 0


if __name__ == "__main__":
    import sys
    if "selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
