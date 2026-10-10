"""Het markdown-runrapport van Run B 10 okt 2026 opbouwen uit de vastgelegde data.

De mechanische delen — dekkingstabel, de 77 wedstrijdblokken, de "Net niet"-tabel en de twee
dagranglijsten — komen hier uit `data/run-state/` en `tmp-run/rb_oct10_results.json`, zodat ze
niet worden overgetypt en niet uiteen kunnen lopen met het dagrapport van §6c (dezelfde eis die
§5 aan report.py stelt). De beschouwende secties staan als tekst in dit script.
"""
import json
from collections import Counter, OrderedDict

DAG = "2026-10-10"
res = json.load(open("tmp-run/rb_oct10_results.json"))
state = json.load(open(f"data/run-state/{DAG}-run-b.json"))
top = json.load(open("tmp-run/rb_oct10_top_b.json"))
s3 = json.load(open("tmp-run/rb_oct10_stage3.json"))
ctx = {c["match_id"]: c for c in json.load(open("tmp-run/rb_oct10_ctx.json"))}
picks = json.load(open("tmp-run/rb_oct10_picks_b.json"))
RUNLIJST = list(s3["fixtures"].keys())
idx = {m["match"]: m for m in res["matches"]}
PUB = {p["home"] + " – " + p["away"] for p in picks}

L = []
def w(s=""): L.append(s)


def pp(v):
    return "—" if v is None else f"{v:+.2f} pp"


def koers(v):
    """Koersen afronden op vier decimalen: `net_price` levert anders 3.1069999999999998."""
    if v is None:
        return "—"
    return f"{round(float(v), 4):g}"


# ---------------------------------------------------------------- kop
w(f"# Run B — {DAG}")
w()
w("**Gestart:** 05:04 CEST · **Afgerond:** 05:40 CEST · **Looptijd:** 36,6 minuten · "
  "**Bets gepubliceerd:** 5 · "
  "**Wedstrijden diep geanalyseerd:** 55 van 77 in het inzetvenster "
  "(48 met een kansbron, 22 afgekapt door `MAX_DEEP_ANALYSES` = 55)")
w()
w("**Dagrapport (§6c):** https://claude.ai/artifact/KRXbnv1jDEnnrCU1PBFKmG")
w()
w("**Branches:** deze run staat op `main`. Stage -2 is volledig gedraaid vóór het lezen van de "
  "regels: `git fetch origin` gaf 60 remote branches, waarvan 47 met commits die `main` niet "
  "heeft. Die 47 zijn **niet** gemerged en dat is na controle de juiste uitkomst — `main` heeft "
  "op 2 oktober 2026 een nieuwe, losse geschiedenis gekregen (`git merge-base` met die takken "
  "geeft *geen* gemeenschappelijke voorouder), dus `rev-list --count` telt daar élke commit van "
  "vóór die knip als \"eigen\". Dat is precies het valse alarm waar Stage -2 voor waarschuwt bij "
  "een ondiepe kloon, nu door een herschreven `main` in plaats van door `--shallow`. "
  "Daarom is er **per regel op de inhoud** vergeleken in plaats van op de commitgraaf, zoals "
  "Stage -2 sinds 27 september eist: alle 367 pick-id's van álle takken zitten in `main`, geen "
  "enkele tak heeft een `picks.jsonl`-regel die hier ontbreekt, en de enige bronsleutel die op "
  "een oudere tak voorkomt en niet in `main` staat is `oddspapi` — op 30 augustus 2026 bewust "
  "verwijderd (\"OddsPapi-reserve verwijderd na overstap naar 20K-plan\"). Er valt dus niets te "
  "verenigen. De vijf openstaande picks in `picks.jsonl` komen van Run A van vanmorgen en niet "
  "van een onafgewikkelde tak.")
w()

# ---------------------------------------------------------------- dekking
w("**Looptijd, en hetzelfde administratieve punt als Run A vanmorgen.** 36,6 minuten voor 77 "
  "duels over zestien competities, op een deadline van 06:30 (§0) — ruim binnen de grens, met "
  "vijftig minuten over. Naast Run A van vanmorgen (56 duels in 25,6 minuten) is dat bijna recht "
  "proportioneel: 38% meer wedstrijden kostte 43% meer tijd. Dat is het vermelden waard omdat §3 "
  "Stage 4 juist zegt dat de kosten per **competitie** liggen en niet per wedstrijd — met zestien "
  "competities tegen twaalf bij Run A gaat die vlieger vandaag dus maar deels op, en de 24 "
  "Engelse en 14 MLS-duels die één competitiedossier delen maken het verschil niet goedkoper dan "
  "lineair. Bij deze looptijden is dat academisch; het wordt het pas als een dag richting de "
  "honderd duels gaat. `duur.gestart` stond eerst op 03:21 UTC in plaats van op 03:04, omdat "
  "`progress.load_or_start` dat veld op het moment van de **eerste save** zet en die deze run "
  "pas in Stage 6 kwam — de looptijd viel daardoor ruim zeventien minuten te kort uit en is "
  "gecorrigeerd, met de reden in `duur.note`. Run A maakte vanmorgen dezelfde correctie en op "
  "2 oktober ook al, dus het is een eigenschap van `progress.py` en geen incident. Het is ook "
  "geen onschuldig punt: §0 zegt dat de cap een **tijds**grens is en dat elke run zijn looptijd "
  "vastlegt zodat te zien is of 55 duels vóór 06:30 passen. Een looptijd die structureel te kort "
  "wordt opgeschreven, maakt juist die meting onbruikbaar — en vandaag is de eerste dag waarop "
  "de cap bij Run B echt bindt.")
w()
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
    n = len(ms)
    afg = sum(1 for m in ms if "AFGEKAPT" in (m.get("reason") or ""))
    none = sum(1 for m in ms if m.get("tier") == "NONE")
    ger = n - afg
    xg = (s3["stats"].get(comp, {}).get("prev") or {}).get("has_xg")
    deel = [f"{n} duel(s) in het venster", f"xG bij Fotmob: {'ja' if xg else 'nee (LIGHT, lat 16,0)'}"]
    if afg:
        deel.append(f"{afg} afgekapt")
    if none:
        deel.append(f"{none} op data_tier NONE")
    status = "GEANALYSEERD" if ger > afg or ger > 0 else "AFGEKAPT"
    if afg and afg == n:
        status = "AFGEKAPT"
    w(f"| {comp} | {status} | {'; '.join(deel)} |")
w()
a = res["afkapping"]
w(f"**Afgekapt door `MAX_DEEP_ANALYSES`:** {a['afgekapt']} wedstrijden op een zaterdagcap van "
  f"{a['cap']}. Laagste die het nog haalde: {a['laagste_die_het_haalde']['match']} "
  f"(datarijkdom {a['laagste_die_het_haalde']['richness']}, "
  f"{a['laagste_die_het_haalde']['markets']} markten). Hoogste die afviel: "
  f"{a['hoogste_die_afviel']['match']} (datarijkdom {a['hoogste_die_afviel']['richness']}, "
  f"{a['hoogste_die_afviel']['markets']} markten). Spreiding over de hele run: "
  f"{a['laagste_richness_in_run']} tot {a['hoogste_richness_in_run']}. "
  "Dat verschil van 0,25 punt tussen de laatste die meedeed en de eerste die afviel is het "
  "hele onderscheid waarop 22 analyses zijn weggelaten, en §3 Stage 4 zegt er zelf bij dat die "
  "score **niet scheidt**: de betkans is vlak over de hele rangorde. Lees de afkapping dus als "
  "\"er moest iets weg\" en niet als \"dit waren de zwakste duels\".")
w()
w("Volledige lijst van de 22 afgekapte duels: " + ", ".join(a["lijst"]) + ".")
w()

