# Betting-analyse routine

Repo achter twee terugkerende geplande taken (Run A en Run B) die dagelijks voetbalwedstrijden
analyseren op valuebets. Deze repo bevat de opdracht, de brondekking en het logboek — zodat elke
run voortbouwt op de vorige in plaats van bij nul te beginnen.

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.

## Waarom deze structuur bestaat

De oorspronkelijke opdracht stond volledig in de scheduler-prompt en liep structureel vast. De
diagnose van 8 aug 2026 staat in `runs/2026-08-08-run-a.md`; de drie doorgevoerde fixes:

| # | Probleem | Fix |
|---|---|---|
| 2 | "Exact één valuebet per wedstrijd" dwong bets af, ook zonder value → overwegend ruis | **0 of 1 bet per wedstrijd**, met een edge-drempel en een harde anti-circulariteitsregel. Nul bets is een geldige uitkomst. |
| 3 | 46 wedstrijden × volledige analyse zonder plafond → elke run liep zijn tijdslimiet in en leverde een halve lijst | **Filteren vóór de analyse** op datadekking, plus een cap van 12 diepe analyses. Afkapping wordt altijd gemeld. |
| 5 | Niets werd bewaard: dezelfde dode bronnen werden elke run opnieuw ontdekt, en "gaat het goed?" was niet te beantwoorden | **Logboek in de repo**: runrapporten, een picks-ledger met uitkomsten, en een bronstatusbestand. |

## Indeling

```
prompts/
  SCHEDULER-RUN-A.txt   korte prompt om in de geplande taak te plakken
  run-a.md              Run A: competitielijst + run-specifieke instellingen
  run-b.md              Run B: idem (competitielijst nog in te vullen)
  _shared-rules.md      de eigenlijke opdracht — parameters, regels, pipeline, format
data/
  coverage.json         welke bron welke competitie kan bedienen, en in welke rol
  source-health.json    wat elke bron laatst deed toen we hem probeerden
  picks.jsonl           het logboek: één gepubliceerde bet per regel
schema/
  pick.schema.json      velddefinitie van een pick
scripts/
  ledger.py             valideren, afwikkelen en meten (alleen stdlib)
runs/
  TEMPLATE.md           vorm van een runrapport
  YYYY-MM-DD-run-a.md   het rapport van elke run
```

De scheduler-prompt is met opzet kort en verwijst naar `prompts/`. **Regels aanpassen doe je in de
repo, niet in de scheduler.**

## Installeren in de scheduler

Vervang de lange prompt van je Run A-taak door de tekst onder de streep in
`prompts/SCHEDULER-RUN-A.txt`. Doe hetzelfde voor Run B zodra de runlijst in `prompts/run-b.md` is
ingevuld.

## Het logboek gebruiken

```bash
python3 scripts/ledger.py validate                  # controleer picks.jsonl tegen schema + regels
python3 scripts/ledger.py add < pick.json           # voeg pick(s) toe (object of lijst)
python3 scripts/ledger.py open --hours 12           # wat moet afgewikkeld worden
python3 scripts/ledger.py settle <id> won --score 2-1
python3 scripts/ledger.py stats                     # hit rate, ROI, Brier, kalibratie
```

`validate` en `add` weigeren een pick die de regels overtreedt: een `implied_prob` die niet gelijk is
aan `1/odds`, een `edge_pp` die niet volgt uit de kansen, een edge onder de drempel voor zijn
datatier, odds buiten de band 1.30–6.00, of een odds-bron als onderbouwing van `my_prob`. Die laatste
is de belangrijkste: hij maakt het onmogelijk om een "edge" te loggen die stilletjes uit de
bookmakerprijs is afgeleid.

### De regel die er echt om gaat

`stats` zet **Brier eigen** naast **Brier markt**: de kwadratische fout van jouw `my_prob` tegenover
die van de marktkans, over dezelfde bets. Is Brier eigen niet lager, dan voegt de analyse geen
kansinformatie toe boven de prijs — hoe goed de hit rate er op korte termijn ook uitziet. Hit rate en
ROI zijn bij tientallen bets vooral ruis; deze vergelijking is het eerste signaal dat richting geeft.

## Nog te doen

**1. API-keys (grootste winst, kan ik niet zelf doen)**

Zeven van de negen bronnen die de routine nodig heeft zijn dicht: 403 (fbref, Forebet, FootyStats,
PredictZ) of JS-only (OddsPortal, BetExplorer, Flashscore). Zolang dat zo is, blijven veel
competities in `BUITEN DATADEKKING` vallen en leveren runs vaak nul bets — de eerlijke uitkomst van
de huidige input, geen defect in de regels.

Twee keys halen dat in één keer weg. Zet ze als omgevingsvariabelen in de omgeving van de geplande
taak (**niet** in de repo — zie `.gitignore`):

| Variabele | Dienst | Levert |
|---|---|---|
| `ODDS_API_KEY` | the-odds-api.com (gratis tier) | echte odds per bookmaker als JSON |
| `API_FOOTBALL_KEY` | api-football / API-Sports | xG, opstellingen, blessures, statistieken |

Beide staan al in `data/coverage.json` met status `untested`. Zodra een key aanwezig is, pikt Stage 3
ze automatisch op.

**2. Run B-runlijst invullen** — `prompts/run-b.md` heeft een lege competitielijst. Die is met opzet
niet geraden.

**3. Fotmob proberen** — de enige onafhankelijke kansbron met brede dekking die nog niet getest is.
Werkt hij, dan komen Eredivisie, Primeira Liga, Belgian Pro League en Ekstraklasa binnen bereik
zonder API-key.

**4. Status van de overige diagnosepunten** — gevraagd waren punt 2, 3 en 5; die zijn af. Van de
rest: punt 4 (dynamische competitielijst) viel vanzelf uit de poort in Stage 2 en is meegenomen;
punt 6 (vroeg-seizoen-behandeling) staat als regel in `_shared-rules.md §4` maar is nog niet in de
praktijk getoetst; punt 1 (API-keys) staat hierboven en vraagt een key van de gebruiker.
