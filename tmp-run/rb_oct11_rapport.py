"""Het markdown-runrapport van Run B 11 okt 2026 opbouwen uit de vastgelegde data.

De mechanische delen — dekkingstabel, de 42 wedstrijdblokken, de "Net niet"-tabel, de
marktbalans en de twee dagranglijsten — komen hier uit `data/run-state/` en
`tmp-run/rb_oct11_results.json`, zodat ze niet worden overgetypt en niet uiteen kunnen lopen met
het dagrapport van §6c (dezelfde eis die §5 aan report.py stelt). De beschouwende secties staan
als tekst in dit script.
"""
import json
from collections import Counter

DAG = "2026-10-11"
SP = "/tmp/claude-0/-home-user-football/dfe99b0f-87d3-58b7-95b6-a5ee330069a3/scratchpad"
res = json.load(open("tmp-run/rb_oct11_results.json"))
state = json.load(open(f"data/run-state/{DAG}-run-b.json"))
top = json.load(open("tmp-run/rb_oct11_top_b.json"))
s3 = json.load(open("tmp-run/rb_oct11_stage3.json"))
ctx = {c["match_id"]: c for c in json.load(open("tmp-run/rb_oct11_ctx.json"))}
picks = json.load(open("tmp-run/rb_oct11_picks_b.json"))
RUNLIJST = list(s3["fixtures"].keys())
PUB = {p["home"] + " – " + p["away"] for p in picks}

L = []
def w(s=""): L.append(s)
def pp(v): return "—" if v is None else f"{v:+.2f} pp"
def koers(v): return "—" if v is None else f"{round(float(v), 4):g}"

# ---------------------------------------------------------------- kop
w(f"# Run B — {DAG}")
w()
w("**Gestart:** 05:06 CEST · **Afgerond:** 05:40 CEST · **Looptijd:** 35 minuten · "
  "**Bets gepubliceerd:** 5 · "
  "**Wedstrijden diep geanalyseerd:** 42 van 42 in het inzetvenster "
  "(39 met een kansbron, 0 afgekapt door `MAX_DEEP_ANALYSES` = 55)")
w()
w("**Dagrapport (§6c):** https://claude.ai/artifact/7onP7DrDTQJofsmpRsxY3A")
w()
w("**Branches: deze run staat op `main`.** Stage -2 is volledig gedraaid vóór het lezen van de "
  "regels, en het verliep in twee stappen die het waard zijn om op te schrijven, want de eerste "
  "stap gaf precies het valse alarm waar Stage -2 voor waarschuwt.")
w()
w("1. **Ondiepe kloon.** `git rev-parse --is-shallow-repository` gaf `true`. De eerste meting op "
  "de commitgraaf wees daarom **48 van de 59 takken** aan met \"eigen\" commits — tot 409 stuks, "
  "en netjes aflopend met de leeftijd van de tak, wat het patroon van een ontbrekende "
  "gemeenschappelijke voorouder is en niet van echt werk. `git merge-base` gaf voor al die "
  "takken niets terug.")
w("2. **Na `git fetch --unshallow`** (`main` van 61 naar 524 commits) staat de teller voor "
  "**alle 59 takken op 0**. Het alarm was dus volledig een artefact van de ondiepe kloon — exact "
  "het geval dat Stage -2 beschrijft, inclusief de orde van grootte.")
w()
w("Daarna de controle die wél iets zegt: `python3 scripts/branchaudit.py`, **per record op de "
  "inhoud** en niet op de graaf. Uitkomst over 58 takken: `picks.jsonl` 377, `shadow.jsonl` 976, "
  "`context-log.jsonl` 1028, `calibration.jsonl` 4464, `source-health.json` 112 bladpaden en "
  "`coverage.json` 301 — **alle zes VOLLEDIG**. De enige afwijking is `sources.oddspapi` op een "
  "oudere tak, en dat is het bekende besluit van 30 augustus 2026 (OddsPapi verwijderd na de "
  "overstap naar het 20K-creditplan), geen verlies. Er valt dus niets te verenigen.")
w()
w("**Wat er wél te mergen viel kwam pas tijdens de run.** Run C pushte om 03:18 UTC naar `main` "
  "terwijl deze run al liep, en de eerste push botste. Opgelost zoals §6a voorschrijft — opnieuw "
  "fetchen, mergen volgens de conflictregels van Stage -2 (**vereniging per record** op "
  "`picks.jsonl` en `shadow.jsonl`, afgewikkeld wint van `pending`), en nog een keer pushen. "
  "Nooit geforceerd. Run C had 0 bets en 0 schaduwrijen, dus de vereniging is onze eigen stand: "
  "382 picks en 1000 schaduwrijen.")
w()
w("**Openstaande picks van een onafgewikkelde tak:** geen. De vijf picks die `ledger.py open` "
  "als openstaand meldt zijn de vijf van Run A van vanmorgen, met een negatieve tijd sinds de "
  "aftrap (−10,4 tot −16,4 uur) omdat die duels vandaag nog gespeeld worden.")
w()

# ---------------------------------------------------------------- dekking
w("## Dekkingsrapportage")
w()
w("| Competitie | Status | Toelichting |")
w("|---|---|---|")
for comp in RUNLIJST:
    blok = state["competitions"].get(comp) or {}
    ms = blok.get("matches") or []
    if not ms:
        w(f"| {comp} | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |")
        continue
    none = sum(1 for m in ms if m.get("tier") == "NONE")
    xg = (s3["stats"].get(comp, {}).get("prev") or {}).get("has_xg")
    deel = [f"{len(ms)} duel(s) in het venster",
            f"xG bij Fotmob: {'ja' if xg else 'nee (LIGHT, lat 16,0)'}"]
    if none:
        deel.append(f"{none} op data_tier NONE (geen gemeten divisiesprong)")
    w(f"| {comp} | GEANALYSEERD | {'; '.join(deel)} |")
w()
a = res["afkapping"]
w(f"**Afgekapt door `MAX_DEEP_ANALYSES`:** {a['afgekapt']} wedstrijden op een zondagcap van "
  f"{a['cap']}. De cap bond vandaag dus niet — 42 duels op 55 plekken. Spreiding van de "
  f"datarijkdom over de hele run: {a['laagste_richness_in_run']} tot "
  f"{a['hoogste_richness_in_run']}. Dat er niets is afgekapt hoort hier net zo expliciet te "
  "staan als een afkapping zelf: §3 Stage 4 verbiedt stille truncatie, en \"nul afgekapt\" is "
  "de uitspraak die dat verbod bevestigt.")
w()

# ---------------------------------------------------------------- bronstatus
w("## Bronstatus deze run")
w()
w("`python3 scripts/api_check.py`, letterlijk overgenomen zoals §3 eist:")
w()
w("```")
w("""=== The Odds API (odds per bookmaker) ===
  OK — 48 actieve voetbalcompetities beschikbaar.
  Quota: 19604 over, 396 gebruikt deze maand.

=== API-Football (statistieken) ===
  API_FOOTBALL_KEY niet gezet — overgeslagen.
  Dat is een besluit van de gebruiker (27 sep 2026), geen storing: hij wil hier geen
  geld aan uitgeven. De kanskant komt van Fotmob en Understat. Zie
  _shared-rules.md §3, 'API_FOOTBALL_KEY komt er niet'. Niet als actiepunt melden.

=== Samenvatting ===
  odds (prijzen)        OK
  statistieken (kansen) niet beschikbaar""")
