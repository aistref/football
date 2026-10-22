"""Run A, 20 okt 2026 — de per-wedstrijdsecties en de drie tabellen van het runrapport.

Waarom dit een script is en geen handwerk: met 10 duels is overtypen de duurste fout die er
te maken valt, en §5 eist per wedstrijd het outputformat met de cijfers per poort. Alles
hieronder komt uit `ra_oct22_results.json` en `ra_oct22_picks_a.json`; de verhalende delen van
het rapport (branchaudit, bevinding, bronstatus) staan in het rapport zelf en niet hier.
"""
import json

res = json.load(open("tmp-run/ra_oct22_results.json"))
picks = {p["home"] + " – " + p["away"]: p for p in json.load(open("tmp-run/ra_oct22_picks_a.json"))}
top = json.load(open("tmp-run/ra_oct22_top_a.json"))
cups = json.load(open("tmp-run/ra_oct22_cups.json"))["cups"]
s3 = json.load(open("tmp-run/ra_oct22_stage3.json"))
_state = json.load(open("data/run-state/2026-10-22-run-a.json"))
GNP = {m["match"]: m["gekwalificeerd_niet_gepubliceerd"]
       for c in _state["competitions"].values() for m in (c.get("matches") or [])
       if m.get("gekwalificeerd_niet_gepubliceerd")}

GATE_NL = {"edge": "edge", "robuustheid": "robuustheid", "tweede_methode": "tweede methode",
           "odds": "odds", "data": "data", "context": "context", "underdog": "underdog (poort 8)",
           "doelpunten_onder": "Under-lat (poort 9)",
           "herijking": "herijking", "herijking_omgekeerd": "herijking (omgekeerd)",
           "lijstlengte": "lijstlengte"}


def _eigen_raw(m, p):
    """De RUWE kans van de GEPUBLICEERDE selectie zelf.

    Tot 18 okt 2026 stond hier `m["near_miss"]["my_raw"]`, en dat is de ruwe kans van een
    ANDERE selectie van hetzelfde duel — de sterkste afgewezen kandidaat. Op 19 oktober gaf dat
    bij Monza - Cagliari "ruw 50.7%" waar de gepubliceerde BTTS-selectie zelf op 54.0% staat, en
    bij Viborg - FC Midtjylland "ruw 56.3%" waar het 43.5% is. Stille faalvorm: de twee getallen
    zien er allebei plausibel uit en niets klaagt. Zoek het dus op in all_candidates.
    """
    for c in m.get("all_candidates") or []:
        if c["market"] == p["market"] and c["selection"] == p["selection"]:
            return c.get("my_raw")
    return None


out = []

# ---------------------------------------------------------------- dekkingsrapportage
out.append("## Dekkingsrapportage\n")
out.append("| Competitie | Status | Toelichting |")
out.append("|---|---|---|")
per_comp = {}
for m in res["matches"]:
    per_comp.setdefault(m["competition"], []).append(m)
for comp in s3["fixtures"]:
    ms = per_comp.get(comp)
    if not ms:
        eerste = None
        out.append(f"| {comp} | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |")
        continue
    tiers = {}
    for m in ms:
        tiers[m["tier"]] = tiers.get(m["tier"], 0) + 1
    tt = ", ".join(f"{v}× `{k}`" for k, v in sorted(tiers.items()))
    bets = sum(1 for m in ms if (m["home"] + " – " + m["away"]) in picks)
    out.append(f"| {comp} | GEANALYSEERD | {len(ms)} duels ({tt}), {bets} gepubliceerde regel(s) |")
for comp, v in cups.items():
    out.append(f"| {comp} | GEEN WEDSTRIJD | eerstvolgende ronde {v.get('eerste_ronde')} "
               f"(UK-tijd), buiten het venster; {v.get('teamparen')} teamparen op de "
               f"fixturepagina, dus de slug is goed en de bron heeft niet gefaald |")
out.append("")
out.append("**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 40 (donderdag, ma-do). 36 duels "
           "in het venster, waarvan 23 doorgerekend en 13 op `NONE`. Dat is de krapste "
           "marge die Run A tot nu toe heeft gehad: vier duels onder de cap. Alle 36 duels "
           "zijn kruis-grens, dus alle 36 lopen langs `scripts/interleague.py`; de dertien "
           "op `NONE` vallen in twee groepen — elf waarvoor het LAND geen gemeten Europese "
           "competitiefactor heeft (Armenië, Slovenië, Kazachstan, Litouwen, Georgië, "
           "Andorra, Letland, Albanië, Bosnië, Finland, Gibraltar), en drie waar de "
           "omgerekende sterkte BUITEN het gemeten bereik valt (OFI Crete, CSKA Sofia, "
           "Mjällby). Eén geval staat los: Torreense speelt in Liga Portugal 2 en niet in "
           "de hoogste divisie waarop de factor is gemeten. Datarijkdom liep van 4.33 tot "
           "6.17 over de doorgerekende duels; er viel niets af door de cap, dus er is geen "
           "'laagste die het haalde' en geen 'hoogste die afviel'.\n")

