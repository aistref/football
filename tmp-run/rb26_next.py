"""Wanneer speelt elke competitie uit de runlijst weer? Voor de dekkingsnotities van §6c.

Scant de Fotmob-daglijsten vooruit en noteert het eerstvolgende duel per competitie. Geen
credits, alleen Fotmob.
"""
import datetime as dt, json
from scripts import fotmob
from scripts.runwindow import kickoff_nl

RUNLIST = {
 122: "Czech First League (CZE)", 135: "Greek Super League (GRE)", 59: "Eliteserien (NOR)",
 67: "Allsvenskan (SWE)", 252: "Croatian HNL (CRO)", 212: "Hungarian NB I (HUN)",
 189: "Romanian SuperLiga (ROU)", 140: "Segunda División (ESP)", 56: "Serie B (ITA)",
 146: "2. Bundesliga (GER)", 69: "Swiss Super League (SUI)", 38: "Austrian Bundesliga (AUT)",
 111: "Keuken Kampioen Divisie (NED)", 108: "English League One (ENG)",
 109: "English League Two (ENG)", 130: "MLS (USA)", 268: "Série A (BRA)",
}

found = {}
start = dt.date(2026, 9, 27)
for i in range(18):
    d = start + dt.timedelta(days=i)
    if len(found) == len(RUNLIST):
        break
    try:
        fx = fotmob.fetch_fixtures(d)
    except Exception as e:
        print(f"  {d}: {type(e).__name__}: {e}")
        continue
    for l in fx.get("leagues", []) or []:
        lid = l.get("primaryId") or l.get("id")
        if lid in RUNLIST and RUNLIST[lid] not in found:
            ms = [m for m in (l.get("matches") or []) if (m.get("status") or {}).get("utcTime")]
            if not ms:
                continue
            ms.sort(key=lambda m: m["status"]["utcTime"])
            m0 = ms[0]
            found[RUNLIST[lid]] = {
                "datum": d.isoformat(), "aantal": len(ms),
                "eerste": f"{m0['home']['name']} – {m0['away']['name']}",
                "aftrap_nl": kickoff_nl(m0["status"]["utcTime"]),
                "utc": m0["status"]["utcTime"]}

for name in RUNLIST.values():
    v = found.get(name)
    print(f"{name:32s} " + (f"{v['datum']} ({v['aantal']} duels) — {v['eerste']} {v['aftrap_nl']} NL"
                            if v else "geen duel binnen 18 dagen"))
json.dump(found, open("tmp-run/rb26_next.json", "w"), ensure_ascii=False, indent=1)
