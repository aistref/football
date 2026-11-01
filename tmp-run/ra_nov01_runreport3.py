"""Run A, 1 nov 2026 — deel 3: afwikkeling, stand van het logboek, dagrapport, openstaande punten."""
import json

DAG = "2026-11-01"
ART = "https://claude.ai/artifact/PVvXeSfUmXxW4dy9THkpxy"
MD = f"https://github.com/aistref/football/blob/main/runs/{DAG}-run-a.dagrapport.md"
settle = json.load(open("tmp-run/ra_nov01_settle.json"))
st31a = json.load(open("data/run-state/2026-10-31-run-a.json"))
st31b = json.load(open("data/run-state/2026-10-31-run-b.json"))


def lees(p):
    return open(p).read().rstrip("\n")


lam = {}
for s in (st31a, st31b):
    for comp, b in s["competitions"].items():
        for m in b.get("matches") or []:
            if m.get("lambdas"):
                lam[m["match"]] = m["lambdas"]["xg"]

L = []
A = L.append

A("## Afwikkeling vorige picks")
A("")
A("Stage 0 heeft **tien picks** en **vierenzeventig schaduwrijen** van 31 oktober afgewikkeld — de "
  "grootste afwikkeling tot nu toe, en een gevolg van de volle zaterdag ervoor en niet van een "
  "stapel die was blijven liggen: er stond geen rij van vóór 31 oktober open. Alle 84 rijen zijn "
  "**competitiewedstrijden**, dus er is geen verlenging of strafschoppenreeks en de eindstand ís "
  "de stand na 90 minuten (§6d). Dat is nagetrokken en niet aangenomen: de negen MLS-duels van "
  "31 oktober zijn de laatste reguliere speelronde en geen play-offduel.")
A("")
A("**Eén rij blijft correct open:** Colorado Rapids – Chicago Fire FC trapte om 01:30 UTC vanochtend "
  "af en de bron meldt hem na 2,1 uur nog niet afgelopen. Die gaat naar de volgende run.")
A("")
A("| Pick | Uitslag | Resultaat | Verwacht (λ) | Werkelijk | Klopte de redenering? |")
A("|---|---|---|---|---|---|")
REFL = {
 "Bradford City – Huddersfield Town": "ja — Bradford kreeg er 1,0 toegeschreven en maakte 0",
 "Modena – Mantova": "nee — Mantova kreeg 0,8 en maakte 1; totaal wél goed",
 "Bayer Leverkusen – VfB Stuttgart": "half — goede kant, model 1,6 doelpunt te laag",
 "Middlesbrough – Charlton Athletic": "**ja, exact** — 3,0 verwacht, 3 gevallen",
 "AFC Bournemouth – Leeds United": "nee — model 1,2 doelpunt te hoog",
 "Moreirense – Estrela da Amadora": "**ja, exact** — 3,0 verwacht, 3 gevallen",
 "Kifisia FC – Olympiacos": "nee — model 2,8 doelpunt te laag, de grootste misser van de dag",
 "Columbus Crew – DC United": "**ja** — 2,8 verwacht, 3 gevallen",
 "Anderlecht – Westerlo": "nee — model 2,0 doelpunt te laag",
 "San Jose Earthquakes – Real Salt Lake": "ja — 3,4 verwacht, 3 gevallen, juiste winnaar",
}
tot_exp = tot_act = 0.0
for r in settle["shadow"]:
    pass
rij = [("Bradford City – Huddersfield Town", "0-3", "won", "BTTS nee @2,22"),
       ("Modena – Mantova", "1-1", "lost", "BTTS nee @2,2936"),
       ("Bayer Leverkusen – VfB Stuttgart", "2-4", "won", "Over 3.5 @1,87"),
       ("Middlesbrough – Charlton Athletic", "3-0", "won", "Under 3.5 @1,87"),
       ("AFC Bournemouth – Leeds United", "2-0", "lost", "Over 2.5 @1,94"),
       ("Moreirense – Estrela da Amadora", "2-1", "won", "Over 2.5 @2,1368"),
       ("Kifisia FC – Olympiacos", "2-3", "lost", "Under 2.5 @1,93"),
       ("Columbus Crew – DC United", "3-0", "won", "Under 3.5 @1,87"),
       ("Anderlecht – Westerlo", "4-1", "lost", "Under 3.5 @1,7742"),
       ("San Jose Earthquakes – Real Salt Lake", "2-1", "won", "1X2 thuis @2,3916")]
for naam, score, resu, markt in rij:
    lv = lam.get(naam)
    exp = sum(lv) if lv else None
    act = sum(int(x) for x in score.split("-"))
    if exp:
        tot_exp += exp
        tot_act += act
    A(f"| {naam} · {markt} | {score} | **{'gewonnen' if resu=='won' else 'verloren'}** | "
      f"{exp:.2f} | {act} | {REFL[naam]} |")
A(f"| **totaal over 10 duels** | | **6 gewonnen, 4 verloren** | **{tot_exp:.2f}** | "
  f"**{int(tot_act)}** | **+{(tot_act-tot_exp)/10:.2f} doelpunt per duel** |")
