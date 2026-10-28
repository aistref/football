"""Run A, 28 okt 2026 — de twee ontbrekende sportkeys in het Stage 3-record zetten.

(Dit script is al uitgevoerd; het staat hier zodat de ingreep na te lopen is.)

`ra_oct28_stage3.py` en `ra_oct28_cupmatches.py` gaven voor de Scottish Premiership en de
League Cup `sportkey = None` mee, overgenomen van de run van 27 oktober. Beide sleutels bestaan
wél en zijn vandaag actief bevonden: `soccer_spl` (coverage.json noteert hem al sinds 9 sep 2026)
en `soccer_england_efl_cup` (staat sinds 10 aug 2026 in `oddsapi.SPORT_KEYS`). Zonder deze
correctie draaien elf van de 33 duels op het gratis marktgemiddelde terwijl de beste prijs te
koop is — §1a meet dat verschil op +1,84 procentpunt edge per selectie.

Het record wordt hier bijgewerkt in plaats van de hele Stage 3 opnieuw te draaien: de 33
contextblokken zijn al opgehaald en een tweede ronde Fotmob-verzoeken verandert daar niets aan.
"""
import json
FIX = {"Scottish Premiership (SCO)": "soccer_spl", "League Cup (ENG)": "soccer_england_efl_cup"}
s3 = json.load(open("tmp-run/ra_oct28_stage3.json"))
for naam, key in FIX.items():
    s3["fixtures"][naam]["sportkey"] = key
json.dump(s3, open("tmp-run/ra_oct28_stage3.json", "w"), ensure_ascii=False, indent=1)
ctx = json.load(open("tmp-run/ra_oct28_ctx.json"))
for c in ctx:
    if c["competition"] in FIX:
        c["sportkey"] = FIX[c["competition"]]
json.dump(ctx, open("tmp-run/ra_oct28_ctx.json", "w"), ensure_ascii=False, indent=1, default=str)