# ---------------------------------------------------------------- bronstatus
w("## Bronstatus deze run")
w()
w("`python3 scripts/api_check.py`, letterlijk overgenomen zoals §3 eist:")
w()
w("```")
w("""=== The Odds API (odds per bookmaker) ===
  OK — 48 actieve voetbalcompetities beschikbaar.
  Quota: 19735 over, 265 gebruikt deze maand.

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
w("`python3 scripts/idcheck.py` — **afsluitcode 0**, alle 33 `fotmob_id`'s uit "
  "`coverage.json` leveren een bruikbare stand, ook die van de competities die vandaag stil "
  "zijn. Geen enkele competitie is stil uit de runlijst verdwenen. De vijf zonder xG staan er "
  "zoals verwacht in: Czech First League (122), Croatian HNL (252), Hungarian NB I (212), "
  "Romanian SuperLiga (189) en Keuken Kampioen Divisie (111).")
w()
w("| Bron | Status | Detail |")
w("|---|---|---|")
w("| fotmob | ok | 2 daglijsten (10 + 11 okt), `fetch_league_stats` voor 16 competities × 2 "
  "seizoenen, standen van de divisies eronder/erboven voor 25 omrekeningen, `matchDetails` voor "
  "alle 77 duels — **nul fouten** |")
w("| betexplorer | ok | 16 competitiepagina's, 183 fixturerijen; gratis 1X2-marktgemiddelde "
  "(§6e + poort 8) en de enige prijsbron voor de 4 competities zonder sportkey |")
w("| the_odds_api | ok | 19.735 van 20.000 credits over; 69 uitgegeven (12 bulk × 3 + 33 BTTS × 1) |")
w("| oddsapi | ok | sleutel geaccepteerd; `net_price` op elke beurskoers |")
w("| understat | ok | **niet aangeroepen** — dekt vijf competities die geen van alle op deze "
  "runlijst staan; per ontwerp een Run A-bron, geen storing |")
w("| api_football | missing_key | besluit van de gebruiker, 27 sep 2026 — geen gat, geen "
  "actiepunt, niet in de notificatie |")
w()
w("**Wijzigingen t.o.v. vorige run:** geen. Geen sleutel afgewezen, geen bron omgevallen. De "
  "Cloudflare-bronnen (fbref, Forebet, FootyStats, PredictZ, Oddschecker) staan onveranderd "
  "dicht en zijn niet geprobeerd te omzeilen (§3).")
w()
w("Twee dingen die hier horen omdat ze van buitenaf niet te zien zijn:")
w()
w("1. **`api_check.py` noemt van de twaalf gekochte competities maar drie** onder \"Relevante "
  "sportkeys\" (`soccer_spain_segunda_division`, `soccer_italy_serie_b`, "
  "`soccer_germany_bundesliga2`), en toch leverden alle twaalf events — Greek Super League 14, "
  "Eliteserien 7, Allsvenskan 8, Swiss Super League 6, Austrian Bundesliga 12, English League "
  "One 13, English League Two 12, MLS 30, Série A 20. Die lijst is een handmatige selectie in "
  "het script en **geen uitspraak over wat de API aanbiedt**. Dit stond al in het rapport van "
  "9 oktober voor twee competities; vandaag is het er negen, dus de waarneming is nu stevig.")
w("2. **BetExplorer markeert `is_today` op zijn eigen kalenderdag.** Bij MLS gaf de pagina 30 "
  "fixturerijen met maar 2 op `is_today`, bij Série A 20 met 1, terwijl Fotmob daar 14 "
  "respectievelijk 2 duels in het inzetvenster zag. Dat is dezelfde tijdzonevraag als Stage 1, "
  "nu aan de prijskant: een MLS-duel dat om 01:30 NL aftrapt valt buiten BetExplorers \"today\". "
  "Het heeft vandaag niets gekost — de MLS-prijzen kwamen van The Odds API — maar wie het "
  "marktgemiddelde ooit als énige 1X2-bron voor MLS wil gebruiken, loopt hier tegenaan.")
w()
# ---------------------------------------------------------------- parameters
w("## Parameters en poorten deze run")
w()
w("| Parameter | Waarde |")
w("|---|---|")
w("| `MAX_DEEP_ANALYSES` | **55** (zaterdag) — en hij **bindt**: 22 duels afgekapt |")
w("| `MAX_SHORTLIST` | **5** (zaterdag) — en hij **bindt**: 8 gekwalificeerde selecties, 5 plekken |")
w("| `EDGE_THRESHOLD_FULL` / `_LIGHT` | 8.0 / 16.0 pp — sinds 20 sep een **afkapping** aan het eind (§5b), geen poort |")
w("| `MAX_LIGHT_IN_SHORTLIST` | 2 — bond niet; alle vijf de regels zijn FULL |")
w("| `MIN_ODDS` / `MAX_ODDS` | 1.30 / 6.00 — 32 selecties vielen hierop af |")
w("| `SHRINK` | 1.00 (sinds 19 sep, §6e) |")
w("| `XG_WEIGHT` | 0.80 |")
w("| `CREDIBILITY_K` | 8 |")
w("| Poort 8 (`UNDERDOG_FLOOR`) | **bindt**, lichte vorm, ondergrens 0.35; `sides.check(..., today=2026-10-10)` |")
w("| Herijking (§1g) | `a=0.996150, b=-0.002498` op 3819 gevallen, `fitted_through=2026-10-09` |")
w()
w("**De herijking is praktisch de identiteit** en haalde 0,10 tot 0,13 pp van de vijf "
  "gepubliceerde edges af (16,50 → 16,38; 12,13 → 12,03; 9,41 → 9,28; 11,07 → 10,97; 10,70 → "
  "10,60). De herijkte en de ruwe dagranglijst zijn daardoor regel voor regel identiek, in "
  "dezelfde orde, en er is **nul** selectie die alleen op §1g sneuvelde. `fitted_through` staat "
  "op de vórige rundag, dus `calibration.py settle` is niet blijven liggen — de controle die "
  "§6b-5c sinds 30 september eist. Lees die identiteit zoals §1e punt 3 voorschrijft: de fit "
  "komt uit de **ongeselecteerde** ijksteekproef en is dus geen uitspraak over de staart die "
  "deze routine kiest.")
w()

# ---------------------------------------------------------------- wedstrijden
w("## Wedstrijden")
w()
w("Alle 77 duels in het inzetvenster, per competitie, in de volgorde van de runlijst. "
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
        extra = " · *op de daglijst van 11 okt*" if sd == "2026-10-11" else ""
        w(f"#### {m['match']} · {ko} NL{extra}")
        w()
        w(f"- **Data:** {m.get('tier')}")
        gek = m.get("gekwalificeerd_niet_gepubliceerd")
        if m["match"] in PUB or gek or (m.get("bet") and (m.get("pick") or {}).get("market")):
            p = m.get("pick") or {}
            gepub = m["match"] in PUB
            kop = "**Bet:**" if gepub else "**Gekwalificeerd, niet gepubliceerd:**"
            w(f"- {kop} {p.get('market')} — {p.get('selection')} — Odds: "
              f"best **{koers(p.get('odds'))}** ({p.get('odds_source')})")
            ip = 1 / p["odds"] * 100 if p.get("odds") else None
            w(f"- **Implied prob:** {ip:.1f}% • **My prob:** {p.get('my_prob', 0)*100:.1f}%"
              if ip else "- **Implied prob:** —")
            w(f"- **Edge:** {pp(p.get('edge_pp'))} • **Confidence:** "
              f"{'Medium' if m.get('tier') == 'FULL' else 'Low'} • "
              f"**selection_score:** {p.get('score')}")
            w(f"- **Per poort:** xG-model {pp(p.get('edge_xg'))} · 2e methode "
              f"{pp(p.get('edge_split'))} · zwakste stand van het (shrink, rho)-grid "
              f"{pp(p.get('edge_robust_min'))}")
            lam = m.get("lambdas") or {}
            if lam.get("xg"):
                w(f"- **Doelverwachting:** xG-methode {lam['xg'][0]:.3f} / {lam['xg'][1]:.3f}"
                  + (f" · splitsmethode {lam['split'][0]:.3f} / {lam['split'][1]:.3f}"
                     if lam.get("split") else ""))
            if not gepub:
                g = gek or {}
                w(f"- **Valt af op LIJSTLENGTE** — rang {g.get('rang')} van 8 gekwalificeerde "
                  f"selecties bij `MAX_SHORTLIST` = 5. Geen poort hield deze selectie tegen; "
                  f"ze gaat als `failed_gate = \"lijstlengte\"` het schaduwlogboek in (§5b).")
        else:
            w(f"- **GEEN BET** — {m.get('reason')}")
            nm = m.get("near_miss") or m.get("near_miss_gepubliceerd")
            if nm:
                w(f"- **Beste kandidaat:** {nm.get('market')} @ {koers(nm.get('odds'))} — xG-model "
                  f"{pp(nm.get('edge_xg'))}, 2e methode {pp(nm.get('edge_split'))}, zwakste "
                  f"stand {pp(nm.get('edge_robust_min'))}; viel af op "
                  f"`{nm.get('failed_gate')}`")
        pn = m.get("promovendi") or {}
        for kant, note in pn.items():
            w(f"- **Omrekening ({kant}):** {note}")
        v = (m.get("context") or {}).get("venue") or {}
        if v.get("relocated"):
            w(f"- **Stadion:** {v.get('note')}")
        w()
# ---------------------------------------------------------------- topselectie
w("## Topselectie")
w()
w("Vijf regels op vijf plekken, en **voor het eerst bij Run B halen ze alle vijf hun eigen "
  "drempel**. Gerangschikt op `selection_score` = edge × kans × (FULL 1.0 | LIGHT 0.5), "
  "dezelfde formule waarmee binnen elke wedstrijd de markt is gekozen (§1a).")
w()
w("| # | Bet | Koers | Probability | Edge | Score | Risicoklasse | Waarom deze |")
w("|---|---|---|---|---|---|---|---|")
RISK = {
    "Toronto FC – CF Montréal": ("Medium", "Hoogste score van de dag met ruime marge (12,26 "
        "tegen 7,46 voor nummer 2) en de enige regel die boven de 14 pp uitkomt op beide "
        "methodes. Under 3.5 is push-vrij en de breedste doelpuntenlijn in de lijst."),
    "Sporting Kansas City – Portland Timbers": ("Medium", "Tweede op score; dezelfde markt en "
        "dezelfde richting als nummer 1, met de laagste doelverwachting van de twee "
        "MLS-regels. Let op de aftrap: 02:30 NL in de nacht ná de rundag."),
    "AIK – Brommapojkarna": ("Medium", "Laagste koers van de vijf (1,55) en daarmee de hoogste "
        "trefkans (73,8%) — precies waar `selection_score` de voorkeur aan geeft boven een paar "
        "procentpunt extra edge."),
    "Magdeburg – Hannover 96": ("High", "Draw No Bet, dus push-beschermd, maar de twee methodes "
        "staan hier het verst uiteen van de hele lijst (7,01 tegen 27,35 pp) en de zwakste "
        "stand van het grid is +2,48 pp. De richting is eensgezind, de omvang niet."),
    "Austria Wien – Sturm Graz": ("High", "Kwartlijn-handicap op de uitploeg; robuustheid "
        "+3,39 pp is de tweede zwakste van de lijst en het is de enige regel op een kant waar "
        "de markt de favoriet buitenshuis zet."),
}
for i, r in enumerate(top["herijkt"], 1):
    risk, why = RISK[r["match"]]
    w(f"| {i} | {r['match']} — {r['market']}: {r['selection']} | {koers(r['odds'])} | "
      f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']} | {risk} | {why} |")
w()
w("**Wat de zesde was en waarom hij er niet staat:** Rosenborg – Sandefjord Under 3.5 @1,85, "
  "+8,42 pp, score 5,261. Hij is niet door een poort tegengehouden — hij haalde alle acht de "
  "poorten én zijn drempel — maar er passen vijf regels in de lijst. Zie \"De lijstlengte "
  "bindt\" hieronder.")
w()
w("**Verdeling over de markten:** drie Over/Under, één Draw No Bet, één Asian Handicap. Vier "
  "van de vijf zijn dus push-beschermd of een doelpuntenmarkt en maar één is een kale kant op "
  "de uitkomst. Dat is geen quotum en is niet nagestreefd (§1 verbiedt bets forceren om een "
  "verdeling te halen), maar het past bij wat §1a over `selection_score` zegt: de weegregel "
  "kiest de minst aan gelijkspel blootgestelde uitdrukking van dezelfde mening.")
w()

# ---------------------------------------------------------------- de twee dagranglijsten
w("### De twee dagranglijsten (§5a)")
w()
w("`python3 scripts/toplist.py --run b --date 2026-10-10`. Beide lijsten geven één regel per "
  "wedstrijd. **Ze zijn vandaag identiek**, regel voor regel en in dezelfde orde, omdat de fit "
  "van §1g de identiteit benadert — het verschil is 0,10 tot 0,13 pp per regel en dat verschuift "
  "geen enkele plaats.")
w()
w("| # | Herijkt (hieruit komen de bets) | Ruw (wat de routine vóór 5 sep zou hebben gezien) |")
w("|---|---|---|")
for i in range(max(len(top["herijkt"]), len(top["ruw"]))):
    h = top["herijkt"][i] if i < len(top["herijkt"]) else None
    rw = top["ruw"][i] if i < len(top["ruw"]) else None
    fmt = lambda r: ("—" if not r else
                     f"{r['match']} — {r['selection']} @ {koers(r['odds'])} · {r['edge_pp']:+.2f} pp · "
                     f"score {r['score']}")
    w(f"| {i+1} | {fmt(h)} | {fmt(rw)} |")
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
    if not nm:
        continue
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
  "ze met de ruimste marge van elke Run B tot nu toe.")
w()
mk = Counter(c["market"] for m in res["matches"] for c in m.get("all_candidates", []))
w("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
w("|---|---|---|---|")
w(f"| 1X2 | 16 van 16 (12 beste prijs via The Odds API, 4 gratis BetExplorer-gemiddelde) | "
  f"{mk['1X2']} | 0 |")
w(f"| Asian Handicap | 12 van 16 (`spreads` uit de bulk) | {mk['Asian Handicap']} | 1 |")
w(f"| Draw No Bet (0.0-lijn) | 12 van 16 — bij 22 duels geen 0.0-lijn in de respons | "
  f"{mk['Draw No Bet']} | 1 |")
w(f"| Double Chance (±0.5-lijn) | 12 van 16 — bij 25 duels geen +0.5-lijn in de respons | "
  f"{mk['Double Chance']} | 0 |")
w(f"| Over/Under | 12 van 16 (`totals` uit de bulk) | {mk['Over/Under']} | 3 |")
w(f"| BTTS | 33 duels met een kandidaat-edge, à 1 credit | {mk['BTTS']} | 0 gepubliceerd "
  f"(2 gekwalificeerd, afgevallen op lijstlengte) |")
w()
w(f"**Totaal {sum(mk.values())} selecties over alle zes de markten.** De controle **slaagt**: "
  "er zijn doelpuntenmarkten (Over/Under 220, BTTS 66) én uitkomstmarkten (1X2 143, AH 199, "
  "DNB 52, DC 23) werkelijk doorgerekend, en niet marginaal maar ruim. `split_budget(448, 12)` "
  "gaf `(12, 12)`, dus **alle twaalf** competities met een sportkey kregen de volledige "
  "bulk-aanroep met `h2h`, `spreads` én `totals` — vijf van de zes markten — en de losse "
  "`totals`-stap plus de rotatie waren niet nodig.")
w()
w("De **vier zonder sportkey** (Czech First League, Croatian HNL, Hungarian NB I, Romanian "
  "SuperLiga) draaien op het gratis BetExplorer-marktgemiddelde. Daar is 1X2 de enige markt en "
  "staan de andere vijf in `markets_checked` met de reden erbij — dat is elf van de 77 duels "
  "met één markt in plaats van zes, en dat moet hier staan omdat het van buitenaf niet te zien "
  "is. De vijftien duels die de BTTS-ronde niet kregen staan er als "
  "`\"BTTS\": \"niet opgevraagd — geen kandidaat-edge in dit duel\"`, niet als gat.")
w()
w("**De BTTS-ronde was vandaag geen formaliteit.** De tweede analyseronde leverde twee extra "
  "gekwalificeerde selecties op die er zonder de inkoop niet waren geweest: Bradford City – "
  "Leyton Orient BTTS nee (+8,29 pp) en Wycombe Wanderers – Luton Town BTTS nee (+11,89 pp). "
  "Zes gekwalificeerde selecties werden er daarmee acht. Beide vielen vervolgens af op de "
  "lijstlengte, dus de gepubliceerde lijst is er niet door veranderd — maar ze staan nu wél in "
  "de reeks `lijstlengte`, en dat is precies waar §1a de vereniging van beide schalen (13 sep) "
  "voor heeft ingevoerd.")
w()
w("**Creditverbruik:** 69 van een plafond van 448 (`suggest_cap(19735, 22)`). 36 aan de twaalf "
  "bulk-aanroepen, 33 aan BTTS. Maandverbruik na deze run 334 van 20.000. Het budget is op geen "
  "enkele manier de beperkende factor; **de tijdsgrens van §0 is dat vandaag wél** — zie de "
  "afkapping van 22 duels.")
w()

# ---------------------------------------------------------------- lijstlengte
w("## De lijstlengte bindt, voor het eerst sinds 26 september")
w()
w("Acht selecties haalden **alle acht de poorten én hun eigen drempel**, en er passen vijf "
  "regels in de lijst van een zaterdag. §5b stap 5 zegt dan dat de drempel de grens is en niet "
  "de rangorde — maar de lijst blijft vijf lang, dus drie gekwalificeerde selecties vallen af "
  "op niets anders dan de lengte van de lijst:")
w()
w("| Rang | Selectie | Koers | Edge | Score |")
w("|---|---|---|---|---|")
for m in res["matches"]:
    g = m.get("gekwalificeerd_niet_gepubliceerd")
    if not g:
        continue
    w(f"| {g.get('rang')} | {m['match']} — {g.get('market')}: {g.get('selection')} | "
      f"{koers(g.get('odds'))} | {g.get('edge_pp'):+.2f} pp | {g.get('score')} |")
w()
w("Die drie zijn **geen afgewezen kandidaten** — er is geen poort die ze tegenhield. Ze staan "
  "als `gekwalificeerd_niet_gepubliceerd` in `data/run-state/` en als `near_miss` met "
  "`failed_gate = \"lijstlengte\"` in `data/shadow.jsonl`, precies zoals §5b dat op "
  "26 september heeft vastgelegd. Eén naam, geen tweede — twee namen zouden één populatie in "
  "twee reeksen splitsen waarna geen van beide ooit de ~30 gevallen haalt die §6d eist.")
w()
w("**De rangorde-anomalie die dit blootlegt, en het is geen fout.** Wycombe Wanderers – Luton "
  "Town heeft met +11,89 pp een **hogere edge** dan drie van de vijf gepubliceerde regels, en "
  "valt er toch buiten. Dat komt doordat `selection_score` edge × kans weegt (§1a) en de kans "
  "op die BTTS-nee maar 43,0% is, tegen 61,0% tot 74,9% bij de vijf die het haalden. De "
  "weegregel geeft met opzet de voorkeur aan een hogere trefkans boven een paar procentpunt "
  "extra edge, en §1a noemt daar ook een inhoudelijk argument bij: de bekende zwakte van dit "
  "model verschuift kansmassa tussen winst en gelijkspel, en een markt die daar ongevoelig voor "
  "is hoort dan voor te gaan. Wie de lijst leest als \"de vijf grootste voordelen van vandaag\" "
  "leest hem verkeerd; het zijn de vijf hoogst **gewogen** selecties.")
w()
w("**De reeks `lijstlengte`** stond op 5 gevallen (5 afgewikkeld, +14,9%) en groeit vandaag naar "
  "8. Niet lezen: §6d eist ~30 gevallen. En **nooit optellen bij `edge`** — `edge` betekent \"te "
  "weinig voordeel\", deze rij betekent \"genoeg voordeel, maar andere wedstrijden hadden "
  "meer\". Twee populaties.")
w()
# ---------------------------------------------------------------- bevindingen
w("## Bevindingen")
w()
w("### 1. Acht duels op `NONE` door een ontbrekende derde divisie — en een foutmelding die de "
  "verkeerde richting aanwijst")
w()
w("Zestien van de 77 duels komen op `data_tier = NONE` uit. **Acht** daarvan om dezelfde "
  "reden: een ploeg die dit seizoen in de tweede divisie speelt en vorig seizoen in de "
  "**derde**, waarvoor `promotion.TIER2` geen divisiepaar heeft.")
w()
w("| Duel | Competitie | De ploeg zonder stand | Kwam uit |")
w("|---|---|---|---|")
w("| Benevento – Cesena | Serie B (ITA) | Benevento | Serie C |")
w("| Südtirol – Ascoli | Serie B (ITA) | Ascoli | Serie C |")
w("| LR Vicenza – Pisa | Serie B (ITA) | LR Vicenza | Serie C |")
w("| Arezzo – Cremonese | Serie B (ITA) | Arezzo | Serie C |")
w("| Darmstadt – Energie Cottbus | 2. Bundesliga (GER) | Energie Cottbus | 3. Liga |")
w("| VfL Osnabrück – Dynamo Dresden | 2. Bundesliga (GER) | VfL Osnabrück | 3. Liga |")
w("| Tranmere Rovers – Rochdale | English League Two (ENG) | Rochdale | National League |")
w("| York City – Northampton Town | English League Two (ENG) | York City | National League |")
w()
w("**De uitkomst is goed, de reden is fout, en dat tweede is wat opgeschreven moet worden.** "
  "Alle acht staan in `data/run-state/` met de reden *\"degradant: 'X' staat niet in de stand "
  "van \\[de divisie **boven** deze competitie\\]\"* — Benevento wordt dus gemeld als degradant "
  "die niet in de Serie A-stand staat, terwijl hij promovendus uit de Serie C is. De oorzaak "
  "zit in de keten van het analysescript: `promotion.TIER2` heeft geen ingang voor "
  "`Serie B (ITA)`, `2. Bundesliga (GER)` of `League Two (ENG)`, dus de promovendi-tak wordt "
  "**overgeslagen zonder een fout achter te laten**, waarna alleen de degradanten-tak nog een "
  "melding plaatst en die melding de hele uitkomst beschrijft. `NONE` is correct — §4 verbiedt "
  "een verzonnen of gepoolde factor — maar de reden wijst de verkeerde richting **en** de "
  "verkeerde divisie aan.")
w()
w("Dat is dezelfde soort stille administratiefout als het Serie B-id dat vier dagen op 56 stond, "
  "als `settled_note` op 27 september en als de ontbrekende `calibration.py settle` van 18 t/m "
  "29 september: niets klaagt, en een latere run die dit leest gaat op zoek naar een kapotte "
  "Serie A-stand die niet kapot is.")
w()
w("**En dit is geen Kroatië.** §4 legt voor `Croatian HNL` vast dat het gat *niet meetbaar* is "
  "omdat Fotmob de Kroatische tweede divisie simpelweg niet heeft. Hier is dat anders, en het is "
  "deze run nagetrokken in `api/data/allLeagues`:")
w()
w("| Divisie | Fotmob-id | Stand 2025/2026 | xG | Vorm |")
w("|---|---|---|---|---|")
w("| Serie C (ITA) | 147 | ja | nee | **drie parallelle groepen** |")
w("| 3. Liga (GER) | 208 | ja, 20 ploegen | nee | één tabel |")
w("| National League (ENG) | 117 | ja, 24 ploegen | nee | één tabel |")
w()
w("Alle acht ploegen van de tabel hierboven staan in de stand van hun derde divisie. Dit is dus "
  "**\"nog niet gemeten\"**, net als Roemenië vóór 9 oktober en de Spaanse derde divisie vóór "
  "5 oktober — niet \"niet te meten\".")
w()
w("**Een waarschuwing voor wie het gaat meten.** 3. Liga en National League zijn één tabel en "
  "gaan zoals de twaalf bestaande paren. **Serie C speelt in drie parallelle groepen** en "
  "`fetch_league_stats(147)` geeft er stil **één** van terug — 20 ploegen, met LR Vicenza erin "
  "en Benevento, Ascoli en Arezzo erbuiten. Dat is exact de val die §4 op 5 oktober voor de "
  "Primera Federación beschrijft, en de machinerie bestaat al: `promotion.lower_table()` zoekt "
  "de groep op, `fotmob.fetch_league_stats(..., group=...)` haalt hem en `measure_gap` meet per "
  "groep. Zonder dat levert de meting bij geluk het goede antwoord in plaats van bij ontwerp.")
w()
w("**Niet vandaag gemeten en niet met terugwerkende kracht toegepast.** §4 zegt sinds 9 oktober "
  "uitdrukkelijk een nieuwe factor liever **vóór** de analyse van de dag te meten dan erna, "
  "omdat een al gepubliceerde run aanvullen een herberekening een andere uitkomst zou geven dan "
  "de run zelf gaf — en §7 kent één notificatie per run. Het staat als besluit bij de "
  "gebruiker. Wat het kost is wel te noemen en het is een terugkerende post: acht van de 77 "
  "duels vandaag, en **vier van de zes Serie B-duels**.")
w()
w("De overige acht `NONE`-duels, voor de volledigheid: zes op `conversion_in_range` (de "
  "omrekening valt buiten het gemeten bereik — Hradec Králové – Artis Brno, Celta Fortuna – "
  "Real Sociedad B, Cambridge United – Blackpool, Leicester City – Peterborough United, Port "
  "Vale – Grimsby Town en Shrewsbury Town – Exeter City), één omdat `Hungarian NB I` geen "
  "divisiepaar heeft (Vasas Budapest – Kisvárda) en één omdat `Série A (BRA)` dat niet heeft "
  "(Vasco da Gama – Remo). Die laatste twee staan zo in `prompts/run-b.md` beschreven en zijn "
  "de verwachte uitkomst. De zes op `conversion_in_range` zijn **correct gedrag**: dat is de "
  "Coventry-val waarvoor die poort bestaat. Celta Fortuna is dezelfde weigering als op "
  "5 oktober (relatieve verdediging 1,042 tegen een gemeten maximum van 0,925) en dus "
  "consistent.")
w()
w("### 2. Poort 5 vangt voor de vijfde dag op rij driekwart weg")
w()
w("703 selecties over zes markten, en de tweede methode is voor de **vijfde dag op rij** de "
  "poort die vrijwel alles wegvangt.")
w()
w("| Poort | Selecties tegengehouden |")
w("|---|---|")
for k, v in Counter(c.get("failed_gate") or "haalde alle poorten"
                    for m in res["matches"] for c in m.get("all_candidates", [])).most_common():
    w(f"| `{k}` | {v} |")
w()
w("De reeks: 40 van 60 (7 okt), 29 van 37 (8 okt), 84 van 110 (9 okt), 553 van 754 (Run A, "
  "10 okt) en nu **538 van 703 = 76,5%**. Dat is vijf dagen rond driekwart over inmiddels ruim "
  "1600 selecties. §5 (\"Net niet\") zegt dat zoiets dagen achtereen een **bevinding** is over "
  "de splitsmethode en geen ruis, en §6e wijst die methode al sinds 22 augustus aan als de "
  "scheefste van de twee.")
w()
w("**Wat het schaduwlogboek ervan zegt, en het is onveranderd ongunstig voor de poort:** "
  "`tweede_methode` staat op 116 kandidaten, 103 afgewikkeld, **+2,1% rendement**. Een poort "
  "die driekwart van het werk wegvangt en daarbij per saldo géld kost in plaats van bespaart, "
  "is geen filter maar een rem op de hele routine. Twee dingen die dat relativeren voordat "
  "iemand eraan sleutelt: +2,1% over 103 gevallen is binnen de ruis die §6d beschrijft, en de "
  "poort is er niet om geld te besparen maar om tegenstrijdige schatters tegen te houden (§1, "
  "herzien 11 aug). Maar het cijfer wijst nu voor de derde meting op rij dezelfde kant op en de "
  "aantallen groeien, dus **dit is de reeks om te volgen**.")
w()
w("Vandaag is de oorzaak op de gepubliceerde regels zelf te zien. Bij Magdeburg – Hannover 96 "
  "geeft de xG-methode 1,470 / 1,841 en de splitsmethode 1,089 / 2,613: dezelfde richting, maar "
  "een factor twee verschil in het doelsaldo. Bij de duels die sneuvelden draait dat verschil "
  "net over de nul. **Niet vandaag een drempel verzetten** (§6d: niet op één dag, en zeker niet "
  "op vijf).")
w()
w("### 3. Tweederde van de dag komt het contextlogboek niet in, en de oorzaak is de klok")
w()
w("`ctxlog.py collect` voegde **25 van de 77** wedstrijden aan het contextlogboek toe, terwijl "
  "alle 77 een contextblok in `data/run-state/` hebben. Dat is geen overgeslagen stap: "
  "`_rows_from_state` eist een meetbaar aandeel ontbrekende selectiewaarde aan **beide** kanten "
  "(`out_share`), en dat bestaat alleen als Fotmob een `squad_value` voor die ploeg geeft. "
  "**90 van de 154 ploegzijden (58%) hebben `squad_value` 0 of ontbrekend.**")
w()
w("**De eerste lezing was \"tweede divisies hebben bij Fotmob geen marktwaardes\", en die is "
  "bij het narekenen onjuist gebleken.** Het competitiepatroon suggereert haar wel — Serie B 6 "
  "van 6 onmeetbaar, Czech First League 4 van 4, 2. Bundesliga 4 van 4, English League Two 10 "
  "van 12 — maar de kruistabel van `lineup_type` tegen `squad_value` wijst iets anders aan:")
w()
w("| `lineup_type` | ploegzijden | met `squad_value` | zonder |")
w("|---|---|---|---|")
w("| `unavailable` | 52 | 0 | **52** |")
w("| leeg / ontbrekend | 14 | 0 | 14 |")
w("| `standard` | 6 | 0 | 6 |")
w("| `lastStarting11` | 78 | **60** | 18 |")
w("| `predicted` | 4 | **4** | 0 |")
w()
w("**Zodra er een opstelling staat, is er in 64 van de 82 gevallen ook een marktwaarde.** Het "
  "probleem zit bij de 72 ploegzijden waar om 05:10 NL nog helemaal geen opstellingsblok is — "
  "en dat is te verwachten bij een aftrap om 13:00 tot 16:00, acht tot elf uur later. Dit "
  "bevestigt de lezing die Run B op 9 oktober in `source-health.json` zette (\"oorzaak is "
  "timing\") en **weerlegt de competitielezing**; de 18 ploegzijden met wél een opstelling en "
  "tóch geen waarde zijn de rest, en die groep is klein.")
w()
w("**Waarom dit meer is dan een voetnoot.** §1c heeft op 5 september gemeten dat er geen effect "
  "van ontbrekende spelers te vinden is, en de uitweg die daar is opgeschreven is een **grotere "
  "steekproef**: *\"door élke wedstrijd met context te loggen in plaats van alleen de "
  "doorgerekende worden het er ruim honderd per dag, en is de vraag over drie tot vier weken "
  "beantwoordbaar.\"* Die rekensom gaat uit van élke wedstrijd. Hij levert vandaag een derde "
  "daarvan, en die drie tot vier weken zijn inmiddels **vijf weken** voorbij: het logboek staat "
  "op 1001 wedstrijden (943 afgewikkeld) en de drempel voor een aantoonbaar effect ligt nog op "
  "~19 pp per eenheid, met het model op `t = -1,12` en de markt op `t = -1,07`. De reeks groeit "
  "dus wél, maar langzamer dan §1c aanneemt — en de reden is nu gemeten in plaats van vermoed.")
w()
w("**Wat de remedie wél en niet is.** Een tweede bron voor marktwaardes helpt hier **niet**: "
  "het ontbrekende gegeven is de opstelling, niet de prijskaart. Wat wél zou werken is de "
  "context een tweede keer ophalen dichter bij de aftrap — maar dat botst rechtstreeks met §0: "
  "de rapporten moeten om 06:30 NL klaar staan omdat de gebruiker tussen 07:00 en 08:00 inzet, "
  "en de vroegste aftrap van vandaag was 13:00. **Een run die op de opstellingen wacht, is te "
  "laat voor de inzet.** Dat is geen gat in de code maar een echte spanning tussen twee eisen, "
  "en ze hoort als zodanig op tafel te liggen in plaats van als ontbrekende regel. Een derde "
  "weg is een gewicht dat niet op de opstelling leunt — speelminuten van dit seizoen per "
  "uitvaller, uit de Opta-respons die §4 beschrijft — maar dat is een nieuwe maat en geen "
  "aanpassing. Het staat als besluit bij de gebruiker.")
w()
w("**Wat er niet is gedaan, en waarom:** `out_share` een nul laten teruggeven waar de waarde "
  "ontbreekt. Dat zou de 52 duels als \"niemand ontbreekt\" in het logboek zetten en de "
  "regressie met een halve steekproef verzonnen nullen vervuilen — precies wat §1c verbiedt "
  "(\"een meting die er niet is, is geen bewijs van een probleem\"). **Voor de poort zelf "
  "verandert er niets:** bij een onmeetbaar aandeel staat poort 7 per definitie open, dus er is "
  "geen bet door tegengehouden of doorgelaten die er anders niet was. Het is de **meting** die "
  "hier ontbreekt, niet de rem.")
w()

# ---------------------------------------------------------------- inzetvenster
w("## Het inzetvenster deed vandaag echt werk")
w()
w("Het venster is `[08:00 NL 10 okt, 08:00 NL 11 okt)`. **71** van de 77 duels stonden op de "
  "daglijst van 10 oktober zelf; **zes** stonden op die van **11 oktober** (`source_day = "
  "DAY + 1`) en horen tóch bij deze run omdat ze in NL-tijd tussen 02:30 en 04:30 in de nacht "
  "ná de rundag aftrappen: Austin FC – Nashville SC, Minnesota United – Houston Dynamo FC, "
  "Sporting Kansas City – Portland Timbers, Colorado Rapids – San Jose Earthquakes, Los Angeles "
  "FC – Vancouver Whitecaps (alle MLS) en São Paulo – Vitória (Série A BRA).")
w()
w("**Dit is precies het geval waarvoor `runwindow.py` op 24 september is gebouwd, en vandaag is "
  "het geen theorie:** één van die zes — **Sporting Kansas City – Portland Timbers**, aftrap "
  "02:30 NL — is een **gepubliceerde bet** geworden, de nummer 2 van de dagranglijst. Onder de "
  "oude UTC-dagregel was dat duel aan de run van morgen toegewezen en dan al gespeeld geweest "
  "voordat iemand het kon inzetten. Dat is exact de faalstand die `prompts/run-b.md` beschrijft "
  "(Seattle Sounders – Real Salt Lake, 24 sep), nu voor het eerst met een echte bet erin.")
w()
w("Alle 77 duels hebben `RunMatch.playable = True`. De vroegste aftrap is 13:00 NL (Magdeburg – "
  "Hannover 96) en de run begon om 05:06 NL, ruim acht uur daarvoor.")
w()

# ---------------------------------------------------------------- niveau en uplift
w("## Competitiebasis: `league_level` en de vroeg-seizoenscorrectie")
w()
vs = res.get("vroeg_seizoen") or {}
w(f"De vroeg-seizoenscorrectie staat op factor **{vs.get('factor'):.4f}** (gepoold "
  f"{vs.get('gepoold'):.4f} over {vs.get('speeldagen')} speeldagen, "
  f"{len(vs.get('competities') or [])} ).")
w()
w("**Acht van de zestien spelende competities vallen uit de pool**, en de reden staat per "
  "competitie vast zoals Stage 5 eist — een stil weggelaten waarneming is hetzelfde probleem "
  "als een stille truncatie:")
w()
w("| Competitie | Waarom buiten de pool |")
w("|---|---|")
for comp, reden in (vs.get("overgeslagen") or {}).items():
    w(f"| {comp} | {reden} |")
w()
w("| Competitie | Route | Thuis / uit doelpunten per duel | Speeldagen lopend | xG |")
w("|---|---|---|---|---|")
for comp, n in (res.get("niveau") or {}).items():
    n = n or {}
    hg, ag = n.get("home_goals_per_match"), n.get("away_goals_per_match")
    w(f"| {comp} | `{n.get('source')}` | "
      f"{('%.3f / %.3f' % (hg, ag)) if hg is not None and ag is not None else '—'} | "
      f"{n.get('played')} van {n.get('length')} | "
      f"{'ja' if n.get('xg_available') else 'nee'} |")
w()
w("**Drie van de vijf gepubliceerde regels staan in de vier competities met route `lopend`** "
  "(AIK in Allsvenskan, Toronto FC en Sporting Kansas City in MLS), dus die route is vandaag "
  "geen voetnoot maar de invoer onder de halve lijst. Dat is de constructie van 24 september: "
  "een seizoen dat over de helft is haalt zijn niveau rechtstreeks uit het lopende seizoen, en "
  "`uplift_observations` houdt die competities uit de gepoolde correctie zodat ze de factor van "
  "de andere niet optillen. Zonder die tweede stap zouden Eliteserien (22 van 30 speeldagen), "
  "Allsvenskan (23 van 30), MLS (28 van 34) en Série A (29 van 38) de factor voor de acht "
  "overige competities omhoog hebben getrokken.")
w()
# ---------------------------------------------------------------- poorten 7 en 8
w("## Poort 7 (context) en poort 8 (underdog)")
w()
w("**Poort 8 bindt**, in de lichte vorm met ondergrens `UNDERDOG_FLOOR` = 0,35, en "
  "`sides.check()` is met `today=2026-10-10` aangeroepen zoals §1e eist — zodat het vervallen "
  "venster van 25 t/m 30 september uit `sides.LAPSED_FROM` / `LAPSED_UNTIL` wordt gelezen en "
  "niet geraden. Hij hield **33 selecties** tegen, verdeeld over 12 wedstrijden: het hoogste "
  "aantal van welke Run B tot nu toe. **Geen van die 33 zou de lijst hebben aangevoerd** — de "
  "hoogste geblokkeerde edge is +9,83 pp (Córdoba bij Eldense, 1X2) en die haalt zijn LIGHT-lat "
  "van 16,0 niet eens. De poort heeft vandaag dus geen bet gekost. `poort8_ruw` is leeg omdat "
  "alle 33 al op de herijkte schaal sneuvelden en §1e verbiedt dezelfde selectie twee keer te "
  "boeken; `poort8_vervallen` is leeg omdat het venster van zes dagen voorbij is.")
w()
w("**De `underdog`-reeks is van teken gedraaid, en dat is de belangrijkste stand van vandaag:**")
w()
w("| Datum | Afgewikkelde kandidaten | Rendement |")
w("|---|---|---|")
w("| 30 sep | 20 | +15,8% |")
w("| 5 okt | 36 | **+16,9%** |")
w("| 9 okt | 45 | +4,6% |")
w("| **10 okt** | **50** | **−2,5%** (48,0% trefkans) |")
w()
w("Een tekenomslag is één van de twee gebeurtenissen waarop §1e zegt de vraag van 25 september "
  "opnieuw voor te leggen. **Maar ze draait de verkeerde kant op om er een vraag van te "
  "maken.** De uitweg van 25 september was *\"positieve ROI over ≥ 30 afgewikkelde "
  "kandidaten\"* — de grond om de poort te verruimen — en die is nu juist **niet** meer waar. De "
  "poort houdt met andere woorden geen winnaars meer tegen, en er is dus geen besluit te "
  "vragen. De gemeten kalibratiefout die de rem verantwoordt staat er nog: **+1,89 pp** te veel "
  "kans op longshots en **−3,64 pp** te weinig op favorieten over 4212 uitkomsten. "
  "`underdog_ruw` staat onveranderd op 17 gevallen met −8,8%. Die twee blijven twee populaties "
  "en worden nooit opgeteld.")
w()
w("**Poort 7 hield 15 selecties tegen**, over zes wedstrijden, allemaal op de blessurekant. De "
  "duidelijkste is **Colorado Rapids – San Jose Earthquakes**: San Jose mist 18% van zijn "
  "selectiewaarde tegen 6% bij Colorado — Reid Roberts geschorst, Darius Johnson en Nonso "
  "Adimabua geblesseerd — en dat duel verliest daarmee zijn enige kandidaat. De **rustkant** van "
  "de poort bond nergens.")
w()
w("`context.check_venue` zet `relocated = True` bij **drie** duels. §1c eist dat een "
  "verplaatsing wordt genoemd ook als de poort opengaat, dus ze staan hier — maar geen van de "
  "drie heeft een bet opgeleverd (twee staan op `NONE`, één is afgekapt) en ze zijn niet "
  "hetzelfde:")
w()
w("| Duel | Melding | Wat het werkelijk is |")
w("|---|---|---|")
w("| Vasas Budapest – Kisvárda | \"Stadion Illovsky Rudolf, niet Illovszky Rudolf Stadion\" | "
  "**geen verplaatsing — een spellingsverschil.** Hetzelfde stadion, twee transliteraties van "
  "dezelfde Hongaarse naam. De controle vergelijkt stadionnamen als tekst en kan dat niet zien. |")
w("| LR Vicenza – Pisa | \"Stadio Romeo Menti, Vicenza, niet Stadio Rino Mercante\" | "
  "**geen verplaatsing — een fout in de stamkaart van de bron.** Het Stadio Romeo Menti ís het "
  "stadion van Vicenza; Fotmob noteert als eigen stadion het Stadio Rino Mercante, dat in "
  "Bassano del Grappa staat. |")
w("| Paksi SE – MTK Budapest | \"Fehervari uti Stadion, niet Paksi FC Stadion\" | de enige die "
  "**eruitziet als een echte verplaatsing**: Paks speelt dan niet in Paks maar in Boedapest. "
  "Zonder nieuwsbron is niet vast te stellen waarom — en §1c zegt zelf dat een geplande run die "
  "niet heeft. |")
w()
w("**Twee van de drie meldingen zijn dus eigenschappen van de bron en niet van de wedstrijd**, "
  "dezelfde soort valse positieve als de vier Nederlandse beloftenploegen op 9 oktober. De "
  "controle **meldt** met opzet alleen en houdt niets tegen (§1c), dus het kost niets — maar wie "
  "hier ooit een poort van maakt, moet eerst de namen normaliseren.")
w()

# ---------------------------------------------------------------- afwikkeling
w("## Afwikkeling vorige picks")
w()
w("**Geen openstaande picks om af te wikkelen**, en dat is de juiste uitkomst en geen "
  "overgeslagen stap. `ledger.py open` meldt vijf picks met de reden *\"bron meldt nog niet "
  "afgelopen\"* en een negatieve tijd sinds de aftrap (−8,9 tot −13,1 uur): het zijn de vijf "
  "picks die **Run A vanmorgen** heeft gepubliceerd, en die duels moeten vandaag nog gespeeld "
  "worden. `shadow.py open` zegt hetzelfde over 85 schaduwrijen. Run A heeft de picks en "
  "schaduwrijen van 9 oktober vanmorgen om 02:30 al afgewikkeld.")
w()
w("Dezelfde controle voor de drie logboeken die een eigen `settle` hebben, want §6b-5c eist "
  "sinds 30 september dat die élke run draait — ook een run met nul bets:")
w()
w("| Logboek | `settle` deze run | Stand |")
w("|---|---|---|")
w("| `calibration.py` | 0 afgewikkeld | 4026 van 4356 compleet, 330 open — alle 330 zijn duels "
  "van vandaag. `recalibrate.load_fit().fitted_through = 2026-10-09`, dus de vórige rundag: "
  "**niet blijven liggen** |")
w("| `ctxlog.py` | 0 afgewikkeld | 1001 wedstrijden, 943 afgewikkeld, 58 open — alle 58 zijn "
  "duels van vandaag |")
w("| `shadow.py` | 0 afgewikkeld | 840 kandidaten, 798 afgewikkeld, 42 open |")
w()
w("Na deze run zijn er **38 schaduwrijen** van Run B bijgeschreven: `underdog` 13, `edge` 10, "
  "`tweede_methode` 6, `robuustheid` 4, **`lijstlengte` 3** en `context` 2.")
w()

# ---------------------------------------------------------------- logboek
w("## Stand van het logboek")
w()
for kop, pad, toel in (
    ("`python3 scripts/ledger.py stats` — wat er wél doorheen kwam",
     "/tmp/claude-0/-home-user-football/cf21451e-ba0b-5b60-ac55-b4b41a8cc117/scratchpad/ledger_stats.txt", None),
    ("`python3 scripts/shadow.py stats` — wat de poorten hebben tegengehouden",
     "/tmp/claude-0/-home-user-football/cf21451e-ba0b-5b60-ac55-b4b41a8cc117/scratchpad/shadow_stats.txt", None),
    ("`python3 scripts/recalibrate.py show` — de stand van de herijking (§1g)",
     "/tmp/claude-0/-home-user-football/cf21451e-ba0b-5b60-ac55-b4b41a8cc117/scratchpad/recal.txt", None),
    ("`python3 scripts/calibration.py stats` — staat het model scheef, en waar (§6e)",
     "/tmp/claude-0/-home-user-football/cf21451e-ba0b-5b60-ac55-b4b41a8cc117/scratchpad/calib.txt", 20),
    ("`python3 scripts/ctxlog.py stats` — het effect van ontbrekende spelers (§1c)",
     "/tmp/claude-0/-home-user-football/cf21451e-ba0b-5b60-ac55-b4b41a8cc117/scratchpad/ctxlog.txt", None),
    ("`python3 scripts/margins.py stats` — klopt de vórm van de uitslag (§6f)",
     "/tmp/claude-0/-home-user-football/cf21451e-ba0b-5b60-ac55-b4b41a8cc117/scratchpad/margins.txt", None),
    ("`python3 scripts/margins.py stats --since 2026-09-20` — alleen lambdas van ná de "
     "shrink-overstap", "/tmp/claude-0/-home-user-football/cf21451e-ba0b-5b60-ac55-b4b41a8cc117/scratchpad/margins_since.txt", None),
):
    w(f"### {kop}")
    w()
    w("```")
    try:
        txt = open(pad).read().rstrip("\n").split("\n")
    except FileNotFoundError:
        txt = ["(niet opgeslagen)"]
    txt = [t for t in txt if not t.startswith("===")]
    if toel:
        txt = txt[:toel]
    w("\n".join(txt))
    w("```")
    w()
w("**Twee dingen uit die uitvoer die apart genoemd horen te worden.**")
w()
w("1. **Het margelogboek is op de nieuwe lambdas van teken gedraaid, maar is nog niet te "
  "lezen.** Over de hele reeks (980 wedstrijden, 228 met een duidelijke favoriet) staat "
  "\"favoriet wint met 4 of meer\" op +2,7 pp — het patroon dat §6f op 19 september vond, "
  "inmiddels sterk afgezwakt. Op alleen de lambdas van ná de shrink-overstap (`--since "
  "2026-09-20`, **46** duels met een favoriet) draait het de ándere kant op: \"favoriet wint "
  "met 3 of meer\" staat op **−13,1 pp**, dus het grid **overschat** daar nu de kans op een "
  "monsterscore. §6f zegt die vraag pas opnieuw te beantwoorden bij ~150 duels met een "
  "favoriet, en het zijn er 46 — dus dit is nog ruis en geen omslag. Wel de reeks om te "
  "volgen, en het is de reden dat er op 19 september géén tweede correctie bovenop de "
  "shrink-wijziging is gezet: dat zou nu een dubbeltelling in de verkeerde richting zijn "
  "geweest.")
w("2. **Het contextlogboek meet nog niets, en model en markt liggen nu op elkaar.** De fout van "
  "het model tegen het beschikbaarheidsverschil staat op `r = -0,039` / `t = -1,12` (helling "
  "−11,2 pp per eenheid), de fout van de **markt** op `r = -0,037` / `t = -1,07` (−10,5 pp). "
  "Dat die twee hellingen vrijwel samenvallen is zelf een waarneming: het model gaat met "
  "ontbrekende spelers **niet aantoonbaar slechter** om dan de bookmaker. Poort 7 blijft dus "
  "een rem en wordt geen bijstelling (§1c).")
w()

# ---------------------------------------------------------------- openstaand
w("## Wat er nog moet gebeuren")
w()
w("1. **Besluit voor de gebruiker — de drie ontbrekende derde divisies meten.** Serie C (ITA, "
  "id 147), 3. Liga (GER, id 208) en National League (ENG, id 117) staan alle drie bij Fotmob "
  "met een bruikbare stand, en hun ontbreken kostte vandaag acht van de 77 duels (vier van de "
  "zes Serie B-duels). Dezelfde route als Roemenië op 9 oktober en de Primera Federación op "
  "5 oktober: eerst `measure_gap` over meerdere seizoenen, dan de ingang in "
  "`promotion.TIER2`. Let bij Serie C op de drie parallelle groepen. **Jouw besluit:** laat "
  "weten of een volgende run deze drie paren mag meten — en dan vóór de analyse van die dag, "
  "niet erna.")
w("2. **Van jou is hier niets nodig — de foutmelding bij een ontbrekend `TIER2`-paar "
  "rechtzetten.** Acht duels werden gemeld als \"degradant die niet in de divisie erboven "
  "staat\" terwijl het promovendi uit de derde divisie zijn; de promovendi-tak wordt "
  "overgeslagen zonder een melding achter te laten. De uitkomst (`NONE`) blijft hetzelfde, de "
  "reden wordt waar. **Ik pak dit op in de eerstvolgende run die aan dit analysescript komt.**")
w("3. **Besluit voor de gebruiker — de blessurekant van poort 7 meetbaar maken, of accepteren "
  "dat hij dat niet is.** 52 van de 77 duels komen het contextlogboek niet in omdat er om "
  "05:10 NL nog geen opstelling staat; de meting van §1c groeit daardoor op een derde van het "
  "tempo dat daar is aangenomen. De drie wegen zijn: later draaien (botst met de 06:30-deadline "
  "van §0 en dus met de inzet), een gewicht dat niet op de opstelling leunt (speelminuten uit "
  "de Opta-respons — een nieuwe maat, geen aanpassing), of accepteren dat deze runlijst de "
  "meting maar beperkt voedt. **Jouw besluit:** welke van de drie.")
w("4. **Van jou is hier niets nodig — poort 5 blijven volgen.** Vijf dagen rond driekwart "
  "weggevangen, en het schaduwlogboek zegt dat die poort per saldo geld kóst (+2,1% over 103 "
  "gevallen). §6d verbiedt een drempel verzetten op een paar dagen. **Ik neem de stand elke run "
  "op onder \"Bevindingen\" en kom erop terug zodra de reeks boven de ruis uitkomt.**")
w("5. **Van jou is hier niets nodig — de stadioncontrole normaliseert geen namen.** Twee van de "
  "drie `relocated`-meldingen van vandaag zijn een spellingsverschil of een fout in de "
  "stamkaart van de bron. De controle meldt alleen en houdt niets tegen, dus het kost niets. "
  "**Ik laat het zoals het is tot iemand er een poort van wil maken; dán moeten de namen eerst "
  "genormaliseerd worden.**")
w()

# ---------------------------------------------------------------- slot
w("6. **Van jou is hier niets nodig — `progress.load_or_start` zet `duur.gestart` op de eerste "
  "save in plaats van op de start van de run.** Dat heeft vandaag bij Run A en bij Run B tot een "
  "te korte looptijd geleid (12,7 in plaats van 25,6 en 18,9 in plaats van 36,6 minuten) en op "
  "2 oktober ook al. Het raakt de enige meting waarmee §0 kan controleren of de cap van 55 duels "
  "vóór 06:30 past, en vandaag bindt die cap voor het eerst bij Run B — dus het is geen "
  "cosmetisch punt. **Ik pak de reparatie op in de eerstvolgende run die aan `progress.py` komt: "
  "`gestart` hoort in Stage -1 te worden gezet en bij een hervatting onveranderd te blijven.**")
w("7. **Van jou is hier niets nodig — dit runrapport miste in zijn eerste versie alle vijftien "
  "omrekennotities.** De wedstrijdblokken lazen `promo_notes` terwijl het veld in "
  "`data/run-state/` `promovendi` heet, dus bij elk van de vijftien omgerekende duels viel de "
  "regel *Omrekening (thuis/uit)* stil weg — inclusief de precieze reden waarom zes duels op "
  "`conversion_in_range` zijn geweigerd. Gevonden doordat de gebruiker naar twee van die duels "
  "vroeg. Hersteld in deze versie; de onderliggende data in `data/run-state/` was altijd "
  "volledig, alleen de weergave niet. **Dit is dezelfde soort stille weergavefout als "
  "`settled_note` op 27 september, en het is het derde voorbeeld vandaag van een stap die "
  "overgeslagen kan worden zonder dat iets klaagt.**")
w("---")
w()
w("> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de "
  "verwachtingswaarde negatief.")
w()

open(f"runs/{DAG}-run-b.md", "w").write("\n".join(L) + "\n")
print(f"runs/{DAG}-run-b.md geschreven: {len(L)} regels")