# ---------------------------------------------------------------- topselectie
out.append("## Topselectie (§5b — rangorde over de hele runlijst)\n")
out.append("| # | Bet | Koers | Kans | Edge | Score | Tier | Risico | Status |")
out.append("|---|---|---|---|---|---|---|---|---|")
RISK = {"FULL": "Medium", "LIGHT": "High"}
for i, r in enumerate(top["herijkt"], 1):
    out.append(f"| {i} | {r['match']} — {r['market']}: {r['selection']} | {r['odds']:.4f} | "
               f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']:.3f} | "
               f"`{r['tier']}` | {RISK[r['tier']]} | {r['status']} |")
out.append("")
out.append("**Beide gepubliceerde regels halen hun eigen lat van 16,0 pp, en beide ook "
           "op de ruwe schaal** (`bet_beide` = TRUE): Braga – Gent, Over 2.5, +23,19 pp "
           "(ruw +22,72), en Omonia Nicosia – Benfica, Under 3, +20,34 pp (ruw +19,85). Bij "
           "beide staan alle negen poorten open. **De lijst is twee regels lang en niet "
           "drie, en dat is niet de drempel maar `MAX_LIGHT_IN_SHORTLIST` = 2** (§0): er is "
           "vandaag geen enkel `FULL`-duel, want alle 36 wedstrijden zijn kruis-grens en een "
           "omgerekende ploeg is nooit `FULL`. Die grens is vandaag DUUR. **Vijf** selecties "
           "haalden alle negen poorten én stonden boven hun eigen lat, en er passen er twee. "
           "De drie die afvallen staan hieronder per wedstrijd en gaan als "
           "`failed_gate = lijstlengte` het schaduwlogboek in (§5b, 26 sep 2026): Union "
           "St.Gilloise – Hapoel Beer Sheva (Under 3.5 @1.67, +16,57 pp, rang 3), Sturm Graz "
           "– Marseille (Marseille wint @2.0584, +17,32 pp, rang 4) en Celtic – Celta Vigo "
           "(Celta Vigo wint @2.5876, +16,66 pp, rang 5). Let op de volgorde: de rangorde "
           "loopt op `selection_score` (edge × kans × datafactor) en niet op edge, dus Sturm "
           "Graz staat met een HOGERE edge lager dan Union SG met een hogere kans. Lees de "
           "lijst niet als een gevonden voordeel: §1g heeft op 552 afgerekende gevallen "
           "gemeten dat er GEEN drempel op de herijkte edge bestaat die geld oplevert.\n")

out.append("### De ruwe dagranglijst (§5a) — een meting, geen tip\n")
out.append("| # | Bet | Koers | Kans | Ruwe edge | Score | Viel af op |")
out.append("|---|---|---|---|---|---|---|")
for i, r in enumerate(top["ruw"], 1):
    out.append(f"| {i} | {r['match']} — {r['market']}: {r['selection']} | {r['odds']:.4f} | "
               f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']:.3f} | "
               f"{r['status']} |")
out.append("")

# ---------------------------------------------------------------- marktbalans
out.append("## Marktbalans (§5, verplicht)\n")
mk = {}
for m in res["matches"]:
    for c in m.get("all_candidates") or []:
        mk[c["market"]] = mk.get(c["market"], 0) + 1
bet_mk = {}
for p in picks.values():
    bet_mk[p["market"]] = bet_mk.get(p["market"], 0) + 1
BRON = {"1X2": "2 van 2 (allemaal beste prijs uit de bulk; beide spelende competities "
               "hebben een sportkey)",
        "Asian Handicap": "2 van 2 (bulk `spreads`)",
        "Draw No Bet": "2 van 2 (de 0.0-lijn uit diezelfde `spreads`, gratis)",
        "Double Chance": "2 van 2 (de ±0.5-lijn uit diezelfde `spreads`, gratis)",
        "Over/Under": "2 van 2 (bulk `totals`)",
        "BTTS": "19 van de 20 duels met een kandidaat-edge (2 credits per duel); FK Crvena Zvezda – FC København stond niet in de spreads-respons en kon niet op event-id worden opgevraagd"}
