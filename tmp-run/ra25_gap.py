"""Run A, 25 sep 2026 — hoe lang duurt deze lege periode nog?

Vijf dagen op rij nul wedstrijden in de hele runlijst is geen storing (Stage 2), maar "nul" zegt
niets over hoe lang het nog duurt. BetExplorer noemt 9–15 oktober als eerstvolgende speelronde;
dit script trekt dat na op de daglijsten van Fotmob, zodat het antwoord op twee bronnen staat en
het runrapport een datum kan noemen in plaats van een schouderophalen.
"""
import json
from datetime import date, timedelta
from scripts import fotmob

NAMES = {
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

START = date(2026, 9, 26)
DAYS = 21
first = {}
per_day = {}
for i in range(DAYS):
    d = START + timedelta(days=i)
    fx = fotmob.fetch_fixtures(d)
    hits = []
    for name, (fm, cc, al) in NAMES.items():
        lg = fotmob.find_league(fx, fm, cc, al)
        n = len(lg.get("matches") or []) if lg else 0
        if n:
            hits.append((name, n))
            first.setdefault(name, (d.isoformat(), n))
    per_day[d.isoformat()] = hits
    print(f"{d}  {sum(n for _, n in hits):3d} wedstrijden  " +
          ", ".join(f"{k} {n}" for k, n in hits))

print("\n--- eerste speeldag per competitie ---")
for name in NAMES:
    print(f"  {name:30s} {first.get(name, ('geen in dit venster', 0))[0]}")
json.dump({"first": first, "per_day": per_day},
          open("tmp-run/ra25_gap.json", "w"), ensure_ascii=False, indent=1)
