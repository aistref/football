"""Stage 5 stap 2, doelpuntenkant — het Pinnacle-oordeel over de TOTALEN, niet over 1X2.

`rb_oct28_pinnacle.py` zet het eigen 1X2 naast Pinnacle's de-vigde 1X2. Dat is het beste
publieke expertoordeel over WIE er wint, en vandaag is de enige gepubliceerde regel een Under —
dus een markt waar die vergelijking niets over zegt.

§6g eist bij een gepubliceerde Under uitdrukkelijk dat erbij staat dat deze kant meetbaar scheef
staat. Dit script levert daar het onafhankelijke cijfer bij: Pinnacle's eigen Over/Under-lijnen,
per lijn de-vigd, naast de eigen kans uit hetzelfde scoregrid. Pinnacle heeft een marge van 3 tot
5% tegen 6 tot 10% bij de rest, dus een verschil tegen Pinnacle is een strengere toets dan een
verschil tegen de aanbieder waar de bet staat.

HARDE GRENS (§2 / §4): dit getal gaat niet in `my_prob` en niet in `prob_sources`. Het is
marktafgeleid en hoort in de vergelijking.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import model
from ra_names import resolve

odds = json.load(open("tmp-run/rb_oct28_odds.json"))
res = json.load(open("tmp-run/rb_oct28_results.json"))
grids = {m["match"]: m for m in res["matches"]}

# Pinnacle's totals per event, per lijn: {lijn: (over, under)}
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
                    pt = o.get("point")
                    if pt is None:
                        continue
                    per.setdefault(float(pt), {})[o["name"].lower()] = o["price"]
                if per:
                    pin[(e["home_team"], e["away_team"])] = per

print(f"Pinnacle-totalen gevonden voor {len(pin)} events\n")

# Run B, 21 okt 2026 — TWEEDE KOPPELPOGING, en ze was nodig. `resolve` accepteert een afkorting
# alleen als VOORVOEGSEL (§4, de Jong-Ajax-regel), en The Odds API noteert de uitploeg van vandaag
# als "D.C. United" waar Fotmob "DC United" schrijft: de punten maken er geen voorvoegsel van, dus
# de enige gepubliceerde regel van deze run — een Under — kreeg geen Pinnacle-vergelijking. Dat is
# precies het cijfer dat §6g bij een Under eist, dus het stil overslaan is geen optie.
# Dezelfde constructie als in `rb_oct28_pinnacle.py`: normaliseren op alfanumeriek, koppelen op
# bevatting of een gemeenschappelijk voorvoegsel van vijf tekens aan BEIDE kanten, en het
# resultaat alleen accepteren als er PRECIES ÉÉN event aan voldoet. Die uniciteitseis is de rem
# tegen de Jong-Ajax-val: twee kandidaten is geen keuze maar geen koppeling.
import re as _re


def _nrm(x):
    import unicodedata
    x = unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower()
    return _re.sub(r"[^a-z0-9]", "", x)


def _los(x, y):
    a, b = _nrm(x), _nrm(y)
    return a in b or b in a or (len(a) >= 5 and len(b) >= 5 and a[:5] == b[:5])


rows = []
for m in res["matches"]:
    per = None
    for (h, a), v in pin.items():
        if resolve(m["home"], {h: 1}) and resolve(m["away"], {a: 1}):
            per = v
            break
    if per is None:
        kand = [v for (h, a), v in pin.items()
                if _los(m["home"], h) and _los(m["away"], a)]
        if len(kand) == 1:
            per = kand[0]
            print(f"  {m['match']}: gekoppeld op de tweede poging (genormaliseerde naam)")
    if not per:
        continue
    lam = (m.get("lambdas") or {}).get("xg")
    if not lam:
        continue
    # Het scoregrid zelf staat niet in het resultaatbestand; de twee lambdas wel. Een
    # onafhankelijk Poisson-grid op diezelfde lambdas geeft de eigen kans op de xG-arm; rho raakt
    # alleen de lage standen.
    import math
    lh, la = lam
    P = [[math.exp(-lh) * lh**i / math.factorial(i) * math.exp(-la) * la**j / math.factorial(j)
          for j in range(12)] for i in range(12)]
    tot = [0.0] * 24
    for i in range(12):
        for j in range(12):
            tot[i + j] += P[i][j]

    # 25 okt 2026 (Run B) — DE VERGELIJKING STOND OP TWEE VERSCHILLENDE GROOTHEDEN, en bij 16
    # van de 25 paren was dat geen afrondingsverschil. Hier stond
    # `mijn_under = sum(... if i + j < lijn)`, oftewel P(totaal < L) zonder push, naast een
    # de-vigde Pinnacle-prijs die de push WEL in zich heeft: op een hele lijn (2.0, 3.0) komt de
    # inzet bij exact L doelpunten terug, en op een kwartlijn (2.75, 3.25) bij de helft van de
    # inzet. De-viggen van zo'n prijs geeft P(onder | geen push) en niet P(onder), dus de twee
    # getallen stonden op een andere noemer.
    #
    # Wat dat deed: alleen de zuivere halve lijnen (2.5, 3.5) waren vergelijkbaar — negen van de
    # 25. Holstein Kiel – Dynamo Dresden kwam er het duidelijkst uit: op lijn 3.00 las de oude
    # vorm "eigen 0.457 tegen Pinnacle 0.497", oftewel Pinnacle zou MEER op de Under zitten dan
    # het model, terwijl de gepubliceerde regel juist een Under is met +5,48 pp eigen voordeel.
    # Dat is geen tegenspraak in het model maar een tegenspraak in deze controle.
    #
    # De eerlijke vergelijking zet de eigen kans op dezelfde noemer als de prijs. Voor een inzet
    # van 1u op de Under tegen koers u is de faire koers die waarbij de verwachtingswaarde nul is,
    # en dan geldt 1/u_fair = (gewicht van de winnende tak) / (1 - pushmassa):
    #
    #   halve lijn  L = k + 0.5   geen push          -> P(totaal <= k)
    #   hele lijn   L = k         push bij totaal k  -> P(<= k-1) / (1 - P(=k))
    #   kwartlijn   L = k + 0.25  halve push bij k   -> (2*P(<= k-1) + P(=k)) / (2 - P(=k))
    #   kwartlijn   L = k + 0.75  halve push bij k+1 -> 2*P(<= k) / (2 - P(=k+1))
    #
    # De eerste regel is wat er stond; de andere drie zijn nieuw. `totals_prob` doet in
    # `scripts/model.py` hetzelfde voor de bet zelf (§1a, "een handicap of totaal met push is geen
    # gewone kans"); deze controle liep daar achteraan. Het raakt geen enkele pick, kans of
    # rangorde van vandaag — het is stap 2 van Stage 5, een lezing, en §2 houdt hem buiten
    # `my_prob`. Het raakt wél de conclusie die eruit wordt gelezen, en dat is precies waarvoor
    # §6g hem gebruikt.
    def eigen_under(L):
        frac = round(L - math.floor(L), 2)
        k = int(math.floor(L))
        onder = lambda n: sum(tot[:n + 1]) if n >= 0 else 0.0
        if frac == 0.5:
            return onder(k), 0.0, "halve lijn, geen push"
        if frac == 0.0:
            push = tot[k]
            return (onder(k - 1) / (1 - push) if push < 1 else float("nan"), push,
                    f"hele lijn, push {push:.3f} bij {k}")
        if frac == 0.25:
            push = tot[k]
            return ((2 * onder(k - 1) + tot[k]) / (2 - push), push / 2,
                    f"kwartlijn, halve push {push:.3f} bij {k}")
        if frac == 0.75:
            push = tot[k + 1]
            return (2 * onder(k) / (2 - push), push / 2,
                    f"kwartlijn, halve push {push:.3f} bij {k + 1}")
        return onder(k), 0.0, "onbekende lijnvorm"

    for lijn, prijzen in sorted(per.items()):
        if "over" not in prijzen or "under" not in prijzen:
            continue
        o, u = prijzen["over"], prijzen["under"]
        vig = 1 / o + 1 / u
        pin_under = (1 / u) / vig
        mijn_under, pushmassa, vorm = eigen_under(lijn)
        zuiver = round(lijn - math.floor(lijn), 2) == 0.5
        rows.append({"match": m["match"], "lijn": lijn, "pin_over": o, "pin_under": u,
                     "marge_pct": round((vig - 1) * 100, 2),
                     "pin_under_devig": round(pin_under, 4),
                     "mijn_under_xg": round(mijn_under, 4),
                     "lijnvorm": vorm, "pushmassa": round(pushmassa, 4),
                     "halve_lijn": zuiver,
                     "verschil_pp": round((mijn_under - pin_under) * 100, 2)})
        print(f"{m['match'][:28]:28s} lijn {lijn:4.2f}  Pinnacle {o:5.2f}/{u:5.2f} "
              f"(marge {(vig-1)*100:4.1f}%)  P(Under) Pinnacle {pin_under:.3f} / eigen "
              f"{mijn_under:.3f}  verschil {(mijn_under-pin_under)*100:+6.2f} pp   {vorm}")

json.dump(rows, open("tmp-run/rb_oct28_pinnacle_ou.json", "w"), ensure_ascii=False, indent=1)
if rows:
    import statistics as S
    print(f"\n{len(rows)} (duel, lijn)-paren · gemiddeld verschil op de Under-kant "
          f"{S.mean([r['verschil_pp'] for r in rows]):+.2f} pp · "
          f"{sum(1 for r in rows if r['verschil_pp'] > 0)} van {len(rows)} boven Pinnacle")
    # De zuivere halve lijnen apart, want dat is de enige groep die ook onder de OUDE
    # (push-blinde) vorm vergelijkbaar was. Staat die subgroep dezelfde kant op als het geheel,
    # dan verandert de reparatie de conclusie niet maar wel het getal.
    zui = [r for r in rows if r["halve_lijn"]]
    if zui:
        print(f"   waarvan zuivere halve lijnen: {len(zui)} paren · "
              f"{S.mean([r['verschil_pp'] for r in zui]):+.2f} pp · "
              f"{sum(1 for r in zui if r['verschil_pp'] > 0)} van {len(zui)} boven Pinnacle")
    rest = [r for r in rows if not r["halve_lijn"]]
    if rest:
        print(f"   met push (hele en kwartlijnen):  {len(rest)} paren · "
              f"{S.mean([r['verschil_pp'] for r in rest]):+.2f} pp · "
              f"{sum(1 for r in rest if r['verschil_pp'] > 0)} van {len(rest)} boven Pinnacle")
