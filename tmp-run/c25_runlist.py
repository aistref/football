import json, sys
from datetime import date
sys.path.insert(0, '.')
from scripts import fotmob, runwindow

DAY = date(2026, 9, 25)
days = runwindow.days_needed(DAY)
fixtures = {d: fotmob.fetch_fixtures(d) for d in days}

# Candidate ids with our chosen display names (run-c.md known ids)
CANDIDATES = {
    10608: "CAF Afrika Cup-kwalificatie (id 10608)",
    9821: "CONCACAF Nations League (id 9821)",
    13287: "FIFA ASEAN Cup (id 13287)",
    114: "Vriendschappelijke interlands (id 114)",
    329: "Arabian Gulf Cup (id 329)",
    9806: "UEFA Nations League A (id 9806)",
    9807: "UEFA Nations League B (id 9807)",
    9808: "UEFA Nations League C (id 9808)",
    9809: "UEFA Nations League D (id 9809)",
}
EXCLUDED_SEEN = {
    9833: "Asian Games — U23-toernooi",
    489: "Club Friendlies — clubteams, run-c.md: NIET gebruiken",
    10437: "EURO U21 Qualification — U21",
    11129: "UEFA Women's Europa Cup — vrouwen + clubteams",
    10369: "Women's World Cup U20 — vrouwen + U20",
}

def all_league_entries(fx):
    return fx.get("leagues") or []

result = {name: [] for name in CANDIDATES.values()}
excluded_report = []
seen_ids = set()

for source_day in days:
    fx = fixtures.get(source_day)
    if not fx:
        continue
    for league in all_league_entries(fx):
        lid = league.get("primaryId") or league.get("id")
        try:
            lid = int(lid)
        except (TypeError, ValueError):
            continue
        lname = league.get("name")
        ccode = league.get("ccode")
        if lid in EXCLUDED_SEEN:
            for m in league.get("matches", []) or []:
                excluded_report.append((lname, lid, (m.get("home") or {}).get("name"), (m.get("away") or {}).get("name"), (m.get("status") or {}).get("utcTime")))
            continue
        if lid not in CANDIDATES:
            continue
        name = CANDIDATES[lid]
        for m in league.get("matches", []) or []:
            status = m.get("status") or {}
            if status.get("cancelled"):
                continue
            utc = status.get("utcTime")
            if not utc:
                continue
            if not runwindow.belongs_to_run(utc, DAY):
                continue
            mid = m.get("id")
            key = (name, mid)
            if key in seen_ids:
                continue
            seen_ids.add(key)
            result[name].append({
                "competition": name, "league_id": lid, "group": lname,
                "match_id": mid,
                "home": (m.get("home") or {}).get("name"),
                "away": (m.get("away") or {}).get("name"),
                "home_id": (m.get("home") or {}).get("id"),
                "away_id": (m.get("away") or {}).get("id"),
                "kickoff_utc": utc, "kickoff_nl": runwindow.kickoff_nl(utc),
                "source_day": source_day.isoformat(),
                "playable": runwindow.playable(utc),
            })

for name in result:
    result[name].sort(key=lambda r: r["kickoff_utc"])

print("=== INBEGREPEN TOERNOOIEN ===")
for name, matches in result.items():
    print(f"\n{name}: {len(matches)} duels")
    for m in matches:
        print(f"   {m['home']} - {m['away']}  {m['kickoff_nl']} NL  (bron {m['source_day']}, groep {m['group']})")

print("\n=== UITGESLOTEN (gezien, niet meegenomen) ===")
for lname, lid, h, a, utc in excluded_report:
    print(f"  id={lid} {lname}: {h} - {a}  {utc}")

with open("tmp-run/c25_runlist.json", "w") as f:
    json.dump(result, f, indent=1, ensure_ascii=False)
