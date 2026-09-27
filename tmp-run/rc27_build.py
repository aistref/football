"""Bouwt de volledige runlijst van Run C, 27 sep 2026."""
import json

by_id = json.load(open("tmp-run/rc27_by_id.json"))

COMP_LABEL = {
    "114": "Vriendschappelijke interlands",
    "9806": "UEFA Nations League A",
    "9807": "UEFA Nations League B",
    "9808": "UEFA Nations League C",
    "9809": "UEFA Nations League D",
    "9821": "CONCACAF Nations League",
    "10608": "CAF Afrika Cup-kwalificatie",
    "329": "Arabian Gulf Cup",
    "13287": "FIFA ASEAN Cup",
}
EXCLUDED_PIDS = {
    "489": "Club Friendlies — clubteams, niet landenteams (run-c.md: NIET gebruiken)",
    "10369": "Women's World Cup U20 — Women + U20",
    "10437": "EURO U21 Qualification — U21 (0 in venster)",
}

matches = {}
for pid, label in COMP_LABEL.items():
    info = by_id.get(pid, {"matches": []})
    in_win = [m for m in info["matches"] if m["in_window"]]
    matches[label] = in_win

print("=== Run C runlijst 27 sep 2026 (na uitsluiting jeugd/vrouwen/club) ===")
for label, ms in matches.items():
    print(f"\n{label}: {len(ms)} duel(en)")
    for m in ms:
        print(f"  {m['home']} - {m['away']}  {m['kickoff_nl']} NL  (source_day={m['source_day']})")

print("\n=== Uitgesloten ===")
for pid, reason in EXCLUDED_PIDS.items():
    info = by_id.get(pid, {"matches": []})
    in_win = [m for m in info["matches"] if m["in_window"]]
    print(f"{pid}: {reason} — {len(in_win)} duel(en) binnen het venster")

total = sum(len(v) for v in matches.values())
print(f"\nTotaal op de runlijst (voor datadekking): {total}")

json.dump(matches, open("tmp-run/rc27_matches.json", "w"), indent=1, ensure_ascii=False)
