"""Run A, 18 nov 2026 - `data/source-health.json` bijwerken (§6b-3).

Vijf dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **De runlijst is voor de tweede Run A op rij VOLLEDIG leeg** - nul van 21, bij twee bronnen
   nagetrokken. Dit is de eerste Run A sinds 10 november: de gebruiker heeft Run A en B op
   12 november stilgezet voor het interlandvenster (zie Run D van 16 nov).
2. **De ondiepe kloon is deze run WEL met `--unshallow` te repareren**, anders dan op
   10 november. Daarmee verdwijnt het valse alarm van 80 takken: 0 van de 91 takken heeft nog
   eigen commits.
3. **De Understat-storing loopt door op dag achttien**, zelfde onderhoudspagina, zelfde 26.719
   bytes. Kostte vandaag niets (geen van de vijf competities speelt), gaat vanaf 20 nov weer
   kosten.
4. **Nul credits uitgegeven**; de marktbalans-controle van §1a is niet van toepassing bij een
   lege kalender.
5. **De reeks `lijstlengte` haalt vandaag voor het eerst de ~30 afgewikkelde gevallen van §6d**
   en staat op +20,8% - maar op t = +0,89, dus nog niets om op te besluiten.
"""
import json

H = "data/source-health.json"
h = json.load(open(H))
S = h["sources"]
VANDAAG = "2026-11-18"


def hist(key, detail, status=None, role=None):
    """Oude detailtekst bewaren in detail_history voordat hij wordt overschreven."""
    S.setdefault(key, {})
    oud = S[key].get("detail")
    if oud:
        S[key].setdefault("detail_history", []).insert(
            0, {"date": S[key].get("last_checked"), "detail": oud})
        S[key]["detail_history"] = S[key]["detail_history"][:8]
    S[key]["detail"] = detail
    S[key]["last_checked"] = VANDAAG
    if status:
        S[key]["status"] = status
    if role:
        S[key]["role"] = role


hist("understat",
     "18 nov (run A): ACHTTIENDE dag onbruikbaar, en de diagnose van 9 november houdt onveranderd "
     "stand. `understat.fetch_league('EPL', '2026')` geeft opnieuw `UnderstatError: geen JSON terug "
     "van https://understat.com/getLeagueData/EPL/2026 (26719 bytes)` - EXACT hetzelfde aantal bytes "
     "als alle dagen ervoor, en de pagina zelf is opnieuw uitgepakt om zeker te zijn dat het geen "
     "nieuwe storing is: HTTP 200, `<title>Understat.com</title>`, zichtbare tekst 'We will come back "
     "soon'. Dat is Understats eigen onderhoudspagina, geen Cloudflare en geen verhuisde route; er is "
     "dus niets om langs te werken (§3, 'Niet doen'). "
     "WAT HET VANDAAG KOST: NIETS, en om dezelfde reden als op 9 en 10 november - geen van de vijf "
     "Understat-competities (EPL, La Liga, Bundesliga, Serie A, Ligue 1) speelt in het inzetvenster, "
     "dus er is geen doorgerekende wedstrijd die een `p_xg_understat`-arm had kunnen krijgen. "
     "WANNEER HET WEER GAAT KOSTEN, EN DAT IS BINNENKORT: op vrijdag 20 november spelen La Liga "
     "(Ath Bilbao - Espanyol), Bundesliga (Bayern - FC Koln) en Ligue 1 (Troyes - Le Havre) weer, en "
     "op 21/22 november de volle speelronde. Vanaf dan is Fotmob opnieuw de enige xG-bron voor elk "
     "duel. §3 (27 sep 2026) schrijft voor dat de kanskant pas VOORAAN in de notificatie hoort zodra "
     "FOTMOB wegvalt; dat is niet gebeurd - Fotmob leverde vandaag twee volledige daglijsten "
     "(47 competities / 122 duels) en alle 33 standen van `idcheck.py` zonder een enkele fout.",
     status="onderhoudspagina")

hist("ondiepe_kloon",
     "18 nov (run A): `git rev-parse --is-shallow-repository` gaf bij de start `true`, en deze keer "
     "REPAREERT `git fetch --unshallow origin` het WEL. Dat is het verschil met 10 november, waar de "
     "knip al naar `origin` gepusht was en de oude geschiedenis onder `main` niet meer bestond. Na het "
     "unshallowen telt `main` 747 commits (was 60 in de container) en geeft "
     "`git rev-list --count HEAD..<tak>` voor ALLE 91 remote takken 0 - waar dezelfde telling VOOR het "
     "unshallowen 84 takken met 27 tot 691 'eigen' commits meldde. Dat is exact de valse-alarmvorm "
     "waarvoor Stage -2 de waarschuwing bevat. DOE DUS ALTIJD EERST `--unshallow` en tel daarna; de "
     "tabel van 20 aug 2026 (7 van 15 takken voor, 0 van 15 na) klopt onverminderd.",
     status="gerepareerd met --unshallow")

