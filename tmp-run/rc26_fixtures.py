import json, sys
from datetime import date
from scripts import fotmob, runwindow

DAY = date(2026, 9, 26)
days = runwindow.days_needed(DAY)
print("days_needed:", days)

fixtures = {d: fotmob.fetch_fixtures(d) for d in days}

# Collect all INT ccode leagues across both days, group by primaryId
by_id = {}
for d, fx in fixtures.items():
    for lg in fx.get("leagues", []) or []:
        if lg.get("ccode") != "INT":
            continue
        pid = lg.get("primaryId")
        name = lg.get("name")
        matches = lg.get("matches", []) or []
        by_id.setdefault(pid, {"names": set(), "matches": []})
        by_id[pid]["names"].add(name)
        for m in matches:
            m["_source_day"] = d.isoformat()
            m["_league_name"] = name
        by_id[pid]["matches"].extend(matches)

print(f"\n{len(by_id)} distinct primaryId groups with ccode=INT across {days}\n")
for pid, info in sorted(by_id.items(), key=lambda kv: -len(kv[1]["matches"])):
    print(f"primaryId={pid}  n_matches={len(info['matches'])}  names={sorted(info['names'])}")
