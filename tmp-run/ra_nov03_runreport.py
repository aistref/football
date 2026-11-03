"""Bouwt runs/2026-11-03-run-a.md: de vaste kop plus de ingesloten logboekuitvoer.

De logboekblokken worden uit de .txt-bestanden van deze run gelezen in plaats van overgetypt
(§6c: overtypen is precies hoe twee rapporten van dezelfde run uiteen gaan lopen).
"""

DEEL1 = open("tmp-run/ra_nov03_runreport_deel1.md").read()
DEEL2 = open("tmp-run/ra_nov03_runreport_deel2.md").read()


def blok(pad, titel, toelichting=""):
    txt = open(pad).read().rstrip()
    kop = f"### {titel}\n\n"
    if toelichting:
        kop += toelichting.rstrip() + "\n\n"
    return kop + "```\n" + txt + "\n```\n"


stand = "\n".join([
    blok("tmp-run/ra_nov03_ledgerstats.txt", "`ledger.py stats` — de gespeelde bets",
         "Het logboek staat op **516 picks**, waarvan 455 afgewikkeld en beslist, op **−7,7%**. "
         "De drie van vandaag staan erin als `pending` en tellen hier nog niet mee. Lees de regel "
         "`Brier markt` ernaast: de markt schat met 0,2408 nog steeds scherper dan het model met "
         "0,2603, en zolang dat zo is is elk gemeten voordeel eerder modelfout dan marktfout "
         "(§1g)."),
    blok("tmp-run/ra_nov03_shadowstats.txt", "`shadow.py stats` — wat de poorten hebben tegengehouden",
         "Twee regels die vandaag tellen. **`doelpunten_onder`**: 35 afgewikkelde kandidaten "
         "(trefkans 37,1%, −30,4%), boven de ~30 die §6d eist — zie \"Poort 9 raakt geen van de "
         "twee Unders\" hierboven. En **`edge`**: 608 kandidaten op **+2,1%**, de enige grote "
         "reeks met een positief teken. Dat is precies waarom §5b de drempel sinds 20 september "
         "aan het eind laat snijden in plaats van vooraf, en het is ook de reden dat regel 3 van "
         "vandaag onder haar lat in de lijst staat."),
    blok("tmp-run/ra_nov03_recalibrate.txt", "`recalibrate.py show` — de stand van de herijking (§1g)",
         "**`fitted_through` = 2026-11-02, dus op de vorige rundag — de controle van §6b-5c staat "
         "groen.** De analyse van vandaag liep met deze fit (`a=1.026, b=0.017` over 6927 "
         "gevallen); `calibration.py settle` van deze run liep vóór de analyse en heeft 87 "
         "waarnemingen afgewikkeld, dus de fit waarmee is gepubliceerd is dezelfde als de fit die "
         "hier staat. **Let op de richting:** deze fit **verhoogt** een kans over de hele "
         "speelbare band (+0,4 pp op 50%, +0,8 pp op 70%). Dat is de reden dat de derde stand van "
         "`bet_beide` vandaag voor het eerst bij een gepubliceerde bet voorkwam — zie de "
         "bevinding."),
    blok("tmp-run/ra_nov03_calibrationstats.txt", "`calibration.py stats` — het kalibratielogboek (§6e)",
         "2387 wedstrijden en 7161 uitkomsten. De scheefstand die poort 8 afdekt staat er nog: "
         "**+1,60 pp te veel kans op longshots en −3,26 pp te weinig op favorieten** over "
         "respectievelijk 2253 en 1092 waarnemingen. **De Understat-arm heeft vandaag geen nieuwe "
         "waarnemingen gekregen**, en dat is deze keer niet door de storing maar doordat geen van "
         "de vijf gedekte competities speelde. De 0,8-arm staat op +2,56 pp op longshots tegen "
         "+0,91 voor de 1,0-arm, en dat verschil is de reden dat `shrink` sinds 19 september op "
         "1,00 staat."),
    blok("tmp-run/ra_nov03_ctxlogstats.txt", "`ctxlog.py stats` — het contextlogboek (§1c)",
         "1972 afgewikkelde wedstrijden. Het effect van ontbrekende spelers op de modelfout staat "
         "op `r = −0,043` (`t = −1,77`), helling −12,0 pp per eenheid, en het teken wijst de "
         "verwachte kant op — maar met deze aantallen is alleen een effect vanaf ~12 pp per "
         "eenheid aantoonbaar. **Poort 7 blijft dus een rem en geen bijstelling**, precies zoals "
         "§1c sinds 5 september voorschrijft. De marge wordt wel kleiner: de drempel van de "
         "aantoonbaarheid staat nu op dezelfde grootte als de gemeten helling, en bij ongeveer "
         "2400 wedstrijden wordt dit voor het eerst een meting in plaats van een richting."),
    blok("tmp-run/ra_nov03_marginsstats.txt", "`margins.py stats` — het margelogboek (§6f)"),
    blok("tmp-run/ra_nov03_margins_since.txt",
         "`margins.py stats --since 2026-09-20` — alleen op `shrink = 1.00`",
         "Twee regels staan hier meer dan twee standaardfouten van de voorspelling af, en het "
         "zijn niet de regels waar §6f naar kijkt: **gelijkspel** (voorspeld 23,7%, werkelijk "
         "20,1%, −3,6 pp) en **0 of 1 doelpunt** (20,4% tegen 18,1%, −2,4 pp). De tweede is de "
         "doelpuntenas en die staat in `goalbias` hieronder scherper gemeten. De eerste is nieuw "
         "genoeg om te noemen en te klein om iets mee te doen: een scoregrid dat te veel "
         "gelijke spelen voorspelt maakt een Draw No Bet juist voorzichtiger dan nodig, en regel "
         "3 van vandaag is een Draw No Bet. Niet lezen onder ~30 gevallen per cel (§6d); dit zijn "
         "er ruim genoeg, maar het is één cel in een tabel van tien."),
    blok("tmp-run/ra_nov03_marginsgoalbias.txt", "`margins.py goalbias` — het doelpuntenlogboek (§6g)",
         "**Lees de twee regels nooit als één getal.** De bovenste meet het **model** en staat op "
         "+0,052 doelpunt per duel (`z = +1,32`) over 1976 duels: dat klopt vrijwel. De regels "
         "eronder meten de **selectie**, en daar staat de gespeelde Under-kant op **+0,651 "
         "doelpunt over 121 gevallen (`z = +4,32`)** tegen −0,268 op de Over-kant (66 gevallen). "
         "Dat is de meting waarop poort 9 rust en ze is vandaag opnieuw bevestigd, met een z die "
         "sinds 2 november van +4,31 naar +4,32 is gelopen. "
         "**En dit is de laatste meting vóór de niveaucorrectie.** Alle lambdas hierin komen van "
         "vóór 3 november en zijn dus ongecorrigeerd; `P(Under 2.5)` staat 2,2 pp te hoog. "
         "`LEVEL_SCALE` = 1.032 hoort daar ongeveer twee procentpunt van af te halen. Of dat zo "
         "is, is pas te zien als er genoeg duels van ná vandaag in dit logboek staan — en tot die "
         "tijd blijft poort 9 staan zoals hij staat (§1h)."),
])

