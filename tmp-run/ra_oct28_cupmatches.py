"""Run A, 28 okt 2026 — de drie bekers die vandaag spelen, uit de Fotmob-daglijst.

**Dit is de bevinding van vandaag en de reden dat dit script bestaat.** De vijf bekers van
`prompts/run-a.md` hebben geen `fotmob_id` in `data/coverage.json`, dus `runwindow.matches_for_run`
kan ze niet filteren en elke run van oktober heeft ze langs BetExplorer gedaan
(`ra_oct28_cups.py`). Vandaag levert die route 22 duels in het inzetvenster — en de Fotmob-daglijst
van 28 oktober heeft ze **alle drie gewoon staan**:

    133  ENG  EFL Cup       5 duels     -> League Cup (ENG)
    209  GER  DFB Pokal     8 duels     -> DFB Pokal (GER)
    235  NED  KNVB Cup      9 duels     -> KNVB Beker (NED)

Dezelfde aantallen als BetExplorer (5, 8, 9), dus de twee bronnen zijn het eens. Het gat zat niet
in de bron maar in de administratie: zonder id in `coverage.json` kijkt de daglijstfilter er niet
naar. Dat is de stille faalvorm van §6b-5b — een controle die groen staat omdat ze één rij niet
meet — en het kostte op 6 oktober vier van de vijf FA Cup-duels, omdat die langs BetExplorer wél
binnenkwamen maar zonder `match_id` en dus zonder context, opstelling en poort 7.

Via de daglijst komen ze mét `match_id`, `home_id`, `away_id` en aftrap in UTC, dus precies zoals
de competitieduels. `primaryId` is de basisdivisie uit `promotion.CUP_BASE` (§4, "In een beker ligt
de basis per WEDSTRIJD"): die bepaalt alleen het competitieniveau waarop genormaliseerd wordt, en
`shared_lower_division` mag dat in de analyse per wedstrijd overrulen.
"""
import json
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from scripts import fotmob

DAY = date(2026, 10, 28)
NL = ZoneInfo("Europe/Amsterdam")

# runlijstnaam -> (fotmob daglijst-id, basisdivisie-id (CUP_BASE), seizoen vorig/huidig,
#                  betexplorer-url, sportkey)
CUPS = {
 "League Cup (ENG)": (133, 47, "2025/2026", "2026/2027",
                      "https://www.betexplorer.com/football/england/efl-cup/", None),
 "DFB Pokal (GER)":  (209, 54, "2025/2026", "2026/2027",
                      "https://www.betexplorer.com/football/germany/dfb-pokal/",
                      "soccer_germany_dfb_pokal"),
 "KNVB Beker (NED)": (235, 57, "2025/2026", "2026/2027",
                      "https://www.betexplorer.com/football/netherlands/knvb-beker/", None),
}

# Het inzetvenster van §3 Stage 1: [08:00 NL op de rundag, 08:00 NL een dag later).
START = datetime.combine(DAY, datetime.min.time(), tzinfo=NL).replace(hour=8)
END = START + timedelta(days=1)

days = [DAY, DAY + timedelta(days=1)]
raw = {d: fotmob.fetch_fixtures(d) for d in days}

out = {}
for name, (lid, base_id, s_prev, s_cur, bx, key) in CUPS.items():
    ms = []
    seen = set()
    for d in days:
        for lg in raw[d].get("leagues", []) or []:
            if (lg.get("primaryId") or lg.get("id")) != lid:
                continue
            for m in lg.get("matches", []) or []:
                mid = m.get("id")
                if mid in seen:
                    continue
                st = m.get("status", {}) or {}
                utc = st.get("utcTime")
                if not utc:
                    continue
                ko = datetime.fromisoformat(utc.replace("Z", "+00:00"))
                if not (START <= ko.astimezone(NL) < END):
                    continue
                seen.add(mid)
                ms.append({"match_id": mid,
                           "home": (m.get("home") or {}).get("name"),
                           "away": (m.get("away") or {}).get("name"),
                           "home_id": (m.get("home") or {}).get("id"),
                           "away_id": (m.get("away") or {}).get("id"),
                           "kickoff_utc": utc,
                           "kickoff_nl": str(ko.astimezone(NL)),
                           "source_day": d.isoformat(),
                           "playable": True,
                           "cup_round": lg.get("name")})
    ms.sort(key=lambda r: r["kickoff_utc"])
    out[name] = {"status": "?" if ms else "GEEN WEDSTRIJD", "primaryId": base_id,
                 "betexplorer": bx, "sportkey": key, "understat": None,
                 "s_prev": s_prev, "s_cur": s_cur, "crossborder": False,
                 "cup": True, "fotmob_daglijst_id": lid, "matches": ms}
    print(f"{name:20s} daglijst-id {lid:5d}  {len(ms)} duels in het venster")
    for m in ms:
        print(f"   {m['kickoff_nl'][11:16]} NL  {m['home']} - {m['away']}  (id {m['match_id']})")

json.dump({"day": DAY.isoformat(), "cups": out},
          open("tmp-run/ra_oct28_cupmatches.json", "w"), ensure_ascii=False, indent=1)
print("\ntotaal bekerduels in het venster:", sum(len(v["matches"]) for v in out.values()))
