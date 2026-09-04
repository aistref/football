"""Samenvatting van de spiegelanalyse: wat had de favorietenkant gedaan?

Twee getallen per groep, en ze zeggen iets anders:

* **trefkans** — hoe vaak de bet was uitgekomen. Dat is letterlijk de vraag van de gebruiker.
* **rendement** — wat het had opgeleverd. Daarvoor is een koers nodig, en die van de spiegelkant
  staat nergens vastgelegd. Hij wordt daarom geschat:
    - Asian Handicap: de twee kanten van een handicap zijn complementair, dus
      `impliciete_kans_spiegel = MARGE_2WEG - impliciete_kans_eigen`.
    - 1X2: uit de de-vigde marktkansen in `calibration` (waar beschikbaar), met dezelfde marge
      er weer bijgeteld.
  Alles wat op een schatting rust, staat apart en is als schatting gelabeld.
"""
import json
from collections import Counter, defaultdict

MARGE_2WEG = 1.02      # gemeten op de handicaplijnen van 4 sep 2026: 1.015 en 1.029
MARGE_1X2 = 1.06       # gebruikelijke marge op een 1X2-drieluik

rows = json.load(open("tmp-run/underdog_mirror.json"))

UNDER = {"underdog", "underdog?"}
FAV = {"favoriet", "favoriet?"}


def label(v):
    return v + (" (geschat uit de eigen koers)" if v and v.endswith("?") else "")


def units(fraction, odds):
    """Nettowinst in eenheden bij 1u inzet: fractie 1 -> odds-1, -1 -> -1, 0.5 -> (odds-1)/2."""
    if fraction > 0:
        return (odds - 1) * fraction
    return fraction


def mirror_odds(r):
    """Geschatte koers van de spiegelbet, of None."""
    if r["kind"] == "ah":
        imp = MARGE_2WEG - r["implied_prob"]
        return round(1 / imp, 3) if imp > 0.02 else None
    if r["kind"] in ("1x2", "dnb", "dc") and r.get("market_probs"):
        ph, px, pa = r["market_probs"]
        opp = pa if r["side"] == "home" else ph
        if r["kind"] == "dnb":
            opp = opp / (ph + pa)
        if r["kind"] == "dc":
            opp = opp + px
        return round(1 / (opp * MARGE_1X2), 3) if opp > 0.02 else None
    return None


def block(name, sel):
    n = len(sel)
    if not n:
        print(f"\n{name}: geen")
        return
    won = sum(1 for r in sel if r["calc"] > 0)
    half = sum(1 for r in sel if abs(r["calc"]) == 0.5)
    push = sum(1 for r in sel if r["calc"] == 0)
    roi = sum(units(r["calc"], r["odds"]) for r in sel)
    mw = sum(1 for r in sel if r["mirror"] is not None and r["mirror"] > 0)
    mp = sum(1 for r in sel if r["mirror"] == 0)
    ml = sum(1 for r in sel if r["mirror"] is not None and r["mirror"] < 0)
    have = [r for r in sel if r["mirror"] is not None]
    mroi, priced = 0.0, 0
    for r in have:
        mo = mirror_odds(r)
        if mo is None:
            continue
        priced += 1
        mroi += units(r["mirror"], mo)
    print(f"\n{name}  (n={n})")
    print(f"  GESPEELD    {won} gewonnen, {half} half, {push} push  ->  trefkans "
          f"{won / n * 100:.1f}%   rendement {roi:+.2f}u = {roi / n * 100:+.1f}%")
    if have:
        print(f"  SPIEGEL     {mw} gewonnen, {mp} push, {ml} verloren  ->  trefkans "
              f"{mw / len(have) * 100:.1f}%   "
              + (f"geschat rendement {mroi:+.2f}u over {priced} = {mroi / priced * 100:+.1f}%"
                 if priced else "geen koers te schatten"))


side_bets = [r for r in rows if r["mirror"] is not None]
print("=" * 78)
print(f"ALLE {len(rows)} AFGEWIKKELDE PICKS — {len(side_bets)} daarvan hebben een kant "
      f"(1X2-zege, AH, DNB, DC) en dus een spiegelbet;")
print(f"{len(rows) - len(side_bets)} niet (Over/Under, BTTS, gelijkspel).")
print("=" * 78)
print("\nverdeling over de kanten:", dict(Counter(r["kant"] for r in rows)))

block("UNDERDOG-KANT (de kant waar de markt de mindere ploeg ziet)",
      [r for r in side_bets if r["kant"] in UNDER])
block("FAVORIETENKANT", [r for r in side_bets if r["kant"] in FAV])
block("PICK'EM / onbeslist", [r for r in side_bets if r["kant"] in ("gelijk", "onbeslist?")])

print("\n" + "-" * 78)
print("UNDERDOG-BETS UITGESPLITST PER MARKT")
und = [r for r in side_bets if r["kant"] in UNDER]
for m in sorted({r["market"] for r in und}):
    block(f"  {m}", [r for r in und if r["market"] == m])

print("\n" + "-" * 78)
print("ALLEEN DE ZEKERE GEVALLEN (kant uit de gemeten markt, niet geschat)")
block("  underdog, gemeten", [r for r in side_bets if r["kant"] == "underdog"])
block("  favoriet, gemeten", [r for r in side_bets if r["kant"] == "favoriet"])

print("\n" + "-" * 78)
print("PER MAAND-HELFT (is het patroon stabiel?)")
for lo, hi, nm in (("2026-08-08", "2026-08-21", "8 t/m 21 aug"),
                   ("2026-08-22", "2026-09-04", "22 aug t/m 4 sep")):
    block(f"  underdog {nm}", [r for r in und if lo <= r["run_date"] <= hi])

print("\n" + "-" * 78)
print("DE 20 GROOTSTE VERLIEZERS AAN DE UNDERDOG-KANT, MET WAT DE SPIEGEL DEED")
worst = sorted([r for r in und if r["calc"] < 0], key=lambda r: r["odds"], reverse=True)[:20]
print(f"  {'datum':11s} {'wedstrijd':38s} {'gespeeld':26s} {'st.':6s} spiegel")
for r in worst:
    mo = mirror_odds(r)
    res = {1.0: "gewonnen", 0.5: "half gew.", 0.0: "push", -0.5: "half verl.",
           -1.0: "verloren"}[r["mirror"]]
    print(f"  {r['run_date']} {(r['home'] + ' – ' + r['away'])[:38]:38s} "
          f"{(r['market'][:3] + ' ' + r['selection'])[:26]:26s} {r['gh']}-{r['ga']:<4} "
          f"{res}" + (f" @~{mo}" if mo else ""))

json.dump({"n": len(rows), "side": len(side_bets)}, open("tmp-run/underdog_summary.json", "w"))
