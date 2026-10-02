import json, sys
from datetime import date
sys.path.insert(0, '.')
from scripts import fotmob, runwindow

DAY = date(2026, 10, 2)
RUNLIST = {
 "Czech First League (CZE)": 122, "Greek Super League (GRE)": 135,
 "Eliteserien (NOR)": 59, "Allsvenskan (SWE)": 67, "Croatian HNL (CRO)": 252,
 "Hungarian NB I (HUN)": 212, "Romanian SuperLiga (ROU)": 189,
 "Segunda División (ESP)": 140, "Serie B (ITA)": 86, "2. Bundesliga (GER)": 146,
 "Swiss Super League (SUI)": 69, "Austrian Bundesliga (AUT)": 38,
 "Keuken Kampioen Divisie (NED)": 111, "English League One (ENG)": 108,
 "English League Two (ENG)": 109, "MLS (USA)": 130, "Série A (BRA)": 268,
}
days = runwindow.days_needed(DAY)
print("daglijsten:", days)
fx = {}
for d in days:
    fx[d] = fotmob.fetch_fixtures(d)
    n = sum(len(l.get("matches") or []) for l in fx[d].get("leagues", []))
    print("  ", d, n, "duels totaal in de daglijst")

per = runwindow.matches_for_run(DAY, fx, RUNLIST)
out = {}
for comp in RUNLIST:
    ms = per.get(comp) or []
    out[comp] = [dict(m.__dict__) for m in ms]
    if ms:
        print(comp, len(ms))
        for m in ms:
            print("    ", m.kickoff_utc, "NL", m.kickoff_nl, m.home, "-", m.away,
                  m.match_id, "bron-dag", str(m.source_day), "speelbaar" if m.playable else "NIET SPEELBAAR")
geen = [c for c in RUNLIST if not out[c]]
print("GEEN WEDSTRIJD (%d):" % len(geen), geen)
print("TOTAAL duels:", sum(len(v) for v in out.values()))
json.dump({k: [{kk: (str(vv) if kk == 'source_day' else vv) for kk, vv in m.items()} for m in v]
           for k, v in out.items()}, open("tmp-run/b2_matches.json", "w"), ensure_ascii=False, indent=1)