A("")
A("**De reflectie van §3 Stage 0, vier vragen:**")
A("")
A("1. **Klopte de redenering, of alleen de uitkomst?** Bij vier van de zes winnaars klopte ze tot "
  "op de halve goal: Middlesbrough – Charlton 3–0 bij 3,03 verwacht, Moreirense – Estrela 2–1 bij "
  "2,99, Columbus – DC United 3–0 bij 2,84 en San Jose – Real Salt Lake 2–1 bij 3,38. Dat zijn "
  "winsten op de juiste redenering. Bij Leverkusen – Stuttgart (2–4 bij 4,36 verwacht) was de kant "
  "goed en de hoogte niet. Omgekeerd was Modena – Mantova een verlies waarbij het totaal klopte "
  "(2 tegen 2,66) en alleen de nul niet kwam — verloren, maar niet verkeerd ingeschat.")
A("2. **Deden de poorten hun werk, in dít geval?** Op zaterdag niet. De vierenzeventig afgewezen "
  "kandidaten stonden samen op **+12,97u over 70 beslechte rijen = +18,5%**, met "
  "`tweede_methode` op +61,6% (13 van 18 goed) en `edge` op +35,4% (14 van 24). Alleen "
  "`robuustheid` (0 van 2), `doelpunten_onder` (1 van 4) en `underdog` (8 van 19) deden wat ze "
  "moeten doen. Dat is één dag en achttien gevallen; over de hele looptijd bespaart "
  "`tweede_methode` nog steeds geld (−3,0% over 237).")
A("3. **Zat er een patroon in?** Ja, en het is het bekende. Over de tien duels vielen er "
  f"**{int(tot_act)} doelpunten tegen {tot_exp:.1f} verwachte** — een halve goal per wedstrijd te "
  "veel. Drie van de vier verliezers waren doelpuntenmarkten die aan de verkeerde kant uitliepen, "
  "en **twee daarvan waren Unders die overschoten** (Kifisia 5 tegen 2,2 verwacht; Anderlecht 5 "
  "tegen 3,0). Dat is precies de richting die §6g meet.")
A("4. **En wat betekent dit niet?** Eén dag is geen reeks. De Under-reeks waar dit in past staat "
  "nu op **+0,668 doelpunt per duel over 115 gevallen (z = +4,32)** — dát is de meting, en de twee "
  "van gisteren zijn er twee van de 115. Er is op grond van deze dag geen drempel, gewicht of "
  "poort verzet, en poort 9 staat onveranderd op `UNDER_EXTRA` = 2,0 pp.")
A("")
A("## Stand van het logboek")
A("")
A("`recalibrate.load_fit().fitted_through` = **2026-10-31**, de vorige rundag — zoals §6b-5c eist. "
  "De 285 waarnemingen die nog open stonden zijn vóór het lezen van de fit afgewikkeld "
  "(`calibration.py settle`), en `ctxlog.py settle` wikkelde 109 wedstrijden af. Fit: `a=0,9943`, "
  "`b=-0,0037` op **6606** afgerekende gevallen; het ruwe model zei gemiddeld 33,3% en het "
  "gebeurde 33,3%. De correctie is daarmee vrijwel de identiteit — ze verlaagt een kans van 50% "
  "met 0,1 pp en een van 80% met 0,2 pp.")
A("")
A("Uitvoer van `python3 scripts/recalibrate.py show`:")
A("")
A("```")
A(lees("tmp-run/ra_nov01_recalibrate.txt"))
A("```")
A("")
A("Uitvoer van `python3 scripts/ledger.py stats`:")
A("")
A("```")
A(lees("tmp-run/ra_nov01_ledgerstats.txt"))
A("```")
A("")
A("Uitvoer van `python3 scripts/shadow.py stats`:")
A("")
A("```")
A(lees("tmp-run/ra_nov01_shadowstats.txt"))
A("```")
A("")
A("Uitvoer van `python3 scripts/calibration.py stats` (§6e):")
A("")
A("```")
A(lees("tmp-run/ra_nov01_calibrationstats.txt"))
A("```")
A("")
A("Uitvoer van `python3 scripts/ctxlog.py stats` (§1c):")
A("")
A("```")
A(lees("tmp-run/ra_nov01_ctxlogstats.txt"))
A("```")
A("")
A("Uitvoer van `python3 scripts/margins.py stats` (§6f):")
A("")
A("```")
A(lees("tmp-run/ra_nov01_marginsstats.txt"))
A("```")
A("")
A("Uitvoer van `python3 scripts/margins.py stats --since 2026-09-20` (§6f):")
A("")
A("```")
A(lees("tmp-run/ra_nov01_margins_since.txt"))
A("```")
A("")
A("Uitvoer van `python3 scripts/margins.py goalbias` (§6g):")
A("")
A("```")
A(lees("tmp-run/ra_nov01_marginsgoalbias.txt"))
A("```")
A("")
A("**Drie dingen die uit deze blokken samen volgen en die niet in één getal passen.** Het logboek "
  "staat op **−8,0% over 439 bets** en de Brier-score van het model (0,2598) is nog steeds hoger "
  "dan die van de markt (0,2398): de analyse voegt over de hele reeks nog geen kansinformatie toe "
  "boven de markt. De `edge`-reeks in het schaduwlogboek staat op **+1,9% over 564 kandidaten** — "
  "de groep die net onder de drempel viel doet het dus iets béter dan de gespeelde bets, wat "
  "precies de meting is waarop §5b rust. En de `lijstlengte`-reeks staat op **+24,2% over 20 "
  "gevallen**; dat is boven de ~30 die §6d eist nog niet leesbaar, maar het is de reeks om in de "
  "gaten te houden, want ze zegt wat de lijstlengte kost op dagen dat er méér kwalificeert dan er "
  "past. Vandaag kostte ze niets: er paste alles.")
