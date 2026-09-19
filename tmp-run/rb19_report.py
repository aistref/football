"""Bouwt runs/2026-09-19-run-b.md uit de vaste tekst plus de blokken die uit de repo komen.

De dekkingstabel en de wedstrijdsecties komen uit `tmp-run/rb19_md.py` (dat leest
`data/run-state/`), de statistiekblokken uit de `*.txt`-uitvoer die deze run is weggeschreven.
Overtypen is precies de fout die §5 en §6c benoemen.
"""
import json

P = json.load(open("tmp-run/rb19_parts.json"))
TXT = lambda p: open(p).read().rstrip()

DOC = f"""# Run B — 2026-09-19

**Gestart:** 05:08 CEST · **Bets gepubliceerd:** 0 · **Wedstrijden diep geanalyseerd:** 42 van 57 · **Afgekapt:** 2

Branch: de sessie startte op `claude/zealous-edison-elu4ga`, maar alle commits van deze run staan
op **`main`** (§6a) — de scheduler-tekst geeft daar expliciet toestemming voor.

**Leesbaar dagrapport:** https://claude.ai/artifact/Cp4UTtLb1UGJdfQHJ1Gfn1

## Samenvatting in één alinea

Veruit de drukste Run B-dag tot nu toe, en nul bets. Vijftien van de zeventien competities uit
`prompts/run-b.md` speelden, samen **57 duels** — met voor het eerst een volledige zaterdagronde in
zowel English League One (11) als English League Two (12). Tweeënveertig duels kwamen door de
datadekkingspoort (24 `FULL`, 18 `LIGHT`); **vijftien kwamen op `NONE` uit**, en die vijftien
vallen in drie groepen van precies vijf — geen divisiepaar voor dat land, een divisie onder de
onderkant van de `TIER2`-ketting, of `conversion_in_range`. Die driedeling is de bevinding van
vandaag. Uit de 42 doorgerekende duels kwamen **460 selecties over alle zes de markten** en nul
bets: 438 vielen af op de edge-poort, 17 op de koersband en 5 op de herijking. De dichtstbijzijnde
bet is Asian Handicap Kristiansund BK +1,25 op **+5,99 pp tegen een drempel van 8,0**. De cap van 55
raakte voor het eerst in weken werkelijk iets — twee duels — maar allebei stonden ze al op `NONE`.

## Stage -2 — Branches

De branchcontrole is als allereerste handeling uitgevoerd, vóór het lezen van de regels.
`git fetch origin` bracht **31 takken** naast `main` in beeld.

De eerste telling, op de ondiepe kloon waarmee de container start
(`git rev-parse --is-shallow-repository` → `true`), gaf **26 takken met 4 tot 184 "eigen"
commits**. Dat is het valse alarm waar Stage -2 expliciet voor waarschuwt: bij een ondiepe kloon
ligt het punt waarop de takken uiteenliepen vóór de knip, dus telt élke commit van vóór die knip
mee als "nog niet hier". `git merge-base` gaf voor alle 26 takken letterlijk *"no merge base"*, en
de wortel van `main` stond op 10 sep 2026 — zes dagen jong, terwijl de repo in augustus begint.

Na `git fetch --unshallow origin` (327 commits geschiedenis) staat de teller op **0 van de 31** —
geen enkele tak bevat een commit die `main` niet heeft, en er viel dus niets te mergen. Dit is
precies de tabel die §3 Stage -2 voor 20 aug 2026 laat zien, nu opnieuw en met dezelfde uitkomst.

Er staan ook geen openstaande picks van een run die op een andere tak nooit is afgewikkeld:
`ledger.py open` gaf *"Geen picks klaar om af te wikkelen"* en `shadow.py open` alleen de zestien
schaduwpicks van Run A van vanochtend, van wedstrijden die vandaag nog gespeeld moeten worden.

De sessie kreeg `claude/zealous-edison-elu4ga` toegewezen; die tak stond exact gelijk aan `main`.
Alles is met `git push origin HEAD:main` gepusht.

## Bronstatus deze run

Uitvoer van `python3 scripts/api_check.py`, letterlijk (§3, Stage 3):

```
{P['api']}
```

**Wat daaruit volgt.** `API_FOOTBALL_KEY` is **niet gezet** — ontbrekend, niet afgewezen:
`api_check.py` slaat de bron over zonder HTTP-verzoek. Dat is onveranderd sinds de eerste run en
geen nieuwe blokkade. Gevolg voor deze run: **geen enkel duel is hierdoor op `NONE` uitgekomen.**
De kansinput kwam van Fotmob, en de vijftien `NONE`-duels gaan allemaal over een omrekening die
niet kon, niet over een ontbrekende sleutel. The Odds API is in orde met 19.012 credits over.

| Bron | Status | Detail deze run |
|---|---|---|
| Fotmob | `ok` | daglijst (15 competities met wedstrijden), standen vorig + lopend seizoen voor alle vijftien, context voor **alle 57 duels zonder één fout**, stadioncontrole |
| BetExplorer | `ok` | vijftien slugs opgehaald, **vijftien raak**, samen 122 rijen — inclusief `albania/abissnet-superiore`, dat op 18 sep nog nul rijen gaf |
| The Odds API | `ok` | 19.012 over; 35 credits uitgegeven (9× bulk à 3 + 8× BTTS à 1 halve ronde van 2) |
| API-Football | `key_missing` | sleutel niet in de omgeving van de geplande taak (README → "Sleutels toevoegen") |
| Understat | niet aangeroepen | dekt alleen de vijf grote competities; geen daarvan staat op de runlijst van Run B |

**Eén verbetering ten opzichte van 18 sep, en het is het openstaande punt 2 van die dag.** De
BetExplorer-slug `albania/abissnet-superiore` gaf gisteren **nul rijen** — geen HTTP-fout, gewoon
een lege tabel — waardoor Vllaznia – Teuta Durrës zonder koers bleef. Vandaag geeft hij er weer
één. Dat is dus geen verhuisde pagina geweest maar een lege kalender, en het punt kan dicht. De
Albanese duels van vandaag stranden op iets anders (zie hieronder), niet op de prijzen.

Uitvoer van `CreditGuard.report()` (§1a), beide rondes:

```
27 van 791 credits gebruikt in 9 aanroep(en), nog 18985 over
8 van 764 credits gebruikt in 8 aanroep(en), nog 18977 over
```

## Dekkingsrapportage

{P['cov']}

**Afgekapt door `MAX_DEEP_ANALYSES`:** 2 wedstrijden. De cap staat op 55 (vr–zo) tegen 57 duels,
en dit is de eerste Run B sinds weken waarop hij werkelijk bindt. Wat de afkapping kostte is
**niets**: Debrecen – Vasas Budapest en FC Dinamo City – Laçi stonden allebei al op `NONE`.

De twee getallen die §3 Stage 4 vraagt staan daarbij opvallend dicht op elkaar. De laagste
datarijkdom die het nog haalde is **4,5** (Vora – Skënderbeu); de hoogste die afviel is **eveneens
4,5** (Debrecen – Vasas Budapest). De cap sneed dus dwars door een gelijkspel in de rangschikking
en de aftraptijd gaf de doorslag. Dat is exact het beeld dat §3 Stage 4 zelf beschrijft — *"de
sortering scheidt niet"* — en het is hier voor het eerst als zodanig te zien in plaats van als
meting achteraf. De spreiding over de hele run liep van 4,5 tot **8,0** (Crewe Alexandra –
Shrewsbury Town).

## Vijftien duels op `NONE`, in drie groepen van vijf

Dit is de bevinding van vandaag, en het is geen datagat: van de 57 duels hadden er **25** minstens
één ploeg die niet in de stand van vorig seizoen van de eigen competitie staat. §4 schrijft voor
zo'n ploeg **eerst de omrekening** voor en pas daarna `NONE`. Voor tien lukte dat; vijftien
stranden, en precies vijf per oorzaak.

**Groep 1 — geen divisiepaar voor dat land (5 duels).** Iraklis (Griekenland), Vasas Budapest
(Hongarije), Austria Lustenau (Oostenrijk), Skënderbeu en Laçi (Albanië). `promotion.TIER2` kent
achttien divisieparen en deze vier landen zitten daar niet bij, dus `promotion.convert` gooit
meteen *"geen divisie boven of onder … bekend"*. Dit is hetzelfde geval als de drie duels van
18 sep (Kroatië, Hongarije, Roemenië) en het staat al als openstaand punt.

**Groep 2 — onder de onderkant van de ketting (5 duels).** Tenerife en Eldense promoveerden naar de
Segunda División; Rochdale en York City naar League Two; VfL Osnabrück staat noch in de 2.
Bundesliga noch in de Bundesliga erboven. De ketting `TIER2` loopt van de Premier League tot League
Two en van La Liga tot LaLiga2 — en daar houdt hij op. Een ploeg die van **onder** die onderkant
komt, is dus niet te volgen. **Voor Run B weegt dat zwaarder dan voor Run A**, en dat is het punt:
deze runlijst zit per definitie aan de onderkant van de ladder, dus waar Run A een ploeg nog een
divisie omlaag kan volgen, staat Run B daar al.

**Groep 3 — `conversion_in_range` (5 duels).** Hier lukte de omrekening wél, maar viel de uitkomst
buiten het bereik waarover het divisiegat is gemeten. Wat opvalt is hoe krap dat "buiten" is:

| Ploeg | Paar | Waarde | Gemeten bereik | Tekort |
|---|---|---|---|---|
| Girona | SP1/SP2 down (n=33) | verdediging 1,074 | 1,078 – 1,809 | **0,004** |
| Cambridge United | E2/E3 up (n=43) | verdediging 0,557 | 0,565 – 1,068 | **0,008** |
| Port Vale | E2/E3 down (n=43) | verdediging 1,008 | 1,033 – 1,861 | **0,025** |
| Exeter City | E2/E3 down (n=43) | verdediging 1,008 | 1,033 – 1,861 | **0,025** |
| Leicester City | E1/E2 down (n=33) | aanval 0,968 | 0,473 – 0,939 | **0,029** |

**Alle vijf binnen drie honderdsten van de grens, en geen van de vijf een uitschieter.** Dat is een
ander beeld dan de Coventry-val waarvoor `conversion_in_range` is gemaakt: daar ging het om een
ploeg die ver buiten het waargenomen bereik viel en +21 pp schijnedge opleverde die alle andere
poorten haalde.

**Toch gaat het bereik niet open, en dat is geen aarzeling maar de regel.** `conversion_in_range`
is een poort en geen aantekening (§4). "Het scheelt maar 0,004" is precies de redenering waarmee
schijnedge binnenkomt, en de grens zélf is een waarneming uit een eindige steekproef — 33 tot 43
paren — dus hem met de hand verschuiven is de steekproef overschrijven met een wens. Wat hier
gebeurt is de regel die werkt zoals hij hoort.

**Wat het zou kosten om het op te lossen.** Niet het bereik oprekken maar het opnieuw méten, in de
geest van 31 aug 2026: het bereik per divisiepaar over meer seizoenen vaststellen, zodat de grenzen
op meer dan 33 à 43 waarnemingen rusten. Valt de grens dan lager uit, dan komen deze duels er
vanzelf binnen; valt hij niet lager uit, dan hoorden ze er niet in. Werk voor een aparte sessie —
zie "Openstaand".

## De omrekeningen die wél konden (§4)

Tien van de 25 kandidaten kwamen erdoor en zijn op `LIGHT` doorgerekend — een omgerekende ploeg is
nooit `FULL`, dus daar staat de drempel op 16,0 pp en gaat de herijking van §1g daar nog overheen.
Geen van de tien kwam vandaag in de buurt van een bet, en dat is de verwachte uitkomst en geen
teleurstelling.

## Stadioncontrole (§1c)

`context.check_venue` sloeg bij **drie** duels aan: Kisvárda – Paksi SE, Real Sociedad B – Mallorca
en FC Andorra – Sporting Gijón. Alle drie zijn ze bij naleggen **geen echte verplaatsing**, en de
oorzaak is in alle drie gevallen dezelfde: het veld `home_ground` komt uit het *clubdossier* en niet
uit de wedstrijd.

* Kisvárda speelt in "Varkert Sportpalya" tegen een clubdossier dat "Várkerti Stadion" zegt — zelfde
  stadion, andere schrijfwijze (diakrieten).
* Real Sociedad B speelt op Campo José Luis Orbegozo in Zubieta, het eigen terrein van het
  beloftenelftal; het clubdossier noemt het stadion van de A-selectie.
* FC Andorra speelt in het Estadi Nacional in Andorra la Vella, wat gewoon hun thuisbasis is.

Bij alle drie geldt `at_away_ground = false`, dus geen van de drie speelt bij de tegenstander en het
thuisvoordeel blijft intact. De poort houdt hier dan ook niets tegen — hij zet alleen de vlag, en
§1c schrijft voor die vlag te noteren ook als de poort opengaat. Dat is hier gedaan. **Wat dit
aanwijst voor later:** drie valse positieven op één dag is veel, en de oorzaak is telkens hetzelfde
veld. Een naamvergelijking die diakrieten negeert zou de eerste al wegnemen. Dat is geen wijziging
voor een dagelijkse run, maar het staat als openstaand punt.

## Wedstrijden

{P['secs']}

## Topselectie

**Geen.** Nul gepubliceerde bets, dus er is niets te rangschikken. §5 is daar expliciet over: zijn
er minder gekwalificeerde bets dan `MAX_SHORTLIST` (5 op vr–zo), lever er dan minder, en vul niet
aan.

Wat er wél is, zijn de twee ranglijsten van §5a — de herijkte en de ruwe — en die staan hieronder en
op de HTML-pagina. Ze komen uit `scripts/toplist.py` en zijn niet overgetypt.

### De dagelijkse top-5, twee keer gerekend (§5a)

```
{TXT('tmp-run/rb19_top.txt')}
```

**Lees de ruwe lijst als meting en niet als tip.** §1g heeft op 552 afgerekende gevallen gemeten dat
er géén drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het *slechtst*
is bij de hoogste geclaimde edge. De ongecorrigeerde edge is precies die grootheid. Wat de lijst
wél doet: elke selectie die alleen op de herijking sneuvelde gaat als schaduwpick het logboek in en
wordt daar afgerekend — vandaag drie stuks.

### Net niet

De volledige cijfers per poort staan per wedstrijd hierboven en in `data/run-state/`. Samengevat,
de vier selecties die het dichtst kwamen:

| Wedstrijd | Selectie | Koers | xG-model | 2e methode | Zwakste stand | Herijkt | Valt af op |
|---|---|---|---|---|---|---|---|
| Kristiansund – Rosenborg | AH Kristiansund BK +1,25 | 1,89 | +18,95 | +24,12 | +15,70 | **+5,99** | `edge` (en ruw op `underdog`) |
| Luzern – Grasshopper | Over 3.5 | 2,02 | +11,80 | +17,76 | +10,12 | **−0,47** | `herijking` |
| Blackpool – Plymouth Argyle | Over 2.75 | 1,81 | +9,34 | +10,51 | +7,57 | **−4,12** | `herijking` |
| Gillingham – Bristol Rovers | Over 2.5 | 1,93 | +8,63 | +9,15 | +7,73 | **−4,49** | `herijking` |

**Eén patroon springt eruit en het is het bekende.** Drie van de vier zijn doelpuntenmarkten aan de
**Over**-kant, alle drie ruim positief op beide methodes én op de zwakste stand van het
(shrink, rho)-grid, en alle drie draait de herijking ze van ruim positief naar negatief. Dat is
geen toeval van vandaag: §1g haalt ongeveer tien tot dertien procentpunt van elke kans in dit
bereik af, en een Over-kans van rond de 62% zakt daarmee naar rond de 49%. Het is ook precies de
reden dat de vroeg-seizoenscorrectie hieronder aandacht krijgt — een correctie die het
doelpuntenniveau **verhoogt** duwt dezelfde selecties omhoog die de herijking daarna weer naar
beneden haalt.

Geen enkele selectie viel deze run af op poort 5 (tweede methode), 6 (robuustheid) of 7 (context).

## Marktbalans (§1a — controle op de inkoop, niet op de uitkomst)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 14 van 14 doorgerekende (9× beste prijs, 5× BetExplorer-gemiddelde) | 126 | 0 |
| Asian Handicap | 9 van 14 (de bulk-aanroep) | 128 | 0 |
| Draw No Bet (0.0-lijn) | 7 van 14 | 40 | 0 |
| Double Chance (±0.5-lijn) | 7 van 14 | 14 | 0 |
| Over/Under | 9 van 14 (de bulk-aanroep) | 136 | 0 |
| BTTS | 5 van 14 — 8 duels met kandidaat-edge, 8 gekocht | 16 | 0 |

**De controle slaagt zo ruim als hij kan:** alle **9 van 9** ingekochte competities hebben zowel een
uitkomstmarkt als een doelpuntenmarkt. `split_budget(791, 9)` gaf 9 spreads / 9 totals en het
plafond liet 3 credits per competitie ruimschoots toe, dus elke inkoopbare competitie kreeg de volle
bulk — vijf van de zes markten in één aanroep.

**Wat de controle níet laat zien en wat hier wel hoort.** Zes van de vijftien spelende competities
zijn helemaal niet in te kopen: Tsjechië, Kroatië, Hongarije, Roemenië, de Keuken Kampioen Divisie
en Albanië hebben geen sportkey bij The Odds API. Dat zijn **tien van de 42** doorgerekende duels,
en die staan op een 1X2-marktgemiddelde zonder handicap-, doelpunten- of BTTS-markt: drie selecties
per duel in plaats van elf tot zeventien. Daar valt de edge systematisch te laag uit — conservatief,
dus geen risico op te veel bets, maar niet vergelijkbaar met de 32 duels waar de beste prijs wél
bekend is. Dat is een dekkingsprobleem en geen creditprobleem: er bleven 756 van 791 credits
ongebruikt.

**De beste prijs t.o.v. het marktgemiddelde**, over de 32 duels waar beide bronnen een prijs gaven:
gemiddeld **+6,74%**, mediaan **+6,41%**. Dat is de ruimste steekproef die deze meting tot nu toe
heeft gehad en ze ligt in lijn met de +7,78% van 5 sep 2026. Waar de beste prijs bij een beurs stond
(Betfair, Matchbook) is hij door `oddsapi.net_price` gehaald: 2% commissie over de nettowinst.

## Vroeg-seizoenscorrectie

De correctie staat deze run op **×1,0904**, gepoold over **vijftien competities en 134 speeldagen**
— opnieuw de ruimste steekproef die deze routine heeft gehad, doordat ook de zes competities zonder
Fotmob-xG meetellen (daar op **doelpunten** gemeten, dezelfde eenheid als waarin die duels rekenen,
dus teller en noemer staan gelijk en er komt geen bookmakerprijs aan te pas).

De controle die §3 Stage 5 vraagt, P(Over 2.5) tegen de de-vigde marktkans:

| | gemiddelde afwijking | gem. absolute fout |
|---|---|---|
| zonder correctie | **−2,19 pp** | 4,29 pp |
| met correctie ×1,0904 | **+3,42 pp** | 4,80 pp |

**De correctie schiet door, en dit is de tweede Run B op rij waarop dat zo uitvalt.** Ze haalt een
onderschatting van ruim twee procentpunt weg en zet er een overschatting van ruim drie voor terug;
de gemiddelde absolute fout loopt daarbij op in plaats van af. Op 18 sep was het beeld hetzelfde
(−3,59 → +2,81) maar toen over **vier** wedstrijden, en dat was ruis. Vandaag zijn het er **23**.

**Wat dit wel en niet betekent.** Het is een **diagnose**, geen stelknop: §1d en §6e verbieden
uitdrukkelijk om deze factor op de markt af te regelen, want dan is `my_prob` van de odds afgeleid
en meet `edge_pp` niets meer (§2). Wat het wél is, is een tweede waarneming in dezelfde richting op
een steekproef die iets begint te zeggen — en ze wijst dezelfde kant op als de "Net niet"-tabel
hierboven, waar drie van de vier bijna-bets Over-selecties zijn die het doelpuntenniveau te hoog
zetten. Komt dit een derde keer terug, dan hoort `early_season_uplift` op **uitkomsten** te worden
nagerekend — dat mag wel, en het is dezelfde route die §0 voor de drempel en §1g voor de herijking
heeft gelopen. Zie "Openstaand".

## Schaduwlogboek (§6d)

Zes schaduwpicks toegevoegd; het logboek staat nu op **510**.

* `underdog_ruw` (3): Kifisia FC om te winnen bij Atromitos @ 4,04 (ruw +8,37 pp), Kristiansund BK
  +1,25 @ 1,89 (ruw +19,98) en Bromley FC +1 @ 1,97 (ruw +18,41).
* `herijking` (3): Over 3.5 bij Luzern – Grasshopper @ 2,02, Over 2.75 bij Blackpool – Plymouth
  @ 1,81 en Over 2.5 bij Gillingham – Bristol Rovers @ 1,93.

De `near_miss` op Kristiansund is **niet** apart geboekt: hij beschrijft dezelfde markt en koers als
de `underdog_ruw`-rij, en §1e schrijft voor dat `shadow.py collect` die dubbeltelling overslaat. Hij
staat wél in `data/run-state/`, want §5 heeft hem nodig voor de "Net niet"-tabel — het *logboek* mag
niet dubbel tellen, het rapport mag geen regel missen.

```
{TXT('tmp-run/rb19_shadow.txt')}
```

**Lees dit met §6d ernaast: onder ~30 afgewikkelde gevallen per poort is elk verschil ruis.** Drie
dingen die daar vandaag onder vallen en die dus géén bevinding zijn: `underdog` staat op 9
afgewikkelde gevallen (+34,8%), `underdog_ruw` op 11 (−46,0%) en `robuustheid` op 22 (−44,8%).

**Poort 8 vervalt over zes dagen, op 25 september**, en de reeks haalt de dertig die §1e eist niet
— dat is op 18 sep aan de gebruiker voorgelegd en hij heeft gekozen voor vervallen zonder meting
(keuze C, vastgelegd in `scripts.sides.LAPSES_ON`). Dat punt staat daarmee niet meer open. Wat
vanaf 25 september in de plaats komt is `would_block`: `sides.check()` blijft aanwijzen welke
selecties de poort zou hebben tegengehouden, en wordt zo'n selectie een gepubliceerde bet, dan gaat
dat als `poort8_zou_hebben_geblokkeerd` in de pick. Dan groeit er een reeks van échte afgerekende
bets op de kant waar de vraag over gaat.

Eén regel uit de tabel verdient wel aandacht omdat hij de dertig ruim haalt: **`edge` staat op 207
afgewikkelde gevallen met een ROI van +0,3%.** Dat is de enige poort die op een volwassen reeks
niet-negatief staat. Lees dat niet als "de drempel mag omlaag" — §1g heeft dat op 552 gevallen
nagerekend en er is géén drempel die geld oplevert — maar als de meting die §0 vraagt bij een
volgende herziening van `EDGE_THRESHOLD_FULL`.

## Contextlogboek (§1c)

44 wedstrijden toegevoegd; het logboek staat op **716**, waarvan 610 afgewikkeld.

```
{TXT('tmp-run/rb19_ctxstats.txt')}
```

De cijfers zijn identiek aan die in `runs/2026-09-19-run-a.md` van vanochtend — er is tussen beide
runs niets bij afgewikkeld, want de duels van vandaag moeten nog gespeeld worden. **Run A heeft de
bevinding erbij al opgeschreven** (Bevinding 1 van dat rapport: het logboek meet voor het eerst een
significant effect, en de markt maakt met −28,7 pp per eenheid vrijwel exact dezelfde fout als het
model met −29,4). Die staat hier dus niet nog een keer; wat Run B eraan toevoegt zijn de 44 nieuwe
wedstrijden, die over enkele dagen afgewikkeld worden en dan zeggen of het teken standhoudt.

Van de 57 duels leverden er 44 een bruikbare rij op. De dertien die afvallen missen een
selectiewaarde bij minstens één ploeg, waardoor `ctxlog.out_share` niets kan uitrekenen — dat is bij
de kleinere competities in deze runlijst de normale situatie en geen storing.

## Kalibratielogboek (§6e)

126 waarnemingen toegevoegd (42 wedstrijden); het logboek staat op **2.751** over 29 dagen.

```
{TXT('tmp-run/rb19_calib.txt')}
```

De bekende scheefstand staat er onverminderd: `my_prob` geeft longshots +1,96 pp méér kans dan de
markt en favorieten −3,79 pp minder, en van die +1,96 op longshots is +1,76 toe te schrijven aan
`shrink`. Het tweede xG-model (Understat) is daarin duidelijk de scheefste van allemaal (+4,58 /
−9,23), maar dat zegt vandaag niets over Run B: geen enkele competitie op deze runlijst wordt door
Understat gedekt, dus die regel komt volledig uit de Run A-dagen.

**Dit blok is en blijft een diagnose en geen correctiefactor** (§1d, ingetrokken instructie van
31 aug 2026): de afwijking is er een ten opzichte van de **markt**, en die van `my_prob` aftrekken
maakt de kansschatting een afgeleide van de odds.

## Afwikkeling vorige picks

Niets af te wikkelen. `ledger.py open` gaf *"Geen picks klaar om af te wikkelen"* — er staat geen
enkele pick meer open (274 picks, 274 afgewikkeld). `shadow.py open` gaf zestien schaduwpicks van
Run A van vanochtend, alle zestien van wedstrijden die vandaag nog gespeeld moeten worden
(*"bron meldt nog niet afgelopen"*). Run A heeft vanochtend de acht schaduwpicks van 18 sep
afgewikkeld; die stap was dus al gedaan toen deze run begon.

## Stand van het logboek

```
{TXT('tmp-run/rb19_ledger.txt')}
```

De stand van de herijking waarmee de kansen van vandaag zijn gepubliceerd (§1g) — elke run een
ander getal, want de fit loopt mee met het logboek:

```
{TXT('tmp-run/rb19_recal.txt')}
```

**De onderste regel van het ledgerblok is de regel die telt:** Brier eigen 0,2552 tegen Brier markt
0,2362. De bookmaker schat scherper dan het model, en dat is nog een gunstige vergelijking, want in
zijn getal zit zijn eigen marge. Zolang die regel zo staat is elk gemeten voordeel eerder modelfout
dan marktfout, en is **"vandaag niets" het juiste antwoord en geen defect**.

## Looptijd (§0)

De cap is een **tijds**grens en geen creditgrens: de rapporten moeten om 06:30 klaar staan. Deze
run startte om 05:08:06 CEST (containerstart) en was om 05:25:15 klaar — **17,2 minuten** voor 57
opgehaalde duels, 42 volledig doorgerekende duels en 460 selecties. Dat is de drukste dag tot nu
toe en hij past er ruim een uur binnen, dus 55 is vandaag aantoonbaar geen knellende grens.

Let op het onderscheid in `data/run-state/`: `duur.minuten` (8,2) telt vanaf het aanmaken van het
voortgangsbestand en laat Stage -2 buiten beschouwing — het unshallowen van de repo en de controle
op 31 takken. `duur.minuten_vanaf_containerstart` (17,2) is de volledige looptijd en is het getal
dat §0 bedoelt.

## Openstaand

1. **Het `conversion_in_range`-bereik rust op 33 à 43 waarnemingen per divisiepaar** (nieuw vandaag,
   kostte vijf duels, alle vijf binnen 0,03 van de grens). De remedie is méten, niet oprekken: het
   bereik per paar over meer seizoenen opnieuw vaststellen, zoals `MEASURED_TIER2_GAP` dat op 31 aug
   2026 voor de factoren zelf deed. Werk voor een aparte sessie.
2. **De `TIER2`-ketting houdt op bij League Two en LaLiga2** (kostte vandaag vier duels). Voor Run B
   is dat structureel, want deze runlijst zit aan de onderkant van de ladder: een ploeg die uit de
   National League of de Primera Federación promoveert is niet te volgen. Eén divisie dieper meten
   zou vier van de vijftien `NONE`-duels van vandaag hebben gered.
3. **Geen divisiepaar voor Griekenland, Hongarije, Oostenrijk en Albanië** (kostte vandaag vijf
   duels; op 18 sep kostte hetzelfde voor Kroatië, Hongarije en Roemenië er drie). Zelfde remedie als
   punt 1 en 2, zelfde waarschuwing: niet raden, meten.
4. **De vroeg-seizoenscorrectie schiet door — tweede waarneming, nu op 23 wedstrijden.** Zie
   hierboven. Als dit een derde keer terugkomt, hoort `early_season_uplift` op **uitkomsten** te
   worden nagerekend in plaats van op de markt. Niet op de markt afregelen (§1d, §2).
5. **`context.check_venue` gaf drie valse positieven op één dag**, alle drie doordat `home_ground`
   uit het clubdossier komt in plaats van uit de wedstrijd (diakrieten, beloftenelftal, tweede
   stadion). Een naamvergelijking die diakrieten negeert neemt er al één weg.
6. **Zes van de vijftien spelende competities zijn niet in te kopen bij The Odds API.** Dat is geen
   creditprobleem (756 van 791 ongebruikt) maar een dekkingsprobleem, en het maakt tien van de 42
   doorgerekende duels structureel armer: 1X2 op een marktgemiddelde, geen handicap, geen
   doelpuntenmarkt, geen BTTS.

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open("runs/2026-09-19-run-b.md", "w").write(DOC)
print("runs/2026-09-19-run-b.md geschreven:", len(DOC), "tekens")
