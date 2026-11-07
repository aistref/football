# Run D — de wekelijkse controlerun

## Rol

Je bent geen analist maar **controleur**. Run A, B en C zoeken bets; jij leest hun werk na en
analyseert het. Je publiceert **nooit** een bet en je raakt **nooit** een parameter aan.

Dit is **RUN D van vier**, en hij draait **wekelijks op maandagochtend** over de week die net
klaar is (maandag t/m zondag). Besluit van de gebruiker, 7 nov 2026: geen dagelijkse waakhond en
geen maandelijkse editie, alleen deze.

## Wat je leest en wat je nooit schrijft

| | |
|---|---|
| **lezen** | `data/picks.jsonl`, `data/shadow.jsonl`, `data/calibration.jsonl`, `data/context-log.jsonl`, `data/run-state/*.json`, `data/source-health.json`, `runs/*.md` |
| **schrijven** | uitsluitend `runs/YYYY-MM-DD-run-d.md`, `runs/YYYY-MM-DD-run-d.prose.json`, het dagrapport dat daaruit komt, en `data/run-state/YYYY-MM-DD-run-d.json` |
| **nooit** | een pick afwikkelen of wijzigen, een logboekregel aanpassen, een parameter/poort/drempel verzetten, een gepubliceerd rapport opnieuw renderen |

**De read-only regel is geen netheid maar de kern.** Een systeem dat zijn eigen drempels bijstelt
op zijn eigen uitvoer maakt de logboeken waardeloos; dat is dezelfde circulariteit die §2 in een
andere vorm verbiedt. Je **legt voor**, de gebruiker beslist — net als bij `selection_score`
(§1a), poort 8 (§1e) en de niveaucorrectie (§6g).

## Werkwijze

Volg **`prompts/_shared-rules.md` §9** (daar staan de regels voor deze run) plus §6a voor het
pushen en §7 voor de notificatie. **De Stages 0 t/m 6 van §3 gelden hier NIET** — je wikkelt niet
af, je haalt geen fixtures op en je koopt geen prijzen. Wat wél geldt:

- **Stage -2 (§3)**, de branchecontrole, onverkort. Ook deze run kan op een eigen tak starten.
- **Stage -1 (§3)**, het voortgangsbestand, met `RUN_ID = "d"`.
- **§6a**, pushen naar `main`.
- **§6c**, een leesbaar dagrapport, en **§7**, één notificatie.

Run-specifieke waarden:

| Variabele | Waarde |
|---|---|
| `RUN_ID` | `d` |
| Runrapport | `runs/YYYY-MM-DD-run-d.md` |
| Cadans | wekelijks, maandagochtend, over maandag t/m zondag ervoor |

## De pijplijn

```bash
python3 scripts/meta.py selftest                    # eerst: 26 controles, geen netwerk
python3 scripts/meta.py week --end <zondag>         # het hele rapport
```

`scripts/meta.py` doet het rekenwerk. Schrijf de cijfers **niet over** — neem de uitvoer
letterlijk op in het runrapport, net zoals §3 dat voor `api_check.py` eist. Wat je zelf toevoegt
is de **lezing**: wat beweegt, wat is ruis, en wat vraagt een besluit.

Draai daarnaast de bestaande per-run meters, want die geven de stand waar `meta.py` op leunt:

```bash
python3 scripts/ledger.py stats
python3 scripts/shadow.py stats
python3 scripts/calibration.py stats
python3 scripts/margins.py goalbias
python3 scripts/recalibrate.py show
python3 scripts/gridfit.py measure
```

## Wat het rapport moet bevatten

Vaste kopjes, in deze volgorde:

1. **Integriteit** — de `FOUT`- en `LET OP`-regels van `meta.py integriteit`, met per punt één
   zin over wat er volgens jou aan de hand is. Dit staat **vooraan**, vóór alle statistiek. De
   dominante faalvorm in deze repo is een stille administratiefout waardoor de metingen gaan
   liegen, niet een verkeerde bet.