w("```")
w()
w("**Geen sleutel afgewezen en geen sleutel ontbreekt onverwacht.** The Odds API accepteerde de "
  "sleutel; `API_FOOTBALL_KEY` ontbreekt met opzet sinds het besluit van 27 september 2026 en "
  "staat hier als boekhouding, niet als gat, niet als actiepunt en niet in de notificatie (§3). "
  "De kanskant komt dus volledig van **Fotmob**, en Fotmob leverde vandaag zonder één fout — dat "
  "is de enige voorwaarde waaronder dat besluit houdbaar is, en de uitzondering die §3 punt 3 "
  "beschrijft (Fotmob valt om) is vandaag niet aan de orde.")
w()
w("`python3 scripts/idcheck.py` — **afsluitcode 0**, alle 33 `fotmob_id`'s uit `coverage.json` "
  "leveren een bruikbare stand, ook die van de competities die vandaag stil zijn. Geen enkele "
  "competitie is stil uit de runlijst verdwenen. De vijf zonder xG staan er zoals verwacht in: "
  "Czech First League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189) "
  "en Keuken Kampioen Divisie (111).")
w()
w("| Bron | Status | Detail |")
w("|---|---|---|")
w("| fotmob | ok | 2 daglijsten (11 + 12 okt), `fetch_league_stats` voor 14 competities × 2 "
  "seizoenen, standen van de divisies eronder/erboven voor de omrekeningen, `matchDetails` voor "
  "alle 42 duels — **nul fouten** |")
w("| betexplorer | ok | 14 competitiepagina's, 130 fixturerijen; gratis 1X2-marktgemiddelde "
  "(§6e + poort 8) en de enige prijsbron voor de 4 competities zonder sportkey |")
w("| the_odds_api | ok | 19.604 van 20.000 credits over bij de start; 51 uitgegeven "
  "(10 bulk × 3 + 21 BTTS × 1) |")
w("| oddsapi | ok | sleutel geaccepteerd; `net_price` op elke beurskoers — vier van de vijf "
  "gepubliceerde regels staan op een beurs |")
w("| understat | ok | **niet aangeroepen** — dekt vijf competities die geen van alle op deze "
  "runlijst staan; per ontwerp een Run A-bron, geen storing |")
w("| api_football | missing_key | besluit van de gebruiker, 27 sep 2026 — geen gat, geen "
  "actiepunt, niet in de notificatie |")
w()
w("**Wijzigingen t.o.v. vorige run:** geen. De Cloudflare-bronnen (fbref, Forebet, FootyStats, "
  "PredictZ, Oddschecker) staan onveranderd dicht en zijn niet geprobeerd te omzeilen (§3).")
w()
w("Eén ding dat hier hoort omdat het van buitenaf niet te zien is: **`api_check.py` noemt van de "
  "tien gekochte competities maar drie** onder \"Relevante sportkeys\" "
  "(`soccer_spain_segunda_division`, `soccer_italy_serie_b`, `soccer_germany_bundesliga2`), en "
  "toch leverden alle tien events — Greek Super League 12, Eliteserien 8, Allsvenskan 6, Swiss "
  "Super League 3, Austrian Bundesliga 9, MLS 32, Série A 18. Die lijst is een handmatige "
  "selectie in het script en **geen uitspraak over wat de API aanbiedt**. Dat staat nu drie "
  "dagen op rij in het rapport en is daarmee een vaste waarneming geworden.")
w()

# ---------------------------------------------------------------- parameters
w("## Parameters en poorten deze run")
w()
w("| Parameter | Waarde |")
w("|---|---|")
w("| `MAX_DEEP_ANALYSES` | **55** (zondag) — bond **niet**: 42 duels, 0 afgekapt |")
w("| `MAX_SHORTLIST` | **5** (zondag) — bond: 5 regels, 1 gekwalificeerde selectie erbuiten |")
w("| `EDGE_THRESHOLD_FULL` / `_LIGHT` | 8.0 / 16.0 pp — sinds 20 sep een **afkapping** aan het "
  "eind (§5b), geen poort |")
w("| `MAX_LIGHT_IN_SHORTLIST` | 2 — bond niet; één van de vijf regels is LIGHT |")
w("| `MIN_ODDS` / `MAX_ODDS` | 1.30 / 6.00 — 14 selecties vielen hierop af |")
w("| `SHRINK` | 1.00 (sinds 19 sep, §6e) |")
w("| `XG_WEIGHT` | 0.80 |")
w("| `CREDIBILITY_K` | 8 |")
w("| Poort 8 (`UNDERDOG_FLOOR`) | **bindt**, lichte vorm, ondergrens 0.35; "
  "`sides.check(..., today=2026-10-11)` |")
w("| Herijking (§1g) | `a=1.008482, b=0.005494` op 4119 gevallen, `fitted_through=2026-10-10` |")
w()
w("**De herijking is praktisch de identiteit, maar hij wijst vandaag de ándere kant op dan de "
  "voorbeelden in §5a.** Deze fit **verhoogt** een kans boven ongeveer 40%, met +0,1 tot +0,3 pp, "
  "en telde dus edge bíj de vijf gepubliceerde regels op in plaats van eraf: 11,13 → 11,37 "
  "(Altach), 10,98 → 11,23 (St. Gallen), 17,39 → 17,66 (Lillestrøm), 8,91 → 9,12 (LASK) en "
  "7,71 → 7,94 (Palmeiras). Dat is precies het geval waarvoor §5a de `bet_beide`-vlag heeft "
  "gebouwd in plaats van op de redenering \"herijkt haalt de drempel, dus ruw ook\" te "
  "vertrouwen — en vandaag bindt die vlag ook echt: bij **Palmeiras – Corinthians** staat "
  "`bet_beide = False`, want die regel haalt de lat van 8,0 op **geen van beide** schalen (7,94 "
  "herijkt, 7,71 ruw). Hij is daarom gepubliceerd op rangorde met dat label erbij, niet als "
  "gevonden voordeel.")
w()
w("`fitted_through` staat op de vórige rundag, dus `calibration.py settle` is niet blijven "
  "liggen — de controle die §6b-5c sinds 30 september eist. Deze run wikkelde er zelf 9 af. "
  "Lees de identiteit zoals §1e punt 3 voorschrijft: de fit komt uit de **ongeselecteerde** "
  "ijksteekproef en is geen uitspraak over de staart die deze routine kiest; §6e meet daar nog "
  "+1,83 pp te veel kans op longshots en −3,58 pp te weinig op favorieten over 4473 uitkomsten.")
w()

