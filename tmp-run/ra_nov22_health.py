"""Run A, 22 nov 2026 — bronprobe voor source-health.json (§6b-3).

ZESENDERTIG duels in het inzetvenster over ELF competities, tegen een zondagcap van 55: niets
afgekapt. Geen beker heeft een ronde en geen Europees toernooi speelt.

GEEN ENKELE BRONSTORING AAN DE KANT VAN DEZE REPO. `store["errors"]` is over de hele run leeg
gebleven en de tweede-bronbevestiging van §1 is het over ALLE 22 competities eens: 36 tegen 36.
De enige bron die niet levert is Understat, en dat is zijn eigen onderhoudspagina — veertiende
dag op rij.
"""

import json, datetime

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
H = json.load(open("data/source-health.json"))
S = H["sources"]


def note(key, status, detail):
    prev = S.get(key, {})
    hist = prev.get("detail_history") or []
    if prev.get("detail") and prev.get("last_checked"):
        hist = (hist + [{"date": prev["last_checked"], "detail": prev["detail"]}])[-6:]
    S[key] = {**prev, "status": status, "last_checked": now[:10], "detail": detail,
              "detail_history": hist}
    print(f"{key:22} {status:12} {detail[:90]}")


note("fotmob", "ok",
     "22 nov (run A): daglijsten 22 en 23 nov opgehaald, en voor de afwikkeling die van 21 en "
     "22 nov. idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. "
     "Standen van alle elf spelende competities over beide seizoenen geleverd, plus de divisie "
     "eronder voor de VIJFTIEN omgerekende ploegen. Context voor ALLE 36 duels zonder een enkele "
     "fout; 21 daarvan leverden een meetbare rij in het contextlogboek (2507 duels nu), de "
     "overige 15 missen aan een kant een bruikbare uitvallerslijst of selectiewaarde en worden "
     "door ctxlog.out_share overgeslagen in plaats van als gemeten nul geboekt. marketform op "
     "33 doorgerekende duels, preview op de 4 gepubliceerde. De afwikkeling van 103 openstaande "
     "rijen van 21 november vond ELKE wedstrijd terug: nul missers. Fotmob is op dit moment "
     "feitelijk de ENIGE xG-bron, want Understat ligt eruit (zie understat); valt deze bron om, "
     "dan bindt §3 punt 3 en hoort de vraag over een betaald statistiekenplan vooraan in de "
     "notificatie. Vandaag is daar geen aanleiding voor.")

note("the_odds_api", "ok",
     "22 nov (run A): api_check.py meldt 46 actieve competities, quota 19185 over van 20000 en "
     "815 verbruikt deze maand; 33 van 34 sportkeys van de repo actief. De enige inactieve is "
     "soccer_italy_coppa_italia, en die competitie staat deze maand BUITEN DE RUNLIJST, dus het "
     "kost niets. Geen enkele sleutel afgewezen. Inkoop: 11 van 11 spelende competities kregen de "
     "VOLLEDIGE bulk (h2h + spreads + totals, 3 credits elk = 33), daarna 29 BTTS-aanroepen van "
     "1 credit voor de duels met een kandidaat-edge (§1a stap 2, de vereniging van beide schalen). "
     "Totaal 62 van een plafond van 1064; 19123 over. De naamfout die de Süper Lig op 21 november "
     "zijn hele prijskant kostte is gerepareerd in oddsapi.sport_key en de Turkse bulk liep "
     "vandaag zonder hapering: alle vier Turkse duels hadden alle zes markten. Marktbalans-"
     "controle geslaagd zo ruim als hij kan: 11 van 11 competities met zowel een uitkomst- als "
     "een doelpuntenmarkt.")

