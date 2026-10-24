"""Run A, 24 okt 2026 — de per-wedstrijdsecties en de drie tabellen van het runrapport.

Waarom dit een script is en geen handwerk: met 10 duels is overtypen de duurste fout die er
te maken valt, en §5 eist per wedstrijd het outputformat met de cijfers per poort. Alles
hieronder komt uit `ra_oct24_results.json` en `ra_oct24_picks_a.json`; de verhalende delen van
het rapport (branchaudit, bevinding, bronstatus) staan in het rapport zelf en niet hier.
"""
import json

res = json.load(open("tmp-run/ra_oct24_results.json"))
picks = {p["home"] + " – " + p["away"]: p for p in json.load(open("tmp-run/ra_oct24_picks_a.json"))}
top = json.load(open("tmp-run/ra_oct24_top_a.json"))
cups = json.load(open("tmp-run/ra_oct24_cups.json"))["cups"]
s3 = json.load(open("tmp-run/ra_oct24_stage3.json"))
_state = json.load(open("data/run-state/2026-10-24-run-a.json"))
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
out.append("**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 55 (vrijdag, vr-zo). 13 duels in "
           "het venster en alle dertien doorgerekend: er is vandaag geen enkel duel op "
           "`NONE`, en dat is voor Run A in weken niet voorgekomen. De marge op de cap is "
           "dus 42 duels — de ruimste in weken, waar het gisteren nog vier duels scheelde. "
           "Zeven duels zijn `FULL`; de zes andere hebben een ploeg die niet in de stand van "
           "2025/2026 staat en zijn via `scripts/promotion.py` omgerekend, wat per definitie "
           "`LIGHT` geeft (Ipswich Town, Monza, Málaga, Bolton Wanderers, Marítimo en "
           "Kortrijk — alle zes binnen `conversion_in_range`, dus geen van de zes strandt op "
           "de Coventry-val). Geen enkel duel is kruis-grens, dus `scripts/interleague.py` "
           "komt deze run niet aan de orde. Datarijkdom liep van 4.50 (Kortrijk – KV "
           "Mechelen, geen opstelling en geen selectiewaarde bij Fotmob) tot 7.50 (VfB "
           "Stuttgart – Borussia Mönchengladbach); er viel niets af door de cap, dus er is "
           "geen 'laagste die het haalde' en geen 'hoogste die afviel'.\n")

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
out.append("**Vier regels, en de lijst is niet door een grens afgekapt maar door een gebrek "
           "aan kandidaten.** `MAX_SHORTLIST` = 5 (vrijdag) en er zijn precies vier "
           "publiceerbare selecties — vier duels waarbij alle acht de andere poorten "
           "openstonden. `MAX_LIGHT_IN_SHORTLIST` = 2 raakt zijn bovengrens exact (twee "
           "`LIGHT`-regels van maximaal twee) maar heeft niets uitgesloten, want er was geen "
           "derde `LIGHT`-kandidaat; de reeks `lijstlengte` groeit vandaag dus niet. **Twee "
           "van de vier halen hun eigen lat**, en bij die twee staat `bet_beide` op TRUE: "
           "Randers FC – Brøndby IF, Under 3, +15,58 pp op `FULL` (ruw +15,56; lat 8,0, met "
           "poort 9 erbij 10,0) en Brest – Nice, Brest wint, +16,29 pp op `FULL` (ruw "
           "+16,27). **De andere twee staan onder hun lat van 16,0 pp en zijn op rangorde "
           "gepubliceerd** (§5b): Deportivo Alavés – Málaga, Over 2.5, +10,07 pp op `LIGHT`, "
           "en Ipswich Town – Nottingham Forest, Over 2.5, +8,41 pp op `LIGHT`. Dat hun lat "
           "op 16,0 staat en niet op 8,0 is geen willekeur maar de prijs van de omrekening: "
           "beide duels hebben een promovendus. Lees die twee dus als 'het beste van vandaag' "
           "en niet als een gevonden voordeel — §1g heeft op 552 afgerekende gevallen gemeten "
           "dat er GEEN drempel op de herijkte edge bestaat die geld oplevert, en dat het "
           "rendement het slechtst is bij de hóógste geclaimde edge. **En dat laatste is "
           "vandaag geen abstractie:** de twee regels die hun lat wél halen zijn precies de "
           "twee duels waar het model het verst van het Pinnacle-oordeel af staat (Brest "
           "+17,5 pp op de thuiszege, Randers +17,4 pp op P(Under 3)) — zie de bevindingen.\n")

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
BRON = {"1X2": "12 van 12 (allemaal beste prijs uit de bulk-`h2h`; alle twaalf spelende "
                "competities hebben een sportkey bij The Odds API)",
        "Asian Handicap": "12 van 12 (bulk `spreads`)",
        "Draw No Bet": "12 van 12 (de 0.0-lijn uit diezelfde `spreads`, gratis)",
        "Double Chance": "12 van 12 (de ±0.5-lijn uit diezelfde `spreads`, gratis)",
        "Over/Under": "12 van 12 (bulk `totals`)",
        "BTTS": "10 van de 13 duels, namelijk alle duels met een kandidaat-edge (2 credits per duel); de drie zonder — Vitória de Guimarães – Marítimo, Kortrijk – KV Mechelen en Motor Lublin – Zagłębie Lubin — staan als ‘niet opgevraagd, geen kandidaat-edge’ in markets_checked en niet als gat"}
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
out.append(f"{rows} regels over 13 duels, en de rest telt als volgt op. TWEE duels hebben "
           f"een `near_miss` die NIET in deze tabel staat omdat de sterkste afgewezen kandidaat "
           f"daar de gepubliceerde bet zelf is geworden (Deportivo Alavés – Málaga en Ipswich "
           f"Town – Nottingham Forest; die staan in de run-state als `near_miss_gepubliceerd`, "
           f"want een andere selectie van een duel waarop is gepubliceerd is dezelfde mening en "
           f"geen afgewezen kandidaat — §1a, §6d). En {GEEN_NM} duels hebben er helemaal geen: "
           f"bij Vitória de Guimarães – Marítimo, Kortrijk – KV Mechelen en Motor Lublin – "
           f"Zagłębie Lubin bleef de sterkste kandidaat onder de NEAR-ondergrens (6,0 pp op "
           f"`LIGHT`, 3,0 pp op `FULL`) — precies de drie duels die ook geen BTTS kregen, want "
           f"geen kandidaat-edge — en bij Randers FC – Brøndby IF en Brest – Nice stonden alle "
           f"negen poorten open, dus daar is niets afgewezen om te melden. De ene poort-8-rij "
           f"(Go Ahead Eagles – Telstar, Telstar wint @5.508, marktkans 18,3%) staat niet in "
           f"deze tabel maar als eigen categorie `underdog` in het schaduwlogboek; de Over 3.25 "
           f"van datzelfde duel, die op de tweede methode afviel, staat hier wel. Er is vandaag "
           f"geen enkel duel op `NONE`, dus er is ook geen regel die ontbreekt omdat er niets "
           f"is doorgerekend.\n")

# ---------------------------------------------------------------- per wedstrijd
out.append("## Wedstrijden\n")
out.append("De 13 duels in het inzetvenster, op aftraptijd. De vier gepubliceerde regels "
           "staan in het volledige format van §5; bij de andere negen staat de reden in één "
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

open("tmp-run/ra_oct24_rapport_secties.md", "w").write("\n".join(out))
print(f"{len(out)} regels weggeschreven naar tmp-run/ra_oct24_rapport_secties.md")
