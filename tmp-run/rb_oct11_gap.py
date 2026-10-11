"""De divisiesprong van Griekenland, Hongarije en Oostenrijk meten (§4).

Opdracht van de gebruiker op 11 okt 2026, punt 2 uit "Wat er nog moet gebeuren" van het
dagrapport van Run B. Aanleiding: drie van de 42 duels van die run kwamen op `data_tier = NONE`
uit omdat `promotion.TIER2` geen ingang had voor deze drie hoogste divisies — Iraklis (GRE),
Kispest Honvéd (HUN) en Austria Lustenau (AUT) zijn alle drie promovendus.

EERST DE KROATIE-CONTROLE, want §4 eist dat onderscheid: heeft Fotmob die tweede divisies
überhaupt? `api/data/allLeagues` geeft onder deze drie ccodes:
  GRE -> Super League 1 (135), Greece Cup (145), Super Cup (8816), **Super League 2 (8815)**
  HUN -> Nemzeti Bajnokság I (212), Magyar Kupa (213), **NB II (9117)**
  AUT -> Bundesliga (38), **2. Liga (119)**, Austrian Cup (278), Landesliga (285)
Alle drie bestaan dus. Dit is "nog niet gemeten", niet "niet meetbaar" — anders dan Kroatie.

METHODE: dezelfde als de twaalf paren die er al in staan — `measure_gap` over de promovendi van
2016/2017 t/m 2024/2025, per ploeg relatief aan zijn eigen competitie in dat seizoen. Geen
`calendar_year`: alle drie lopen van augustus tot mei.

VALIDATIE VOORAF: Roemenie wordt meegemeten. Dat paar staat sinds 9 okt in
`MEASURED_TIER2_GAP` op (0.541, 1.811, n=16) met bereik 0.888-1.740 / 0.285-1.250. Komt deze
runner daar niet op uit, dan is de aggregatie hier anders dan die van 9 oktober en mogen de drie
nieuwe getallen niet in de tabel.
"""
import json
from scripts import promotion
from scripts.promotion import Tier2, measure_gap

NIEUW = {
    "Greek Super League (GRE)":  Tier2(8815, "Super League 2 (GRE)"),
    "Hungarian NB I (HUN)":      Tier2(9117, "NB II (HUN)"),
    "Austrian Bundesliga (AUT)": Tier2(119,  "2. Liga (AUT)"),
}
for naam, t2 in NIEUW.items():
    promotion.TIER2.setdefault(naam, t2)

JAREN = range(2016, 2025)        # promovendi van 2016/2017 t/m 2024/2025
TE_METEN = ["Romanian SuperLiga (ROU)"] + list(NIEUW)   # ROU = validatie
COV = json.load(open("data/coverage.json"))["competitions"]

uit = {}
for naam in TE_METEN:
    top_id = COV[naam]["fotmob_id"]
    t2 = promotion.TIER2[naam]
    try:
        g = measure_gap(naam, top_id, JAREN)
    except Exception as e:
        print(f"{naam:28s} FOUT {type(e).__name__}: {e}")
        continue
    a0 = sorted(s[4] for s in g.samples)
    d0 = sorted(s[5] for s in g.samples)
    rng = (round(a0[0], 3), round(a0[-1], 3), round(d0[0], 3), round(d0[-1], 3))
    uit[naam] = {"tier2_id": t2.fotmob_id, "tier2_naam": t2.name,
                 "aanval": round(g.attack, 3), "verdediging": round(g.defence, 3), "n": g.n,
                 "bereik_aanval": [rng[0], rng[1]], "bereik_verdediging": [rng[2], rng[3]],
                 "jaren": sorted({s[1] for s in g.samples}),
                 "ploegen": [(s[0], s[1], s[2], s[3], s[4], s[5]) for s in g.samples]}
    print(f"{naam:28s} aanval {g.attack:.3f}  verdediging {g.defence:.3f}  n={g.n:3d}  "
          f"invoerbereik aanval {rng[0]:.3f}-{rng[1]:.3f}, verdediging {rng[2]:.3f}-{rng[3]:.3f}")

json.dump(uit, open("tmp-run/rb_oct11_gap.json", "w"), ensure_ascii=False, indent=1)
print("\nGEPOOLD, als vergelijking:", promotion.POOLED_GAP)
