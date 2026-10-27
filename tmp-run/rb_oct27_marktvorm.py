"""Run B, 27 okt 2026 — de doelpunten- en BTTS-frequenties bij de bets van vandaag.

Tweelingscript van `ra_oct17_marktvorm.py`, voor Run B. Het verzoek van de gebruiker (17 okt) gold
niet één run maar de manier waarop élke bet wordt onderbouwd, en Run B had zijn dagrapport al
gerenderd vóórdat `scripts/marketform.py` bestond. Vier van de vijf regels van Run B staan op de
UNDER-kant, dus juist hier is de telling van §6g relevant.

Let op wat dit NIET is: de telling gaat niet in `my_prob` en verandert geen enkele pick, kans of
rangorde van vandaag (§2, §4).
"""
import json
from scripts import marketform

RUN = "b"
res = json.load(open("tmp-run/rb_oct27_results.json"))
s3 = json.load(open("tmp-run/rb_oct27_stage3.json"))
picks = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/rb_oct27_picks_b.json"))}

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
          open("tmp-run/rb_oct27_marktvorm.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(uit)} wedstrijden geteld, {len(fouten)} fout(en)")
for k, v in fouten.items():
    print("  FOUT", k, v)

print("\n=== DE DRIE GEPUBLICEERDE REGELS VAN RUN B ===")
for naam, p in picks.items():
    b = uit.get(naam)
    if not b:
        print(f"\n{naam}: GEEN BLOK"); continue
    lijn = None
    if p["market"] == "Over/Under":
        ruw = float(p["selection"].split()[-1])
        lijn = 3.5 if ruw == 3.0 else ruw
        if lijn not in {float(x) for x in b["lines"]}:
            lijn = min((float(x) for x in b["lines"]), key=lambda x: abs(x - lijn))
    onder = p["selection"].startswith("Under")
    print(f"\n{naam} — {p['market']} {p['selection']} @{p['odds']:.4f} "
          f"(model: {p['my_prob']*100:.1f}%)" + (f"  [geteld op lijn {lijn:g}]" if lijn else ""))
    for rol in ("home", "away"):
        t = b["teams"][rol]
        for sleutel, label in (("lopend_recent", "laatste 5"), ("lopend", "lopend seizoen"),
                               ("lopend_kant", "thuis" if rol == "home" else "uit"),
                               ("vorig", "vorig seizoen")):
            d = t[sleutel]
            if not d["found"]:
                print(f"   {t['team']:24s} {label:16s} speelde die competitie niet")
                continue
            if not d["n"]:
                continue
            n = d["n"]
            regel = f"   {t['team']:24s} {label:16s} n={n:2d}  "
            if lijn is not None:
                boven = d["over"][str(lijn)]
                aantal = n - boven if onder else boven
                woord = f"onder {lijn:g}" if onder else f"boven {lijn:g}"
                regel += f"{woord}: {aantal:2d} ({100*aantal/n:3.0f}%)  "
            regel += (f"BTTS: {d['btts']:2d} ({d['btts_pct']:3.0f}%)  "
                      f"gem. {d['goals_per_match']:.2f}")
            print(regel)

# --- in data/run-state/ ---
STATE = f"data/run-state/2026-10-27-run-{RUN}.json"
st = json.load(open(STATE))
gezet = 0
for comp, blok in st["competitions"].items():
    for m in blok.get("matches") or []:
        b = uit.get(m.get("match"))
        if b:
            m["marktvorm"] = b
            gezet += 1
st["marktvorm_toegevoegd"] = (
    "Vaste stap sinds 17 okt 2026 (§6b-5h), hier gezet NA het publiceren van deze run. Dit blok "
    "is een TELLING en verandert niets: geen pick, geen my_prob, geen edge, geen rangorde en geen "
    "regel in picks.jsonl. Een herberekening van 27 oktober geeft daarom exact dezelfde drie "
    "regels als de run zelf gaf. Zie _shared-rules.md §4, 'Hoe vaak ging deze markt eerder op?'. "
    "LET OP BIJ VIRTUS ENTELLA - AVELLINO: de telling SPREEKT de gepubliceerde 'beide ploegen "
    "scoren - nee' TEGEN (beide ploegen op 62% BTTS dit seizoen, en in de laatste vijf duels 60% "
    "respectievelijk 80%). Dat hoort vooraan in de why-tekst en niet in een voetnoot (§4 punt 2).")
json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nmarktvorm-blok op {gezet} wedstrijden in run-state gezet")