# ---------------------------------------------------------------- wedstrijden
w("## Wedstrijden")
w()
w("Alle 42 duels in het inzetvenster, per competitie, in de volgorde van de runlijst. "
  "Aftraptijden in **NL-tijd** (`runwindow.kickoff_nl`, met echte zomertijd via `zoneinfo`).")
w()
for comp in RUNLIJST:
    blok = state["competitions"].get(comp) or {}
    ms = blok.get("matches") or []
    if not ms:
        continue
    w(f"### {comp}")
    w()
    for m in sorted(ms, key=lambda x: x.get("kickoff_utc") or ""):
        c = ctx.get(m.get("match_id"), {})
        ko = m.get("kickoff_nl") or c.get("kickoff_nl") or "?"
        sd = c.get("source_day")
        extra = " · *op de daglijst van 12 okt*" if sd == "2026-10-12" else ""
        w(f"#### {m['match']} · {ko} NL{extra}")
        w()
        w(f"- **Data:** {m.get('tier')}")
        gek = m.get("gekwalificeerd_niet_gepubliceerd")
        gepub = m["match"] in PUB
        if gepub:
            p = next(x for x in picks if x["home"] + " – " + x["away"] == m["match"])
            w(f"- **Bet:** {p['market']} — {p['selection']} — Odds: best "
              f"**{koers(p['odds'])}** ({p['odds_source']})")
            w(f"- **Implied prob:** {p['implied_prob']*100:.1f}% • **My prob:** "
              f"{p['my_prob']*100:.1f}%")
            w(f"- **Edge:** {pp(p['edge_pp'])} • **Confidence:** {p['confidence']}")
            cand = next((cc for cc in m.get("all_candidates", [])
                         if cc["market"] == p["market"] and cc["selection"] == p["selection"]), {})
            w(f"- **Per poort:** xG-model {pp(cand.get('edge_xg'))} · 2e methode "
              f"{pp(cand.get('edge_split'))} · zwakste stand van het (shrink, rho)-grid "
              f"{pp(cand.get('edge_robust_min'))} · ruwe edge {pp(cand.get('edge_raw'))} · "
              f"`bet_beide={cand.get('bet_beide')}`")
        elif gek:
            w(f"- **Gekwalificeerd, niet gepubliceerd:** {gek.get('market')} — "
              f"{gek.get('selection')} @ {koers(gek.get('odds'))}, {pp(gek.get('edge_pp'))}, "
              f"score {gek.get('score')}")
            w(f"- **Valt af op LIJSTLENGTE** — rang {gek.get('rang')} bij `MAX_SHORTLIST` = 5. "
              "Geen poort hield deze selectie tegen; ze gaat als "
              "`failed_gate = \"lijstlengte\"` het schaduwlogboek in (§5b).")
        else:
            w(f"- **GEEN BET** — {m.get('reason')}")
            nm = m.get("near_miss") or m.get("near_miss_gepubliceerd")
            if nm:
                w(f"- **Beste kandidaat:** {nm.get('market')} @ {koers(nm.get('odds'))} — "
                  f"xG-model {pp(nm.get('edge_xg'))}, 2e methode {pp(nm.get('edge_split'))}, "
                  f"zwakste stand {pp(nm.get('edge_robust_min'))}; viel af op "
                  f"`{nm.get('failed_gate')}`")
        lam = m.get("lambdas") or {}
        if lam.get("xg"):
            w(f"- **Doelverwachting:** xG-methode {lam['xg'][0]:.3f} / {lam['xg'][1]:.3f}"
              + (f" · splitsmethode {lam['split'][0]:.3f} / {lam['split'][1]:.3f}"
                 if lam.get("split") else ""))
        for kant, note in (m.get("promovendi") or {}).items():
            w(f"- **Omrekening ({kant}):** {note}")
        v = (m.get("context") or {}).get("venue") or {}
        if v.get("relocated"):
            w(f"- **Stadion:** {v.get('note')}")
        w()

# ---------------------------------------------------------------- topselectie
w("## Topselectie")
w()
w("Vijf regels op vijf plekken. Gerangschikt op `selection_score` = edge × kans × "
  "(FULL 1.0 | LIGHT 0.5), dezelfde formule waarmee binnen elke wedstrijd de markt is gekozen "
  "(§1a).")
