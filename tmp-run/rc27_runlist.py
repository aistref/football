import json
from datetime import date
from scripts import fotmob, runwindow

DAY = date(2026, 9, 27)
days = runwindow.days_needed(DAY)
fixtures = {d: fotmob.fetch_fixtures(d) for d in days}

EXCLUDE_TERMS = ["women", "w.", "u17", "u19", "u20", "u21", "u23", "olympic"]

def is_excluded(name):
    n = (name or "").lower()
    return any(t in n for t in EXCLUDE_TERMS)

by_id = {}
all_int_leagues = []
for d, fx in fixtures.items():
    for lg in fx.get("leagues", []) or []:
        if lg.get("ccode") != "INT":
            continue
        pid = lg.get("primaryId")
        name = lg.get("name")
        all_int_leagues.append((d, pid, name, len(lg.get("matches", []) or [])))
        for m in lg.get("matches", []) or []:
            kickoff = m["status"]["utcTime"]
            in_window = runwindow.belongs_to_run(kickoff, DAY, include_carry_over=False)
            rec = {
                "primaryId": pid,
                "league_name": name,
                "source_day": d.isoformat(),
                "home": m["home"]["name"],
                "away": m["away"]["name"],
                "home_id": m["home"]["id"],
                "away_id": m["away"]["id"],
                "match_id": m["id"],
                "kickoff_utc": kickoff,
                "kickoff_nl": runwindow.kickoff_nl(kickoff),
                "in_window": in_window,
            }
            by_id.setdefault(pid, {"names": set(), "matches": []})
            by_id[pid]["names"].add(name)
            by_id[pid]["matches"].append(rec)

print("=== all INT-ccode league entries seen (day, primaryId, name, n_matches) ===")
for row in sorted(all_int_leagues, key=lambda r: (str(r[0]), r[1] or 0)):
    print(row)

print("\n=== per primaryId, matches within betting window ===")
for pid, info in sorted(by_id.items(), key=lambda kv: (kv[0] is None, kv[0])):
    names = sorted(info["names"])
    in_win = [m for m in info["matches"] if m["in_window"]]
    excluded_name = any(is_excluded(n) for n in names)
    print(f"\nprimaryId={pid} names={names} excluded_by_name={excluded_name}")
    print(f"  total_matches={len(info['matches'])}  in_window={len(in_win)}")
    for m in in_win:
        print(f"    {m['home']} - {m['away']}  kickoff_nl={m['kickoff_nl']} source_day={m['source_day']} ({m['league_name']})")
        if is_excluded(m['home']) or is_excluded(m['away']):
            print(f"      !! team-naam bevat uitsluitingsterm: {m['home']} / {m['away']}")

with open("tmp-run/rc27_by_id.json", "w") as f:
    json.dump({str(k): v for k, v in by_id.items()}, f, default=str, indent=1)
