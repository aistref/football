"""Run A, 5 okt 2026 — Stage 6: voortgangsbestand vullen uit de Stage 1/2/3-meting."""
import json
from datetime import date, datetime, timezone
from scripts.progress import load_or_start, mark, save

DAY = date(2026, 10, 5)
st3 = json.load(open("tmp-run/ra_oct05_stage3.json"))

# eerstvolgende speeldag per competitie, uit de BetExplorer-fixturepagina (methode 2)
NEXT = {}
for name, v in st3["betexplorer"].items():
    eerste = (v or {}).get("eerste") or []
    if eerste:
        NEXT[name] = eerste[0]
    elif (v or {}).get("n") == 0:
        NEXT[name] = "geen ronde gepland op BetExplorer"
    else:
        NEXT[name] = "niet bepaald"

VENSTER = "[08:00 NL 5 okt, 08:00 NL 6 okt)"
TOEL = ("interlandperiode — geen duel in het inzetvenster {v}. Twee bronnen apart "
        "gecontroleerd: Fotmob-daglijsten van 5 en 6 okt en de BetExplorer-fixturepagina. "
        "Eerstvolgende speeldag: {n}.")

state = load_or_start("a", DAY)
state.setdefault("duur", {})
state["duur"].setdefault("gestart", "2026-10-05T02:15:00+00:00")

for name in st3["fixtures"]:
    mark(state, name, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "toelichting": TOEL.format(v=VENSTER, n=NEXT.get(name, "niet bepaald")),
    })

state["parameters"] = {
    "MAX_DEEP_ANALYSES": 40,
    "MAX_SHORTLIST": 3,
    "dagsoort": "ma (werkweek)",
    "EDGE_THRESHOLD_FULL": 8.0,
    "EDGE_THRESHOLD_LIGHT": 16.0,
    "poort8_bindt": "ja — vanaf 1 okt 2026 weer (sides.LAPSED_UNTIL = 2026-10-01)",
}
state["stage1"] = {
    "venster": "[2026-10-05T06:00Z, 2026-10-06T06:00Z) = [08:00 NL, 08:00 NL +1)",
    "bronnen": [
        "Fotmob daglijst 2026-10-05 (30 competities)",
        "Fotmob daglijst 2026-10-06 (58 competities)",
        "BetExplorer fixturepagina per competitie (21 van 21 opgevraagd)",
    ],
    "wedstrijden_in_venster": 0,
    "afgekapt_door_max_deep": 0,
    "fotmob_ids_gevonden": 0,
    "fotmob_ids_toelichting": (
        "0 van 21 — geen runlijstcompetitie staat in een van beide daglijsten. Dat is consistent "
        "met een lege kalender en niet met een kapotte koppeling: de daglijsten zelf kwamen "
        "normaal binnen (30 + 58 competities) en bevatten de interlandtoernooien die Run C "
        "behandelt."
    ),
}
state["bets"] = 0
save(state)
print("voortgangsbestand geschreven:", len(state["competitions"]), "competities")
print(json.dumps({k: v["toelichting"][-40:] for k, v in list(state["competitions"].items())[:3]},
                 ensure_ascii=False, indent=1))
