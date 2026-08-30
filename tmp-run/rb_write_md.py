import json, subprocess
sec = json.load(open("tmp-run/rb_sec.json"))
def run(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.rstrip()
apicheck = run("python3 scripts/api_check.py")
ledger = run("python3 scripts/ledger.py stats")
shadow = run("python3 scripts/shadow.py stats")
calib  = run("python3 scripts/calibration.py stats")

md = f"""# Run B — 2026-08-30

**Gestart:** 05:10 CEST · **Dagrapport:** ARTIFACT_LINK · **Bets gepubliceerd:** 10 · **Wedstrijden diep geanalyseerd:** 35 van 38 gekwalificeerd (45 op de daglijst)

De run staat op `main`.

## Stage -2 — takken

`git fetch origin` gaf 22 takken. De repo kwam opnieuw als **ondiepe kloon** binnen
(`--is-shallow-repository` → `true`), precies het vals alarm dat §3 beschrijft: veertien takken
telden 27 tot 107 "eigen" commits. Die telling is hier niet met `--unshallow` weggenomen maar op
**inhoud** nagegaan, wat dezelfde vraag beantwoordt en niet van de kloondiepte afhangt:

- Voor elk van de veertien takken is `data/picks.jsonl` uitgelezen en per pick op
  (datum, wedstrijd, markt, selectie) vergeleken met `main`. Uitkomst: **0 picks die niet al op
  `main` staan** — `main` heeft er 189, de rijkste tak 63.
- Ook op bestandsniveau: `git ls-tree -r --name-only` van elke tak tegen die van `main` gaf **geen
  enkel bestand** dat alleen op een tak bestaat.
- De drie takken met de nieuwste commits (`stoic-davinci-38pm7k`, `zealous-edison-fwkjig` en deze
  sessie) wijzen alle drie exact naar `a1dc5e0`, de kop van `main`.

Er viel dus niets te mergen, en er waren geen openstaande picks van een run die op een andere tak
nooit is afgewikkeld.

## Dekkingsrapportage

{sec['dekking']}

**Afgekapt door `MAX_DEEP_ANALYSES` (35, zondag):** 3 wedstrijden, alle drie `LIGHT` en alle drie
onderaan de datarijkdomsortering — Osijek – Slaven (datarijkdom **6.25**, 1 markt),
Sparta Prague – Slavia Prague (6.0, 1 markt) en Teuta Durrës – KF Tirana (4.17, **0** markten). De
laagste die het nog haalde was FCSB – UTA Arad met **6.5**; de hoogste die afviel Osijek – Slaven
met **6.25**. Dat verschil is klein, en het is eerlijker om te zeggen dat de tier-sleutel hier het
werk deed: alle 27 `FULL`-duels gingen voor, waarna er nog acht van de elf `LIGHT`-plekken over
waren. Twee van de drie afgekapte duels lieten in een voorverkenning wél een kandidaat zien; ze
zijn niet gepubliceerd, want een cap die je opzij zet zodra hij iets kost is geen cap.

**Tier NONE:** 7 wedstrijden, alle om dezelfde reden — minstens één ploeg heeft geen historie in
deze divisie in het referentieseizoen (promovendus of degradant): Mallorca – AD Ceuta FC,
Arezzo – Palermo, Benevento – Südtirol, Pisa – Catanzaro, St. Pauli – Kaiserslautern,
FC Vaduz – Grasshopper en FC Eindhoven – Heracles. Zonder onafhankelijke kansinput geen bet (§2).

### Bevinding: elf van de achttien "NONE" waren een naamprobleem, geen datagat

De eerste doorrekening zette **18** duels op `NONE`. Bij nazicht bleken er elf niets met ontbrekende
data te maken te hebben maar met de naam: de Fotmob-**daglijst** gebruikt de korte weergavenaam en
de Fotmob-**standtabel** de volledige. "Wigan" tegen "Wigan Athletic", "Cádiz" tegen "Cadiz",
"Viktoria Plzeň" tegen "Viktoria Plzen", "HamKam" tegen "Hamarkameratene". Dat leest als
"promovendus, geen historie" terwijl het gewoon dezelfde club is.

Met een koppeling op genormaliseerde naam (diakrieten weg, cluballerlei als *FC*, *Town*, *United*
weg) plus een gelijkenismatch over het hele ploegenpaar bleven er **7** echte NONE-gevallen over —
allemaal aantoonbaar gepromoveerd of gedegradeerd. Elf duels die anders ongezien waren afgevallen,
zijn nu doorgerekend; drie ervan leverden een bet op (Cádiz – Real Valladolid, Kisvárda – Györi ETO,
Mansfield – Luton). Dezelfde koppeling redde aan de prijzenkant Kisvárda – Györi ETO: BetExplorer
noemt de uitploeg "Gyor", en zonder gelijkenismatch was de enige prijs van dat duel weggevallen.

Dit is een defect dat stil was: een `NONE` in de dekkingstabel ziet er precies zo uit of hij nu een
promovendus of een spelfout betreft. De koppelcode staat in `tmp-run/rb_names.py`; hij hoort op
termijn in `scripts/` thuis, dat staat onder "Nog te doen" hieronder.

## Bronstatus deze run

Letterlijke uitvoer van `python3 scripts/api_check.py`:

```
{apicheck}
```

**API_FOOTBALL_KEY ontbreekt** — twintigste dag op rij. Dit is de sleutel die telt: zonder hem hangt
de hele kansinput aan Fotmob alleen. Zie `README.md` → "Sleutels toevoegen".

**De reserve-oddsbron OddsPapi is niet inzetbaar.** `should_use(56)` gaf letterlijk
`(False, 'ODDSPAPI_KEY niet gezet')`, en `ensure_discovered()` gaf
`(False, 'ODDSPAPI_KEY niet gezet — niets te ontdekken')`. De §1b-controle "test het noodaggregaat
vóór de stroomstoring" is dus voor de zoveelste run niet uitgevoerd, niet omdat hij is overgeslagen
maar omdat er niets te testen valt. Zou The Odds API leeglopen, dan staat er geen reserve klaar.

| Bron | Status | Detail |
|---|---|---|
| Fotmob | ok | Alle 15 spelende competities opgehaald, geen fout. Context + transfers voor alle 38 duels met een tier. |
| BetExplorer | ok | 14 van de 15 slugs leverden rijen; `albania/kategoria-superiore` opnieuw 0 (gat sinds 13 aug). |
| The Odds API | ok | 56 credits over bij aanvang, 9 uitgegeven, 47 na de run. Alle 9 sportkeys actief, geen 4xx. |
| API-Football | key_missing | Sleutel niet in de omgeving (dag 20). |
| OddsPapi (reserve) | key_missing | Zie hierboven; niet getest, niet inzetbaar. |

Wijzigingen t.o.v. vorige run: **één verbetering** — Fotmob heeft nu ook xG voor **English League
One in het lopende seizoen 2026/2027** (`has_xg=true`, league_id 108, na 3 speeldagen). De
dekkingsnotitie zei nog "alleen 2025/2026". Verder geen bron omgevallen of hersteld.

### Creditbudget (§1a)

Plafond `suggest_cap(56, 2)` = **9**. Uitgegeven: **9 van 9 credits in 9 aanroepen, nog 47 over.**

Verdeling volgens §1a stap 0 — spreads eerst, want één credit levert er drie markten mee:

- **spreads (8 credits, 8 competities):** 2. Bundesliga, Allsvenskan, Austrian Bundesliga,
  Eliteserien, Greek Super League, Segunda División, Serie B, Swiss Super League. Elk daarvan
  heeft daarmee vier van de zes markten (1X2 gratis + AH + DNB + DC).
- **totals (1 credit):** English League One, de competitie die vandaag aan de beurt was in
  `rotate_for_day`.
- **BTTS:** 0 — 2 credits per wedstrijd past niet in een plafond van 9.

**Marktbalanscontrole op de inkoop:** er zit minstens één competitie met een doelpuntenmarkt
(English League One, totals) én ruimschoots een met een uitkomstmarkt in de run. De controle is
dus groen, maar wel krap: bij een plafond van 9 en negen competities met een sportkey kon er
precies één doelpuntenmarkt bij. Dat verklaart de ene Over/Under-bet hieronder — niet een oordeel
over doelpuntenmarkten, maar de portemonnee.

## Marktbalans

{sec['marktbalans']}

De aantallen "selecties doorgerekend" komen uit `all_candidates` in `data/run-state/`, dat per
wedstrijd op twaalf regels is afgetopt; bij de duels met elf of twaalf kandidaten is het echte
aantal dus gelijk of iets hoger. De verhouding klopt wel: **9 van de 10 bets komen uit vier
verschillende markten**, tegen 12 van de 14 uit één markt op 29 augustus. Double Chance stond
in zes competities te koop en won nergens de `selection_score` — dat is een uitkomst, geen gat.

## Wedstrijden

{sec['wedstrijden']}

## Topselectie

De topselectie is de bovenste vijf op `selection_score` (= edge × kans × 1.0 voor FULL / 0.5 voor
LIGHT), met ten hoogste twee `LIGHT`-bets. Die grens beet: Kisvárda – Györi ETO en VVV-Venlo –
FC Emmen vulden de twee LIGHT-plekken, waardoor Teplice – Jablonec (score 1.769) en FCSB – UTA Arad
(1.514) er buiten bleven ook al zijn ze wél gepubliceerd.

{sec['top']}

**Waarom nummer 1 en 2, en waarom ze tegelijk `high` risico zijn.** Beide zijn een handicap op de
underdog en beide steunen op een groot verschil met de markt: bij Salzburg – Austria Wien geeft de
markt Salzburg 68.7% (de-vigd), het xG-model 50.8% en de splitsmethode 42.2%. Zo'n gat van 18 tot
26 procentpunt is precies waar dit model zijn bekende zwakte heeft — het kent geen competitiesterkte
en verwerkt geen zomertransfers — en het is niet te zeggen of de markt of het model gelijk heeft.
De score rangschikt, de risicoklasse waarschuwt; die twee zijn hier met opzet niet hetzelfde.

**Let bovendien op de split-rondes bij Zwitserland en Oostenrijk.** In beide competities dekt de
xG-respons méér duels dan de stand (SUI 38 tegen 33, AUT 32 tegen 22), zoals de docstring van
`fotmob.fetch_league_stats` waarschuwt. Bij St. Gallen – Thun loopt dat zichtbaar uit elkaar: de
xG-methode geeft Thun 28.9% winstkans, de splitsmethode 48.0%. Ze wijzen dezelfde kant op — dat is
wat poort 5 eist en wat de docstring als voorwaarde stelt om op zo'n competitie te betten — maar de
afstand tussen de twee is groot genoeg om deze bet niet zwaarder te wegen dan zijn risicoklasse
toestaat.

## Net niet

{sec['netniet']}

Vijftien kandidaten met een echte edge zijn afgewezen. De verdeling is opvallend en past bij wat
§6d over poort 5 zegt: **acht** van de vijftien vielen af op `tweede_methode`, en in zeven van die
acht is het de **xG-methode** die negatief staat terwijl de splitsmethode +9 tot +25 pp geeft.
Vijf van die zeven staan in de Eliteserien, waar het lopende seizoen (17 speeldagen) de basis is.
Dat is één dag en dus geen bevinding — maar het is precies het patroon dat §6d als "één poort vangt
structureel alles weg" laat opsporen, en het is het volgen waard.

## Afwikkeling vorige picks

Geen openstaande picks ouder dan `SETTLE_AFTER_HOURS` (12 uur): `ledger.py open` gaf
"Geen openstaande picks ouder dan 12 uur". Run A heeft vanochtend de picks van 29 augustus
afgewikkeld. De 24 openstaande schaduwpicks zijn alle van vandaag (Run A) en worden morgen
afgerekend.

## Stand van het logboek

`python3 scripts/ledger.py stats`:

```
{ledger}
```

`python3 scripts/shadow.py stats`:

```
{shadow}
```

`python3 scripts/calibration.py stats`:

```
{calib}
```

**Vroeg-seizoenscorrectie.** Gemeten factor **1.0563** (ruwe gepoolde verhouding 1.0758 over 23
speeldagen, 7 competities met xG in beide seizoenen). Eliteserien en Allsvenskan tellen niet mee en
krijgen factor 1.0: daar is het **lopende** seizoen (17 resp. 19 speeldagen) de basis, dus er is
geen niveau uit vorig jaar om te corrigeren. De correctie is volledig uit xG-waarnemingen bepaald
en op geen enkel punt tegen de markt afgeregeld (§2). Tegenover de markt gemeten: de kalibratietabel
hierboven zet de gemiddelde afwijking op longshots vandaag op **+1.31 pp** over 60 waarnemingen,
tegen +1.34 gisteren en +4.19/+4.04 op 22–23 augustus. De reeks loopt dus de goede kant op, maar
één dag zegt daar niets over.

## Nog te doen

1. **`API_FOOTBALL_KEY` zetten.** Twintigste dag. Zolang die ontbreekt is Fotmob de enige kansbron
   en valt bij elke Fotmob-storing de hele run stil.
2. **`ODDSPAPI_KEY` zetten**, al is het maar om `ensure_discovered()` één keer te laten draaien.
   Nu is de reserve een noodaggregaat dat nooit is aangeslingerd.
3. **De naamkoppeling uit `tmp-run/rb_names.py` naar `scripts/` verhuizen.** Elf ten onrechte op
   `NONE` gezette duels op één dag is geen incident; elke run die de daglijst tegen de standtabel
   legt heeft dit nodig.
4. **BetExplorer heeft nog steeds geen kalender voor Albanië.** Zeventien dagen open. Zonder
   oddsbron blijft Kategoria Superiore een competitie die we wel kunnen analyseren en niet kunnen
   spelen.

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""
open("runs/2026-08-30-run-b.md", "w").write(md)
print("geschreven:", len(md), "tekens")
