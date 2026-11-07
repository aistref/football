"""Run A, 7 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Vier dingen die hier vastgelegd moeten worden en die een volgende run anders opnieuw moet
uitzoeken:

1. **Understat ligt er de zesde dag uit**, en vandaag raakt het achttien duels in plaats van
   vijf: alle vijf zijn competities hadden een volle speelronde.
2. **Het Fotmob-id 132 van de FA Cup heeft zich meteen terugbetaald.** Gisteren gevonden, vandaag
   drieëndertig duels die anders als `GEEN WEDSTRIJD` waren weggeschreven.
3. **`preview.week_around` koppelde op NAAM en haalde clubs met dezelfde naam uit andere
   competities binnen.** Vanochtend gemeten op Nacional en gerepareerd; raakt geen enkele kans of
   pick, alleen de tekst die de gebruiker leest.
4. **De cap bond voor het eerst sinds weken**, en de knip liep dwars door een gelijkspel in de
   datarijkdom-score — precies wat §4 op 5 september had gemeten.
"""
import json

H = "data/source-health.json"
h = json.load(open(H))
S = h["sources"]


def hist(key, detail, status=None, role=None):
    """Oude detailtekst bewaren in detail_history voordat hij wordt overschreven."""
    S.setdefault(key, {})
    oud = S[key].get("detail")
    if oud:
        S[key].setdefault("detail_history", []).insert(
            0, {"date": S[key].get("last_checked"), "detail": oud})
        S[key]["detail_history"] = S[key]["detail_history"][:8]
    S[key]["detail"] = detail
    S[key]["last_checked"] = "2026-11-07"
    if status:
        S[key]["status"] = status
    if role:
        S[key]["role"] = role


hist("understat",
     "7 nov (run A): ZESDE dag op rij onbruikbaar, en de duurste tot nu toe. Alle vijf de "
     "competities geven exact dezelfde fout: `UnderstatError: geen JSON terug van "
     "https://understat.com/getLeagueData/<code>/2025 (26719 bytes)` — vijf verzoeken, vijf keer "
     "EXACT 26.719 bytes. Vier dagen op rij hetzelfde antwoord in dezelfde grootte wijst op een "
     "blokkadepagina of een permanent gewijzigde route, niet op een storing die voorbijgaat. De "
     "reeks: 1 nov HTTP 502 op de CONNECT van de netwerkgateway, 3 nov `Connection reset by "
     "peer`, 4/5/6/7 nov 26.719 bytes zonder JSON. "
     "WAT HET VANDAAG KOST, en het is ruim drie keer gisteren: alle vijf de Understat-competities "
     "(PL, La Liga, Bundesliga, Serie A, Ligue 1) hadden een volle zaterdagronde, dus 18 van de "
     "52 doorgerekende duels missen hun `p_xg_understat`-arm in het kalibratieblok van §6e — "
     "gisteren waren dat 5 van de 15. Drie van de vijf gepubliceerde bets staan in die vijf "
     "competities (Málaga – Racing Santander, Mainz 05 – Bayern München, Roma – Sassuolo). "
     "WAT HET NIET KOST: geen enkel duel wordt hierdoor `NONE`. Fotmob levert en is voor vrijwel "
     "elke competitie de xG-bron, dus §2 blijft gedekt. §3 (27 sep 2026) schrijft voor dat de "
     "kanskant pas vooraan in de notificatie hoort zodra FOTMOB wegvalt; dat is niet het geval. "
     "Wat weg is, is de REDUNDANTIE waarvoor Understat op 31 augustus is toegevoegd — zes dagen, "
     "en als Fotmob ook omvalt is er niets meer.")

