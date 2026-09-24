import json, datetime as dt
from scripts import fotmob

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

out = {}
for day in ["2026-09-24", "2026-09-25"]:
    d = dt.date.fromisoformat(day)
    fx = fotmob.fetch_fixtures(d)
    leagues = fx.get("leagues", [])
    print(f"=== {day}: {len(leagues)} competities, {sum(len(l.get('matches',[])) for l in leagues)} wedstrijden")
    byid = {}
    for l in leagues:
        pid = l.get("primaryId") or l.get("id")
        byid[pid] = l
    for name, lid in RUNLIST.items():
        l = byid.get(lid)
        if l:
            ms = l.get("matches", [])
            print(f"  HIT {name} (id {lid}): {len(ms)} duels")
            for m in ms:
                print("     ", m.get("home",{}).get("name"), "-", m.get("away",{}).get("name"), m.get("status",{}).get("utcTime"))
            out.setdefault(day, {})[name] = [
                {"id": m.get("id"), "home": m.get("home",{}).get("name"), "away": m.get("away",{}).get("name"),
                 "utc": m.get("status",{}).get("utcTime"), "league_id": lid,
                 "home_id": m.get("home",{}).get("id"), "away_id": m.get("away",{}).get("id")}
                for m in ms]
    # also dump all league names/ids for audit
    out.setdefault("_all_"+day, sorted([(l.get('primaryId') or l.get('id'), l.get('ccode'), l.get('name'), len(l.get('matches',[]))) for l in leagues]))
json.dump(out, open("tmp-run/rb24_fx.json","w"), ensure_ascii=False, indent=1)
print("written")
