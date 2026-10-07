"""Run C, 7 okt 2026 — lege runlijst: voortgangsbestand vullen."""
from datetime import date
from scripts.progress import load_or_start, mark, save
DAY = date(2026, 10, 7)
VENSTER = "[08:00 NL 7 okt, 08:00 NL 8 okt)"
TOEL = ("geen duel in het inzetvenster " + VENSTER + ". Fotmob-daglijsten van 7 en 8 okt: de enige "
        "INT-regels zijn USA – Canada, Mexico – Chile en Frans-Guyana – Belize (aftrap 02:00-04:30 NL "
        "op 7 okt, dus voor 08:00 en bij de run van 6 okt) en de ASEAN Club Championship (clubs, niet "
        "op de runlijst). BetExplorer bevestigt het: oefeninterlands alleen Mexico – Chile (03:30), "
        "CONCACAF NL, Gulf Cup, AFCON-kwal. en ASEAN Cup 0 rijen.")
st = load_or_start("c", DAY)
for name in ["Vriendschappelijke interlands (id 114)", "UEFA Nations League A (id 9806)",
             "UEFA Nations League B (id 9807)", "UEFA Nations League C (id 9808)",
             "UEFA Nations League D (id 9809)", "CONCACAF Nations League (id 9821)",
             "CAF Afrika Cup-kwalificatie (id 10608)", "Arabian Gulf Cup (id 329)",
             "FIFA ASEAN Cup (id 13287)"]:
    mark(st, name, {"status": "GEEN WEDSTRIJD", "matches": [], "toelichting": TOEL})
st["parameters"] = {"MAX_DEEP_ANALYSES": 40, "MAX_SHORTLIST": 3, "dagsoort": "wo",
                    "EDGE_THRESHOLD_LIGHT": 16.0}
st["uitgesloten_competities"] = ["ASEAN Club Championship A/B (clubs; 3 duels in venster)"]
st["stage1"] = {"venster": VENSTER, "wedstrijden_in_venster": 0, "afgekapt_door_max_deep": 0}
st["credits"] = {"plafond": 0, "uitgegeven": 0, "markten_gekocht": {}}
st["bets"] = 0
save(st)
print("ok")
