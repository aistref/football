"""Run A, 19 okt 2026 — de doelpunten- en BTTS-frequenties bij de bets van vandaag.

Op verzoek van de gebruiker (17 okt): de onderbouwing van een Over/Under- of BTTS-bet noemde de
doelverwachting van het model en de vorm als `WWDLW`, maar nooit hoe vaak de markt werkelijk
opging. Deze aanroep telt dat met `scripts/marketform.py` voor elke doorgerekende wedstrijd en
legt het in `data/run-state/` onder `marktvorm`.

Let op wat dit NIET is: de telling gaat niet in `my_prob` en verandert geen enkele pick, kans of
rangorde van vandaag. Ze komt naast het model te staan (§2, §4 — een getal met een gewicht
verzinnen waarvoor geen meting bestaat is verboden).
"""
import json
from scripts import marketform

res = json.load(open("tmp-run/ra_oct21_results.json"))
s3 = json.load(open("tmp-run/ra_oct21_stage3.json"))
picks = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/ra_oct21_picks_a.json"))}

meta = {naam: (v.get("primaryId"), v.get("s_prev"), v.get("s_cur"))
        for naam, v in s3["fixtures"].items()}

uit, fouten = {}, {}
for m in res["matches"]:
    lid, s_prev, s_cur = meta.get(m["competition"], (None, None, None))
    if not lid or m["tier"] == "NONE":
        continue
    try:
        uit[m["match"]] = marketform.match_block(lid, s_cur, s_prev, m["home"], m["away"])
    except Exception as e:
        fouten[m["match"]] = f"{type(e).__name__}: {e}"

json.dump({"blokken": uit, "fouten": fouten},
          open("tmp-run/ra_oct21_marktvorm.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(uit)} wedstrijden geteld, {len(fouten)} fout(en)")
for k, v in fouten.items():
    print("  FOUT", k, v)

LIJN = {"Over 3": 3.0, "Under 3.5": 3.5, "Over 2.5": 2.5, "DNB — Besiktas JK": 2.5, "Beide ploegen scoren — nee": 2.5}
print("\n=== DE DRIE GEPUBLICEERDE REGELS ===")
for naam, p in picks.items():
    b = uit.get(naam)
    if not b:
        print(f"\n{naam}: geen blok"); continue
    lijn = LIJN.get(p["selection"], 2.5)
    # Op een hele lijn (Over 3) telt "meer dan 3" — marketform telt strikt groter dan de lijn,
    # dus 3.5 en 3.0 geven hetzelfde antwoord voor "4 of meer". Voor de leesbaarheid tellen we
    # op de gangbare lijn 2.5 én op de lijn van de bet zelf.
    toon = 3.5 if lijn == 3.0 else lijn
    print(f"\n{naam} — {p['market']} {p['selection']} @{p['odds']:.4f} "
          f"(model: {p['my_prob']*100:.1f}%)")
    for rol in ("home", "away"):
        t = b["teams"][rol]
        for sleutel, label in (("lopend_recent", "laatste 5 in de competitie"),
                               ("lopend", "heel lopend seizoen"),
                               ("lopend_kant", "dit seizoen thuis" if rol == "home" else "dit seizoen uit"),
                               ("vorig", "heel vorig seizoen")):
            d = t[sleutel]
            if not d["found"]:
                print(f"   {t['team']:22s} {label:28s} speelde die competitie niet")
                continue
            if not d["n"]:
                continue
            o = d["over"][str(toon)]
            print(f"   {t['team']:22s} {label:28s} n={d['n']:2d}  "
                  f">{toon:g} doelp.: {o:2d} ({100*o/d['n']:3.0f}%)  "
                  f"BTTS: {d['btts']:2d} ({d['btts_pct']:3.0f}%)  "
                  f"gem. {d['goals_per_match']:.2f}")

# --- en in data/run-state/, zodat report.py het kan renderen -------------------------------
STATE = "data/run-state/2026-10-21-run-a.json"
st = json.load(open(STATE))
gezet = 0
for comp, blok in st["competitions"].items():
    for m in blok.get("matches") or []:
        b = uit.get(m.get("match"))
        if b:
            m["marktvorm"] = b
            gezet += 1
st["marktvorm_toegevoegd"] = (
    "19 okt 2026, NA het publiceren van deze run. Dit blok is een TELLING en verandert niets: "
    "geen pick, geen my_prob, geen edge, geen rangorde en geen regel in picks.jsonl. Een "
    "herberekening van 19 oktober geeft daarom exact dezelfde drie regels als de run zelf gaf. "
    "Zie _shared-rules.md §4, 'Hoe vaak ging deze markt eerder op?'. LET OP: het STATE-pad stond "
    "in de versie van 18 oktober HARDGECODEERD op dat van die dag en is door de sed-overname van "
    "vandaag niet meegegaan; de eerste doorloop schreef daardoor in het run-state-bestand van "
    "GISTEREN en zette daar nul blokken (geen van de 35 wedstrijdnamen van 18 oktober komt in de "
    "lijst van vandaag voor). Dat bestand is met `git checkout` teruggezet voordat er iets was "
    "gecommit; de enige wijziging was deze sleutel zelf. Zie het runrapport, 'Wat ik nog moet "
    "doen', punt over het hardgecodeerde pad.")
json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nmarktvorm-blok op {gezet} wedstrijden in run-state gezet")
