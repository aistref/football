import json
from datetime import date
from scripts import fotmob, runwindow

DAY = date(2026, 10, 5)
days = runwindow.days_needed(DAY)
fixtures = {d: fotmob.fetch_fixtures(d) for d in days}
EXCLUDE_TERMS = ["women", "w.", "u17", "u19", "u20", "u21", "u23", "olympic"]
def is_excluded(name):
    n = (name or "").lower()
    return any(t in n for t in EXCLUDE_TERMS)
by_id = {}
for d, fx in fixtures.items():
    for lg in fx.get("leagues", []) or []:
        if lg.get("ccode") != "INT":
            continue
        pid = lg.get("primaryId"); name = lg.get("name")
        for m in lg.get("matches", []) or []:
            kickoff = m["status"]["utcTime"]
            rec = {"primaryId": pid, "league_name": name, "source_day": d.isoformat(),
                   "home": m["home"]["name"], "away": m["away"]["name"],
                   "home_id": m["home"]["id"], "away_id": m["away"]["id"], "match_id": m["id"],
                   "kickoff_utc": kickoff, "kickoff_nl": runwindow.kickoff_nl(kickoff),
                   "in_window": runwindow.belongs_to_run(kickoff, DAY, include_carry_over=False)}
            by_id.setdefault(pid, {"names": set(), "matches": []})
            by_id[pid]["names"].add(name); by_id[pid]["matches"].append(rec)
for pid, info in sorted(by_id.items(), key=lambda kv: (kv[0] is None, kv[0])):
    names = sorted(info["names"]); inw = [m for m in info["matches"] if m["in_window"]]
    print(f"\n{pid} {names} excl_name={any(is_excluded(n) for n in names)} total={len(info['matches'])} in_window={len(inw)}")
    for m in inw:
        print(f"   {m['home']} - {m['away']} {m['kickoff_nl']} src={m['source_day']}", "!!TEAM-EXCL" if is_excluded(m['home']) or is_excluded(m['away']) else "")
json.dump({str(k): v for k, v in by_id.items()}, open("tmp-run/rc05_by_id.json", "w"), default=str, indent=1)
