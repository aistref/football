"""Bewijs bij de reparatie van `toplist._cut` van 2 november 2026 (§5b stap 5 + §5).

Drie gevallen, geen netwerk en geen repo-state nodig. Geval 1 is de fout van vandaag: precies
`MAX_SHORTLIST` selecties boven hun lat, waardoor `len(boven) > n` onwaar was en een selectie
ONDER de lat een selectie ERBOVEN verdrong. Geval 2 is dezelfde fout buiten de grens: met minder
dan `n` boven de lat kon een gekwalificeerde selectie volledig uit de lijst vallen zodra er genoeg
hoger scorende kandidaten onder hun lat stonden. Geval 3 toont dat het gedrag onveranderd is zodra
er méér dan `n` boven de lat staan — dan is de drempel de grens, precies zoals voorheen.
"""
from scripts import toplist


def mk(match, market, tier, edge, prob, odds=2.0):
    lat = 8.0 if tier == "FULL" else 16.0
    return {"match": match, "market": market, "selection": market, "odds": odds,
            "tier": tier, "edge_pp": edge, "my_prob": prob, "my_raw": prob,
            "edge_raw": edge, "implied": 1 / odds,
            "failed_gate": None if edge >= lat else "edge",
            "poorten": {"odds": True, "tweede_methode": True, "context": True,
                        "underdog": True, "doelpunten_onder": True, "robuustheid": True},
            "bet_beide": edge >= lat, "bet_ruw": edge >= lat, "kickoff_nl": "20:00"}


def state(rows, day="2026-11-02"):
    return {"date": day, "run": "A", "competitions": {"X": {
        "status": "GEANALYSEERD",
        "matches": [{"match": r["match"], "tier": r["tier"], "kickoff_nl": "20:00",
                     "bet": r["failed_gate"] is None, "all_candidates": [r]} for r in rows]}}}


def namen(rows, n=3):
    return [r["match"] for r in toplist.build(state(rows), n=n)["herijkt"]]


# 1 — precies n boven de lat: de drie gekwalificeerde horen erin, de vierde niet.
r1 = [mk("A – B", "OU", "FULL", 14.8, 0.79), mk("C – D", "1X2", "FULL", 18.2, 0.63),
      mk("E – F", "1X2", "FULL", 8.18, 0.46), mk("G – H", "OU", "FULL", 7.39, 0.68)]
assert namen(r1) == ["A – B", "C – D", "E – F"], namen(r1)

# 2 — één boven de lat, drie hoger scorend eronder: die ene mag niet wegvallen.
r2 = [mk("A – B", "1X2", "FULL", 8.1, 0.40), mk("C – D", "OU", "FULL", 7.9, 0.95),
      mk("E – F", "OU", "FULL", 7.5, 0.90), mk("G – H", "OU", "FULL", 7.0, 0.88)]
assert "A – B" in namen(r2) and namen(r2)[0] == "C – D", namen(r2)

# 3 — vier boven de lat: ongewijzigd, drempel is de grens en score bepaalt de rangorde.
r3 = [mk("A – B", "OU", "FULL", 20.0, 0.70), mk("C – D", "1X2", "FULL", 15.0, 0.60),
      mk("E – F", "1X2", "FULL", 12.0, 0.55), mk("G – H", "OU", "FULL", 9.0, 0.50)]
assert namen(r3) == ["A – B", "C – D", "E – F"], namen(r3)

# 4 — BINNEN één wedstrijd: een selectie die haar lat haalt gaat voor op een hoger scorende
#     die dat niet doet. Zonder deze regel koos `build` de DNB en noemde de analyse het 1X2.
r4 = [mk("Z – K", "1X2", "FULL", 8.18, 0.4621, odds=2.63),
      mk("Z – K", "DNB", "FULL", 6.50, 0.6105, odds=1.75),
      mk("S – F", "OU", "FULL", 7.39, 0.6836, odds=1.64),
      mk("A – P", "OU", "FULL", 14.8, 0.7931, odds=1.55),
      mk("R – S", "AH", "FULL", 18.22, 0.6336, odds=2.22)]
lijst = toplist.build(state(r4), n=3)["herijkt"]
assert [r["match"] for r in lijst] == ["A – P", "R – S", "Z – K"], lijst
assert [r["market"] for r in lijst][2] == "1X2", lijst       # niet de DNB
assert all(r["edge_pp"] >= 8.0 for r in lijst), lijst        # geen sub-lat-regel in de lijst

# 5 — haalt binnen de wedstrijd GEEN enkele selectie haar lat, dan blijft de hoogste score de
#     vertegenwoordiger: dat is de rangorde-aanvulling die §5b uitdrukkelijk wil.
r5 = [mk("Q – R", "1X2", "FULL", 5.0, 0.30, odds=3.0), mk("Q – R", "OU", "FULL", 4.0, 0.80)]
lijst5 = toplist.build(state(r5), n=3)["herijkt"]
assert [r["market"] for r in lijst5] == ["OU"], lijst5       # 4.0*0.80=3.2 > 5.0*0.30=1.5

print("toplist: alle vijf de gevallen OK")