note("betexplorer", "ok",
     "22 nov (run A): fetch_league_fixtures leverde voor alle 11 spelende competities het gratis "
     "1X2-marktgemiddelde, en voor alle 22 competities van de runlijst de fixturepagina voor de "
     "tweede-bronbevestiging van §1. Uitkomst: 22 van 22 competities eens over het aantal duels "
     "in het inzetvenster, 36 tegen 36 in totaal — inclusief de vijf competities zonder "
     "wedstrijd en inclusief de zes bekers, want juist daar moet een tweede bron kijken. Geen "
     "verhuisde slug en geen lege tabel. De prijzen van deze bron zijn NIET gebruikt voor de "
     "bets zelf (§1a: gemiddelde om te meten, beste prijs om te spelen), alleen voor het "
     "kalibratieblok van §6e en voor poort 8.")

note("understat", "http_503",
     "22 nov (run A): UnderstatError 'geen JSON terug van "
     "https://understat.com/getLeagueData/<liga>/2025 (26719 bytes)' voor alle vijf competities "
     "(EPL, La_liga, Bundesliga, Serie_A, Ligue_1). VEERTIENDE DAG OP RIJ. De 26719 bytes zijn "
     "Understats eigen onderhoudspagina, vastgesteld op 9 nov 2026 — geen blokkade tegen bots en "
     "geen storing in deze repo, dus §3 ('niet omheen werken') is hier niet aan de orde en er is "
     "niets te repareren. WAT HET RAAKT: uitsluitend p_xg_understat in het kalibratieblok van "
     "§6e, dus de vergelijking tussen twee xG-modellen groeit niet. my_prob, de tiers en de "
     "prob_sources komen van Fotmob en veranderen er niet door (§4). WAT HET WEL BETEKENT: de "
     "redundantie die §4 op 31 aug 2026 heeft ingebouwd is er feitelijk niet, en Fotmob is de "
     "enige xG-bron voor elke competitie.")

note("pinnacle_via_odds_api", "ok",
     "22 nov (run A): Pinnacle zat bij 30 duels in de 1X2-respons en bij 30 (duel, lijn)-paren "
     "in de doelpuntenrespons, met een gemiddelde marge van 3,57% tegen 6 tot 10% bij de rest. "
     "Gebruikt als TOETS naast de eigen kans (§3 Stage 5 stap 2), nooit in my_prob of "
     "prob_sources (§2). Gemiddelde absolute afstand tot het Pinnacle-1X2-oordeel 4,15 pp over "
     "30 duels; op de Under-kant gemiddeld -0,64 pp over 30 paren, met 18 van de 30 boven "
     "Pinnacle. ALLE VIER DE GEPUBLICEERDE REGELS STAAN 10 TOT 16 PP VAN DAT OORDEEL AF en alle "
     "vier in de richting van hun eigen bet, terwijl de dag als geheel vlak staat. Bij "
     "Osasuna - Malaga is Pinnacle bovendien ZELF de beste prijs (Over 2,5 @2,06), dus daar zet "
     "het model de uitkomst 15 pp hoger in dan de bookmaker die hem aanbiedt.")

note("forebet", "http_403",
     "22 nov (run A): onveranderd achter Cloudflare, niet opnieuw geprobeerd te omzeilen (§3).")
note("pinnacle_articles", "http_404",
     "22 nov (run A): /betting-articles/soccer/ bestaat nog steeds niet. Onveranderd sinds "
     "20 sep 2026.")
note("matchbook_blog", "http_530",
     "22 nov (run A): server ligt er nog uit. Onveranderd sinds 20 sep 2026.")
note("betfair_blog", "http_403",
     "22 nov (run A): onveranderd achter Cloudflare.")

