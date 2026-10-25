"""Run A, 25 okt 2026 — de per-wedstrijdsecties en de drie tabellen van het runrapport.

Waarom dit een script is en geen handwerk: met 46 duels is overtypen de duurste fout die er
te maken valt, en §5 eist per wedstrijd het outputformat met de cijfers per poort. Alles
hieronder komt uit `ra_oct25_results.json` en `ra_oct25_picks_a.json`; de verhalende delen van
het rapport (branchaudit, bevinding, bronstatus) staan in het rapport zelf en niet hier.
"""
import json

res = json.load(open("tmp-run/ra_oct25_results.json"))
picks = {p["home"] + " – " + p["away"]: p for p in json.load(open("tmp-run/ra_oct25_picks_a.json"))}
top = json.load(open("tmp-run/ra_oct25_top_a.json"))
cups = json.load(open("tmp-run/ra_oct25_cups.json"))["cups"]
s3 = json.load(open("tmp-run/ra_oct25_stage3.json"))
_state = json.load(open("data/run-state/2026-10-25-run-a.json"))
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
out.append("**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 55 (zondag, vr-zo). 46 duels in "
           "het venster en 44 ervan doorgerekend. De marge op de cap is dus NEGEN duels, "
           "ruimer dan gisteren (vier) maar krapper dan de weken ervoor. 36 duels zijn "
           "`FULL`; 10 hebben een ploeg die niet in de stand van 2025/2026 staat en zijn via "
           "`scripts/promotion.py` omgerekend, waarvan 8 op `LIGHT` uitkomen. TWEE duels "
           "komen op `NONE` uit: Hull City – Brentford en AC Horsens – Sønderjyske, beide "
           "omdat een ploeg buiten `conversion_in_range` valt — de Coventry-val, en de juiste "
           "uitkomst, want buiten het gemeten bereik is doorrekenen raden. Geen enkel duel is "
           "kruis-grens, dus `scripts/interleague.py` komt deze run niet aan de orde. "
           "Datarijkdom liep van 4.50 (Genk – Standard Liège en Union St.Gilloise – Cercle "
           "Brugge) tot 8.00 (Barcelona – Real Madrid en Manchester United – AFC "
           "Bournemouth); er viel niets af door de cap, dus er is geen 'laagste die het "
           "haalde' en geen 'hoogste die afviel'. De context is voor alle 46 duels opgehaald "
           "zoals §1c eist, met nul fouten.\n")

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
out.append("**Vijf regels, en voor het eerst in weken halen ze ALLE VIJF hun eigen lat.** "
           "`MAX_SHORTLIST` = 5 (zondag) en er zijn ZES duels met een publiceerbare "
           "selectie — zes duels waarbij alle acht de andere poorten openstonden en de edge "
           "boven de NEAR-ondergrens bleef. Er passen vijf regels in, dus er valt er precies "
           "één af. Alle vijf gepubliceerde regels staan op `FULL` en halen de lat van "
           "8,0 pp: Sunderland – Leeds United Over 2.5 (+13,19 pp, ruw +13,72), Real "
           "Sociedad – Levante Over 2.5 (+9,37 pp, ruw +10,09), NEC Nijmegen – FC Groningen "
           "Over 3.5 (+11,14 pp, ruw +11,68), Manchester United – AFC Bournemouth Over 2.5 "
           "(+9,45 pp, ruw +10,15) en Lecce – Juventus BTTS 'nee' (+9,53 pp). Bij alle vijf "
           "staat `bet_beide` op TRUE. Dat is het tegenovergestelde van gisteren, toen drie "
           "van de vijf hun lat haalden en twee `LIGHT`-regels op rangorde werden "
           "gepubliceerd. **`MAX_LIGHT_IN_SHORTLIST` = 2 bindt NIET en kan niets uitsluiten:** "
           "er staat geen enkele `LIGHT`-regel in de lijst, want de enige `LIGHT`-kandidaat "
           "van de dag viel af op lijstlengte. "
           "**En die ene afvaller is het spiegelbeeld van de uitkomst van gisteren:** Śląsk "
           "Wrocław – Wieczysta Kraków, Over 3.5 @2.4308, +17,12 pp op `LIGHT` — ruim boven "
           "zijn eigen lat van 16,0 pp — staat op rang 6 en haalt de lijst niet. Gisteren "
           "vielen juist twee `LIGHT`-regels ONDER hun lat de lijst in terwijl een `FULL` "
           "boven zijn lat eraf viel. Beide uitkomsten volgen uit §5b plus `selection_score`: "
           "er staan zes selecties boven hun eigen lat en er passen er vijf, dus de drempel "
           "bindt hier WEL als grens, maar hij snijdt alle zes door en dan beslist de "
           "rangorde alsnog — en in `selection_score` verslaat +9,53 pp op `FULL` (5,946) een "
           "+17,12 pp op `LIGHT` × 0,5 (4,987). Lees de lijst dus als 'het beste van vandaag' "
           "en niet als een gevonden voordeel: §1g heeft op 552 afgerekende gevallen gemeten "
           "dat er GEEN drempel op de herijkte edge bestaat die geld oplevert, en dat het "
           "rendement het slechtst is bij de hóógste geclaimde edge. Zie bevinding 2.\n")

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
BRON = {"1X2": "12 van 12 — 11 op de beste prijs uit de bulk-`h2h`, en de Scottish "
                "Premiership (2 duels) op het gratis BetExplorer-MARKTGEMIDDELDE, want die "
                "competitie heeft geen sportkey bij The Odds API; daar is de bookmaker niet "
                "herleidbaar en valt de edge systematisch te laag uit (§1a)",
        "Asian Handicap": "11 van 12 (bulk `spreads`; geen spreads voor de Scottish Premiership)",
        "Draw No Bet": "11 van 12 (de 0.0-lijn uit diezelfde `spreads`, gratis)",
        "Double Chance": "11 van 12 (de ±0.5-lijn uit diezelfde `spreads`, gratis)",
        "Over/Under": "11 van 12 (bulk `totals`; geen totals voor de Scottish Premiership)",
        "BTTS": "30 van de 32 duels met een kandidaat-edge (1 credit per duel). De twee die "
                "afvielen zijn Hibernian – Celtic en Motherwell – Heart of Midlothian: geen "
                "sportkey, dus geen event-id om de markt op op te vragen. De 12 duels zonder "
                "kandidaat-edge staan als 'niet opgevraagd — geen kandidaat-edge in dit duel' "
                "in `markets_checked` en niet als gat"}
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
# Tel uit de RUN-STATE en niet uit results.json: de `lijstlengte`-rij krijgt haar `near_miss`
# pas in `ra_oct25_publiceer.py` en staat in results.json dus nog zonder. Op 25 okt 2026 gaf dat
# 23 tegen 22 en liep de optelling in deze alinea één duel uit de pas.
GEEN_NM = len([m for c in _state["competitions"].values() for m in (c.get("matches") or [])
               if not (m.get("near_miss") or m.get("near_miss_gepubliceerd"))])
