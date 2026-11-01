"""Run A, 1 nov 2026 — deel 2 van het runrapport: bevinding t/m openstaande punten."""
import json
from collections import Counter

DAG = "2026-11-01"
st = json.load(open(f"data/run-state/{DAG}-run-a.json"))
res = json.load(open("tmp-run/ra_nov01_results.json"))
picks = json.load(open("tmp-run/ra_nov01_picks_a.json"))
top = json.load(open("tmp-run/ra_nov01_top_a.json"))
pin = {r["match"]: r for r in json.load(open("tmp-run/ra_nov01_pinnacle.json"))}
pou = {r["match"]: r for r in json.load(open("tmp-run/ra_nov01_pinnacle_ou.json"))}
settle = json.load(open("tmp-run/ra_nov01_settle.json"))
ART = "https://claude.ai/artifact/PVvXeSfUmXxW4dy9THkpxy"
MD = f"https://github.com/aistref/football/blob/main/runs/{DAG}-run-a.dagrapport.md"


def lees(p):
    return open(p).read().rstrip("\n")


allc = [c for m in res["matches"] for c in m.get("all_candidates", [])]
idx = {m["match"]: m for m in res["matches"]}
L = []
A = L.append

A("## Bevinding — de BTTS-ronde van §1a stap 2 bepaalde wélke twee bets er zijn")
A("")
A("**Niet alle prijzen kosten hetzelfde, en dat heeft vandaag de gepubliceerde lijst veranderd.** "
  "§1a stap 2 schrijft voor dat BTTS pas in een tweede ronde wordt gekocht, voor duels die al een "
  "kandidaat-edge tonen, omdat die markt per **duel** afrekent (1 credit) waar spreads, totals en "
  "h2h per **competitie** afrekenen. Vandaag ging die tweede ronde langs 23 van de 37 duels, voor "
  "23 credits.")
A("")
A("Wat er zonder die ronde was gepubliceerd, en wat er mét die ronde is gepubliceerd:")
A("")
A("| Wedstrijd | vóór de BTTS-ronde | score | ná de BTTS-ronde | score |")
A("|---|---|---|---|---|")
A("| Juventus – Napoli | Over/Under Under 2.5 @1,91 (+11,69 pp) | 7,485 | "
  "**BTTS nee @2,1564 (+12,75 pp)** | **7,538** |")
A("| Kasımpaşa – Beşiktaş | Over/Under Under 2.75 @2,01 (+10,72 pp) | 6,480 | "
  "**BTTS nee @2,4896 (+13,22 pp)** | **7,058** |")
A("")
A("Dat zijn de **enige twee** wedstrijden van vandaag waarop een selectie alle negen poorten "
  "haalt, dus de tweede ronde raakt niet een voetnoot maar de hele kop van de lijst. De keuze "
  "binnen de wedstrijd is die van §1a: `selection_score` beslist, en bij beide duels scoort de "
  "BTTS-kant hoger dan de Under die er zonder die aankoop had gestaan. In de kern is het dezelfde "
  "mening — weinig doelpunten — in een beter betaalde markt.")
A("")
A("**Waarom dit het opschrijven waard is.** Er zit een stille verleiding in die tweede ronde. Ze "
  "kost credits per duel, ze komt achteraan in de pijplijn, en als een run haar overslaat klaagt "
  "er niets: het runrapport ziet er daarna volkomen normaal uit, met twee Unders erin en een "
  "kloppende marktbalanstabel. Dat is dezelfde stille faalstand als `calibration.py settle` "
  "(§6b-5c, elf dagen onopgemerkt) en de verhuisde BetExplorer-slug van 16 oktober. Vandaag is er "
  "een gemeten geval dat zegt dat die stap werkelijk bijt.")
A("")
A("**Wat het níet is.** Geen wijziging, geen voorstel en geen reden om BTTS voor élk duel te "
  "kopen: dat zou 37 credits per run kosten in plaats van 23, en §1a koopt met opzet alleen daar "
  "waar al iets te vinden lijkt. De vereniging van de ruwe en de herijkte lezing van "
  "\"kandidaat-edge\" (sinds 31 okt) heeft vandaag gewoon gewerkt zoals ze bedoeld is.")
