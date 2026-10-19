"""Run A, 19 okt 2026 — de per-wedstrijdsecties en de drie tabellen van het runrapport.

Waarom dit een script is en geen handwerk: met 8 duels is overtypen de duurste fout die er te
maken valt, en §5 eist per wedstrijd het outputformat met de cijfers per poort. Alles hieronder
komt uit `ra_oct19_results.json` en `ra_oct19_picks_a.json`; de verhalende delen van het rapport
(branchaudit, bevinding, bronstatus) staan in het rapport zelf en niet hier.
"""
import json

res = json.load(open("tmp-run/ra_oct19_results.json"))
picks = {p["home"] + " – " + p["away"]: p for p in json.load(open("tmp-run/ra_oct19_picks_a.json"))}
top = json.load(open("tmp-run/ra_oct19_top_a.json"))
cups = json.load(open("tmp-run/ra_oct19_cups.json"))["cups"]
s3 = json.load(open("tmp-run/ra_oct19_stage3.json"))

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
out.append("**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 40 (maandag, ma-do). 8 duels in het "
           "venster en alle 8 doorgerekend: er is vandaag geen enkel duel op `NONE`. Datarijkdom "
           "liep van 5.0 (Trabzonspor – Beşiktaş) tot 6.0 (vijf duels); er viel niets af, dus er "
           "is geen 'laagste die het haalde' en geen 'hoogste die afviel'.\n")

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
out.append("**Eén van de drie haalt zijn eigen lat, en ook op de ruwe schaal** (`bet_beide` = "
           "TRUE): Trabzonspor – Beşiktaş, Draw No Bet op Beşiktaş, +9,49 pp op een FULL-lat van "
           "8,0 (ruw +9,00). De twee andere staan op rangorde onder hun lat: Viborg – FC "
           "Midtjylland BTTS nee op +5,35 pp tegen een FULL-lat van 8,0, en Monza – Cagliari "
           "BTTS nee op +7,18 pp tegen een LIGHT-lat van 16,0. Beide staan boven de "
           "NEAR-ondergrens die §5b als vloer gebruikt (3,0 op `FULL`, 6,0 op `LIGHT`) en bij "
           "alle drie staan alle negen poorten open. Er stond dus ÉÉN selectie boven de drempel "
           "en er passen DRIE regels in de lijst van een maandag, dus de drempel is vandaag geen "
           "afkapping (§5b stap 5) en er valt geen gekwalificeerde selectie op de lijstlengte: er "
           "is geen `lijstlengte`-rij in het schaduwlogboek van vandaag.\n")

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
BRON = {"1X2": "7 van 7 (allemaal beste prijs uit de bulk; geen enkele competitie zonder sportkey)",
        "Asian Handicap": "7 van 7 (bulk `spreads`)",
        "Draw No Bet": "7 van 7 (de 0.0-lijn uit diezelfde `spreads`, gratis)",
        "Double Chance": "7 van 7 (de ±0.5-lijn uit diezelfde `spreads`, gratis)",
        "Over/Under": "7 van 7 (bulk `totals`)",
        "BTTS": "8 van 8 duels met een kandidaat-edge (1 credit per duel)"}
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
out.append(f"{rows} regels. Van de 8 duels hebben {GEEN_NM} geen `near_miss`: bij Tottenham "
           f"Hotspur – Coventry City en Braga – Gil Vicente staat de sterkste afgewezen kandidaat "
           f"niet hier maar als eigen categorie `underdog` in het schaduwlogboek (poort 8), en bij "
           f"Trabzonspor – Beşiktaş is de sterkste selectie juist de gepubliceerde bet. "
           f"Monza – Cagliari en Viborg – FC Midtjylland hebben er wél een, maar die is hierboven "
           f"weggelaten omdat die duels een gepubliceerde regel hebben: een andere selectie van "
           f"een duel waarop is gepubliceerd is dezelfde mening en geen afgewezen kandidaat "
           f"(§1a, §6d). Er is vandaag geen duel op `NONE`, dus dat is hier niet de reden.\n")

# ---------------------------------------------------------------- per wedstrijd
out.append("## Wedstrijden\n")
out.append("De 8 duels in het inzetvenster, op aftraptijd. De drie gepubliceerde regels staan "
           "in het volledige format van §5; bij de andere vijf staat de reden in één regel, met "
           "de cijfers per poort in de tabel \"Net niet\" hierboven.\n")
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
    else:
        out.append(f"- **Data:** `{m['tier']}`" + (f" · datarijkdom {m['richness']}"
                                                   if m["tier"] != "NONE" else ""))
        out.append(f"- **GEEN BET** — {m['reason']}")
    out.append("")

open("tmp-run/ra_oct19_rapport_secties.md", "w").write("\n".join(out))
print(f"{len(out)} regels weggeschreven naar tmp-run/ra_oct19_rapport_secties.md")
