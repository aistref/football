"""Run B, 28 okt 2026 — de doelpunten- en BTTS-frequenties bij de bets van vandaag.

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
res = json.load(open("tmp-run/rb_oct28_results.json"))
s3 = json.load(open("tmp-run/rb_oct28_stage3.json"))
picks = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/rb_oct28_picks_b.json"))}

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
          open("tmp-run/rb_oct28_marktvorm.json", "w"), ensure_ascii=False, indent=1)
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
STATE = f"data/run-state/2026-10-28-run-{RUN}.json"
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
    "regel in picks.jsonl. Een herberekening van 28 oktober geeft daarom exact dezelfde drie "
    "regels als de run zelf gaf. Zie _shared-rules.md §4, 'Hoe vaak ging deze markt eerder op?'. "
    "LET OP: DE TELLING SPREEKT ALLE DRIE DE GEPUBLICEERDE UNDERS OP MINSTENS EEN REEKS TEGEN, en "
    "dat hoort vooraan in de why-tekst en niet in een voetnoot (§4 punt 2). TORONTO FC - DC UNITED "
    "is het scherpste geval: Toronto kwam dit seizoen in zijn ZESTIEN THUISDUELS op gemiddeld 4,12 "
    "doelpunten en bleef daar maar 56% van de keren onder 3,5, en in ALLE ZESTIEN scoorden beide "
    "ploegen - een Under 3,5 is dus precies tegen het thuispatroon van deze ploeg in. Dat de "
    "reeksen van vorig seizoen de andere kant op wijzen (82% onder 3,5, gemiddeld 2,38) maakt het "
    "niet beter maar laat zien waar de modelkans vandaan komt: de teamsterktes komen voor de helft "
    "uit dat vorige seizoen (blend_seasons, k=8). SANTOS - PALMEIRAS: Santos bleef in zijn laatste "
    "vijf duels maar EEN keer onder 2,5 (20%) en beide ploegen scoorden in alle vijf; over het "
    "lopende seizoen is het 34%. Palmeiras wijst de andere kant op (80% in de laatste vijf). NEW "
    "YORK CITY FC - ATLANTA UNITED is het mildste geval: NYCFC zit dit seizoen op 74% onder 3,5, "
    "maar Atlanta bleef in zijn laatste vijf maar 20% onder die lijn, op gemiddeld 4,00 doelpunten "
    "- al staat Atlanta UIT wel op 73%.")

json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nmarktvorm-blok op {gezet} wedstrijden in run-state gezet")
