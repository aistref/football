"""Bouwt runs/2026-11-02-run-a.md: de vaste kop plus de ingesloten logboekuitvoer.

De logboekblokken worden uit de .txt-bestanden van deze run gelezen in plaats van overgetypt
(§6c: overtypen is precies hoe twee rapporten van dezelfde run uiteen gaan lopen).
"""
import json

DEEL1 = open("tmp-run/ra_nov02_runreport_deel1.md").read()
DEEL2 = open("tmp-run/ra_nov02_runreport_deel2.md").read()


def blok(pad, titel, toelichting=""):
    txt = open(pad).read().rstrip()
    kop = f"### {titel}\n\n"
    if toelichting:
        kop += toelichting.rstrip() + "\n\n"
    return kop + "```\n" + txt + "\n```\n"


stand = "\n".join([
    blok("tmp-run/ra_nov02_ledgerstats.txt", "`ledger.py stats` — de gespeelde bets",
         "Het logboek staat op **510 picks**, waarvan 447 afgewikkeld en beslist. De drie van "
         "vandaag staan erin als `pending` en tellen hier nog niet mee."),
    blok("tmp-run/ra_nov02_shadowstats.txt", "`shadow.py stats` — wat de poorten hebben tegengehouden",
         "De regel die vandaag telt is **`doelpunten_onder`**: 35 afgewikkelde kandidaten, boven "
         "de ~30 die §6d eist. Zie de bevinding hierboven over poort 9."),
    blok("tmp-run/ra_nov02_recalibrate.txt", "`recalibrate.py show` — de stand van de herijking (§1g)",
         "**Let op het verschil met de fit waarmee vandaag is gepubliceerd.** De analyse liep met "
         "`a=0.994, b=-0.004` over 6606 gevallen t/m **2026-10-31**; `calibration.py settle` van "
         "deze run heeft daarna 234 waarnemingen afgewikkeld en de fit staat nu op `a=1.020, "
         "b=0.013` over 6840 gevallen t/m **2026-11-01**. Dat is de volgorde die §6b voorschrijft "
         "(settle hoort bij Stage 6, niet bij Stage 0) en het verschil is in deze band tienden "
         "van procentpunten, maar het staat hier zodat narekenen van de picks van vandaag met de "
         "juiste fit gebeurt. `fitted_through` = 2026-11-01, dus op de vorige rundag — de "
         "controle van §6b-5c staat groen."),
    blok("tmp-run/ra_nov02_calibrationstats.txt", "`calibration.py stats` — het kalibratielogboek (§6e)",
         "Vandaag zes waarnemingen in de longshotbak op +4,77 pp; dat is **één dag en zes "
         "gevallen** en zegt niets (§6d eist ~150). De reeks eronder is wat telt: 2240 "
         "waarnemingen in die bak. **De Understat-arm ontbreekt vandaag** voor de Premier League, "
         "Serie A, La Liga en Ligue 1 — zie Bronstatus."),
    blok("tmp-run/ra_nov02_ctxlogstats.txt", "`ctxlog.py stats` — het contextlogboek (§1c)",
         "1948 afgewikkelde wedstrijden. Het effect van ontbrekende spelers op de modelfout staat "
         "op `r = -0.042` (`t = -1.72`) en het teken wijst de verwachte kant op, maar met deze "
         "aantallen is alleen een effect vanaf ~13 pp per eenheid aantoonbaar. **Poort 7 blijft "
         "dus een rem en geen bijstelling**, precies zoals §1c sinds 5 september voorschrijft."),
    blok("tmp-run/ra_nov02_marginsstats.txt", "`margins.py stats` — het margelogboek (§6f)"),
    blok("tmp-run/ra_nov02_margins_since.txt",
         "`margins.py stats --since 2026-09-20` — alleen op `shrink = 1.00`"),
    blok("tmp-run/ra_nov02_marginsgoalbias.txt", "`margins.py goalbias` — het doelpuntenlogboek (§6g)",
         "**Lees de twee regels nooit als één getal.** De bovenste meet het model en staat op "
         "+0,052 doelpunt per duel (`z = +1,32`) over 1950 duels: dat klopt vrijwel. De regels "
         "eronder meten de **selectie**, en daar staat de gespeelde Under-kant op +0,660 doelpunt "
         "over 117 gevallen (`z = +4,31`) tegen -0,268 op de Over-kant. Dat is de meting waarop "
         "poort 9 rust, en ze is vandaag opnieuw bevestigd."),
])

OPEN = """## Openstaande punten

1. **Welke van de twee methodes zit er stelselmatig naast?** `tweede_methode` vangt vandaag 121
   van de 173 selecties (70%), de vierde dag op rij rond de zeventig procent. §5 noemt een poort
   die structureel alles wegvangt uitdrukkelijk een bevinding en geen ruis. Wat nog nergens is
   gemeten, is wélke van de twee methodes de fout maakt. Vandaag is het verschil opnieuw groot:
   bij Radomiak Radom +12,20 pp (xG) tegen +43,08 pp (splits), bij Atalanta – Parma +12,29 tegen
   +25,78, bij Gil Vicente +9,40 tegen +38,64. De splitsmethode is stelselmatig de optimistische
   en weegt met 0,20 mee (§1f, op uitslagen gemeten); het **gewicht** is dus gemeten, de
   **oorzaak** van het verschil niet. Dit hoort uit het kalibratielogboek te komen, dat de twee
   armen al per wedstrijd apart bijhoudt, en niet uit een redenering. Geen parameter aanraken op
   grond van één dag (§6d).
2. **Understat.** Onbereikbaar vanmorgen, met een 502 op de CONNECT van de netwerkgateway. Dat
   kost het kalibratieblok een arm voor vier competities en geen enkele bet (§2). Een volgende run
   ziet in `source-health.json` of dit één dag was of een nieuwe toestand. Valt **Fotmob** ook om,
   dan geldt de uitzondering van §3 punt 3 en moet dat vooraan in de notificatie.
3. **De hardgecodeerde `+02:00` elders in de repo.** `runwindow.kickoff_nl` rekent met `zoneinfo`
   en dus met echte winter-/zomertijd; de rest van de repo gebruikt nog een vaste offset. Sinds de
   laatste zondag van oktober staat Nederland op wintertijd, dus dat verschil is nu één uur in
   plaats van nul. Dit raakt de **weergave** en niet de selectie, en het staat hier sinds
   24 september open.
4. **De vraag van 15 oktober over de leesroute van het dagrapport** staat nog open en is een
   besluit van de gebruiker (§6c). Zolang er niets wordt gezegd, blijft de HTML-pagina de eerste
   route en de Markdown-versie op GitHub de tweede, en bevat de notificatie beide links.
"""

md = DEEL1 + "\n## Stand van het logboek\n\n" + stand + "\n" + DEEL2 + "\n" + OPEN
open("runs/2026-11-02-run-a.md", "w").write(md)
print(f"runs/2026-11-02-run-a.md geschreven — {len(md.splitlines())} regels")
