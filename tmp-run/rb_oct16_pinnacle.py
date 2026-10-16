"""Stage 5 stap 2 — 'wat anderen voorspellen', in de enige vorm die vandaag bereikbaar is.

§3 Stage 5 meet op 20 sep 2026 dat geschreven voorspellingen vrijwel niet te halen zijn (Forebet
403, Pinnacle-artikelen 404, Matchbook 530, voetbalwedden.net zonder de duels van de dag). Wat er
wél is, is **de prijs van Pinnacle apart**: de scherpste bookmaker van de markt, en zijn de-vigde
1X2 is het beste publieke expertoordeel dat beschikbaar is. Die zet je naast je eigen kans, LOS
van de beste prijs waarop je speelt.

HARDE GRENS (§2 / §4): dit getal mag nooit in `my_prob` of in `prob_sources`. Het is andermans
lezing en het is marktafgeleid; het hoort in de vergelijking, niet in de kansschatting.
"""
import json, re, sys, unicodedata
sys.path.insert(0, "tmp-run")
from scripts import calibration
from ra_names import best_pair, resolve


def nrm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", t)

odds = json.load(open("tmp-run/rb_oct16_odds.json"))
res = json.load(open("tmp-run/rb_oct16_results.json"))

by_match = {}
for comp, events in (odds["raw"].get("h2h") or {}).items():
    for e in events:
        for bm in e.get("bookmakers", []):
            if bm.get("key") != "pinnacle":
                continue
            for mk in bm.get("markets", []):
                if mk.get("key") != "h2h":
                    continue
                pr = {o["name"]: o["price"] for o in mk.get("outcomes", [])}
                h, a = e["home_team"], e["away_team"]
                if h in pr and a in pr and "Draw" in pr:
                    by_match[(h, a)] = [pr[h], pr["Draw"], pr[a]]

print(f"Pinnacle 1X2 gevonden voor {len(by_match)} events in de responsen\n")
rows = []
for m in res["matches"]:
    # Naamkoppeling via `ra_names.resolve`, niet via een eigen prefixtruc: die miste op de eerste
    # poging Eyüpspor (trema) en AGF (The Odds API noteert "AGF Aarhus").
    pin = None
    for (h, a), q in by_match.items():
        if resolve(m["home"], {h: 1}) and resolve(m["away"], {a: 1}):
            pin = q
            break
    if pin is None:
        for (h, a), q in by_match.items():
            nh, na = nrm(h), nrm(a)
            if (nh.startswith(nrm(m["home"])[:5]) or nrm(m["home"]).startswith(nh[:5])) and \
               (na.startswith(nrm(m["away"])[:5]) or nrm(m["away"]).startswith(na[:5])):
                pin = q
                break
    if pin is None:
        # Run A, 14 okt 2026 — DERDE poging, en ze was nodig: Lens – Sporting CP viel op de twee
        # bovenstaande weg. The Odds API noteert de ploegen als "RC Lens" en "Sporting Lisbon".
        # `resolve` accepteert een afkorting alleen als VOORVOEGSEL (§4, de Jong-Ajax-regel) en
        # "Lens" is geen voorvoegsel van "RC Lens"; de prefixtruc hierboven faalt om dezelfde
        # reden, en "Sporting CP" zit niet in "Sporting Lisbon".
        #
        # Deze variant koppelt op bevatting ÓF een gemeenschappelijk voorvoegsel van minstens
        # vijf tekens, aan BEIDE kanten van het duel, en accepteert het resultaat alleen als er
        # PRECIES ÉÉN event aan voldoet. Die eis van uniciteit is de rem: §4 waarschuwt met de
        # Jong-Ajax-val tegen een soepele naamvergelijking, en wat die val gevaarlijk maakt is
        # dat ze stil het verkeerde paar pakt. Twee kandidaten betekent hier dus geen keuze maar
        # geen koppeling.
        def _los(x, y):
            nx, ny = nrm(x), nrm(y)
            if len(nx) < 4 or len(ny) < 4:
                return False
            if nx in ny or ny in nx:
                return True
            k = 0
            for cx, cy in zip(nx, ny):
                if cx != cy:
                    break
                k += 1
            return k >= 5
        kand = [q for (h, a), q in by_match.items()
                if _los(m["home"], h) and _los(m["away"], a)]
        if len(kand) == 1:
            pin = kand[0]
        elif len(kand) > 1:
            print(f"{m['match'][:32]:32s} {len(kand)} Pinnacle-kandidaten, niet gekoppeld")

    cal = m.get("calibration") or {}
    mine = cal.get("p_xg")
    if not pin or not mine:
        print(f"{m['match'][:32]:32s} geen Pinnacle-1X2 of geen eigen 1X2")
        continue
    dv = calibration.devig(pin)
    marge = sum(1 / x for x in pin) - 1
    # het eigen 1X2 zoals de poorten het zagen: gewogen (§1f) en herijkt (§1g) staat in
    # all_candidates; hier de kale xG-methode naast de splits, want `calibration` bewaart beide
    sp = cal.get("p_split")
    rows.append({"match": m["match"], "pinnacle": pin, "pin_devig": [round(x, 4) for x in dv],
                 "marge_pct": round(marge * 100, 2), "p_xg": mine, "p_split": sp,
                 "verschil_pp": [round((a - b) * 100, 2) for a, b in zip(mine, dv)]})
    print(f"{m['match'][:30]:30s} marge {marge*100:4.1f}%  "
          f"Pinnacle {dv[0]:.3f}/{dv[1]:.3f}/{dv[2]:.3f}  "
          f"eigen xG {mine[0]:.3f}/{mine[1]:.3f}/{mine[2]:.3f}  "
          f"verschil {rows[-1]['verschil_pp']}")

json.dump(rows, open("tmp-run/rb_oct16_pinnacle.json", "w"), ensure_ascii=False, indent=1)
if rows:
    import statistics as S
    alle = [abs(v) for r in rows for v in r["verschil_pp"]]
    print(f"\n{len(rows)} duels · gemiddelde absolute afstand tot het Pinnacle-oordeel "
          f"{S.mean(alle):.2f} pp · gemiddelde Pinnacle-marge "
          f"{S.mean([r['marge_pct'] for r in rows]):.2f}%")