out.append("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
out.append("|---|---|---|---|")
for markt in ("1X2", "Asian Handicap", "Draw No Bet", "Double Chance", "Over/Under", "BTTS"):
    out.append(f"| {markt} | {BRON[markt]} | {mk.get(markt, 0)} | {bet_mk.get(markt, 0)} |")
out.append(f"| **totaal** | | **{sum(mk.values())}** | **{sum(bet_mk.values())}** |")
out.append("")

# ---------------------------------------------------------------- net niet
out.append("### Net niet\n")
out.append("| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |")
out.append("|---|---|---|---|---|---|")
rows = 0
for m in res["matches"]:
    nm = m.get("near_miss") or m.get("near_miss_gepubliceerd")
    if not nm:
        continue
    if (m["home"] + " – " + m["away"]) in picks:
        continue
    def f(x):
        return "—" if x is None else f"{x:+.2f} pp"
    out.append(f"| {m['match']} | {nm['market']} @ {nm['odds']:.4f} | {f(nm.get('edge_xg'))} | "
               f"{f(nm.get('edge_split'))} | {f(nm.get('edge_robust_min'))} | "
               f"{GATE_NL.get(nm.get('failed_gate'), nm.get('failed_gate'))} |")
    rows += 1
out.append("")
GEEN_NM = len([m for m in res["matches"]
               if not (m.get("near_miss") or m.get("near_miss_gepubliceerd"))])
out.append(f"{rows} regels. Van de 10 duels hebben {GEEN_NM} geen `near_miss`. Bij "
           f"Inter – Shakhtar Donetsk en Real Betis – Feyenoord bleef de sterkste kandidaat "
           f"onder de NEAR-ondergrens van 6,0 pp op `LIGHT` en is er dus niets om te melden. "
           f"Bij Bayern München – Arsenal is er geen kandidaat omdat het duel op `NONE` staat "
           f"en geen enkele markt is doorgerekend. En bij Real Madrid – RB Leipzig en Aston "
           f"Villa – Viking is de sterkste selectie juist de gepubliceerde bet: een andere "
           f"selectie van een duel waarop is gepubliceerd is dezelfde mening en geen "
           f"afgewezen kandidaat (§1a, §6d). De drie poort-8-rijen (Aston Villa – Viking, "
           f"Club Brugge – Lens en Real Madrid – RB Leipzig) staan niet in deze tabel maar "
           f"als eigen categorie `underdog` in het schaduwlogboek; voor Club Brugge staat "
           f"hier wel de Under-kandidaat die daarnaast afviel op edge.\n")

# ---------------------------------------------------------------- per wedstrijd
out.append("## Wedstrijden\n")
out.append("De 10 duels in het inzetvenster, op aftraptijd. De twee gepubliceerde regels "
           "staan in het volledige format van §5; bij de andere acht staat de reden in één "
           "regel, met de cijfers per poort in de tabel \"Net niet\" hierboven.\n")
for m in sorted(res["matches"], key=lambda m: (m["kickoff_utc"], m["match"])):
    naam = m["home"] + " – " + m["away"]
    p = picks.get(naam)
    out.append(f"### {m['match']} · {m['kickoff_nl']} NL · {m['competition']}")
    if p:
        src = p["odds_source"]
        out.append(f"- **Data:** `{m['tier']}` · datarijkdom {m['richness']}")
        out.append(f"- **Bet:** {p['market']} — {p['selection']} — Odds: best "
                   f"**{p['odds']:.4f}** ({src})")
        out.append(f"- **Implied prob:** {p['implied_prob']*100:.1f}%  •  **My prob:** "
                   f"{p['my_prob']*100:.1f}%  (ruw {_eigen_raw(m, p)*100:.1f}%)"
                   if _eigen_raw(m, p) is not None else
                   f"- **Implied prob:** {p['implied_prob']*100:.1f}%  •  **My prob:** "
                   f"{p['my_prob']*100:.1f}%")
        out.append(f"- **Edge:** {p['edge_pp']:+.2f} pp  •  **Confidence:** {p['confidence']}")
        lam = (m.get("lambdas") or {})
        out.append(f"- **Doelverwachting:** xG-methode {lam['xg'][0]:.3f} / {lam['xg'][1]:.3f} · "
                   f"splitsmethode {lam['split'][0]:.3f} / {lam['split'][1]:.3f}"
                   + (f" · Understat {m['understat']['lambdas'][0]:.3f} / "
                      f"{m['understat']['lambdas'][1]:.3f}" if m.get("understat") else ""))
        out.append(f"- **Inputs:** " + " · ".join(p["prob_sources"][:3]))
        out.append(f"- **Onderbouwing:** {p['notes']}")
    elif m["match"] in GNP:
        g = GNP[m["match"]]
        lam = (m.get("lambdas") or {})
        out.append(f"- **Data:** `{m['tier']}` · datarijkdom {m['richness']}")
        out.append(f"- **GEKWALIFICEERD, NIET GEPUBLICEERD** — {g['market']} — "
                   f"{g['selection']} @ {g['odds']:.4f}, edge {g['edge_pp']:+.2f} pp, "
                   f"selection_score {g['score']}, rang {g['rang']} op de dagranglijst. "
                   f"{g['reden']}")
        if lam.get("xg"):
            out.append(f"- **Doelverwachting:** xG-methode {lam['xg'][0]:.3f} / "
                       f"{lam['xg'][1]:.3f} · splitsmethode {lam['split'][0]:.3f} / "
                       f"{lam['split'][1]:.3f}")
    else:
        out.append(f"- **Data:** `{m['tier']}`" + (f" · datarijkdom {m['richness']}"
                                                   if m["tier"] != "NONE" else ""))
        out.append(f"- **GEEN BET** — {m.get('reason', 'geen reden vastgelegd')}")
    out.append("")

open("tmp-run/ra_oct22_rapport_secties.md", "w").write("\n".join(out))
print(f"{len(out)} regels weggeschreven naar tmp-run/ra_oct22_rapport_secties.md")
