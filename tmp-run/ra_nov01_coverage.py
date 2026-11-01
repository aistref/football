"""Run A, 1 nov 2026 — de dekkingsprobe van deze run vastleggen in coverage.json.

`coverage.json` beschrijft wat een bron in PRINCIPE dekt; `source-health.json` wat er laatst
werkte. Deze notities horen dus hier: ze zeggen wat er per competitie te halen was en met welke
route het niveau is bepaald, zodat een volgende run dat niet opnieuw hoeft uit te zoeken.

GEGENEREERD uit `data/run-state/2026-11-01-run-a.json` in plaats van met de hand getypt. Dat was
op 31 oktober al de bedoeling — de docstring van `ra_oct31_coverage.py` zegt het — maar de
notities stonden daar als letterlijke tekst in een tabel, en dan is 'gegenereerd' een belofte en
geen eigenschap. Deze versie leest de run-state werkelijk uit, zodat de notitie niet kan
uiteenlopen met wat de run heeft gedaan (dezelfde regel als §6c over het dagrapport).
"""
import json, datetime
from collections import Counter

C = json.load(open("data/coverage.json"))
COMP = C["competitions"]
DAG = "2026-11-01"
ST = json.load(open(f"data/run-state/{DAG}-run-a.json"))
niveaus = ST.get("niveau") or {}
# De gepubliceerde regels komen uit picks_a.json en NIET uit `m["pick"]`: onder §5b publiceert de
# rangorde ook selecties die op de drempel sneuvelden, en bij die duels is `m["pick"]` None.
PICKS = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/ra_nov01_picks_a.json"))}

N = {}
for comp, blok in ST["competitions"].items():
    ms = blok.get("matches") or []
    if not ms:
        continue
    tiers = Counter(m["tier"] for m in ms)
    tiertekst = "/".join(f"{tiers[t]} {t}" for t in ("FULL", "LIGHT", "NONE") if tiers[t])
    lv = niveaus.get(comp) or {}
    basis = lv.get("avg_xg_per_match")
    regels = [f"Run A 1 nov 2026: {len(ms)} duel(s) in het venster, {tiertekst}."]
    if lv:
        regels.append(
            f"Basis 2025/2026 (xG beschikbaar: {str(lv.get('xg_available')).lower()}); lopend "
            f"seizoen op {lv.get('played', '?')} van {lv.get('length', '?')} speeldagen, route "
            f"{lv.get('source', '?')} (thuis {lv.get('home_goals_per_match'):.3f} / uit "
            f"{lv.get('away_goals_per_match'):.3f}, basis {basis:.3f}).")
    bets = [m for m in ms if m.get("bet")]
    if bets:
        for m in bets:
            p = PICKS.get(m["match"]) or {}
            regels.append(
                f"GEPUBLICEERD: {m['match']} {p.get('market')} {p.get('selection')} "
                f"@{p.get('odds'):.4f} ({p.get('edge_pp'):+.2f} pp, tier {p.get('data_tier')}, "
                f"bron {p.get('odds_source')}).")
    else:
        regels.append("GEEN bet.")
    # NORMALISEER DE REDEN VOOR JE TELT. Deed de vorige versie niet, en dan staat er
    # "1x edge onder drempel, 1x edge onder drempel, 1x edge onder drempel" omdat elke reden zijn
    # eigen getallen tussen haakjes meedraagt. Een telling die niet samenvoegt, telt niet.
    def kort(r):
        r = r.split(" — ")[0].split(" (")[0].strip()
        return {"edge niet robuust over het": "edge niet robuust over het (shrink, rho)-grid",
                "omrekening buiten het gemeten bereik": "data_tier NONE: omrekening buiten het "
                                                        "gemeten bereik"}.get(r, r)
    redenen = Counter(kort(m["reason"]) for m in ms
                      if not m.get("bet") and m.get("reason"))
    if redenen:
        regels.append("Afgevallen: " + ", ".join(
            f"{n}x {r}" for r, n in redenen.most_common()) + ".")
    omg = [m["match"] for m in ms if m.get("promovendi")]
    if omg:
        regels.append(f"{len(omg)} duel(s) met een omgerekende ploeg: " + ", ".join(omg) + ".")
    nones = [m["match"] for m in ms if m["tier"] == "NONE"]
    if nones:
        regels.append("OP NONE door conversion_in_range: " + ", ".join(nones) + ".")
    N[comp] = " ".join(regels) + " "

for comp, note in N.items():
    if comp not in COMP:
        print("ONBEKEND in coverage.json:", comp)
        continue
    COMP[comp]["notes"] = note
    COMP[comp]["last_checked"] = DAG
    print(f"{comp:30s} bijgewerkt ({len(note)} tekens)")

C["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(C, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("\ncoverage.json bijgewerkt.")