A("")
A("## Topselectie")
A("")
A("Rangschikking op `selection_score` = `edge_pp × my_prob × (FULL 1.0 | LIGHT 0.5)`, dezelfde "
  "formule waarmee binnen een wedstrijd de markt is gekozen (§5).")
A("")
A("| # | Wedstrijd | Markt + selectie | Koers | Kans | Edge | Score | Risico | Status |")
A("|---|---|---|---|---|---|---|---|---|")
for i, p in enumerate(picks, 1):
    r = next(x for x in top["herijkt"] if x["match"] == p["home"] + " – " + p["away"])
    risk = {"High": "High", "Medium": "Medium", "Low": "Low"}[p["confidence"]]
    A(f"| {i} | {p['home']} – {p['away']} | {p['market']} — {p['selection']} | "
      f"{p['odds']:.4f} | {p['my_prob']*100:.1f}% | {p['edge_pp']:+.2f} pp | {r['score']:.3f} | "
      f"{risk} | {r['status']} |")
A("")
A("**Twee van de vijf halen hun lat, drie staan erin op rangorde.** §5b: de drempel snijdt aan het "
  "eind van de dag en niet per selectie vooraf, en staan er minder gekwalificeerde selecties dan "
  "er plekken zijn — twee tegen `MAX_SHORTLIST` = 5 op zondag — dan bepaalt de rangorde de lijst "
  "en gaat de drempel mee als **label** per regel. De `lijstlengte`-reeks krijgt vandaag dus geen "
  "enkele rij: er valt niets buiten de lijst.")
A("")
A("**Bij alle drie de regels onder de lat zijn de zeven andere poorten wél opengegaan** — "
  "koersband, anti-circulariteit, datatier, tweede methode, robuustheid, context en underdog. Er "
  "is geen poort die ze afwees; alleen de drempel. Twee van die drie staan robuust krap: Getafe – "
  "Sevilla op **+1,06 pp** en Liverpool – Arsenal op **+0,73 pp** in de zwakste hoek van het "
  "`(shrink, rho)`-grid. Dat is boven nul, dus poort 6 gaat open, maar het is het randje.")
A("")
A("**Vier van de vijf koersen zijn een beurskoers bij Matchbook** (§5, Odds — beide getallen "
  "verplicht): Juventus – Napoli 2,18 bruto / 2,1564 na 2% commissie; Kasımpaşa – Beşiktaş 2,52 / "
  "2,4896; Getafe – Sevilla 1,80 / 1,784; Liverpool – Arsenal 1,83 / 1,8134. De vijfde (Lyon – "
  "Angers, 1,60) staat bij Tipico. `edge_pp` en `selection_score` rekenen met de koers ná "
  "commissie.")
A("")
A("**`bet_beide`:** de twee regels boven de lat halen hem op de herijkte **en** op de ruwe schaal; "
  "de drie op rangorde halen hem op geen van beide. Geen enkele selectie van deze run sneuvelde "
  "**alleen** op de herijking — de `herijking`-reeks van §5a krijgt vandaag dus ook geen rij. Met "
  "een fit die vrijwel de identiteit is (`a=0,994`, `b=-0,004`) is dat te verwachten, maar het is "
  "per selectie met de vlag gecontroleerd en niet beredeneerd (§5a waarschuwt daar uitdrukkelijk "
  "voor).")