A("")
A("## Dagrapport (§6c)")
A("")
A(f"- HTML-pagina, als Artifact gepubliceerd: **{ART}**")
A(f"- Tweede route, door GitHub gerenderd: **{MD}**")
A("")
A("De rendercontrole van §6c (15 okt) is **preventief** gedraaid met Chromium uit "
  "`/opt/pw-browsers`, in licht én donker:")
A("")
A("```")
A(lees("tmp-run/ra_nov01_rendercheck.txt"))
A("```")
A("")
A("21.618 px hoog, 54.299 tekens zichtbare tekst, 56 blokken, 6 tabellen, 5 bets en **nul console- "
  "of pagefouten**, in beide thema's met de juiste achtergrond- en tekstkleur. Blijkt de Artifact "
  "voor de gebruiker onbereikbaar, dan is opnieuw publiceren dus zinloos en is de Markdown-route "
  "het antwoord (§6c, 14 en 15 okt).")
A("")
A("Vijf voorbeschouwingen van 510 tot 578 woorden, één per gepubliceerde bet, binnen de norm van "
  "300–600 van §6c. Bij Kasımpaşa – Beşiktaş en Getafe – Sevilla opent de tekst met wat de bet "
  "tegenspreekt, zoals §6c eist zodra de frequenties dat doen.")
A("")
A("## Openstaande punten")
A("")
A("1. **Welke van de twee rekenmethodes zit er stelselmatig naast?** `tweede_methode` vangt nu "
  "drie dagen op rij meer dan 70% van alle doorgerekende selecties weg (74% vandaag, 356 van 479). "
  "§5 noemt dat expliciet een bevinding en geen ruis. Wat ontbreekt is de meting wélke arm fout "
  "is: vandaag staat bij Marseille – Toulouse het xG-model op +11,52 pp en de splitsmethode op "
  "−3,68 pp, bij Elche – Valencia precies omgekeerd (+0,26 tegen +17,03), en bij de gepubliceerde "
  "Getafe – Sevilla op +9,38 tegen +0,03. Dat is na te rekenen over de duizenden afgerekende "
  "waarnemingen in `calibration.jsonl`, waar beide methodes apart in staan — §6e meet nu alleen "
  "hun afstand tot de markt per kansband en niet hun onderlinge tegenspraak tegen uitkomsten. "
  "**Van de gebruiker is hier niets nodig; dit is werk voor een volgende run.**")
A("2. **Moeten de twee picks van 3 en 4 oktober uit het logboek?** Onveranderd sinds 31 oktober en "
  "nog niet beantwoord. Exeter City – Rotherham United en Girona – Mallorca zijn onder de "
  "`match_tier`-fout gepubliceerd en hadden onder de regels niet mogen bestaan; beide zijn "
  "gewonnen. Twee van 500 afgewikkelde picks verschuiven geen enkel cijfer in §6d. **Dit is een "
  "besluit van de gebruiker over zijn eigen administratie.**")
A("3. **Markdown of Artifact als eerste route voor het dagrapport?** Onveranderd sinds 15 oktober. "
  "De Artifact heeft het sinds die datum goed gedaan en de rendercontrole hierboven staat schoon, "
  "dus er is geen aanleiding om te wisselen. **Dit is een besluit van de gebruiker over hoe hij "
  "zijn rapport wil lezen; een run verandert die volgorde niet op eigen initiatief, en de vraag "
  "wordt niet elke dag opnieuw gesteld.**")
A("4. **De te soepele naamregel in `settling` is nooit over de hele looptijd geaudit.** "
  "Onveranderd: niet nagegaan of hij in het verleden al eens een verkeerde uitslag heeft "
  "weggeschreven. Dat is een audit over 68 rundagen en vandaag niet gedaan. **Werk voor een "
  "volgende run.**")
A("")
A("---")
A("")
A("> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de "
  "verwachtingswaarde negatief.")

open("tmp-run/ra_nov01_runreport_deel3.md", "w").write("\n".join(L) + "\n")
print("deel 3:", len(L), "regels")
