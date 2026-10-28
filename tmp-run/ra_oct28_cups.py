"""Run A, 28 okt 2026 — de vijf bekers van de runlijst, uit TWEE bronnen.

Waarom dit anders gaat dan op 27 oktober: toen stond hier dat de bekers "voor de Fotmob-daglijst
geen bron" zijn omdat ze geen `fotmob_id` in `data/coverage.json` hebben. Dat eerste is niet waar
— het id ontbreekt in de administratie, niet bij de bron. In de daglijst van vandaag staan drie
van de vijf er gewoon in, met `primaryId`:

    League Cup (ENG) -> 133 (Fotmob noemt hem "EFL Cup")
    DFB Pokal (GER)  -> 209
    KNVB Beker (NED) -> 235 ("KNVB Cup")

Dat is de betere bron, want ze levert `match_id`, de ploeg-id's en de aftrap in UTC — precies wat
Stage 4 en 5 nodig hebben en wat een BetExplorer-rij niet geeft. De id's gaan **niet** naar
`coverage.json` onder `fotmob_id`: `scripts/idcheck.py` eist van elk id daar een bruikbare stand
en een beker heeft er geen, dus dat zou elke run een vals alarm geven op precies de controle die
voor een stil verdwenen competitie is gebouwd. Ze gaan onder `notes`, zodat een volgende run ze
niet opnieuw hoeft te zoeken.

BetExplorer blijft ernaast staan, voor de twee bekers die vandaag niet in de daglijst voorkomen
(FA Cup, Coppa Italia). "Niet in de daglijst" mag nooit als `GEEN WEDSTRIJD` worden opgeschreven
zonder tweede bron — dat is het gat dat Run A op 6 oktober 2026 vijf duels kostte.
"""
import json, urllib.request
from datetime import date
from scripts import fotmob, betexplorer as bx
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 10, 28)

CUP_IDS = {"League Cup (ENG)": 133, "DFB Pokal (GER)": 209, "KNVB Beker (NED)": 235}

SLUGS = {
 "FA Cup (ENG)":      "https://www.betexplorer.com/football/england/fa-cup/",
 "League Cup (ENG)":  "https://www.betexplorer.com/football/england/efl-cup/",
 "Coppa Italia (ITA)":"https://www.betexplorer.com/football/italy/coppa-italia/",
 "KNVB Beker (NED)":  "https://www.betexplorer.com/football/netherlands/knvb-beker/",
 "DFB Pokal (GER)":   "https://www.betexplorer.com/football/germany/dfb-pokal/",
}

fixtures = {d: fotmob.fetch_fixtures(d) for d in days_needed(DAY)}
per_comp = matches_for_run(DAY, fixtures, CUP_IDS)

out = {}
for name, lid in CUP_IDS.items():
    ms = per_comp.get(name) or []
    out[name] = {"bron": "fotmob-daglijst", "fotmob_id": lid,
                 "status": "GEEN WEDSTRIJD" if not ms else "?",
                 "matches": [{"match_id": m.match_id, "home": m.home, "away": m.away,
                              "home_id": m.home_id, "away_id": m.away_id,
                              "kickoff_utc": m.kickoff_utc, "kickoff_nl": str(m.kickoff_nl),
                              "source_day": m.source_day.isoformat(), "playable": m.playable}
                             for m in ms]}
    print(f"{name:20s} fotmob id {lid}: {len(ms)} duels in het venster")
    for m in ms:
        print(f"   {m.home} - {m.away}  {m.kickoff_nl} NL (lijst {m.source_day}, speelbaar={m.playable})")

for name in ("FA Cup (ENG)", "Coppa Italia (ITA)"):
    out[name] = {"bron": "betexplorer", "fotmob_id": None, "status": "GEEN WEDSTRIJD", "matches": []}

# BetExplorer als tweede bron voor alle vijf, inclusief de drie die uit Fotmob komen.
for name, url in SLUGS.items():
    fu = url.rstrip("/") + "/fixtures/"
    raw = urllib.request.urlopen(urllib.request.Request(fu, headers=bx.HEADERS), timeout=30).read()
    text = raw.decode(errors="replace")
    carried, rijen = "", []
    for row in bx._FIX_ROW_RE.findall(text):
        w = bx._WHEN_RE.search(row)
        if w and w.group(1).strip() and w.group(1).strip() != "&nbsp;":
            carried = w.group(1).strip()
        tm = bx._TEAMS_RE.search(row)
        if tm:
            rijen.append({"home": tm.group(1), "away": tm.group(2), "when": carried})
    in_venster = [r for r in rijen if r["when"].startswith(("Today", "28.10.", "29.10."))]
    eerste = next((r["when"] for r in rijen if r["when"]), None)
    out[name]["betexplorer"] = {
        "slug": fu, "bytes": len(raw), "teamparen": len(rijen),
        "koersen": len(bx._ODDS_RE.findall(text)),
        "in_venster": in_venster, "eerste_ronde": eerste}
    print(f"BX {name:20s} {len(rijen):3d} teamparen, {len(in_venster)} in venster, "
          f"eerstvolgende ronde: {eerste}")

json.dump({"day": DAY.isoformat(), "cups": out},
          open("tmp-run/ra_oct28_cups.json", "w"), ensure_ascii=False, indent=1)