A("")
A("### Marktbalans (verplicht, §1a)")
A("")
A("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
A("|---|---|---|---|")
mk = Counter(c["market"] for c in allc)
bet_mk = Counter(p["market"] for p in picks)
MKT = [("1X2", "11 van 11 (bulk h2h + gratis BetExplorer-gemiddelde)", "1X2"),
       ("Double Chance", "11 van 11 (afgeleid uit h2h + spreads)", "Double Chance"),
       ("Draw No Bet", "11 van 11 (afgeleid uit h2h + spreads)", "Draw No Bet"),
       ("Asian Handicap", "11 van 11 (bulk spreads)", "Asian Handicap"),
       ("Over/Under", "11 van 11 (bulk totals)", "Over/Under"),
       ("BTTS", "23 duels apart gekocht (§1a stap 2), 1 credit per duel", "BTTS")]
for naam, waar, key in MKT:
    A(f"| {naam} | {waar} | {mk[key]} | {bet_mk[key]} |")
A(f"| **totaal** | **11 van 11 spelende competities** | **{len(allc)}** | **{len(picks)}** |")
A("")
A("**De controle is gehaald op de inkoop en zo ruim als ze kan:** alle elf spelende competities "
  "hebben een sportkey en kregen de volledige bulk, dus elke gekochte competitie heeft zowel een "
  "uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U). **Geen enkel duel draait voor "
  "de bet zelf op het gratis BetExplorer-marktgemiddelde** — dat gemiddelde is alleen gebruikt om "
  "te meten (§6e) en voor poort 8.")
A("")
A("**Wat eruit kwam: drie markten in de lijst.** Drie BTTS, één Over/Under en één Draw No Bet. Dat "
  "is het noemen waard omdat de twee voorgaande rundagen voor honderd procent uit Over/Under "
  "bestonden — 30 okt vier van vier, 31 okt vijf van vijf — en de gebruiker daar op 19 september "
  "terecht over viel. Er is niets veranderd in de regels of de weging; het laat alleen zien dat "
  "die eentonigheid een uitkomst was en geen structurele vorm. Het aantal doorgerekende selecties "
  "per duel loopt van 7 tot 21, omdat de spreads-respons per competitie verschillende "
  "handicaplijnen levert; dat staat per duel in `markets_checked` met de reden erbij en niet als "
  "gat (§6b-5b).")
A("")
A("`python3 scripts/progress.py verify --run a --date 2026-11-01` staat groen: alle 36 "
  "geanalyseerde wedstrijden hebben alle zes markten gehad; 1 overgeslagen zonder kansbron (tier "
  "NONE), 0 afgekapt.")
A("")
A(f"### Poortverdeling over {len(allc)} selecties")
A("")
A("| Eerste dichte poort | Selecties | Aandeel |")
A("|---|---|---|")
fg = Counter(c["failed_gate"] for c in allc)
for k, n in fg.most_common():
    naam = "**geen — alles open**" if k is None else f"`{k}`"
    A(f"| {naam} | {n} | {100*n/len(allc):.1f}% |")
A("")
A("**`tweede_methode` vangt 356 van de 479 selecties — 74%, en dat is de derde dag op rij boven "
  "de 70%** (71% op 31 oktober). §5 (\"Net niet\") zegt dat een poort die structureel alles "
  "wegvangt een **bevinding** is en geen ruis, en dit is die bevinding — maar hij hoort met zijn "
  "eigen cijfer gelezen te worden. Het schaduwlogboek meet die poort nu op **246 kandidaten, 237 "
  "afgewikkeld: 45,6% trefkans en −3,0% rendement**. Dat is minder slecht dan het logboek van de "
  "gespeelde bets (−8,0%) en slechter dan nul: de poort bespaart geld, maar niet veel, en hij is "
  "met afstand de grofste zeef in de routine.")
A("")
A("De vijf selecties met alles open liggen op **twee** wedstrijden (Juventus – Napoli: BTTS nee én "
  "Under 2.5; Kasımpaşa – Beşiktaş: BTTS nee, Under 2.5 én Under 2.75). De 0-of-1-bet-regel laat "
  "er per duel één door, dus er zijn twee bets boven de lat en geen vijf. De drie die het binnen "
  "hun wedstrijd niet werden staan in `data/run-state/` onder `binnen_wedstrijd_niet_gekozen` — ze "
  "zijn géén afgewezen kandidaat (§6d/§1a: dezelfde mening in een andere markt is één bevinding).")
A("")
A("**Wat dit niet is: een reden om poort 5 vandaag te verzetten.** §6d eist een richting over "
  "weken en verbiedt uitdrukkelijk een parameterwijziging op grond van één dag. De vraag "
  "eronder — wélke van de twee methodes er stelselmatig naast zit — is een meting die nog niet is "
  "gedaan, en ze staat als openstaand punt onderaan.")
A("")
A("### Poort 9 — zes selecties tegengehouden, twee bovenaan de ruwe lijst")
A("")
A("Poort 9 (§1h: een Under op `FULL`-data moet 10,0 pp halen in plaats van 8,0) hield vandaag zes "
  "selecties als eerste dichte poort tegen, en twee daarvan voeren de **ruwe** dagranglijst mee "
  "aan:")
A("")
A("| Wedstrijd | Selectie | Koers | edge | waarom tegengehouden |")
A("|---|---|---|---|---|")
A("| Excelsior – FC Twente | Under 3.5 | 1,72 | +9,22 pp | tussen 8,0 en 10,0 — poort 9 bijt |")
A("| Eintracht Frankfurt – Hamburger SV | Under 3.5 | 1,84 | +9,35 pp | idem |")
A("")
A("De reeks staat nu op **29 afgewikkelde kandidaten met −22,0% rendement** (41,4% trefkans): de "
  "poort doet zijn werk, en hij nadert de ~30 gevallen die §6d eist voordat die reeks gelezen mag "
  "worden.")
A("")
A("**De meting eronder is vandaag opnieuw bevestigd.** `margins.py goalbias` over 1870 "
  "doorgerekende duels: het model klopt op het **totaal** (+0,041 doelpunt per duel, z = +1,01), "
  "maar de **gespeelde Under-kant** staat op +0,668 doelpunt over 115 gevallen (z = +4,32) tegen "
  "−0,245 op de Over-kant (65 gevallen, z = −1,08). Die twee regels zijn twee populaties — het "
  "model en de selectie — en mogen nooit worden opgeteld.")
A("")
A("De gepubliceerde Under van vandaag (Lyon – Angers, +6,74 pp) valt **onder** die band en poort 9 "
  "laat hem met opzet door: daar hoort `edge` de bindende poort te zijn, en dat is hij ook — de "
  "regel staat op rangorde in de lijst en niet op een gehaalde lat. **Het gat tussen §5b en §1h "
  "dat op 28, 30 en 31 oktober is gemeld, bijt vandaag dus niet:** er is geen wedstrijd waarin "
  "poort 9 de hoogste Under tegenhield en §5b een lagere Under van hetzelfde duel doorliet.")
A("")
A("### Poort 8 — veertien selecties, en de duurste blokkade van de dag")
A("")
A("Poort 8 (§1e, ondergrens `UNDERDOG_FLOOR` = 0,35) hield **veertien** selecties tegen. De "
  "zwaarste: **Lazio – Cagliari, Cagliari +1.5 @1,69 met +9,83 pp** — nummer 3 op de ruwe "
  "dagranglijst, en met `selection_score` 6,784 hoger dan drie van de vijf gepubliceerde regels. "
  "Dat is wat deze poort vandaag kost, en het hoort hier te staan.")
A("")
A("De `underdog`-reeks staat op **271 afgewikkelde kandidaten met −4,8% rendement** (49,4% "
  "trefkans). Dat is de reeks die op 5 oktober de meetlat van ≥30 gevallen met positief rendement "
  "haalde en waarop de gebruiker toen besloot: *\"Rem blijft zoals die nu is.\"* Sindsdien is ze "
  "van +16,9% naar −4,8% gedraaid, dus de aanleiding om de vraag opnieuw te stellen is er niet — "
  "ze is juist verdwenen. De kalibratiefout die de poort afdekt is er ook nog: **+1,57 pp te veel "
  "kans op longshots en −3,22 pp te weinig op favorieten** over 6951 uitkomsten.")
A("")
A("### Poort 7 — vijftien selecties over twee wedstrijden")
A("")
A("De contextpoort hield vijftien selecties tegen, allemaal op twee duels:")
A("")
A("- **Arouca – Nacional** — Nacional mist 18% van de selectiewaarde tegen 6% bij Arouca (Léo "
  "Santos, Ulisses Rocha en Filipe Soares, alle drie *day to day*). Dit was de enige wedstrijd "
  "waarvan de **beste** selectie op poort 7 sneuvelde (1X2 Nacional @5,018, +4,73 pp).")
A("- Bij **Getafe – Sevilla** en **Lyon – Angers** staat de poort dicht voor de kant van de "
  "thuisploeg (Getafe mist 45% van de selectiewaarde, Lyon 37%) maar **open** voor de "
  "gepubliceerde selectie, want die heeft geen kant: bij Over/Under en BTTS is `side = None` en "
  "dan staat poort 7 per ontwerp open (§1c). Dat is geen omzeiling — er is geen ploeg om te "
  "benadelen — maar het is wel het soort geval dat je moet kunnen navertellen, en daarom staat het "
  "hier.")
A("")
A("Geen enkele wedstrijd is vandaag verplaatst: `context.check_venue` gaf voor alle 37 duels "
  "`relocated = False` en het stadion van de thuisploeg.")
A("")
A("### Marktvorm — de telling is bij drie van de vijf regels niet eenduidig (§6b-5h)")
A("")
A("`marketform.match_block` is voor 36 van de 37 duels geteld (het 37e staat op tier NONE). Bij de "
  "vijf gepubliceerde regels:")
A("")
A("| Regel | Wat de telling zegt |")
A("|---|---|")
A("| Juventus – Napoli, BTTS nee | **steunt.** Juventus 3 van 9 met BTTS dit seizoen (33%), thuis "
  "1 van 4 (25%); vorig seizoen 45%. Napoli 5 van 9 (56%) en uit 3 van 5 (60%) — dat is de kant "
  "die tegenspreekt. |")
A("| Kasımpaşa – Beşiktaş, BTTS nee | **spreekt tegen.** Kasımpaşa 6 van 9 (67%) en thuis 3 van 4 "
  "(75%); Beşiktaş 4 van 9 (44%). En de h2h: **5 van 5** met doelpunten aan beide kanten. Hoogste "
  "edge van de dag, zwakste frequentiesteun. |")
A("| Lyon – Angers, Under 3.5 | **steunt breed, spreekt dun tegen.** Lyon 25% boven 3,5 dit "
  "seizoen en 32% vorig jaar, Angers 38% en 18%; maar Lyon **thuis** 2 van 4 (gem. 3,25) en Angers "
  "**uit** 2 van 3 (3,33). Reeksen van drie en vier duels. |")
A("| Getafe – Sevilla, BTTS nee | **gespleten.** Getafe thuis **0 van 5** boven 2,5 doelpunt (gem. "
  "1,60) maar wél 3 van 5 met BTTS; Sevilla uit 4 van 5 met BTTS (80%, gem. 3,60). De bet leunt "
  "volledig op de thuisploeg. |")
A("| Liverpool – Arsenal, DNB Arsenal | **neutraal.** Een doelpuntentelling zegt over een DNB "
  "niets; wat ze toont is dat beide ploegen dit seizoen lager scoren dan vorig jaar (Liverpool "
  "2,38 tegen 3,05; Arsenal 2,25 tegen 2,58) en dat Arsenal in vier uitduels geen enkele keer BTTS "
  "haalde. |")
A("")
A("§6c eist dat zo'n tegenspraak **vooraan** in de voorbeschouwing staat en niet in een voetnoot; "
  "bij Kasımpaşa – Beşiktaş en Getafe – Sevilla is dat in het dagrapport de openingsalinea.")
A("")
A("### Net niet (§5)")
A("")
A("| Wedstrijd | Tier | Beste selectie | Koers | xG-model | 2e methode | zwakste stand | valt af op |")
A("|---|---|---|---|---|---|---|---|")
for comp, b in st["competitions"].items():
    for m in b.get("matches") or []:
        nm = m.get("near_miss")
        if not nm:
            continue
        def g(k):
            v = nm.get(k)
            return f"{v:+.2f}" if isinstance(v, (int, float)) else "—"
        A(f"| {m['match']} | {m['tier']} | {nm.get('market')} | {nm.get('odds'):.4f} | "
          f"{g('edge_xg')} | {g('edge_split')} | {g('edge_robust_min')} | `{nm.get('failed_gate')}` |")
A("")
A("Zestien kandidaten met een echte edge, en de spreiding over de poorten is breed: zeven op "
  "`edge`, vijf op `tweede_methode`, twee op `robuustheid`, één op `context`. Twee rijen zijn het "
  "aankijken waard. **Marseille – Toulouse**: het xG-model geeft Toulouse +11,52 pp en de "
  "splitsmethode −3,68 pp — de grootste tegenspraak van de dag. En **Elche – Valencia**: "
  "splitsmethode +17,03 pp, xG-model +0,26 pp, zwakste stand van het grid −0,35 pp. Dat zijn "
  "precies de twee gevallen die het openstaande punt over poort 5 concreet maken.")
A("")
A("## Wat anderen voorspellen (Stage 5 stap 2)")
A("")
A("Geschreven voorspellingen blijven onbereikbaar (§3 Stage 5, meting van 20 sep: Forebet 403, "
  "Pinnacle-artikelen 404, Matchbook 530, voetbalwedden.net zonder de duels van de dag). Wat er "
  "wél is, is **de prijs van Pinnacle apart** — de scherpste bookmaker van de markt, en zijn "
  "de-vigde kans is het beste publieke expertoordeel dat beschikbaar is. **Dit getal gaat nooit in "
  "`my_prob` of `prob_sources` (§2).**")
A("")
A("Over 30 duels met een Pinnacle-1X2: gemiddelde absolute afstand tot het Pinnacle-oordeel **3,69 "
  "pp**, gemiddelde Pinnacle-marge **3,48%** (de rest van de markt zit op 6 tot 10%). Op de "
  "Under-kant, over 30 (duel, lijn)-paren: gemiddeld **+3,07 pp** boven Pinnacle, en 21 van de 30 "
  "boven hem. Dat is dezelfde richting als §6g meet.")
A("")
A("Bij de gepubliceerde regels:")
A("")
A("| Regel | Pinnacle | mijn kans | verschil |")
A("|---|---|---|---|")
A("| Juventus – Napoli (op P(Under 2.5) als dichtstbijzijnde meetbare kant) | 52,2% | 67,0% | "
  "**+14,8 pp** |")
A("| Juventus – Napoli (1X2, Juventus wint) | 40,8% | 49,7% | +8,9 pp |")
A("| Getafe – Sevilla (P(Under 2.0), push meegerekend) | 51,8% | 61,7% | +9,9 pp |")
A("| Lyon – Angers (P(Under 3.0), push meegerekend) | 49,1% | 57,5% | +8,4 pp |")
A("| Liverpool – Arsenal (DNB Arsenal, uit de de-vigde 1X2) | 54,6% | 61,4% | +6,8 pp |")
A("| Kasımpaşa – Beşiktaş | **geen Pinnacle-prijs** | 53,4% | niet te meten |")
A("")
A("**Pinnacle is het met alle vier de meetbare regels oneens, en op dezelfde kant.** Dat is geen "
  "bevestiging en het is ook geen veto; het is het publieke expertoordeel dat naast de eigen kans "
  "hoort te staan. Bij Juventus – Napoli is het verschil het grootst van de dag (+14,8 pp op de "
  "doelpuntenkant), en dat is precies de kant waar §6g zegt dat de routine te hoog staat — tel er "
  "in gedachten ongeveer twee procentpunt af. Dat de regel met de **hoogste** edge van vandaag "
  "(Kasımpaşa – Beşiktaş) helemaal **geen** Pinnacle-prijs heeft, is een eigen waarneming: daar is "
  "geen onafhankelijke toets op.")
A("")
A("## Niveau per competitie (Stage 5)")
A("")
A("| Competitie | Route | Speeldagen lopend | thuis / uit | basis |")
A("|---|---|---|---|---|")
for comp, lv in (st.get("niveau") or {}).items():
    A(f"| {comp} | `{lv.get('source')}` | {lv.get('played')} van {lv.get('length')} | "
      f"{lv.get('home_goals_per_match'):.3f} / {lv.get('away_goals_per_match'):.3f} | "
      f"{lv.get('avg_xg_per_match'):.3f} |")
vs = res.get("vroeg_seizoen") or {}
A("")
A(f"De gepoolde vroeg-seizoenscorrectie is gemeten over **{vs.get('speeldagen')} speeldagen** in "
  f"{len(vs.get('competities') or [])} competities en staat op factor **{vs.get('factor'):.4f}** "
  f"(gepoold {vs.get('gepoold'):.4f}).")
A("")
A("**Eén competitie is bij die pool overgeslagen en dat staat er met zoveel woorden bij** (§3 "
  "Stage 5 — een stil weggelaten waarneming is hetzelfde probleem als een stille truncatie in "
  "Stage 4):")
A("")
for k, v in (vs.get("overgeslagen") or {}).items():
    A(f"- **{k}** — {v}")
A("")
A("De Danish Superliga is daarmee de enige competitie van vandaag die de route `lopend` neemt: 13 "
  "van 22 speeldagen is over de helft, dus het niveau komt uit het lopende seizoen zelf en "
  "ongeschaald (`SEASON_MATURE_SHARE`).")
A("")
A("## Promovendi en degradanten")
A("")
A("Negen van de 37 duels hebben een omgerekende ploeg (§4, \"Promovendi: eerst omrekenen, dan pas "
  "`NONE`\"). Acht daarvan komen op `data_tier = LIGHT` uit en één op `NONE`:")
A("")
A("| Wedstrijd | Omgerekende ploeg | Uit | Tier |")
A("|---|---|---|---|")
PROMO = [("Como – Venezia", "Venezia", "Serie B (ITA)", "LIGHT"),
         ("Frosinone – Torino", "Frosinone", "Serie B (ITA)", "LIGHT"),
         ("Racing Santander – Real Madrid", "Racing Santander", "LaLiga2 (ESP)", "LIGHT"),
         ("PEC Zwolle – ADO Den Haag", "ADO Den Haag", "Eerste Divisie (NED)", "LIGHT"),
         ("Académico Viseu – Rio Ave", "Académico Viseu", "Liga Portugal 2 (POR)", "LIGHT"),
         ("Marítimo – Santa Clara", "Marítimo", "Liga Portugal 2 (POR)", "LIGHT"),
         ("Lommel – Gent", "Lommel", "First Division B (BEL)", "LIGHT"),
         ("Amed Sportif – Eyüpspor", "Amed Sportif", "1. Lig (TUR)", "LIGHT"),
         ("Viborg – AC Horsens", "AC Horsens", "1. Division (DEN)", "**NONE**")]
for r in PROMO:
    A(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
A("")
A("**Viborg – AC Horsens staat op `NONE` en is niet doorgerekend.** De omrekening van AC Horsens "
  "valt buiten het bereik waarin `conversion_in_range` is gemeten, en dan schrijft §4 `NONE` voor "
  "in plaats van een slag naar de waarde. Sinds de reparatie van 31 oktober "
  "(`promotion.match_tier`, \"de zwakste kant wint\") kan die `NONE` niet meer stil worden "
  "overschreven door een geldige omrekening aan de andere kant — dat was de bevinding van die dag, "
  "en vandaag werkt ze zoals bedoeld: het duel staat op NONE met de uitploeg als oorzaak.")
A("")
A("Geen van de negen omgerekende duels is een bet geworden; de lat van 16,0 pp voor `LIGHT` werd "
  "door geen enkele in de buurt gekomen (hoogste: Frosinone – Torino, +8,85 pp).")
A("")

open("tmp-run/ra_nov01_runreport_deel2.md", "w").write("\n".join(L) + "\n")
print("deel 2:", len(L), "regels")
