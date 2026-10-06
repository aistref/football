"""Run A, 6 okt 2026 — Stage 6: voortgangsbestand vullen uit Stage 1/2/3 en de analyse."""
import json
from datetime import date
from scripts.progress import load_or_start, mark, save

DAY = date(2026, 10, 6)
st3 = json.load(open("tmp-run/ra_oct06_stage3.json"))
res = json.load(open("tmp-run/ra_oct06_results.json"))

NEXT = {}
for name, v in st3["betexplorer"].items():
    eerste = (v or {}).get("eerste") or []
    if eerste:
        NEXT[name] = eerste[0]
    elif (v or {}).get("n") == 0:
        NEXT[name] = "geen ronde gepland op BetExplorer"
    else:
        NEXT[name] = "niet bepaald"

VENSTER = "[08:00 NL 6 okt, 08:00 NL 7 okt)"
TOEL = ("interlandperiode — geen duel in het inzetvenster {v}. Twee bronnen apart "
        "gecontroleerd: Fotmob-daglijsten van 6 en 7 okt en de BetExplorer-fixturepagina. "
        "Eerstvolgende speeldag: {n}.")

state = load_or_start("a", DAY)
state.setdefault("duur", {})

for name in st3["fixtures"]:
    if name == "FA Cup (ENG)":
        continue
    mark(state, name, {"status": "GEEN WEDSTRIJD", "matches": [],
                       "toelichting": TOEL.format(v=VENSTER, n=NEXT.get(name, "niet bepaald"))})

mark(state, "FA Cup (ENG)", {
    "status": "GEANALYSEERD",
    "fixturebron": ("BetExplorer — de Fotmob-daglijsten van 6 en 7 okt noemen de FA Cup niet, "
                    "terwijl de fixturepagina vijf duels op 6 okt 19:45 UK geeft. Dat is de "
                    "bevinding van 2 en 5 oktober, voor de derde keer gemeten."),
    "prijsbron": ("BetExplorer-marktgemiddelde over 2 boeken (1X2). Geen sportkey bij The Odds "
                  "API voor de FA Cup, dus spreads/totals/BTTS zijn niet te koop — niet "
                  "opgevraagd, geen gat (§6b-5b)."),
    "matches": res["matches"],
    "toelichting": ("vijf duels in de vierde kwalificatieronde; vier op data_tier NONE omdat de "
                    "twee ploegen in verschillende (of in geen enkele door Fotmob gedekte) "
                    "divisie staan, één doorgerekend in National League North."),
})

state["parameters"] = {
    "MAX_DEEP_ANALYSES": 40, "MAX_SHORTLIST": 3, "dagsoort": "di (werkweek)",
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
    "poort8_bindt": "ja — vanaf 1 okt 2026 weer (sides.LAPSED_UNTIL = 2026-10-01)",
}
state["stage1"] = {
    "venster": "[2026-10-06T06:00Z, 2026-10-07T06:00Z) = [08:00 NL, 08:00 NL +1)",
    "bronnen": ["Fotmob daglijst 2026-10-06 (59 competities)",
                "Fotmob daglijst 2026-10-07 (24 competities)",
                "BetExplorer fixturepagina per competitie (21 van 21 opgevraagd)"],
    "wedstrijden_in_venster": 5,
    "wedstrijden_via_fotmob": 0,
    "wedstrijden_via_betexplorer": 5,
    "afgekapt_door_max_deep": 0,
    "fotmob_ids_gevonden": 0,
    "fotmob_ids_toelichting": (
        "0 van 21 — geen runlijstcompetitie staat in een van beide daglijsten, de FA Cup "
        "inbegrepen. De daglijsten zelf kwamen normaal binnen (59 + 24 competities). De vijf "
        "FA Cup-duels komen daarom van de tweede fixturebron."),
}
state["vroeg_seizoen"] = res["vroeg_seizoen"]
state["niveau"] = res["niveau"]
state["afkapping"] = res["afkapping"]
state["bets"] = sum(bool(m["bet"]) for m in res["matches"])
save(state)
print("voortgangsbestand geschreven:", len(state["competitions"]), "competities,",
      state["bets"], "bets")
