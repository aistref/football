"""Stage 5 stap 2, doelpuntenkant — het Pinnacle-oordeel over de TOTALEN, niet over 1X2.

`ra_oct27_pinnacle.py` zet het eigen 1X2 naast Pinnacle's de-vigde 1X2. Dat is het beste publieke
expertoordeel over WIE er wint, en het zegt niets over een Under. §6g eist bij een gepubliceerde
Under uitdrukkelijk dat erbij staat dat deze kant meetbaar scheef staat; dit script levert daar
het onafhankelijke cijfer bij.

HARDE GRENS (§2 / §4): dit getal gaat niet in `my_prob` en niet in `prob_sources`. Het is
marktafgeleid en hoort in de vergelijking.

**DE PUSH-FOUT, gevonden en gerepareerd op 25 okt 2026.** `rb_oct21_pinnacle_ou.py` — waarvan dit
script is overgenomen — vergeleek twee getallen die niet op dezelfde schaal staan:

  eigen kans   = `sum(P[i][j] for i+j < lijn)`, de KALE kans dat het totaal onder de lijn blijft
  Pinnacle     = `(1/under) / (1/over + 1/under)`, de PUSH-GECORRIGEERDE eerlijke kans

Op een halve lijn (2.5) is er geen push en zijn die twee hetzelfde, dus daar klopte de meting. Op
een hele lijn (3.0) en op elke kwartlijn (2.25, 2.75, 3.25) niet: daar komt een deel van de massa
terug als inzet, en de Pinnacle-prijzen verwerken dat wél en de kale kans niet. Het verschil is
niet klein. Randers FC – Brøndby IF, lijn 3.00, de gepubliceerde Under van vandaag:

  oude meting   P(Under) Pinnacle 0.514 / eigen 0.517  ->  +0.25 pp   ("Pinnacle is het eens")
  nieuwe meting P(Under) Pinnacle 0.514 / eigen 0.651  ->  +13.7 pp   ("het model staat erboven")

Die eerste regel zou in het dagrapport als externe bevestiging zijn beland van precies de kant
waarvan §6g heeft gemeten dat ze scheef staat. Daarom rekent dit script de eigen kans met
`model.totals_prob(grid, lijn, "under", pinnacle_under_prijs)` — dezelfde functie die de poorten
gebruiken (§1a: "gebruik voor markten met push altijd asian_prob / dnb_prob / totals_prob en nooit
de kale winkans, anders staan de markten niet op dezelfde schaal"). Op Pinnacle's eigen prijs, niet
op de prijs waarop gespeeld wordt, want een push-gecorrigeerde kans hangt van de koers af en de
vergelijking moet over één en dezelfde koers gaan.

Het grid wordt opnieuw opgebouwd uit de twee opgeslagen lambdas van de xG-arm, met dezelfde
`DEFAULT_RHO` als `analyze_match`; dat is exact het grid waarop `totals_prob` in de analyse werkte.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import model
from ra_names import resolve

odds = json.load(open("tmp-run/ra_oct27_odds.json"))
res = json.load(open("tmp-run/ra_oct27_results.json"))

# Pinnacle's totals per event, per lijn: {lijn: {"over": prijs, "under": prijs}}
pin = {}
for comp, events in (odds["raw"].get("totals") or {}).items():
    for e in events:
        for bm in e.get("bookmakers", []):
            if bm.get("key") != "pinnacle":
                continue
            for mk in bm.get("markets", []):
                if mk.get("key") != "totals":
                    continue
                per = {}
                for o in mk.get("outcomes", []):
                    if o.get("point") is None:
                        continue
                    per.setdefault(float(o["point"]), {})[o["name"].lower()] = o["price"]
                if per:
                    pin[(e["home_team"], e["away_team"])] = per
print(f"Pinnacle-totalen gevonden voor {len(pin)} events\n")


def _los(a, b):
    """Soepele naamkoppeling: vijf gelijke beginletters na normalisatie."""
    import re, unicodedata
    n = lambda t: re.sub(r"[^a-z0-9]", "",
                         unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower())
    x, y = n(a), n(b)
    return bool(x and y) and (x[:5] == y[:5] or x in y or y in x)


rows = []
for m in res["matches"]:
    per = None
    for (h, a), v in pin.items():
        if resolve(m["home"], {h: 1}) and resolve(m["away"], {a: 1}):
            per = v
            break
    if not per:
        kand = [v for (h, a), v in pin.items() if _los(m["home"], h) and _los(m["away"], a)]
        if len(kand) == 1:
            per = kand[0]
            print(f"  {m['match']}: gekoppeld op de tweede poging (genormaliseerde naam)")
    lam = (m.get("lambdas") or {}).get("xg")
    if not per or not lam:
        continue
    lh, la = lam
    grid = model.score_grid(lh, la)
    for lijn, prijzen in sorted(per.items()):
        if "over" not in prijzen or "under" not in prijzen:
            continue
        o, u = prijzen["over"], prijzen["under"]
        vig = 1 / o + 1 / u
        pin_under = (1 / u) / vig
        # zelfde functie en zelfde koers als Pinnacle, dus zelfde push-behandeling (§1a)
        mijn_under = model.totals_prob(grid, lijn, "under", u)
        kaal = sum(grid[i][j] for i in range(len(grid)) for j in range(len(grid[0])) if i + j < lijn)
        rows.append({"match": m["match"], "lijn": lijn, "pin_over": o, "pin_under": u,
                     "marge_pct": round((vig - 1) * 100, 2),
                     "pin_under_devig": round(pin_under, 4),
                     "mijn_under_xg": round(mijn_under, 4),
                     "mijn_under_kaal": round(kaal, 4),
                     "push": round(1 - kaal - sum(grid[i][j] for i in range(len(grid))
                                                  for j in range(len(grid[0])) if i + j > lijn), 4),
                     "verschil_pp": round((mijn_under - pin_under) * 100, 2)})
        print(f"{m['match'][:28]:28s} lijn {lijn:4.2f}  Pinnacle {o:5.2f}/{u:5.2f} "
              f"(marge {(vig-1)*100:4.1f}%)  P(Under) Pinnacle {pin_under:.3f} / eigen "
              f"{mijn_under:.3f}  verschil {(mijn_under-pin_under)*100:+6.2f} pp")

json.dump(rows, open("tmp-run/ra_oct27_pinnacle_ou.json", "w"), ensure_ascii=False, indent=1)
if rows:
    import statistics as S
    print(f"\n{len(rows)} (duel, lijn)-paren · gemiddeld verschil op de Under-kant "
          f"{S.mean([r['verschil_pp'] for r in rows]):+.2f} pp · "
          f"{sum(1 for r in rows if r['verschil_pp'] > 0)} van {len(rows)} boven Pinnacle")
