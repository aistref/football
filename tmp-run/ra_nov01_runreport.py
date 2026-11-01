"""Run A, 1 nov 2026 — het markdown-runrapport van §6b-1 genereren.

De tabellen komen uit `data/run-state/` en de statistiekblokken letterlijk uit de uitvoer van de
scripts, zodat het runrapport en het dagrapport niet uiteen kunnen lopen (§6c). De lopende tekst
staat hier wel letterlijk: die is van deze run en van geen andere.
"""
import json
from collections import Counter

DAG = "2026-11-01"
ART = "https://claude.ai/artifact/PVvXeSfUmXxW4dy9THkpxy"
MD = f"https://github.com/aistref/football/blob/main/runs/{DAG}-run-a.dagrapport.md"

st = json.load(open(f"data/run-state/{DAG}-run-a.json"))
res = json.load(open("tmp-run/ra_nov01_results.json"))
picks = json.load(open("tmp-run/ra_nov01_picks_a.json"))
top = json.load(open("tmp-run/ra_nov01_top_a.json"))
bev = json.load(open("tmp-run/ra_nov01_bevestiging.json"))
cups = json.load(open("tmp-run/ra_nov01_cups.json"))["cups"]
pin = {r["match"]: r for r in json.load(open("tmp-run/ra_nov01_pinnacle.json"))}
pou = {r["match"]: r for r in json.load(open("tmp-run/ra_nov01_pinnacle_ou.json"))}
settle = json.load(open("tmp-run/ra_nov01_settle.json"))


def lees(p):
    return open(p).read().rstrip("\n")


allc = [c for m in res["matches"] for c in m.get("all_candidates", [])]
L = []
A = L.append

A(f"# Run A — {DAG}")
A("")
A("**Gestart:** 03:05 CET · **Bets gepubliceerd:** 5 · **Wedstrijden diep geanalyseerd:** "
  "37 van 37 in het inzetvenster (1 op `data_tier = NONE`)")
A("")
A("**Branch:** deze run is op `claude/stoic-davinci-dnxlwo` gestart en **naar `main` gepusht** "
  "(§6a); de scheduler-prompt geeft daar expliciet toestemming voor. Er is dus niets te mergen "
  "voor een volgende run.")
A("")
A("**Dit rapport is voor de repo.** Het leesbare dagrapport staat op")
A(f"[de HTML-pagina]({ART}) en, als tweede route (§6c, 14 okt), in")
A(f"[`runs/{DAG}-run-a.dagrapport.md`]({MD}).")
A("")
A("---")
A("")
A("## Stage -2 — takken")
A("")
A("`git rev-parse --is-shallow-repository` gaf **true**: de container kreeg de repo opnieuw als "
  "ondiepe kloon. Vóór het unshallowen leken **72 van de 82 takken** eigen commits te hebben (3 "
  "tot 604 stuks); ná `git fetch --unshallow origin` (668 commits lokaal) zijn dat **nul van de "
  "82**. Dat is exact het valse alarm dat §3 Stage -2 beschrijft, en het is de reden dat die stap "
  "vóór alles komt.")
A("")
A("De commitgraaf is echter niet het antwoord (§3 Stage -2, 27 sep). `scripts/branchaudit.py "
  "--ref HEAD` vergelijkt alle vijf de logboeken **per record op de inhoud**:")
A("")
A("```")
A(lees("tmp-run/ra_nov01_branchaudit.txt"))
A("```")
A("")
A("`HEAD` was bij de start bit-voor-bit gelijk aan `origin/main` (0 commits voor, 0 achter). Er "
  "viel niets te verenigen. **Wat er wél openstond zijn picks en niet takken:** `picks.jsonl` had "
  "tien openstaande picks van 31 oktober en `shadow.jsonl` vijfenzeventig schaduwrijen; die horen "
  "bij Stage 0 en staan daar.")
A("")
A("Eén bekend verschil blijft staan en is géén vondst: `sources.oddspapi` staat op vijf oude "
  "takken en niet op `HEAD`. OddsPapi is op 30 aug 2026 verwijderd na de overstap naar het "
  "20K-creditplan (commit `f342894`). Besluit, geen verlies — `branchaudit.py` merkt dat zelf aan.")
A("")
A("## Stage -1 — hervatting")
A("")
A("Geen voortgangsbestand voor 1 november bij de start, dus dit is een verse run. `resumed_count` "
  "= 0 en `sessies` bevat één id — géén hervatting, en dat is sinds 16 oktober een afgeleid getal "
  "in plaats van een teller (§3 Stage -1).")
A("")
A("## Dekkingsrapportage")
A("")
A("| Competitie | Status | n | bets | datalabels / eerstvolgende ronde |")
A("|---|---|---|---|---|")
rows = []
for comp, b in st["competitions"].items():
    ms = b.get("matches") or []
    if ms:
        t = Counter(m["tier"] for m in ms)
        rows.append((comp, "GEANALYSEERD", len(ms), sum(1 for m in ms if m.get("bet")),
                     ", ".join(f"{t[x]} {x}" for x in ("FULL", "LIGHT", "NONE") if t[x])))
    else:
        rows.append((comp, b.get("status", "GEEN WEDSTRIJD"), 0, 0,
                     b.get("eerstvolgende_ronde") or "—"))