hist("fa_cup_id",
     "7 nov (run A): HET ID 132 HEEFT ZICH DE EERSTE DAG AL TERUGBETAALD. Gisteren vastgesteld en "
     "onder `notes` in `coverage.json` gezet; vandaag speelde de hele eerste ronde met 33 duels. "
     "Zonder die aantekening had de competitiepoort `GEEN WEDSTRIJD` geschreven bij 33 duels die "
     "er gewoon waren — het gat dat Run A op 6 oktober 2026 vijf duels kostte, nu zes keer zo "
     "groot. TWEE BRONNEN, ZELFDE AANTAL: de Fotmob-daglijst geeft onder `primaryId` 132 "
     "33 duels in het inzetvenster en BetExplorer (`/england/fa-cup/fixtures/`, 38 teamparen) "
     "geeft er 33, met dezelfde ploegen en aftraptijden. "
     "WAT HET OPLEVERDE: 6 van de 33 komen op `FULL` via `promotion.shared_lower_division` "
     "(beide ploegen in dezelfde divisie onder de Premier League, dus niets te overbruggen), de "
     "andere 27 blijven `NONE` omdat daar een profclub tegen een non-league-club staat en juist "
     "dat niveauverschil de onbekende is. Eén van de zes werd een volledig gekwalificeerde "
     "selectie: Newport County – Walsall, 1X2 2 @2.61, +8,46 pp, alle negen poorten open — maar "
     "rang 7 van 8 en dus gevallen op `lijstlengte` (§5b). "
     "LET OP HET VOORBEHOUD: de FA Cup heeft geen actieve sportkey (`soccer_england_fa_cup` staat "
     "niet in de 50 actieve competities van `api_check.py`), dus hij leunt op het gratis "
     "BetExplorer-marktgemiddelde en de edge valt daar systematisch te LAAG uit. Twee FA "
     "Cup-duels kregen daardoor ook geen BTTS-ronde; dat staat in `markets_checked` als 'niet "
     "opgevraagd — geen sportkey' en niet als 'opgevraagd maar geen boek noteerde deze markt'.",
     status="gevonden")

hist("preview_weekoverzicht",
     "7 nov (run A): GEREPAREERD — `preview.week_around` koppelde uitsluitend op de "
     "GENORMALISEERDE NAAM, en de Fotmob-daglijst bevat álle competities ter wereld. Elke club "
     "met dezelfde genormaliseerde naam kwam daardoor in het weekoverzicht van een andere club "
     "terecht. Vanochtend gemeten op NACIONAL (Primeira Liga, Funchal): zijn weekoverzicht bevatte "
     "twee duels van Club Nacional de Football (Liga AUF Uruguaya) en twee van Club Nacional uit "
     "Asunción (Division Profesional) — vier duels van twee andere clubs, naast het enige echte "
     "duel (Arouca – Nacional, 1 nov, 1-0). De voorbeschouwing zou een drukke week hebben "
     "beschreven waar de ploeg er één wedstrijd speelde. "
     "DEZELFDE FAMILIE ALS DE æ-LIGATUUR (13 sep) EN DE POOLSE ł (17 okt), MAAR NIET DEZELFDE "
     "OORZAAK: `teamnames.norm` doet hier precies wat hij moet doen; het probleem is de aanname "
     "dat een naam een sleutel is. `week_around` koppelt nu op `id` zodra dat bekend is en valt "
     "alleen op de naam terug als er geen id is (dan is de oude, ruimere koppeling beter dan "
     "niets); elke rij draagt `gekoppeld_op` = id|naam zodat het van buitenaf te zien is. "
     "`match_block` neemt `home_id`/`away_id` aan en het runscript haalt ze uit de Stage 3-uitvoer "
     "(de wedstrijdrecords in `data/run-state/` dragen ze niet — dat is een apart, klein "
     "administratiegat dat hier wordt genoteerd en niet stil gedicht). "
     "WAT HET NIET RAAKTE: niets. §2 houdt dit blok met opzet buiten `my_prob` en "
     "`prob_sources`, dus de vijf picks van vandaag zijn met en zonder de fout identiek. Wat het "
     "WEL raakte is het enige deel van de run dat voor de gebruiker is gemaakt (§6c). De "
     "voorbeschouwingen van vandaag zijn na de fix opnieuw gegenereerd. "
     "`python3 scripts/preview.py selftest` dekt het geval af met drie clubs die Nacional heten "
     "op één daglijst, en toetst BEIDE kanten: dat de nieuwe koppeling ze scheidt (1 rij) en dat "
     "de oude ze door elkaar haalde (3 rijen), zodat zichtbaar blijft wát er is gerepareerd. "
     "32 controles, geen netwerk.",
     status="gerepareerd",
     role="voorbeschouwingsmateriaal (§6b-5i) — h2h, insights, weer en weekoverzicht")