H["last_run"] = now
H["updated"] = now[:10]
H["last_run_run_a"] = (
    "22 nov 2026, Run A (zondag). 11 van de 16 competities op de runlijst spelen, 36 duels in het "
    "inzetvenster [08:00 NL 22 nov, 08:00 NL 23 nov), zondagcap 55 dus NIETS AFGEKAPT. 22 duels "
    "FULL, 11 LIGHT, 3 op NONE — alle drie omdat promotion.conversion_in_range de omrekening van "
    "de promovendus weigert (Hull City, Erzurumspor FK, AC Horsens), dus een gemeten weigering en "
    "geen bronngat. 460 selecties doorgerekend over alle zes markten. "
    "VIJF SELECTIES HAALDEN ALLE NEGEN POORTEN EN ER PASSEN VIER REGELS IN: MAX_SHORTLIST is "
    "sinds 19 nov 4 op zondag, dus voor het eerst sinds die wijziging valt er op een zondag een "
    "gekwalificeerde selectie buiten de lijst (Marseille - Le Mans Over 3,5 @2,36, +18,46 pp, "
    "rang 5 van 5), geboekt als lijstlengte en groen gemarkeerd bovenaan de dekkingsrapportage. "
    "Gepubliceerd: Lorient - Rennes Over 2,5 @1,94 (+17,22 pp, FULL); Getafe - Atletico Under 2,5 "
    "@1,84 (+11,28, FULL, haalt ook de 10,0 van poort 9); Go Ahead Eagles - Fortuna Sittard 1 "
    "@1,7742 (Betfair netto, +10,15, FULL); Osasuna - Malaga Over 2,5 @2,06 (+17,97, LIGHT). Alle "
    "vier bet_beide = True. "
    "TWEE VOORBEHOUDEN: bij drie van de vier komt het voordeel grotendeels uit de SPLITSMETHODE "
    "(de scheefste van de twee, §6e), en alle vier staan 10 tot 16 pp van het Pinnacle-oordeel af "
    "terwijl de dag vlak staat. "
    "Stage 0: 10 picks (5 gewonnen, 4 verloren, 1 void) en 93 schaduwrijen (39/50/4), geen misser. "
    "recalibrate.fitted_through op 2026-11-21."
)
H["last_run_bevinding"] = (
    "22 nov 2026, Run A — TWEE BEVINDINGEN, EN DE EERSTE IS GOED NIEUWS. "
    "(1) DE NIVEAUCORRECTIE VAN 3 NOVEMBER DOET MEETBAAR WAT ZE MOEST DOEN. gridfit.py measure op "
    "1565 homogene duels: gemiddeld totaal voorspeld 3,028 tegen werkelijk 3,067 (+0,039, "
    "z = +0,86), waar het op 2 november +0,100 met z = +1,93 was over 1147 duels; de fout op "
    "P(Under 2.5) zakte van -2,35 naar -1,21 pp. §6g eiste die controle en schreef: blijft hij op "
    "+0,1, dan hoort de correctie eruit. Hij is er niet op gebleven. ER IS TOCH NIETS TE "
    "BESLISSEN: 392 van de 1565 duels dragen de correctie al in zich, dus de regel scale = 1.032 "
    "toetst daar een DUBBELE correctie, en measure meldt dat nu zelf (gridfit.LEVEL_SWITCH). "
    "Poort 9 blijft onveranderd staan; een run verzet hem niet op eigen initiatief. De tweede "
    "laag staat er juist slechter voor: goalbias meet op de Under-kant +0,677 doelpunt per duel "
    "over 144 gevallen, z = +4,89 (gisteren +0,668 over 139, z = +4,74). "
    "(2) EEN HERGEBRUIKT SCRIPT SCHREEF NAAR HET VOORTGANGSBESTAND VAN GISTEREN. "
    "tmp-run/ra_nov22_marktvorm.py is met sed uit de versie van 21 november overgenomen; de "
    "rundatum stond op TWEE plekken en de aanpassing ving alleen de modulenaam, niet het pad "
    "data/run-state/2026-11-21-run-a.json. Het heeft niets beschadigd en dat is toeval: de duels "
    "van vandaag staan niet in dat bestand, dus er werden nul blokken gezet en het bestand bleef "
    "byte-identiek (git diff leeg). Bij een overlappende naam was er stil een telling van vandaag "
    "in een al gepubliceerd dagrapport bijgekomen, wat §6c verbiedt. Niets klaagde: het script "
    "meldde 'op 0 wedstrijden gezet' en gaf exit 0. Dezelfde stille faalvorm als de sportkey van "
    "21 nov, de status BUITEN DE RUNLIJST van 20 nov en het Serie B-id. Pad gerepareerd; de "
    "telling staat nu op alle 33 doorgerekende duels van vandaag en het bestand van 21 november "
    "is niet aangepast."
)

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt")