OPEN = """## Openstaande punten

1. **De `abandoned()`-controle staat in een runscript en hoort in `scripts/settling.py`.** Nieuw
   vandaag. Een gestaakt duel komt bij Fotmob binnen als `finished = true` met een tussenstand, en
   zonder die controle wordt die tussenstand als eindstand geboekt — vandaag stonden twee
   schaduwrijen van Run B op het punt onterecht als `lost` te worden afgerekend. Zolang de
   controle in `tmp-run/` staat, heeft de volgende run hem alleen als zij hem overneemt. Dat is
   dezelfde reden waarom de aliastabel op 5 oktober van `tmp-run/ra_names.py` naar
   `scripts/teamnames.py` is verhuisd (§3 Stage -2). **Ik pak dit op in de run van 4 november**, met
   een zelftest erbij.
2. **Welke van de twee methodes zit er stelselmatig naast?** Van de negen "Net niet"-regels van
   vandaag vielen er **drie** af op `tweede_methode`, en bij alle drie staat de splitsmethode
   ónder de marktkans terwijl de xG-methode erboven staat — bij Barcelona – Aston Villa met 23
   procentpunt ertussen (+21,50 tegen −1,84). Bij drie andere wedstrijden staat de splitsmethode
   juist extreem hoog: +25,59 bij Blackburn, +30,32 bij QPR – Burnley, +22,24 bij Manchester
   United – Roma. Over de hele reeks vangt `tweede_methode` 255 kandidaten op −2,0%, dus de poort
   bespaart geld; wat nergens is gemeten is **wélke** van de twee methodes de fout maakt. Dit hoort
   uit het kalibratielogboek te komen, dat de twee armen al per wedstrijd apart bijhoudt, en niet
   uit een redenering. Geen parameter aanraken op grond van één dag (§6d).
3. **Understat, tweede dag onbereikbaar, met een ander symptoom.** Gisteren een 502 op de CONNECT
   van de netwerkgateway, vandaag `[Errno 104] Connection reset by peer`. Het kostte vandaag niets
   omdat geen van de vijf gedekte competities speelde; dat is toeval en geen herstel. Een derde dag
   op rij maakt het een toestand in plaats van een hapering, en dan hoort het in de notificatie en
   niet alleen in `source-health.json`. Valt **Fotmob** ook om, dan geldt de uitzondering van §3
   punt 3 en moet dat vooraan in de notificatie.
4. **De hardgecodeerde `+02:00` elders in de repo.** `runwindow.kickoff_nl` rekent met `zoneinfo`
   en dus met echte winter-/zomertijd; de rest van de repo gebruikt nog een vaste offset. Sinds de
   laatste zondag van oktober staat Nederland op wintertijd, dus dat verschil is nu één uur in
   plaats van nul. Dit raakt de **weergave** en niet de selectie, en het staat open sinds
   24 september.
5. **De vraag van 15 oktober over de leesroute van het dagrapport** staat nog open en is een
   besluit van de gebruiker (§6c). Zolang er niets wordt gezegd, blijft de HTML-pagina de eerste
   route en de Markdown-versie op GitHub de tweede, en bevat de notificatie beide links.
6. **De datarijkdom-score meet vandaag het tijdstip van de run en niet de wedstrijden.** De negen
   Champions League-duels staan op 7,0–8,0 en de negen Championship-duels op 5,0–5,5, en het hele
   verschil zit in het opstellingsblok: om 03:00 NL staat er voor een Europees avondduel al een
   voorspelde opstelling en voor de Championship niet. Vandaag bindt de cap niet, dus het kost
   niets; op een dag dat hij wél bindt zou de rangschikking een hele competitie achteraan zetten om
   een reden die niets met de wedstrijden te maken heeft. §3 Stage 4 heeft al gemeten dat deze
   score de betkans niet scheidt; dit is een tweede reden om hem niet zwaarder te maken dan
   "er moet iets afvallen als de cap knelt". **Geen ingreep op grond van één dag**, maar het hoort
   opgeschreven.
"""

md = DEEL1 + "\n## Stand van het logboek\n\n" + stand + "\n" + DEEL2 + "\n" + OPEN
open("runs/2026-11-03-run-a.md", "w").write(md)
print(f"runs/2026-11-03-run-a.md geschreven — {len(md.splitlines())} regels")
