import json, sys
from datetime import datetime, timezone
sys.path.insert(0, '.')

results = json.load(open("tmp-run/c25_final.json"))

competitions = {}

def comp_status(matches):
    if not matches:
        return "GEEN WEDSTRIJD"
    tiers = {m["tier"] for m in matches}
    if tiers <= {"BUITEN_DATADEKKING"}:
        return "BUITEN DATADEKKING"
    return "GEANALYSEERD"

for comp in ["UEFA Nations League A (id 9806)", "UEFA Nations League B (id 9807)",
             "UEFA Nations League C (id 9808)", "CAF Afrika Cup-kwalificatie (id 10608)",
             "CONCACAF Nations League (id 9821)", "Vriendschappelijke interlands (id 114)",
             "FIFA ASEAN Cup (id 13287)"]:
    mlist = results.get(comp, [])
    st = comp_status(mlist)
    entry = {"status": st, "matches": mlist}
    if st == "BUITEN DATADEKKING":
        entry["note"] = "geen prijsbron — geen sportkey bij The Odds API, geen BetExplorer-pagina met koersen (fifa-asean-cup/asean-championship gaven 0 rijen mét prijs, alleen de Challenge Division-teams uit de vorige editie stonden er nog op)"
    competitions[comp] = entry

competitions["UEFA Nations League D (id 9809)"] = {
    "status": "GEEN WEDSTRIJD", "matches": [],
    "note": "geen enkele Grp.-regel met primaryId 9809 op de Fotmob-daglijst van 25 of 26 sep binnen het inzetvenster"}
competitions["Arabian Gulf Cup (id 329)"] = {
    "status": "GEEN WEDSTRIJD", "matches": [],
    "note": "Gulf Cup Grp. A (Kuwait–Iraq, Oman–Saudi Arabia) staat op de daglijst van 26 sep, "
            "aftrap 17:00/20:00 NL — dat valt NA 08:00 NL 26 sep en dus buiten het inzetvenster "
            "[08:00 NL 25 sep, 08:00 NL 26 sep) van deze run. Hoort bij de run van 26 september."}

state = {
    "run": "C", "date": "2026-09-25", "resumed_count": 0,
    "competitions": competitions,
    "completed": True,
    "duur": {"gestart": None, "afgerond": None, "minuten": None},  # invullen bij het wegschrijven
    "parameters": {
        "MAX_DEEP_ANALYSES": 55, "afkapping": 0, "MAX_SHORTLIST": 5,
        "MAX_LIGHT_IN_SHORTLIST": "n.v.t. voor Run C (scripts/toplist.py slaat de cap over)",
        "weging": "0.70 landenrating / 0.30 selectiewaarde",
        "poort8": "VERVALLEN per 2026-09-25 (sides.LAPSES_ON) — would_block nog wel vastgelegd, zie poort8_vervallen per duel",
        "herijking": "recalibrate.load_fit() a=1.030 b=0.019 (2346 gevallen t/m 18 sep 2026)",
    },
    "credits": {
        "gebruikt_geschat": 9,
        "quota_start": 18716,
        "quota_eind": 18707,
        "toelichting": "1 bulk-aanroep h2h+spreads+totals op soccer_uefa_nations_league (3 credits, dekt alle 8 NL-duels van vandaag); 3x btts+double_chance per wedstrijd (2 credits elk = 6) voor de drie NL-duels met een kandidaat-edge op de vrije markten (Turkiye–France, Poland–Bosnia and Herzegovina, Montenegro–Cyprus). BetExplorer (AFCON-kwal, CONCACAF NL, Friendlies) kost geen credits.",
        "markten_gekocht": {"soccer_uefa_nations_league": ["h2h", "spreads", "totals", "btts", "double_chance"]},
    },
    "uitgesloten_competities": {
        "Asian Games (id 9833)": "team namen bevatten U23 — jeugd, uitgesloten",
        "EURO U21 Qualification (id 10437)": "U21 — jeugd, uitgesloten (7 groepen, 15 duels gezien)",
        "Club Friendlies (id 489)": "clubteams (Rijeka – Union Berlin) — run-c.md: NIET gebruiken",
        "UEFA Women's Europa Cup (id 11129)": "Women — vrouwen, uitgesloten (en clubteams: FC Minsk – Fenerbahçe)",
        "Women's World Cup U20 (id 10369)": "Women + U20 — vrouwen en jeugd, uitgesloten",
    },
}

with open("tmp-run/c25_state.json", "w") as f:
    json.dump(state, f, indent=1, ensure_ascii=False)

n_bets = sum(1 for c in competitions.values() for m in c["matches"] if m.get("bet"))
n_analyzed = sum(1 for c in competitions.values() for m in c["matches"] if m["tier"] == "LIGHT")
n_buiten = sum(1 for c in competitions.values() for m in c["matches"] if m["tier"] == "BUITEN_DATADEKKING")
n_none = sum(1 for c in competitions.values() for m in c["matches"] if m["tier"] == "NONE")
print(f"bets={n_bets} analyzed(LIGHT)={n_analyzed} buiten_datadekking={n_buiten} none={n_none}")
