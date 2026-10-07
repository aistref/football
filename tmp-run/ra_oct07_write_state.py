"""Run A, 7 okt 2026 — Stage 6: voortgangsbestand vullen uit Stage 1/2/3.

Lege runlijst: alle 21 competities op GEEN WEDSTRIJD, met per competitie de eerstvolgende
speeldag die de tweede fixturebron (BetExplorer) geeft, zodat de nul naleesbaar is.
"""
import json
from datetime import date
from scripts.progress import load_or_start, mark, save

DAY = date(2026, 10, 7)
st3 = json.load(open("tmp-run/ra_oct07_stage3.json"))

NEXT = {}
for name, v in st3["betexplorer"].items():
    eerste = (v or {}).get("eerste") or []
    if eerste:
        NEXT[name] = eerste[0]
    elif (v or {}).get("n") == 0:
        NEXT[name] = "geen ronde gepland op BetExplorer"
    else:
        NEXT[name] = "niet bepaald"

VENSTER = "[08:00 NL 7 okt, 08:00 NL 8 okt)"
TOEL = ("interlandperiode — geen duel in het inzetvenster {v}. Twee bronnen apart "
        "gecontroleerd: de Fotmob-daglijsten van 7 en 8 okt en de BetExplorer-fixturepagina. "
        "Eerstvolgende speeldag: {n}.")

state = load_or_start("a", DAY)
state.setdefault("duur", {})

for name in st3["fixtures"]:
    mark(state, name, {"status": "GEEN WEDSTRIJD", "matches": [],
                       "toelichting": TOEL.format(v=VENSTER, n=NEXT.get(name, "niet bepaald"))})

state["parameters"] = {
    "MAX_DEEP_ANALYSES": 40, "MAX_SHORTLIST": 3, "dagsoort": "wo (werkweek)",
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
    "poort8_bindt": "ja — vanaf 1 okt 2026 weer (sides.LAPSED_UNTIL = 2026-10-01)",
}
state["stage1"] = {
    "venster": "[2026-10-07T06:00Z, 2026-10-08T06:00Z) = [08:00 NL, 08:00 NL +1)",
    "bronnen": ["Fotmob daglijst 2026-10-07 (28 competities)",
                "Fotmob daglijst 2026-10-08 (20 competities)",
                "BetExplorer fixturepagina per competitie (21 van 21 opgevraagd)"],
    "wedstrijden_in_venster": 0,
    "wedstrijden_via_fotmob": 0,
    "wedstrijden_via_betexplorer": 0,
    "afgekapt_door_max_deep": 0,
    "fotmob_ids_gevonden": 0,
    "fotmob_ids_toelichting": (
        "0 van 21 — geen runlijstcompetitie staat in een van beide daglijsten. De daglijsten zelf "
        "kwamen normaal binnen (28 + 20 competities, met het interlandvenster en de "
        "kalenderjaarcompetities erop), dus dit is een lege runlijst en geen bronstoring. "
        "BetExplorer bevestigt het per competitie."),
    "eerstvolgende_speeldag": NEXT,
}
state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "toelichting": ("geen wedstrijd in het venster, dus geen competitie om prijzen voor te kopen. "
                    "De marktbalans-controle van §1a is daarmee niet van toepassing: er is niets "
                    "ingekocht, niet eenzijdig ingekocht."),
}
state["afkapping"] = {
    "max_deep_analyses": 40, "kandidaten": 0, "doorgerekend": 0, "afgekapt": 0,
    "laagste_score_die_het_haalde": None, "hoogste_score_die_afviel": None,
    "toelichting": "geen kandidaten — de cap heeft niets geknepen.",
}
state["bets"] = 0
save(state)
print("voortgangsbestand geschreven:", len(state["competitions"]), "competities, 0 bets")
