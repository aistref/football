import json, sys
from datetime import date
sys.path.insert(0, '.')
from scripts import fotmob, runwindow

DAY = date(2026, 9, 25)
days = runwindow.days_needed(DAY)
print("days_needed:", days)
fixtures = {d: fotmob.fetch_fixtures(d) for d in days}
for d in days:
    fx = fixtures[d]
    print(d, "leagues:", len(fx.get("leagues", [])) if isinstance(fx, dict) else type(fx))

# collect INT ccode leagues
out = {}
for d in days:
    fx = fixtures[d]
    leagues = fx.get("leagues") if isinstance(fx, dict) else None
    if not leagues:
        continue
    for lg in leagues:
        ccode = lg.get("ccode")
        if ccode == "INT":
            pid = lg.get("primaryId") or lg.get("id")
            name = lg.get("name")
            matches = lg.get("matches") or []
            out.setdefault((pid, name, d.isoformat()), []).extend(matches)

with open("tmp-run/c25_fx_dump.json", "w") as f:
    json.dump({f"{k[0]}|{k[1]}|{k[2]}": [
        {"id": m.get("id"), "home": (m.get("home") or {}).get("name"),
         "away": (m.get("away") or {}).get("name"),
         "status": m.get("status"), } for m in v
    ] for k, v in out.items()}, f, indent=1, default=str)

for (pid, name, d), matches in sorted(out.items(), key=lambda x: (x[0][1])):
    print(f"{d}  id={pid}  {name}  ({len(matches)} duels)")
    for m in matches:
        h = (m.get("home") or {}).get("name")
        a = (m.get("away") or {}).get("name")
        st = m.get("status") or {}
        print(f"    {h} - {a}   utcTime={st.get('utcTime')}")
