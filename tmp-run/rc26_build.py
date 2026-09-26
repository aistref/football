"""Bouwt de volledige runlijst van Run C, 26 sep 2026, met odds gekoppeld per duel."""
import json, re, unicodedata
import sys
sys.path.insert(0, '.')
from scripts import betexplorer as bx

by_id = json.load(open("tmp-run/rc26_by_id.json"))

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
RUNLIST_PIDS = list(COMP_LABEL.keys())
EXCLUDED_PIDS = {
    "9833": "Asian Games — teamnamen bevatten U23",
    "10369": "Women's World Cup U20 — Women + U20",
    "10437": "EURO U21 Qualification — U21",
    "11129": "UEFA Women's Europa Cup — Women (en clubteams)",
    "489": "Club Friendlies — clubteams, niet landenteams (run-c.md: NIET gebruiken)",
}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


matches = {}
for pid, label in COMP_LABEL.items():
    info = by_id.get(pid, {"matches": []})
    in_win = [m for m in info["matches"] if m["in_window"]]
    matches[label] = in_win

print("=== Run C runlijst 26 sep 2026 (na uitsluiting jeugd/vrouwen) ===")
for label, ms in matches.items():
    print(f"\n{label}: {len(ms)} duel(en)")
    for m in ms:
        print(f"  {m['home']} - {m['away']}  {m['kickoff_nl']} NL  (source_day={m['source_day']})")

print("\n=== Uitgesloten (jeugd/vrouwen/club) ===")
for pid, reason in EXCLUDED_PIDS.items():
    info = by_id.get(pid, {"matches": []})
    in_win = [m for m in info["matches"] if m["in_window"]]
    print(f"{pid}: {reason} — {len(in_win)} duel(en) binnen het venster")

total = sum(len(v) for v in matches.values())
print(f"\nTotaal op de runlijst (voor datadekking): {total}")

json.dump(matches, open("tmp-run/rc26_matches.json", "w"), indent=1, ensure_ascii=False)
