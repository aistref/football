import json, datetime as dt
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

RUNLIST = {
 "Czech First League (CZE)": 122,
 "Greek Super League (GRE)": 135,
 "Eliteserien (NOR)": 59,
 "Allsvenskan (SWE)": 67,
 "Croatian HNL (CRO)": 252,
 "Hungarian NB I (HUN)": 212,
 "Romanian SuperLiga (ROU)": 189,
 "Segunda División (ESP)": 140,
 "Serie B (ITA)": 56,
 "2. Bundesliga (GER)": 146,
 "Swiss Super League (SUI)": 69,
 "Austrian Bundesliga (AUT)": 38,
 "Keuken Kampioen Divisie (NED)": 111,
 "English League One (ENG)": 108,
 "English League Two (ENG)": 109,
 "MLS (USA)": 130,
 "Série A (BRA)": 268,
}

DAY = dt.date(2026, 9, 25)
days = days_needed(DAY)
print("daglijsten nodig:", [d.isoformat() for d in days])

fixtures = {}
for d in days:
    fx = fotmob.fetch_fixtures(d)
    fixtures[d] = fx
    n = sum(len(l.get("matches", []) or []) for l in fx.get("leagues", []) or [])
    print(f"  {d}: {len(fx.get('leagues', []) or [])} competities, {n} wedstrijden")

per_comp = matches_for_run(DAY, fixtures, RUNLIST)

out = {}
tot = 0
for name, ms in per_comp.items():
    if not ms:
        continue
    tot += len(ms)
    print(f"HIT {name}: {len(ms)} duels")
    for m in ms:
        print(f"   {m.home} - {m.away}  {m.kickoff_nl} NL  (utc {m.kickoff_utc}, lijst {m.source_day}, speelbaar={m.playable})")
    out[name] = [m.as_dict() for m in ms]
print("TOTAAL duels in het inzetvenster:", tot)

# audit: alle competities op beide daglijsten
audit = {}
for d, fx in fixtures.items():
    audit[d.isoformat()] = sorted(
        [(l.get("primaryId") or l.get("id"), l.get("ccode"), l.get("name"), len(l.get("matches", []) or []))
         for l in fx.get("leagues", []) or []],
        key=lambda r: (r[1] or "", r[2] or ""))

json.dump({"day": DAY.isoformat(), "per_comp": out, "audit": audit},
          open("tmp-run/rb25_fx.json", "w"), ensure_ascii=False, indent=1)
print("written")
