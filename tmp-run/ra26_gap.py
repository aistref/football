"""Run A, 26 sep 2026 — twee losse eindjes van de bevestiging (§3 Stage 1: meerdere bronnen).

1. De drie bekers zonder BetExplorer-URL in `ra26_bevestiging.py` (FA Cup, KNVB Beker, DFB Pokal)
   krijgen hier alsnog een tweede bron, zodat de lege dag niet voor 18 van de 21 competities met
   twee bronnen vaststaat en voor 3 met één.
2. De eerstvolgende speeldag wordt óók op Fotmob nagelopen, niet alleen op BetExplorer, zodat het
   getal '9 oktober' uit twee bronnen komt in plaats van uit één.
"""
import json
from datetime import date, timedelta
from scripts import betexplorer, fotmob

DAY = date(2026, 9, 26)

CUPS = {
 "FA Cup (ENG)":     "https://www.betexplorer.com/football/england/fa-cup/",
 "KNVB Beker (NED)": "https://www.betexplorer.com/football/netherlands/knvb-beker/",
 "DFB Pokal (GER)":  "https://www.betexplorer.com/football/germany/dfb-pokal/",
}
stamp = DAY.strftime("%d.%m.")
cups = {}
for name, url in CUPS.items():
    try:
        fx = betexplorer.fetch_league_fixtures(url)
        times = sorted({f.when for f in fx if f.when})
        today = [f for f in fx if f.is_today or (f.when or "").startswith(stamp)]
        cups[name] = {"n": len(fx), "vandaag": len(today), "eerste": times[:2]}
        print(f"{name:20s} {len(fx):3d} fixtures, vandaag {len(today)}, eerstvolgende {times[:2]}")
    except Exception as e:
        cups[name] = {"error": f"{type(e).__name__}: {e}"}
        print(f"{name:20s} FOUT {type(e).__name__}: {e}")

# --- 2. Fotmob-daglijsten tot en met 11 oktober, op de namen van de runlijst ---------
S = json.load(open("tmp-run/ra26_stage3.json"))
NAMES = {   # runlijstnaam -> (fotmob-daglijstnaam, ccode, aliassen)
 "Premier League (ENG)": ("Premier League", "ENG", ()),
 "Serie A (ITA)": ("Serie A", "ITA", ()),
 "La Liga (ESP)": ("LaLiga", "ESP", ("La Liga",)),
 "Bundesliga (GER)": ("Bundesliga", "GER", ()),
 "Ligue 1 (FRA)": ("Ligue 1", "FRA", ()),
 "Championship (ENG)": ("Championship", "ENG", ()),
 "Eredivisie (NED)": ("Eredivisie", "NED", ()),
 "Primeira Liga (POR)": ("Liga Portugal", "POR", ("Primeira Liga",)),
 "Belgian Pro League (BEL)": ("Pro League", "BEL", ("Belgian Pro League", "Jupiler Pro League")),
 "Süper Lig (TUR)": ("Super Lig", "TUR", ("Süper Lig",)),
 "Scottish Premiership (SCO)": ("Premiership", "SCO", ()),
 "Danish Superliga (DEN)": ("Superligaen", "DEN", ("Superliga",)),
 "Ekstraklasa (POL)": ("Ekstraklasa", "POL", ()),
 "UEFA Champions League": ("Champions League", "INT", ()),
 "UEFA Europa League": ("Europa League", "INT", ()),
 "UEFA Conference League": ("Conference League", "INT", ("Europa Conference League",)),
 "FA Cup (ENG)": ("FA Cup", "ENG", ()),
 "League Cup (ENG)": ("EFL Cup", "ENG", ("League Cup", "Carabao Cup")),
 "Coppa Italia (ITA)": ("Coppa Italia", "ITA", ()),
 "KNVB Beker (NED)": ("KNVB Beker", "NED", ()),
 "DFB Pokal (GER)": ("DFB Pokal", "GER", ()),
}
scan = {}
for i in range(16):
    d = DAY + timedelta(days=i)
    fx = fotmob.fetch_fixtures(d)
    hits = {}
    for name, (fm, cc, al) in NAMES.items():
        lg = fotmob.find_league(fx, fm, cc, al)
        if lg is not None:
            hits[name] = len(lg.get("matches", []) or [])
    scan[d.isoformat()] = hits
    print(f"{d}  {len(fx.get('leagues', []) or []):3d} competities op de daglijst  "
          f"runlijst: {sum(hits.values())} wedstrijd(en) in {len(hits)} competitie(s)"
          + (f"  {hits}" if hits else ""))

json.dump({"cups": cups, "scan": scan}, open("tmp-run/ra26_gap.json", "w"),
          ensure_ascii=False, indent=1)
eerste = [k for k, v in scan.items() if v]
print("\neerste dag met een runlijstwedstrijd volgens Fotmob:", eerste[0] if eerste else "geen binnen 16 dagen")