hist("max_deep_analyses_knip",
     "7 nov (run A): DE CAP BOND VOOR HET EERST SINDS WEKEN EN KOSTTE ZES ANALYSES, NIET "
     "EENENDERTIG. 86 duels in het inzetvenster op een zaterdagcap van 55 "
     "(`ranking.max_deep_analyses`), dus 31 afgekapt. Van die 31 komen er 25 op `tier = NONE` uit "
     "— allemaal FA Cup-duels met een non-league-club waar geen vergelijkbare historie is — en "
     "zes op `LIGHT`: Blackburn Rovers – West Ham United, Queens Park Rangers – Lincoln City, "
     "Royal Antwerp – Lommel, Galatasaray – Amed Sportif, St. Johnstone – Dundee FC en Górnik "
     "Zabrze – Wieczysta Kraków. Die 25 waren met of zonder cap niet doorgerekend. "
     "DE KNIP LIEP DWARS DOOR EEN GELIJKSPEL, en dat is de meetuitkomst van §4 en geen toeval: de "
     "laagste die het haalde (Wrexham – Wolverhampton Wanderers) en de hoogste die afviel "
     "(Blackburn Rovers – West Ham United) hebben EXACT dezelfde datarijkdom (5,5) en EXACT "
     "hetzelfde aantal markten (5); de rangorde is door de aftraptijd beslist. §4 heeft op 5 sep "
     "2026 gemeten dat deze score niet scheidt (betkans vlak: 29,1% op plek 1–10 tegen 30,0% op "
     "31–35) en dat afkappen dus naar rato kost. Vandaag is dat aan de knip zelf te zien. "
     "Bereik in de run: 3,5 tot 8,0. "
     "GEEN AANLEIDING OM DE CAP TE VERHOGEN: het is een TIJDSgrens en geen creditgrens (§0) en de "
     "55 is op 5 september op een meting gezet. De looptijd van vandaag staat in "
     "`data/run-state/` onder `duur`.",
     status="bond_vandaag",
     role="afkapping Stage 4 (§3) — tijdsgrens, geen creditgrens")

hist("the_odds_api",
     "7 nov (run A): OK, en de ruimste marktbalans die deze controle ooit heeft gehaald. "
     "`api_check.py`: 50 actieve voetbalcompetities, quota 19.687 over en 313 verbruikt deze "
     "maand, en 32 van de 34 sportkeys van de repo actief (Coppa Italia en Conference League "
     "niet — beide spelen vandaag ook niet). De bulk-aanroep (h2h + spreads + totals, 3 credits "
     "per competitie) is voor ALLE DERTIEN inkoopbare competities gelukt: 39 credits, plus 36 "
     "voor de BTTS-tweede ronde op 36 duels met een kandidaat-edge (§1a stap 2) = 75 van een "
     "plafond van 409. Marktbalans op de INKOOP: 13 van de 13 competities kregen zowel een "
     "uitkomst- als een doelpuntenmarkt. Dat is hier geen formaliteit: alle vijf de gepubliceerde "
     "bets staan op Over/Under, en zonder dit cijfer is van buitenaf niet te zien of die "
     "eenzijdigheid uit de analyse of uit de portemonnee komt (§1a, 29 aug 2026). Ze komt uit de "
     "analyse — 668 doorgerekende selecties, verdeeld over O/U 220, AH 159, 1X2 144, BTTS 72, "
     "DNB 49 en DC 24.",
     status="ok")

hist("poort_5_bevestiging",
     "7 nov (run A): DERDE DAG OP RIJ DE POORT DIE DE DAG BEPAALT, nu op een ruim drie keer zo "
     "grote steekproef. 498 van de 668 doorgerekende selecties sneuvelen op poort 5 (74,6%), "
     "tegen 149 van 186 (80,1%) op 6 nov en alle 17 selecties van het enige analyseerbare duel "
     "op 5 nov. Daarna: `edge` 62 (9,3%), `context` 34 (5,1%), `odds` 29 (4,3%), `robuustheid` "
     "17 (2,5%), `underdog` 14 (2,1%), `doelpunten_onder` 1 (0,1%); 13 selecties (1,9%) halen "
     "alle poorten. "
     "DE SCHADUWREEKS ZEGT DAT DE POORT ZIJN WERK DOET en dat is de maat die §6d voorschrijft, "
     "niet het aandeel van vandaag: `tweede_methode` staat op 265 kandidaten, 256 afgewikkeld, "
     "trefkans 46,5%, rendement -1,0% (-2,63u). Een poort met een negatief rendement op 256 "
     "gevallen bespaart geld. §1f: als KANSBRON voegt de splitsmethode vrijwel niets toe (Brier "
     ".23674 tegen .23625), als VETO bespaart ze aantoonbaar geld. "
     "ER IS VANDAAG NIETS VERZET. Drie dagen is geen reeks (§6d, §1g).",
     status="derde_dag")