hist("branchaudit",
     "18 nov (run A): 91 remote takken, en na `--unshallow` heeft GEEN ENKELE eigen commits. De "
     "inhoudelijke controle van §3 Stage -2 (27 sep 2026) is er evengoed bovenop gedaan, want '0 eigen "
     "commits' is een uitspraak over de graaf en niet over de metingen: per tak de id's uit alle vijf "
     "de logboeken tegen `main` gelegd. `picks.jsonl` 561 van 561 (vereniging over alle takken = main), "
     "`calibration.jsonl` 2813 van 2813, `context-log.jsonl` 2373 van 2373. In `shadow.jsonl` staan op "
     "oudere takken VIER id's die main niet heeft, en die horen daar NIET bij: het zijn precies de "
     "kale vormen van Canada-Peru, Croatia-England, Estonia-Luxembourg en Switzerland-Slovenia van "
     "3 oktober, die op 7 november met opzet zijn verwijderd omdat ze een dubbeltelling waren (§3 "
     "Stage -2, de uitzondering op de vereniging). Ze zijn dus bewust NIET aangevuld. Er valt niets te "
     "mergen en de run staat op `main`.",
     status="ok")

hist("the_odds_api",
     "18 nov (run A): `api_check.py` geeft OK - 46 actieve voetbalcompetities, quota 19385 over / 615 "
     "gebruikt deze maand, en 33 van de 34 sportkeys van de repo actief. NIET actief vandaag: "
     "`soccer_italy_coppa_italia` (Coppa Italia), wat klopt - die beker speelt pas 2 december. ZES "
     "actieve sportkeys die de repo niet kent: soccer_brazil_serie_b, soccer_germany_bundesliga_women, "
     "soccer_germany_liga3, soccer_spain_copa_del_rey, soccer_sweden_superettan, "
     "soccer_uefa_champs_league_women. Dat is dezelfde lijst als op 10 november; alleen de Copa del "
     "Rey valt binnen de soort competities die de runlijsten volgen, en dat punt staat al als besluit "
     "bij de gebruiker (zie `copa_del_rey_buiten_alle_runlijsten`). NUL CREDITS UITGEGEVEN deze run: "
     "zonder duel in het inzetvenster is er geen competitie om prijzen voor te kopen.",
     status="ok")

hist("fotmob",
     "18 nov (run A): levert zonder fout. Twee daglijsten (18 en 19 nov) met samen 47 competities en "
     "122 duels, en geen van die 122 hoort bij de Run A-runlijst. De drie id's die makkelijk verwarren "
     "zijn nagekeken en zijn alle drie een andere competitie dan de runlijst: `Ligue 1 [516]` is "
     "ALGERIJE (niet Frankrijk, dat is 53), en de drie `Cup`-ingangen zijn Slovenie (174), Egypte "
     "(9941) en Colombia (9490). `Copa del Rey - 1st Round [138]` speelt 6 duels en staat in geen "
     "enkele runlijst. `idcheck.py`: alle 33 id's uit coverage.json leveren een bruikbare stand.",
     status="ok")

hist("bevestiging_tweede_bron_leeg",
     "18 nov (run A): de tweede bron is opnieuw voor alle vijf de bekers EN voor vier competities "
     "gedraaid, en geeft hetzelfde antwoord als de daglijst. `betexplorer.fetch_league_fixtures` per "
     "pagina: FA Cup 20 rijen (eerste 4 dec), League Cup 4 (15 dec), Coppa Italia 2 (2 dec), DFB Pokal "
     "8 (1 dec), KNVB Beker 0 rijen op de pagina, Premier League 20 (21 nov 13:30), Serie A 20 "
     "(21 nov 15:00), Eredivisie 18 (21 nov 16:30), Champions League 18 (24 nov 18:45). NUL rijen in "
     "het venster 18/19 nov bij alle negen. Dit blijft de controle die het gat van 6 oktober 2026 "
     "dicht: 'niet in de daglijst' mag nooit als GEEN WEDSTRIJD worden opgeschreven zonder tweede "
     "bron. LET OP BIJ DE KNVB BEKER: daar geeft de pagina nul rijen in plaats van een latere ronde, "
     "dus de tweede bron BEVESTIGT daar niets - hij spreekt de daglijst alleen niet tegen. Dat is een "
     "zwakkere waarneming dan bij de andere vier en hoort als zodanig gelezen te worden.",
     status="ok")