out.append(f"{rows} regels over 46 duels, en de rest telt als volgt op. GEEN ENKEL duel "
           f"heeft deze run een `near_miss_gepubliceerd`: bij de vijf duels van de "
           f"topselectie was de sterkste kandidaat de bet zelf en bleef er geen tweede "
           f"kandidaat boven de NEAR-ondergrens over. {GEEN_NM} duels hebben dus helemaal "
           f"geen `near_miss`, en die splitsen in drie groepen: de VIJF gepubliceerde duels, "
           f"de TWEE op `NONE` (Hull City – Brentford en AC Horsens – Sønderjyske, die niets "
           f"doorgerekend hebben om af te wijzen) en VIJFTIEN waar de sterkste kandidaat "
           f"onder de NEAR-ondergrens bleef (6,0 pp op `LIGHT`, 3,0 pp op `FULL`). De "
           f"VEERTIEN poort-8-rijen en de DRIE poort-9-rijen staan niet in deze tabel maar "
           f"als eigen categorie (`underdog`, `doelpunten_onder`) in het schaduwlogboek, en "
           f"de ene `lijstlengte`-rij (Śląsk Wrocław – Wieczysta Kraków, Over 3.5) net zo — "
           f"die drie categorieën zijn drie aparte populaties en mogen nooit bij `edge` "
           f"worden opgeteld (§1e, §1h, §5b).\n")

# ---------------------------------------------------------------- per wedstrijd
out.append("## Wedstrijden\n")
out.append("De 46 duels in het inzetvenster, op aftraptijd. De vijf gepubliceerde regels "
           "staan in het volledige format van §5; bij de andere 41 staat de reden in één "
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

open("tmp-run/ra_oct25_rapport_secties.md", "w").write("\n".join(out))
print(f"{len(out)} regels weggeschreven naar tmp-run/ra_oct25_rapport_secties.md")