w()
w("| # | Bet | Koers | Probability | Edge | Score | Risicoklasse | Waarom deze |")
w("|---|---|---|---|---|---|---|---|")
RISK = {
 "Altach – Wolfsberger AC": ("Medium",
   "Hoogste score van de dag en de enige regel die op álle drie de maten ruim boven de lat "
   "blijft: xG-methode +11,57, splitsmethode +9,37, zwakste stand van het grid +9,50. Die laatste "
   "is de hoogste van de lijst, dus deze regel hangt niet aan één instelling. Enige regel bij "
   "Pinnacle."),
 "St. Gallen – Lausanne": ("Medium",
   "Tweede op score, met de twee methodes eensgezind over richting én omvang (+10,28 / +13,80). "
   "Zwakste stand van het grid is +7,47 — net onder de lat, en dat is het zwakke punt."),
 "Lillestrøm – Molde": ("High",
   "Grootste edge van de dag (+17,66) maar op LIGHT-data, dus tegen een lat van 16,0: hij haalt "
   "die met 1,66 pp over. De twee methodes staan hier het verst uiteen van de hele lijst "
   "(+13,88 tegen +31,47) — dezelfde richting, factor twee in omvang."),
 "LASK – Rapid Wien": ("High",
   "De xG-methode komt hier zélf niet boven de lat (+7,58) en de zwakste stand van het grid "
   "evenmin (+7,58); dat de regel op +9,12 uitkomt, komt doordat de splitsmethode (+14,05) voor "
   "een vijfde meeweegt. Laagste koers van de vijf en daarmee de hoogste trefkans."),
 "Palmeiras – Corinthians": ("High",
   "Gepubliceerd op RANGORDE: +7,94 pp tegen een lat van 8,0, en ook ruw (+7,71) onder de lat. "
   "Zwakste stand van het grid is +1,62 pp — met afstand het laagste van de lijst, dus deze "
   "regel hangt wél aan de instellingen. Enige regel uit een competitie met een volle agenda "
   "(3 à 4 dagen rust)."),
}
for i, r in enumerate(top["herijkt"], 1):
    risk, why = RISK[r["match"]]
    w(f"| {i} | {r['match']} — {r['market']}: {r['selection']} | {koers(r['odds'])} | "
      f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']} | {risk} | {why} |")
w()
w("**Wat de zesde was en waarom hij er niet staat:** Catanzaro – Mantova, Asian Handicap "
  "Catanzaro −0.25 @2,09, **+8,61 pp** en daarmee bóven zijn lat, met alle acht de poorten open. "
  "Hij is niet door een poort tegengehouden maar door de lengte van de lijst — zie \"De "
  "lijstlengte bindt\" hieronder, want dat is vandaag een subtieler geval dan gisteren.")
w()
w("**Verdeling over de markten: vier Over/Under en één BTTS — de hele lijst is een "
  "doelpuntenmarkt.** Er staat geen enkele uitkomstmarkt in, terwijl 1X2, Asian Handicap, Draw "
  "No Bet en Double Chance samen 273 van de 447 doorgerekende selecties leveren. En de vijf "
  "wijzen alle vijf dezelfde kant op: minder doelpunten dan de markt verwacht. Zie Bevinding 3.")
w()

# ---------------------------------------------------------------- dagranglijsten
w("### De twee dagranglijsten (§5a)")
w()
w(f"`python3 scripts/toplist.py --run b --date {DAG}`. Beide lijsten geven één regel per "
  "wedstrijd. **Ze zijn vandaag niet identiek, en het verschil is informatief:** de ruwe lijst "
  "wordt aangevoerd door de twee selecties die poort 8 heeft tegengehouden (Grasshopper en "
  "Padova), want de ruwe lijst kent geen poorten. Drie van de vijf regels staan op beide "
  "lijsten, in dezelfde orde.")
w()
w("| # | Herijkt (hieruit komen de bets) | Ruw (wat de routine vóór 5 sep zou hebben gezien) |")
w("|---|---|---|")
for i in range(max(len(top["herijkt"]), len(top["ruw"]))):
    h = top["herijkt"][i] if i < len(top["herijkt"]) else None
    rw = top["ruw"][i] if i < len(top["ruw"]) else None
    fmt = lambda r: ("—" if not r else
                     f"{r['match']} — {r['selection']} @ {koers(r['odds'])} · "
                     f"{r['edge_pp']:+.2f} pp · score {r['score']}")
    w(f"| {i+1} | {fmt(h)} | {fmt(rw)} |")
w()
w("**Nul selecties sneuvelden alleen op §1g**, en dat kan ook niet anders bij een fit die "
  "verhoogt: de herijking maakt een kans vandaag groter, dus ze houdt niets tegen. Wat ze wél "
  "doet is een selectie die ruw onder de lat zit erboven tillen, en dát is waarom "
  "`bet_beide` bestaat — zie de parameters hierboven.")
w()

# ---------------------------------------------------------------- net niet
w("### Net niet")
w()
w("Elke afgewezen kandidaat met een echte edge, met het cijfer **per poort** — niet alleen de "
  "poort die hem afwees, zodat zichtbaar is of het één poort was of een breed tekort (§5). "
  "Dezelfde cijfers staan als `near_miss` in `data/run-state/`, waar `report.py` de tabel van "
  "het dagrapport uit opbouwt.")
w()
w("| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |")
w("|---|---|---|---|---|---|")
rows = []
for m in res["matches"]:
    nm = m.get("near_miss") or m.get("near_miss_gepubliceerd")
    if nm:
        rows.append((nm.get("edge_pp") or 0, m["match"], nm))
for _, naam, nm in sorted(rows, key=lambda r: -r[0]):
    w(f"| {naam} | {nm.get('market')} @ {koers(nm.get('odds'))} | {pp(nm.get('edge_xg'))} | "
      f"{pp(nm.get('edge_split'))} | {pp(nm.get('edge_robust_min'))} | "
      f"`{nm.get('failed_gate')}` |")
w()
gates = Counter(nm.get("failed_gate") for _, _, nm in rows)
w("Verdeling over de poorten in deze tabel: "
  + ", ".join(f"`{k}` {v}" for k, v in gates.most_common()) + ".")
w()

# ---------------------------------------------------------------- marktbalans
w("## Marktbalans — de controle op de inkoop")
w()
w("§1a (29 aug): de controle gaat over de **inkoop** en niet over de uitkomst. Vandaag slaagt "
  "ze ruim, en juist daarom is de eenzijdige uitkomst een uitspraak over de analyse.")
w()
mk = Counter(c["market"] for m in res["matches"] for c in m.get("all_candidates", []))
w("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
w("|---|---|---|---|")
w(f"| 1X2 | 14 van 14 (10 beste prijs via The Odds API, 4 gratis BetExplorer-gemiddelde) | "
  f"{mk['1X2']} | 0 |")
w(f"| Asian Handicap | 10 van 14 (`spreads` uit de bulk) | {mk['Asian Handicap']} | 0 |")
w(f"| Draw No Bet (0.0-lijn) | 10 van 14 — bij een deel van de duels geen 0.0-lijn in de "
  f"respons | {mk['Draw No Bet']} | 0 |")
w(f"| Double Chance (±0.5-lijn) | 10 van 14 — bij een deel geen +0.5-lijn in de respons | "
  f"{mk['Double Chance']} | 0 |")
w(f"| Over/Under | 10 van 14 (`totals` uit de bulk) | {mk['Over/Under']} | 4 |")
w(f"| BTTS | 21 duels gekocht van 22 met een kandidaat-edge, à 1 credit | {mk['BTTS']} | 1 |")
w()
w(f"**Totaal {sum(mk.values())} selecties over alle zes de markten.** De controle **slaagt**: er "
  f"zijn doelpuntenmarkten (Over/Under {mk['Over/Under']}, BTTS {mk['BTTS']}) én "
  f"uitkomstmarkten (1X2 {mk['1X2']}, AH {mk['Asian Handicap']}, DNB {mk['Draw No Bet']}, "
  f"DC {mk['Double Chance']}) werkelijk doorgerekend, en niet marginaal maar ruim. "
  "`split_budget(466, 10)` gaf `(10, 10)`, dus **alle tien** competities met een sportkey kregen "
  "de volledige bulk-aanroep met `h2h`, `spreads` én `totals` — vijf van de zes markten — en de "
  "losse `totals`-stap plus de rotatie waren niet nodig.")
w()
w("De **vier zonder sportkey** (Czech First League, Croatian HNL, Hungarian NB I, Romanian "
  "SuperLiga) draaien op het gratis BetExplorer-marktgemiddelde. Daar is 1X2 de enige markt, "
  "staan de andere vijf in `markets_checked` met de reden erbij, en is de bookmaker niet "
  "herleidbaar — dat is 10 van de 42 duels met één markt in plaats van zes. De 20 duels die de "
  "BTTS-ronde niet kregen staan er als `\"BTTS\": \"niet opgevraagd — geen kandidaat-edge in dit "
  "duel\"`, niet als gat.")
w()
w("**De BTTS-ronde heeft vandaag de lijst werkelijk veranderd, en dat is op de meeste dagen "
  "niet zo.** De vijfde gepubliceerde regel — Palmeiras – Corinthians, BTTS nee @1,8036 — "
  "bestaat alleen doordat BTTS in de tweede ronde is gekocht; zonder die ronde was plek 5 naar "
  "Catanzaro – Mantova gegaan. Bij Altach – Wolfsberger AC leverde ronde twee een derde "
  "gekwalificeerde selectie op (BTTS nee @2,4504, +9,83 pp) die het binnen de wedstrijd verloor "
  "van Under 3. Eén duel kreeg geen BTTS ondanks een kandidaat-edge: **Györi ETO – Puskás FC "
  "Academy**, want de Hungarian NB I heeft geen sportkey en er is dus geen event-id om de markt "
  "op te vragen. Dat staat zo in `markets_checked` en is iets anders dan \"opgevraagd, maar geen "
  "boek noteerde deze markt\".")
w()
w("**Creditverbruik:** 51 van een plafond van 466 (`suggest_cap(19604, 21)`). 30 aan de tien "
  "bulk-aanroepen, 21 aan BTTS. Maandverbruik na deze run 447 van 20.000. Noch het budget noch "
  "de tijdsgrens van §0 was vandaag de beperkende factor.")
w()

# ---------------------------------------------------------------- lijstlengte
w("## De lijstlengte bindt — en vandaag legt ze een grensgeval in §5b bloot")
w()
w("Er waren **vijf** selecties die alle acht de poorten haalden én boven hun eigen drempel "
  "stonden — één per wedstrijd, volgens de 0-of-1-bet-regel: Lillestrøm, Altach, St. Gallen, "
  "LASK en Catanzaro. En er passen op zondag **vijf** regels in de lijst. Vijf om vijf, dus.")
w()
w("**Toch staat Catanzaro er niet op, en Palmeiras wél.** §5b stap 5 zegt: *\"staan er méér dan "
  "`MAX_SHORTLIST` selecties bóven de drempel, dan is de drempel de grens en niet de rangorde.\"* "
  "Exact gelijk is niet \"méér\", dus `toplist._cut` valt terug op de rangorde over de hele "
  "publiceerbare groep — en daarin scoort Palmeiras (5,033) hoger dan Catanzaro (4,863), ook al "
  "zit Palmeiras met +7,94 pp **onder** zijn lat en Catanzaro met +8,61 pp erboven. Het "
  "resultaat is dat een selectie die de drempel haalt wordt verdrongen door een die hem niet "
  "haalt.")
w()
w("| Rang | Selectie | Koers | Edge | Score | Boven de lat? |")
w("|---|---|---|---|---|---|")
for m in res["matches"]:
    g = m.get("gekwalificeerd_niet_gepubliceerd")
    if g:
        w(f"| {g.get('rang')} | {m['match']} — {g.get('market')}: {g.get('selection')} | "
          f"{koers(g.get('odds'))} | {g.get('edge_pp'):+.2f} pp | {g.get('score')} | ja |")
w("| 5 (gepubliceerd) | Palmeiras – Corinthians — BTTS: beide ploegen scoren — nee | 1.8036 | "
  "+7.94 pp | 5.033 | **nee** |")
w()
w("**Is dat fout? Niet volgens de letter, en het is ook niet eigenmachtig rechtgezet.** De "
  "implementatie in `scripts/toplist.py` ís de vastgelegde lezing van §5b, en §5a verbiedt "
  "uitdrukkelijk de lijsten over te typen in plaats van ze door die module te laten bepalen. Een "
  "run die hier op eigen initiatief van afwijkt, maakt de reeks over dagen heen "
  "onvergelijkbaar. Maar de **uitkomst** wringt met de bedoeling die er in dezelfde paragraaf "
  "staat — \"dan is de drempel de grens en niet de rangorde\" — en dat hoort opgeschreven in "
  "plaats van opgelost. Het is een besluit voor de gebruiker: moet `>` een `>=` worden, zodat de "
  "drempel ook bij gelijkspel de grens is?")
w()
w("Catanzaro staat als `gekwalificeerd_niet_gepubliceerd` in `data/run-state/` en als "
  "`near_miss` met `failed_gate = \"lijstlengte\"` in `data/shadow.jsonl`, precies zoals §5b dat "
  "op 26 september heeft vastgelegd. Eén naam, geen tweede. **De reeks `lijstlengte`** staat nu "
  "op 9 kandidaten (8 afgewikkeld, +19,9%). Niet lezen: §6d eist ~30 gevallen. En **nooit "
  "optellen bij `edge`** — twee populaties.")
w()

# ---------------------------------------------------------------- bevindingen
w("## Bevindingen")
w()
w("### 1. Poort 8 kost voor het eerst bij Run B aantoonbaar de kop van de lijst — en blijft "
  "staan")
w()
w("De underdog-poort hield 22 selecties tegen over 9 wedstrijden. **Twee daarvan zouden op de "
  "herijkte schaal bóven élke gepubliceerde regel zijn uitgekomen:**")
w()
w("| Selectie | Koers | Edge | `selection_score` | Tier |")
w("|---|---|---|---|---|")
w("| Grasshopper – Young Boys — AH Grasshopper +1.25 | 1.89 | +13,84 pp | **9,238** | FULL |")
w("| Padova – Carrarese — DC Carrarese of gelijk (AH +0.5) | 1.9702 | +11,87 pp | **7,433** | FULL |")
w()
w("De hoogste gepubliceerde score is 7,340 (Altach). Zonder deze poort was de dagranglijst dus "
  "aangevoerd door Grasshopper en had Padova plek 2 of 3 gehad. Dat is ook precies wat de **ruwe** "
  "lijst van §5a toont, waar die twee op 1 en 2 staan.")
w()
w("**En toch is er geen grond om de poort te verruimen — het cijfer is deze week omgeslagen.** De "
  "`underdog`-schaduwreeks, de meting die de vraag van 25 september moet beantwoorden:")
w()
w("| Datum | Afgewikkelde kandidaten | Rendement |")
w("|---|---|---|")
w("| 5 okt | 36 | **+16,9%** |")
w("| 9 okt | 45 | +4,6% |")
w("| 10 okt | 50 | −2,5% |")
w("| **11 okt** | **79** | **−8,7%** |")
w()
w("De uitweg die §1e noemt — *\"positieve ROI over ≥ 30 afgewikkelde kandidaten\"* — was op "
  "5 oktober gehaald en is dat nu niet meer, met ruim twee keer zoveel waarnemingen. De poort "
  "houdt dus **geen winnaars meer tegen**, en de gemeten kalibratiefout die hem verantwoordt "
  "staat er nog: +1,83 pp te veel kans op longshots en −3,58 pp te weinig op favorieten over "
  "4473 uitkomsten. §1e zegt bovendien uitdrukkelijk de vraag niet elke dag opnieuw voor te "
  "leggen; ze is op 5 oktober beantwoord en wat er sindsdien veranderde, wijst de kant op van "
  "houden. `underdog_ruw` staat onveranderd op 17 gevallen met −8,8%; die twee reeksen blijven "
  "twee populaties en worden nooit opgeteld.")
w()
w("**Wat hier onder zit en wat het echte werk is.** Twee keer op één dag is de sterkst gewogen "
  "bevinding van de routine een selectie op de kant die de markt de mindere vindt, en twee keer "
  "moet een rem hem tegenhouden. Dat is de bekende scheefstand: de splitsmethode drukt het "
  "verschil tussen ploegen samen (§1d, §6e). Een rem is daar een pleister op. De vraag blijft "
  "welke rekenstap de mindere ploeg te sterk maakt, en dat is werk aan het model en niet aan de "
  "poort.")
w()
w("### 2. Poort 5 vangt voor de zesde dag op rij driekwart weg — en de schaduwreeks is van "
  "teken gedraaid")
w()
w("447 selecties over zes markten, en **341 (76,3%)** sneuvelden op `tweede_methode`: de twee "
  "methodes verslaan de markt niet dezelfde kant op. Daarna 51 op de edge, 22 op de "
  "underdog-poort, 14 op de koersband, 5 op context en 4 op robuustheid; **10 selecties over 5 "
  "wedstrijden** haalden alle poorten.")
w()
w("De reeks: 40 van 60 (7 okt), 29 van 37 (8 okt), 84 van 110 (9 okt), 553 van 754 (Run A "
  "10 okt), 538 van 703 (Run B 10 okt) en nu 341 van 447. Zes dagen rond driekwart, over ruim "
  "2100 selecties. §5 (\"Net niet\") zegt dat zoiets dagen achtereen een **bevinding** is over "
  "de splitsmethode en geen ruis, en `calibration.py stats` bevestigt het opnieuw: de xG-methode "
  "wijkt op longshots +2,23 pp af en de splitsmethode +1,42, maar op favorieten −4,28 tegen "
  "−2,85 pp. Twee schatters van dezelfde grootheid die structureel verschillend scheef staan — "
  "precies wat poort 5 als tegenstrijdig ziet.")
w()
w("Vandaag is het op de lijst zelf te zien: bij **Lillestrøm – Molde** geeft de xG-methode "
  "+13,88 pp en de splitsmethode +31,47 — dezelfde richting, factor twee in omvang (lambdas "
  "1,588/1,347 tegen 1,481/0,623). Bij de selecties die sneuvelden draait dat verschil net over "
  "de nul.")
w()
w("**Wat het schaduwlogboek ervan zegt is vandaag omgeslagen.** `tweede_methode` staat op 133 "
  "kandidaten, 119 afgewikkeld, **−5,2%** rendement. Gisteren was dat +2,1% over 103. Dat 16 "
  "extra afgewikkelde gevallen het teken omdraaien, is zelf het bewijs dat deze reeks nog te "
  "klein is om er een drempel op te verzetten. **Niet vandaag een drempel verzetten** (§6d: niet "
  "op één dag, en zeker niet op zes).")
w()
w("### 3. De hele lijst is een doelpuntenmarkt en wijst één kant op")
w()
w("Alle vijf de gepubliceerde regels zijn een doelpuntenmarkt en alle vijf wijzen **dezelfde** "
  "kant op: vier keer Under (Under 3 bij Altach, Under 3.5 bij St. Gallen, Lillestrøm en LASK) "
  "en één keer BTTS nee bij Palmeiras. Er staat geen enkele uitkomstmarkt in, terwijl 1X2, AH, "
  "DNB en DC samen 273 van de 447 doorgerekende selecties leveren.")
w()
w("**Dit is geen inkoopartefact, en dat is waarom het hier hoort.** De marktbalanscontrole van "
  "§1a slaagt ruim: tien van de veertien spelende competities kregen de volledige bulk met h2h, "
  "spreads én totals. De eenzijdigheid komt dus uit de **analyse**: het model verwacht vandaag "
  "in deze wedstrijden systematisch minder doelpunten dan de bookmakers — en het doet dat "
  "terwijl de vroeg-seizoenscorrectie het doelpuntenniveau juist **optilt** (factor 1,0563).")
w()
w("§5b zegt hierover: blijft de lijst dagen achtereen uit één hoek komen, dan is dat een signaal "
  "over het model en niet over de selectieregel. Vandaag is het één dag — gisteren kwamen de vijf "
  "regels uit drie markten (drie OU, één DNB, één AH) — dus dit is een **reeks om te volgen** en "
  "geen bevinding om op te handelen.")
w()
w("**En het margelogboek wijst hier een andere kant op, wat het lezen moeilijker maakt in plaats "
  "van makkelijker.** `margins.py stats` meet op 1076 wedstrijden dat het totaal aantal "
  "doelpunten in de staart te **hoog** wordt voorspeld: \"6 of meer\" voorspeld 9,8% tegen "
  "werkelijk 7,3%, meer dan twee standaardfouten. Als het grid daar te veel doelpunten verwacht, "
  "dan is een Under-overwicht niet zonder meer als modelfout te lezen — het zou juist de "
  "correcte kant kunnen zijn. Dat is geen bevestiging en geen weerlegging; het is de reden om "
  "deze reeks te volgen in plaats van er vandaag iets aan te doen.")
w()

# ---------------------------------------------------------------- NONE-duels
w("## De drie duels op `NONE`: drie hoogste divisies zonder gemeten divisiesprong")
w()
w("Drie van de 42 duels komen op `data_tier = NONE` uit, en alle drie om dezelfde reden:")
w()
w("| Duel | Competitie | Ploeg zonder stand vorig seizoen |")
w("|---|---|---|")
w("| Iraklis – Levadiakos | Greek Super League (GRE) | Iraklis |")
w("| Kispest Honvéd – Újpest | Hungarian NB I (HUN) | Kispest Honvéd |")
w("| Hartberg – Austria Lustenau | Austrian Bundesliga (AUT) | Austria Lustenau |")
w()
w("De melding luidt in alle drie *\"geen divisie boven of onder '[competitie]' bekend\"*, en die "
  "melding is **juist** — anders dan de acht gevallen van gisteren, waar promovendi als "
  "degradant werden gemeld. `promotion.TIER2` heeft twintig divisieparen en Griekenland, "
  "Hongarije en Oostenrijk zitten er niet bij. De uitkomst `NONE` is daarmee correct: §4 verbiedt "
  "een gepoolde of verzonnen factor, en `conversion_in_range` is een poort en geen aantekening.")
w()
w("**Maar het is \"nog niet gemeten\" en niet \"niet te meten\"**, en dat onderscheid is precies "
  "wat §4 voor Kroatië vastlegt. Het is dezelfde categorie als Roemenië vóór 9 oktober, de "
  "Spaanse derde divisie vóór 5 oktober en de drie derde divisies van gisteren: een meetbaar gat "
  "dat elke run opnieuw als `NONE` wordt afgeschreven. Het raakt juist de promovendi van drie "
  "competities die elk seizoen twee tot vier ploegen wisselen.")
w()
w("**Niet vandaag gemeten en niet met terugwerkende kracht toegepast.** §4 zegt sinds 9 oktober "
  "uitdrukkelijk een nieuwe factor liever **vóór** de analyse van de dag te meten dan erna, "
  "omdat een al gepubliceerde run aanvullen een herberekening een andere uitkomst zou geven dan "
  "de run zelf gaf. Het staat als besluit bij de gebruiker. Wie het gaat meten: controleer eerst "
  "in `api/data/allLeagues` óf Fotmob de tweede divisie van die drie landen heeft. Is dat niet "
  "zo, dan is het Kroatië en niet Roemenië, en is `NONE` het definitieve antwoord.")
w()

# ---------------------------------------------------------------- inzetvenster
w("## Het inzetvenster, en wat `league_level` deed")
w()
w("**Alle 42 duels stonden op de daglijst van 2026-10-11 zelf**; geen enkel duel kwam van de "
  "daglijst van 12 oktober. Dat is anders dan gisteren (zes van de 77) en de reden is de klok: "
  "het MLS-duel van vandaag trapt om 23:00 UTC af, oftewel 01:00 NL op 12 oktober — nog steeds "
  "binnen het venster `[08:00 NL 11 okt, 08:00 NL 12 okt)`, maar wél op de UTC-daglijst van "
  "vandaag. Vijf Braziliaanse duels zitten in dezelfde band (21:00 tot 00:30 NL). Alle 42 duels "
  "hebben `RunMatch.playable = True`; de vroegste aftrap is 13:00 NL en de run begon om 05:06 NL.")
w()
w("**Onder de oude UTC-dagregel zou het MLS-duel vandaag goed zijn gegaan**, dus dit is geen dag "
  "waarop `runwindow.py` een duel heeft gered. Wel een dag die laat zien dat \"vandaag\" en \"de "
  "UTC-dag\" niet hetzelfde zijn — en dat de regel in beide richtingen werkt.")
w()
w("De vroeg-seizoenscorrectie staat op **factor 1,0563** (gepoold 1,0661 over 46 speeldagen, zes "
  "competities). **Acht** van de veertien spelende competities vallen uit de pool, en de reden is "
  "per competitie vastgelegd zoals Stage 5 eist — een stil weggelaten waarneming is hetzelfde "
  "probleem als een stille truncatie:")
w()
w("| Competitie | Reden | Route | Niveau (thuis / uit) |")
w("|---|---|---|---|")
for comp, blok in (res.get("niveau") or {}).items():
    reden = (res.get("vroeg_seizoen", {}).get("overgeslagen") or {}).get(comp)
    lg = blok.get("league") or {}
    w(f"| {comp} | {reden or 'in de pool'} | `{blok.get('source')}` | "
      f"{lg.get('home_goals_per_match', 0):.3f} / {lg.get('away_goals_per_match', 0):.3f} |")
w()
w("**Twee van de vijf gepubliceerde regels staan in een competitie met route `lopend`** "
  "(Lillestrøm in de Eliteserien, Palmeiras in de Série A), dus die route is ook vandaag geen "
  "voetnoot maar de invoer onder twee vijfde van de lijst.")
w()

# ---------------------------------------------------------------- poort 7
w("## Poort 7 (context) en de stadioncontrole")
w()
w("**Poort 7 hield 5 selecties tegen over twee wedstrijden, beide op de blessurekant:**")
w()
w("- **Cádiz – Sporting Gijón** — Sporting Gijón mist 38% van de selectiewaarde tegen 26% bij "
  "Cádiz (Juan Otero, Nacho Martín en Konrad de la Fuente, alle drie terug eind oktober). Dit "
  "duel verliest daarmee zijn enige kandidaat.")
w("- **Atlético-MG – Santos** — Atlético-MG mist 47% tegen 35% (Tomás Pérez en Tomás Cuello "
  "geschorst, Fred geblesseerd). Idem.")
w()
w("**De rustkant van de poort bond nergens, en dat is te begrijpen:** het interlandvenster is net "
  "voorbij, dus de Europese ploegen komen met twintig tot drieëntwintig dagen rust de wedstrijd "
  "in. De enige uitzondering is de Série A (BRA), met drie tot vier dagen — en daar is de "
  "gepubliceerde regel een doelpuntenmarkt, waar poort 7 per definitie openstaat omdat er geen "
  "kant is om te benadelen (§1c).")
w()
w("**`context.check_venue` zet `relocated` bij geen enkel duel — nul van de 42.** Dat is het "
  "vermelden waard omdat de controle gisteren drie meldingen gaf waarvan twee een eigenschap van "
  "de bron bleken (een transliteratieverschil en een foutieve stamkaart) en niet van de "
  "wedstrijd. Vandaag is er niets te melden.")
w()
w("**En de aantekening die bepaalt hoeveel poort 7 vandaag kón doen.** Van de 42 duels had er om "
  "05:10 NL **geen enkele** een bevestigde opstelling: 4 stonden op `predicted`, 9 op "
  "`lastStarting11`, 2 op `standard`, 22 op `unavailable` en bij 5 was het veld leeg. Daardoor "
  "komen er maar **13 van de 42** in het contextlogboek. Dat is dezelfde klokbevinding als "
  "gisteren en geen eigenschap van deze runlijst: Run B draait zeven tot zestien uur voor de "
  "aftrap en opstellingen komen een uur ervoor.")
w()

# ---------------------------------------------------------------- afwikkeling
w("## Afwikkeling vorige picks")
w()
w("**Eén pick afgewikkeld, en hij verloor.** `ledger.py open` gaf precies één regel rijp: "
  "Sporting Kansas City – Portland Timbers (MLS, 10 okt), Under 3.5 @1,9996 bij Matchbook — de "
  "nummer 2 van de dagranglijst van gisteren. Het werd **3–3**, dus zes doelpunten en de "
  "weddenschap is **verloren**. Dat was een duel uit de MLS-nachtband waarvoor `runwindow.py` "
  "op 24 september is gebouwd; het is dus ook de eerste afgerekende bet uit die band.")
w()
w("**Eén schaduwpick afgewikkeld:** Austin FC – Nashville SC, Under 2.5 @2,22, viel af op "
  "robuustheid — het werd 1–4, dus **verloren**, en de poort deed daar zijn werk.")
w()
w("De vijf picks die `ledger.py open` verder als openstaand meldt zijn die van **Run A van "
  "vanmorgen**, met een negatieve tijd sinds de aftrap (−10,4 tot −16,4 uur): die duels moeten "
  "vandaag nog gespeeld worden. Hetzelfde geldt voor de openstaande schaduwrijen.")
w()
w("Dezelfde controle voor de drie logboeken die een eigen `settle` hebben, want §6b-5c eist "
  "sinds 30 september dat die **élke** run draait:")
w()
w("| Logboek | `settle` deze run | Stand |")
w("|---|---|---|")
w("| `calibration.py` | **9 afgewikkeld** | 4326 van 4587 compleet, 261 open — die 261 zijn de "
  "duels van vandaag. `recalibrate.load_fit().fitted_through = 2026-10-10`, dus de vórige "
  "rundag: **niet blijven liggen** |")
w("| `ctxlog.py` | **3 afgewikkeld** | 1041 wedstrijden, 43 open — alle 43 van vandaag |")
w("| `shadow.py` | **1 afgewikkeld** | 927 kandidaten, 51 open |")
w()
w("Na deze run zijn er **24 schaduwrijen** van Run B bijgeschreven: `underdog` 9, `edge` 8, "
  "`tweede_methode` 4, `context` 2 en **`lijstlengte` 1**.")
w()

# ---------------------------------------------------------------- logboek
w("## Stand van het logboek")
w()
for kop, pad, cap in (
    ("`python3 scripts/ledger.py stats` — wat er wél doorheen kwam", f"{SP}/ledger_stats.txt", None),
    ("`python3 scripts/shadow.py stats` — wat de poorten hebben tegengehouden", f"{SP}/shadow_stats.txt", None),
    ("`python3 scripts/recalibrate.py show` — de stand van de herijking (§1g)", f"{SP}/recal.txt", None),
    ("`python3 scripts/calibration.py stats` — staat het model scheef, en waar (§6e)", f"{SP}/calib.txt", 20),
    ("`python3 scripts/ctxlog.py stats` — het effect van ontbrekende spelers (§1c)", f"{SP}/ctxlog.txt", None),
    ("`python3 scripts/margins.py stats` — klopt de vórm van de uitslag (§6f)", f"{SP}/margins.txt", None),
    ("`python3 scripts/margins.py stats --since 2026-09-20` — alleen lambdas van ná de "
     "shrink-overstap", f"{SP}/margins_since.txt", None),
):
    w(f"### {kop}")
    w()
    w("```")
    try:
        txt = open(pad).read().rstrip("\n").split("\n")
    except FileNotFoundError:
        txt = ["(niet opgeslagen)"]
    txt = [t for t in txt if not t.startswith("===")]
    if cap:
        txt = txt[:cap]
    w("\n".join(txt))
    w("```")
    w()
w("**Drie dingen uit die uitvoer die apart genoemd horen te worden.**")
w()
w("1. **Het logboek staat op 316 afgerekende bets met −7,6% rendement, en de markt schat nog "
  "steeds scherper.** Brier eigen 0,2537 tegen markt 0,2372 — dat verschil van −0,0165 is de "
  "enige regel die zegt of de edge-schatting kansinformatie toevoegt, en het antwoord is nog "
  "steeds nee. De kalibratie zegt hetzelfde: verwacht 182,7 winnaars, werkelijk 141. Dat hoort "
  "boven elke lijst van vijf regels te staan.")
w("2. **Het margelogboek is op de nieuwe lambdas niet te lezen, en dat is geen uitvlucht.** Over "
  "de hele reeks (1076 wedstrijden, 258 met een duidelijke favoriet) staat \"favoriet wint met 4 "
  "of meer\" op +2,0 pp — het patroon dat §6f op 19 september vond, inmiddels sterk afgezwakt. Op "
  "alleen de lambdas van ná de shrink-overstap (`--since 2026-09-20`, **76** duels met een "
  "favoriet) draait het de ándere kant op: \"favoriet wint met 3 of meer\" staat op **−7,9 pp**, "
  "dus het grid **overschat** daar nu de kans op een monsterscore. §6f zegt die vraag pas "
  "opnieuw te beantwoorden bij ~150 duels met een favoriet, en het zijn er 76 — ruim de helft, "
  "dus dit is de reeks die binnen twee weken een antwoord geeft.")
w("3. **Het contextlogboek meet nog niets, en model en markt liggen op elkaar.** De fout van het "
  "model tegen het beschikbaarheidsverschil staat op `r = −0,026` / `t = −0,77` (helling −7,5 pp "
  "per eenheid), de fout van de **markt** op `r = −0,023` / `t = −0,67` (−6,4 pp). Dat die twee "
  "hellingen vrijwel samenvallen is zelf een waarneming: het model gaat met ontbrekende spelers "
  "**niet aantoonbaar slechter** om dan de bookmaker. Poort 7 blijft dus een rem en wordt geen "
  "bijstelling (§1c).")
w()

# ---------------------------------------------------------------- openstaand
w("## Wat er nog moet gebeuren")
w()
w("1. **Besluit voor de gebruiker — de divisiesprong van Griekenland, Hongarije en Oostenrijk "
  "meten.** Kostte vandaag drie van de 42 duels, en het raakt elk seizoen opnieuw de promovendi "
  "van drie competities die twee tot vier ploegen per jaar wisselen. Dezelfde route als Spanje "
  "(5 okt) en Roemenië plus vier andere landen (9 okt): `measure_gap` over meerdere seizoenen, "
  "dan de ingang in `promotion.TIER2`. Controleer eerst of Fotmob die tweede divisies "
  "überhaupt heeft — zo niet, dan is het Kroatië en is `NONE` definitief. **Jouw besluit:** laat "
  "weten of een volgende run deze drie paren mag meten, en dan vóór de analyse van die dag.")
w("2. **Besluit voor de gebruiker — moet §5b stap 5 `>` of `>=` zijn?** Vandaag stonden er exact "
  "`MAX_SHORTLIST` selecties boven hun drempel, en omdat \"exact gelijk\" niet \"méér\" is, "
  "besliste de rangorde — waardoor Catanzaro (+8,61 pp, bóven de lat) werd verdrongen door "
  "Palmeiras (+7,94 pp, eronder). De letter is gevolgd; de bedoeling van de paragraaf wringt "
  "ermee. **Jouw besluit:** laat weten of bij gelijkspel de drempel de grens moet zijn.")
w("3. **Van jou is hier niets nodig — de foutmelding bij een ontbrekend `TIER2`-paar "
  "rechtzetten.** Gisteren werden acht promovendi gemeld als \"degradant die niet in de divisie "
  "erboven staat\"; vandaag was de melding juist, maar de onderliggende keten is ongewijzigd (de "
  "promovendi-tak wordt overgeslagen zonder een melding achter te laten). De uitkomst (`NONE`) "
  "blijft hetzelfde, de reden wordt waar. **Ik pak dit op in de eerstvolgende run die aan dit "
  "analysescript komt.**")
w("4. **Van jou is hier niets nodig — poort 5 blijven volgen.** Zes dagen rond driekwart "
  "weggevangen, en de schaduwreeks is vandaag van teken gedraaid (+2,1% over 103 → −5,2% over "
  "119). §6d verbiedt een drempel verzetten op een paar dagen. **Ik neem de stand elke run op "
  "onder \"Bevindingen\" en kom erop terug zodra de reeks boven de ruis uitkomt.**")
w("5. **Van jou is hier niets nodig — de eenzijdige markt­verdeling volgen.** Vandaag zijn alle "
  "vijf de regels een doelpuntenmarkt die dezelfde kant op wijst; gisteren kwamen ze uit drie "
  "markten. §5b zegt dat dagen achtereen uit één hoek een signaal over het model is. **Ik noteer "
  "de verdeling elke run en meld het als bevinding zodra het drie dagen aanhoudt.**")
w("6. **Van jou is hier niets nodig — de blessuremeting groeit op een derde van het tempo.** 29 "
  "van de 42 duels komen het contextlogboek niet in omdat er om 05:10 NL geen opstelling staat. "
  "De drie wegen zijn: later draaien (botst met de 06:30-deadline van §0), een maat die niet op "
  "de opstelling leunt (speelminuten uit de Opta-respons — een nieuwe maat, geen aanpassing), of "
  "accepteren dat deze runlijst de meting maar beperkt voedt. **Ik werk de drie varianten uit "
  "voordat ik ze als besluit voorleg; vandaag is er niets van jou nodig.**")
w()
w("---")
w()
w("> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de "
  "verwachtingswaarde negatief.")
w()

open(f"runs/{DAG}-run-b.md", "w").write("\n".join(L) + "\n")
print(f"runs/{DAG}-run-b.md geschreven: {len(L)} regels")