hist("herijking_fitted_through",
     "18 nov (run A): `recalibrate.load_fit().fitted_through` = 2026-11-17, de vorige rundag, dus "
     "`calibration.py settle` is niet blijven liggen (§6b-5c). De fit staat op a=1.0541, b=0.0349 over "
     "7983 waarnemingen. `settle` wikkelde deze run 126 waarnemingen af; het logboek staat op 8382 van "
     "8415 compleet, 33 nog open.",
     status="ok")

S.setdefault("lijstlengte_reeks", {})
hist("lijstlengte_reeks",
     "18 nov (run A): de reeks `lijstlengte` haalt VOOR HET EERST de ~30 afgewikkelde gevallen die §6d "
     "eist. Stand na deze run: 30 bets, 15 winnaars, +6,24u = +20,8% (`shadow.py stats`; drie rijen met "
     "maar een methode staan daar buiten, zoals het script ze altijd apart houdt). Voor deze run waren "
     "het 28 bets op +20,5%, dus de vier afgewikkelde rijen van 17 november (Denmark-Norway lost, "
     "Ireland-Kosovo won, Malawi-Egypt won, Mauritania-Burkina Faso won) brengen hem over de grens. "
     "LEES HEM NOG NIET ALS EEN UITKOMST: t = +0,89 over 30 bets, dus het rendement is niet van nul te "
     "onderscheiden, en de reeks loopt over drie runs (A 14, B 9, C 7) en acht weken. De grens van §6d "
     "is een ondergrens om een reeks te MOGEN lezen, geen bewijs dat er iets staat. Er is dus geen "
     "besluit aan de gebruiker voorgelegd - dat zou dezelfde fout zijn als een poort verzetten op een "
     "enkele dag. Noem de stand elke run onder 'Stand van het logboek' en leg hem pas voor als het "
     "teken bij meer gevallen standhoudt.",
     status="meting loopt")

h["last_run"] = {
    "run": "A",
    "date": VANDAAG,
    "note": (
        "DE RUNLIJST VAN RUN A IS VOLLEDIG LEEG: EENENTWINTIG VAN DE EENENTWINTIG COMPETITIES EN "
        "TOERNOOIEN HEBBEN GEEN WEDSTRIJD IN HET INZETVENSTER [08:00 NL 18 nov, 08:00 NL 19 nov). "
        "Oorzaak is het FIFA-interlandvenster van november, dat op 17/18 november afloopt: de dertien "
        "clubcompetities liggen stil, de drie Europese toernooien spelen niet en de vijf bekers hebben "
        "hun eerstvolgende ronde in december. Bij TWEE bronnen nagetrokken (Fotmob-daglijsten 18 en "
        "19 nov; BetExplorer-fixturepagina per competitie). Nul doorgerekende selecties, dus nul bets, "
        "nul credits en geen enkele poort die iets heeft tegengehouden - dat laatste is iets anders dan "
        "een dag waarop de poorten alles wegvangen. "
        "DIT IS DE EERSTE RUN A SINDS 10 NOVEMBER: de gebruiker heeft Run A en Run B op 12 november "
        "stilgezet voor de duur van het interlandvenster (vastgelegd in Run D van 16 nov), en de zeven "
        "ontbrekende voortgangsbestanden van 11 t/m 17 november zijn die pauze en geen storing. "
        "WANNEER RUN A WEER WERK HEEFT: de run van 19 november heeft nul duels in zijn venster; de run "
        "van VRIJDAG 20 NOVEMBER heeft er zeven (La Liga 1, Bundesliga 1, Ligue 1 1, Belgian Pro "
        "League 1, Danish Superliga 1, Ekstraklasa 2), en 21/22 november is de volle speelronde."
    ),
}
h["last_run_bevinding"] = (
    "18 nov (run A): de reeks `lijstlengte` - de selecties die alle poorten EN hun drempel haalden "
    "maar niet in de top 3/5 pasten - haalt vandaag voor het eerst de ~30 afgewikkelde gevallen die "
    "§6d eist, en staat op +20,8% over 30 bets (15 winnaars). Dat is de reeks die moet meten wat de "
    "lijstlengte kost. Hij staat positief, maar op t = +0,89: niet van nul te onderscheiden. Geen "
    "besluit, geen wijziging, alleen vanaf nu elke run de stand melden."
)
h["updated"] = VANDAAG
json.dump(h, open(H, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", VANDAAG, "| sources:", len(S))