hist("poort_9_doelpunten_onder",
     "7 nov (run A): DE REEKS IS BOVEN DE ~30 VAN §6d EN DUIDELIJK NEGATIEF — de rem doet zijn "
     "werk. `doelpunten_onder` staat op 35 kandidaten, alle 35 afgewikkeld, trefkans 37,1%, "
     "rendement -30,4% (-10,63u). Vandaag hield de poort één selectie tegen. "
     "DE ONDERLIGGENDE SCHEEFSTAND IS GEGROEID, NIET GEKROMPEN: `margins.py goalbias` meet over "
     "127 gespeelde Unders +0,626 doelpunt per duel boven de eigen lambda (z = +4,25), tegen "
     "126 gevallen / +0,614 / z = +4,16 gisteren. Hammarby – Elfsborg van 6 nov (Under 3 @1,93, "
     "uitslag 4-1, vijf doelpunten tegen een verwachting van 2,90) is daar de nieuwste steen op. "
     "Over-kant onveranderd rustig: 67 gevallen, -0,267, z = -1,20. In het logboek: "
     "`Over/Under — Under` 159 picks / -15,7%, `Over/Under — Over` 90 picks / +6,6%. "
     "ÉÉN VAN DE VIJF BETS VAN VANDAAG STAAT OP DEZE KANT (Roma – Sassuolo, Under 3.5 @1,9506, "
     "+11,22 pp en dus ruim boven de verzwaarde lat van 10,0), en bij dat duel spreken de "
     "frequenties van §4 de bet rechtstreeks tegen (Roma 18 doelpunten in 5 duels, gemiddeld 4,2; "
     "Sassuolo 4,8). Dat staat vooraan in de `why`-tekst, zoals §4 punt 2 eist. "
     "ER IS NIETS VERZET, en de vraag hoort nog niet gesteld: `gridfit.py measure` zegt dat maar "
     "84 van de 1257 homogene duels lambdas van ná 3 nov dragen, dus de niveaucorrectie "
     "`LEVEL_SCALE` = 1.032 is nog niet te beoordelen (§6g, §1h).",
     status="meting_loopt")

h["updated"] = "2026-11-07"
h["last_run"] = {
    "run": "A",
    "date": "2026-11-07",
    "note": (
        "DE VOLSTE DAG VAN DE REEKS: 86 duels in het inzetvenster uit dertien competities van de "
        "runlijst plus een volledige eerste ronde FA Cup (33 duels). De zaterdagcap van 55 bond "
        "dus voor het eerst sinds weken: 31 afgekapt, waarvan 25 op `NONE` uitkwamen — de cap "
        "kostte zes echte analyses. VIJF BETS, EN ALLE VIJF OP OVER/UNDER (vier Over, één Under). "
        "Dat is de analyse en niet de inkoop: de bulk is voor alle dertien inkoopbare competities "
        "gelukt en 13 van de 13 kregen zowel een uitkomst- als een doelpuntenmarkt, met 668 "
        "doorgerekende selecties over zes markten. Acht selecties haalden alle negen poorten én "
        "hun drempel; er passen vijf regels in een zaterdaglijst, dus drie vielen op "
        "`lijstlengte` (§5b) — Osasuna – Athletic Club, Newport County – Walsall en Leeds United "
        "– Tottenham Hotspur. `MAX_LIGHT_IN_SHORTLIST` hield niets tegen (twee LIGHT in de lijst, "
        "twee in de hele run). Poort 5 hield voor de derde dag op rij driekwart van alles tegen "
        "(498 van 668). Gerepareerd: `preview.week_around` koppelde op naam en haalde twee andere "
        "clubs die Nacional heten in het weekoverzicht — raakt geen pick, wel de tekst die de "
        "gebruiker leest. Afwikkeling van 6 nov: 3 van 4 bets gewonnen; de verliezer was de enige "
        "Under (Hammarby – Elfsborg, 4-1 op een verwachting van 2,90) en die past in de reeks van "
        "127 gevallen die §6g meet. Understat zesde dag uit, raakt 18 duels, kost geen enkel duel."
    ),
    "matches_in_window": 86,
    "analysed": 52,
    "truncated": 31,
    "truncated_cost_real_analyses": 6,
    "bets": 5,
    "qualified_not_published": 3,
    "credits": "75 van een plafond van 409 (39 bulk voor 13 competities + 36 BTTS voor 36 duels); 19.612 over",
    "samenvatting": "5 bets, alle vijf Over/Under; cap bond (31 afgekapt, 6 met data); poort 5 derde dag op 74,6%",
}
json.dump(h, open(H, "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt:", len(S), "bronnen")