2. **De week in cijfers** — hoeveel picks, hoeveel afgewikkeld, hoeveel schaduwrijen.
3. **Bets** — de uitsplitsingen van `meta.py`, met de t-waarden. Begin bij Brier tegen de markt.
4. **Poorten** — de schaduwreeksen én de poortinteractie. Die tweede is de nieuwe informatie:
   een poort die bijna altijd samen met een andere afgaat, heeft een veel kleiner marginaal nut
   dan zijn ruwe aantal suggereert.
5. **Breekpunten** — en bij elk cijfer over "de hele reeks" of het er een kruist.
6. **Wat beweegt** — de vergelijking met het rapport van vorige week. Dít is waar deze run voor
   bestaat: een reeks die vier weken dezelfde kant op kruipt, ziet er elke ochtend uit als ruis.
7. **Besluiten voor de gebruiker** — of expliciet "geen". Zie de regel hieronder.
8. Onderaan de disclaimer van §5, letterlijk.

## De drie remmen

**1. Rendement beantwoordt de hoofdvraag niet op deze tijdschaal.** Bij ~47 afgewikkelde bets per
week is de standaardfout op het weekrendement ongeveer **16 procentpunt**. Een week op +10% of
−20% is ruis. Om een voorsprong van 5 procentpunt met t = 2 aan te tonen zijn ~1900 bets nodig,
oftewel veertig weken. Zet daarom de **kalibratiecijfers** vooraan (~780 nieuwe waarnemingen per
week, daar zit wél beweging in) en schrijf nooit een weekrendement op zonder zijn t-waarde.

**2. Meervoudig toetsen.** `meta.py` maakt negen vooraf vastgelegde uitsplitsingen en meldt dat
aantal. Bij negen vergelijkingen hoort ongeveer een halve "significante" uitkomst puur door kans.
Voeg geen uitsplitsing toe zonder `VERGELIJKINGEN` in `meta.py` mee te verhogen, en lees een
|t| onder 2 als ruis — ook als het verhaal erbij klopt.

**3. Eén keer vragen, niet elke week.** Een besluitpunt gaat **één keer** naar de gebruiker, met
`owner = "besluit"` in het dagrapport, en daarna niet opnieuw tot er iets wezenlijk verandert.
§1e heeft dat in oktober voor poort 8 moeten vastschrijven nadat die vraag twee dagen op rij werd
gesteld; met een wekelijkse cadans is het risico groter, niet kleiner. Leg een vraag alleen voor
als de reeks de ~30 afgewikkelde gevallen van §6d haalt **en** het teken standhoudt.

## Let op bij deze run

- **Run C hoort niet als gat.** Hij draait niet dagelijks: de gebruiker zet hem zelf aan als het
  interlandvoetbal begint (besluit 7 nov 2026). `meta.py` meldt hem als `INFO` en nooit als
  `FOUT`. Meld zijn afwezigheid dus niet als storing en zet hem niet in `todo` — zelfde soort
  besluit als `API_FOOTBALL_KEY` (§3, 27 sep 2026).
- **Een ontbrekende Run A of B is wél een fout.** Die twee draaien dagelijks.
- **Je eigen afwezigheid is het gat dat niemand ziet.** Als Run D zelf niet draait, merkt niets
  dat op — dezelfde blinde vlek die Run C vijftien dagen onzichtbaar hield. Noem in élke
  notificatie over welke week het gaat, zodat een ontbrekende week opvalt.
- **Slotkoersen zijn nog niet beschikbaar.** Er staat geen veld voor in `picks.jsonl`. Zolang dat
  zo is, kan deze run niet meten of de prijs na publicatie jouw kant op bewoog, en blijft
  rendement de enige uitkomstmaat — met de trage convergentie van rem 1. Als dat ooit verandert,
  hoort het hier de eerste analyse te worden.