rows.sort(key=lambda r: (-r[2], -r[3], r[0]))
for r in rows:
    A(f"| {r[0]} | `{r[1]}` | {r[2]} | {r[3]} | {r[4]} |")
A("")
A("**Niets afgekapt.** 37 duels tegen een zondagcap van 55 (`MAX_DEEP_ANALYSES`). De "
  "datarijkdom-score liep van **4,75** (laagste in de run) tot **8,5** (hoogste); §3 Stage 4 eist "
  "die twee getallen zodra de cap knelt, en ze staan er ook als hij dat niet doet — anders is "
  "achteraf niet na te gaan of de afkapping ergens op sloeg.")
A("")
A("Alle 37 duels stonden op de daglijst van de rundag zelf; geen enkel duel komt van de lijst van "
  "2 november en geen enkel duel was bij het eerste verzoek al afgetrapt "
  "(`RunMatch.playable = True` voor alle 37).")
A("")
A("## Bronstatus deze run")
A("")
A("Uitvoer van `python3 scripts/api_check.py`, letterlijk:")
A("")
A("```")
A(lees("tmp-run/ra_nov01_apicheck.txt"))
A("```")
A("")
A("Wat daaruit volgt voor deze run:")
A("")
A("- **The Odds API: 20000 credits over, 0 verbruikt.** De maandwissel heeft het quotum gereset. "
  "November heeft 30 dagen, dus `suggest_cap` zet het dagplafond op **333**. Gebruikt: **33** voor "
  "de bulk (h2h + spreads + totals, 3 per competitie × 11) plus **23** voor de BTTS-ronde = **56 "
  "van 20000**.")
A("- **`API_FOOTBALL_KEY` ontbreekt.** Dat is een besluit van de gebruiker van 27 september 2026 "
  "en geen gat, geen actiepunt en geen notificatieonderwerp (§3). De kanskant komt van Fotmob "
  "(alle elf competities) en Understat (vijf, vandaag alle vijf spelend). Fotmob leverde voor alle "
  "37 duels, dus de uitzondering van §3 punt 3 is niet aan de orde.")
A("- **Geen sleutel is afgewezen** en geen bron gaf een fout. `store[\"errors\"]` is over de hele "
  "run leeg gebleven.")
A("- Twee bekende sportkeys staan vandaag op NIET ACTIEF (Coppa Italia, DFB Pokal) en dat klopt "
  "met BetExplorer. Vier actieve sportkeys kent de repo niet: `soccer_brazil_serie_b`, "
  "`soccer_germany_liga3`, `soccer_sweden_superettan` en `soccer_uefa_nations_league`. Geen van de "
  "vier staat op de runlijst van Run A — de eerste drie zijn Run B-gebied, de Nations League is "
  "Run C.")
A("")
A("### Bevestiging door een tweede methode (§1)")
A("")
A("De bevestigingspoort is op de **runlijst zelf** gedraaid en niet alleen op de analyse: de "
  "Fotmob-daglijst naast de BetExplorer-fixturepagina per competitie, twee losse bronnen.")
A("")
A("| Competitie | Fotmob | BetExplorer | eens |")
A("|---|---|---|---|")
for naam in sorted(bev):
    v = bev[naam]
    A(f"| {naam} | {v.get('fotmob')} | {v.get('betexplorer', '—')} | "
      f"{'ja' if v.get('eens') else 'NEE'} |")
A(f"| **totaal** | **{sum(v.get('fotmob', 0) for v in bev.values())}** | "
  f"**{sum(v.get('betexplorer', 0) or 0 for v in bev.values())}** | "
  f"**{sum(1 for v in bev.values() if v.get('eens'))} van {len(bev)}** |")
A("")
A("**Eens over alles.** Dat is de eerste run in weken zonder enig verschil tussen de twee "
  "bronnen; op 31 oktober stond er nog één duel verschil (Cambuur – Go Ahead Eagles).")
A("")
A("De vijf bekers zijn apart langs twee bronnen gegaan, want ze hebben geen `fotmob_id` in "
  "`coverage.json`:")
A("")
A("| Beker | Fotmob-daglijst | BetExplorer |")
A("|---|---|---|")
for naam, v in cups.items():
    bx = v.get("betexplorer") or {}
    fm = ("id " + str(v["fotmob_id"]) + ": 0 duels" if v.get("fotmob_id") else "geen id")
    A(f"| {naam} | {fm} | {bx.get('teamparen', 0)} teamparen, eerstvolgende ronde "
      f"{bx.get('eerste_ronde') or '**geen**'} |")
A("")
A("**De DFB Pokal-fixturepagina van BetExplorer is vandaag leeg** (0 teamparen op een respons van "
  "200). Daar is Fotmob dus de enige bron die iets zegt, en dat is genoteerd als *niet bevestigd* "
  "en niet als bevestiging. Dat onderscheid is precies wat 6 oktober 2026 vijf FA Cup-duels "
  "kostte, met de rollen omgedraaid.")
A("")

open("tmp-run/ra_nov01_runreport_deel1.md", "w").write("\n".join(L) + "\n")
print("deel 1:", len(L), "regels")
