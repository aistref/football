"""Run A, 9 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Vier dingen die hier vastgelegd moeten worden en die een volgende run anders opnieuw moet
uitzoeken:

1. **De achtdaagse Understat-storing is EINDELIJK gediagnosticeerd.** Acht runrapporten noemen
   "geen JSON terug, 26.719 bytes" zonder te zeggen wát er dan wel terugkomt. Vandaag is die
   respons uitgepakt: het is Understats EIGEN onderhoudspagina — `<title>Understat.com</title>`
   met als enige zichtbare tekst *"We will come back soon"*. Geen Cloudflare, geen 403, geen
   verhuisde route, geen blokkade: de site staat er zelf uit.
2. **Het interlandvenster legt de hele runlijst stil**: één wedstrijd in het inzetvenster, bij
   twee bronnen nagetrokken.
3. **Die ene wedstrijd komt op `NONE` uit** omdat beide ploegen op het achtste niveau spelen, in
   twee verschillende groepen van dezelfde divisie.
4. **Nul credits uitgegeven en de marktbalans-controle van §1a slaagt niet** — niet door een krap
   plafond maar door een lege kalender.
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
    S[key]["last_checked"] = "2026-11-09"
    if status:
        S[key]["status"] = status
    if role:
        S[key]["role"] = role


hist("understat",
     "9 nov (run A): ACHTSTE dag onbruikbaar, EN VOOR HET EERST MET EEN DIAGNOSE. De acht "
     "voorgaande rapporten schreven `UnderstatError: geen JSON terug van "
     "https://understat.com/getLeagueData/<code>/2025 (26719 bytes)` zonder te zeggen wát er dan "
     "wél terugkomt. Vandaag is die respons uitgepakt (HTTP 200, nginx/1.24.0 (Ubuntu), "
     "Content-Encoding gzip, 5.783 bytes over de lijn en 26.719 na uitpakken): het is UNDERSTATS "
     "EIGEN ONDERHOUDSPAGINA — `<title>Understat.com</title>` met als enige zichtbare tekst "
     "'We will come back soon', nul `teamsData`, nul `datesData`, nul `JSON.parse`. "
     "DAT VERANDERT DE CONCLUSIE VAN DE REEKS. Er stond acht dagen 'wijst op een blokkadepagina "
     "of een permanent gewijzigde route'; het is geen van beide. Geen Cloudflare-challenge (geen "
     "CF-RAY, geen 'Just a moment'), geen 403, geen 404, geen verhuisde URL — de route werkt en "
     "antwoordt met 200. De site is door zijn eigen beheerder uit de lucht gehaald. Dat de "
     "respons acht dagen EXACT 26.719 bytes is, is precies wat een statische onderhoudspagina "
     "doet, en het was dus geen aanwijzing voor een blokkade maar voor het tegendeel. "
     "WAT ER NIET AAN TE DOEN IS, en dat is nu ook zeker: er is niets om langs te werken. §3 "
     "('Niet doen') verbiedt het omzeilen van een challenge; hier is er geen challenge, er is "
     "geen data. Een headless browser, een andere user-agent of een proxy zouden dezelfde "
     "onderhoudspagina krijgen. Hij komt terug als de beheerder hem terugzet, en de dagcache van "
     "`understat.fetch_league` pakt dat automatisch op. "
     "WAT HET VANDAAG KOST: NIETS. Nul van de vijf Understat-competities (PL, La Liga, "
     "Bundesliga, Serie A, Ligue 1) speelt vandaag — het interlandvenster is begonnen — en de "
     "enige wedstrijd van de run komt op `tier = NONE` uit. Gisteren kostte het 24 van de 55 "
     "duels hun `p_xg_understat`-arm, vandaag nul van nul. De reeks: 1 nov HTTP 502 op de CONNECT "
     "van de netwerkgateway, 3 nov `Connection reset by peer`, 4 t/m 9 nov de onderhoudspagina. "
     "WAT HET WEL BLIJFT KOSTEN: de REDUNDANTIE waarvoor Understat op 31 augustus is toegevoegd. "
     "Fotmob is nu voor vrijwel elke competitie de enige xG-bron, en §3 (27 sep 2026) schrijft "
     "voor dat de kanskant pas vooraan in de notificatie hoort zodra FOTMOB wegvalt. Dat is niet "
     "gebeurd: Fotmob leverde vandaag twee daglijsten, de FA Cup-ronde onder id 132, de stand van "
     "twee seizoenen en één wedstrijdcontext, zonder een enkele fout.",
     status="onderhoudspagina")

hist("the_odds_api",
     "9 nov (run A): OK, maar niet gebruikt. `api_check.py`: 30 actieve voetbalcompetities, quota "
     "19.444 over en 556 verbruikt deze maand, 21 van de 34 sportkeys van de repo actief. "
     "ER IS NUL CREDIT UITGEGEVEN en dat is geen plafondkwestie: `suggest_cap(19444, 22)` geeft "
     "441 credits, het ruimste plafond van de maand, en `split_budget(441, 0)` geeft (0, 0) omdat "
     "er NUL inkoopbare competitie in de run zit. De enige competitie die speelt is de FA Cup, en "
     "`soccer_england_fa_cup` staat niet bij de 21 actieve keys. "
     "DE MARKTBALANS-CONTROLE VAN §1a SLAAGT DAARMEE NIET — nul competities met een "
     "doelpuntenmarkt en nul met een uitkomstmarkt — en §1a schrijft voor dat je dan meldt dat "
     "het plafond te krap is voor de runlijst. DAT IS HIER DE OORZAAK NIET, en dat onderscheid is "
     "het hele punt van die controle: ze bestaat om te zien wanneer een scheve uitkomst uit de "
     "portemonnee komt in plaats van uit de data. Vandaag komt ze uit de kalender. "
     "Dertien van de 34 sportkeys staan vandaag op NIET ACTIEF, waaronder negen die normaal wel "
     "draaien (Belgian Pro League, Primeira Liga, Süper Lig, Danish Superliga, Ekstraklasa, "
     "Coppa Italia, Swiss Super League, Allsvenskan, MLS) plus de Conference League. Dat is het "
     "interlandvenster en geen storing: The Odds API zet een key op inactief zolang er geen "
     "wedstrijden zijn.",
     status="ok")

hist("fotmob",
     "9 nov (run A): OK, en vandaag de ENIGE bron die iets heeft geleverd. Twee daglijsten "
     "(9 nov: 36 competities / 57 duels; 10 nov: 34 / 76), de FA Cup onder `primaryId` 132, de "
     "stand van de Premier League voor 2025/2026 en 2026/2027 als bekerbasis, en één "
     "wedstrijdcontext. Geen enkele fout. "
     "WAT FOTMOB NIET HEEFT, en dat is hier de bepalende waarneming: géén selectiewaarde voor "
     "Plymouth Parkway en Berkhamsted. `squad_value` 0, `out_value` 0, `team_id` 0, `lineup_type` "
     "leeg. Vorm (WLWLW / WWLDD), rustdagen (6,0 / 9,2) en stadion (Manadon Sports Hub, het "
     "eigen veld, niet verplaatst) komen er wél uit. Bij clubs op het achtste niveau is dat te "
     "verwachten, en het is de reden dat `ctxlog.py collect` vandaag nul rijen toevoegt: "
     "`out_share` = out/(basis+out) geeft `None` bij een nulnoemer, en een nul boeken waar niets "
     "is gemeten zou precies de fout zijn die §1c verbiedt.",
     status="ok")

hist("betexplorer",
     "9 nov (run A): OK, en voor het eerst in deze reeks de ENIGE prijsbron. "
     "`fetch_league_fixtures` op /england/fa-cup/ geeft één rij met koersen over zestien boeken: "
     "Plymouth Parkway 2,07 / gelijk 3,63 / Berkhamsted 3,09. Dat is het marktgemiddelde en niet "
     "de beste prijs; met `tier = NONE` is er geen `my_prob` om ertegen af te zetten, dus het is "
     "hier boekhouding en geen meting (§1a: gemiddelde om te meten, beste prijs om te spelen). "
     "De fixturepagina's van de andere vier bekers zijn ook gelezen, als TWEEDE bron naast de "
     "Fotmob-daglijst, en ze bevestigen dat er niets te spelen is: League Cup 4 teamparen met de "
     "eerstvolgende ronde op 15 dec, Coppa Italia 8 op 1 dec, KNVB Beker 16 op 1 dec, DFB Pokal "
     "8 op 1 dec. Twee bronnen, hetzelfde antwoord — en dat is de controle die Run A op "
     "6 oktober 2026 vijf duels kostte toen ze er niet was.",
     status="ok")

hist("settling_klokterugval",
     "9 nov (run A): NIET OPNIEUW VOORGEKOMEN. Gisteren vond Stage 0 een stille faalstand — de "
     "pick van 7 nov op Nacional – Academico Viseu werd op de klokterugval van 2 uur als "
     "afwikkelbaar aangeboden terwijl de wedstrijd een dag was opgeschoven. Die pick is vandaag "
     "op de gecorrigeerde aftrap gewoon afgewikkeld (1-0, Over 2.25 verloren), en alle elf de "
     "openstaande picks van vandaag kwamen met `bron meldt afgelopen` plus uitslag binnen, dus "
     "geen van de elf leunde op de terugval. Het onderliggende gat blijft bestaan en staat nog "
     "als `gat`: valt de bron weg, dan is 2 uur na de aftrap nog steeds het antwoord, en bij een "
     "verschoven wedstrijd is dat het verkeerde antwoord.",
     status="gat")

hist("poort_9_doelpunten_onder",
     "9 nov (run A): DE REEKS HAALT DE ~30 VAN §6d EN STAAT OP 41 AFGEWIKKELDE GEVALLEN — 15 "
     "winnaars, 36,6% trefkans, −12,92u, −31,5% rendement. Dat is de meting waar het besluit van "
     "12 oktober om vroeg ('twee hoeft nog niet op de zwakke data; eerst kijken wat deze rem "
     "doet'), en ze is nu voor het eerst leesbaar. "
     "DE REM DOET ZIJN WERK: de reeks is sterk NEGATIEF, dus poort 9 houdt verliezers tegen en "
     "bespaart geld. §1h noemt twee aanleidingen om de vraag opnieuw voor te leggen — de reeks "
     "DRAAIT VAN TEKEN bij voldoende gevallen, of de vormfout van §6g is gerepareerd. Geen van "
     "beide is gebeurd: het teken is niet gedraaid maar bevestigd, en keuze (a) is op 28 oktober "
     "gemeten en afgewezen. ER WORDT DUS NIETS VOORGELEGD EN NIETS VERZET. Dit staat hier als "
     "boekhouding, zoals §1h punt 3 voorschrijft ('noem de stand van die reeks gewoon in het "
     "runrapport'), en niet als besluit.",
     status="reeks_leesbaar_rem_werkt")

hist("max_deep_analyses",
     "9 nov (run A): DE RUIMSTE MARGE VAN DE REEKS, en de spiegel van gisteren. Eén wedstrijd in "
     "het inzetvenster op een maandagcap van 40 (`ranking.max_deep_analyses`), dus 39 plekken "
     "over en nul afgekapt. Gisteren kwamen 55 duels uit op een zondagcap van 55: nul marge. "
     "Datarijkdom liep vandaag van 3,5 tot 3,5 — één duel, dus de laagste die het haalde en de "
     "hoogste die afviel zijn beide leeg. De cap is een TIJDSgrens en geen creditgrens (§0), en "
     "vandaag bindt geen van beide.",
     status="nul_duels_in_de_cap")

h["updated"] = "2026-11-09"
h["last_run"] = {
    "run": "A",
    "date": "2026-11-09",
    "note": (
        "HET INTERLANDVENSTER IS BEGONNEN EN TWINTIG VAN DE EENENTWINTIG COMPETITIES VAN DE "
        "RUNLIJST SPELEN NIET. Er is precies ÉÉN wedstrijd in het inzetvenster: FA Cup, Plymouth "
        "Parkway – Berkhamsted, 20:30 NL. Dat is `GEEN WEDSTRIJD` en geen storing (§5), en het is "
        "bij TWEE bronnen nagetrokken: de Fotmob-daglijst geeft voor League Cup (133), DFB Pokal "
        "(209) en KNVB Beker (235) nul duels in het venster, en BetExplorer noemt de "
        "eerstvolgende ronde erbij (Coppa Italia 1 dec, KNVB Beker 1 dec, DFB Pokal 1 dec, "
        "League Cup 15 dec). "
        "DAT ENE DUEL KOMT OP `data_tier = NONE` UIT, en dat is een gemeten antwoord. In een "
        "beker ligt de basis per WEDSTRIJD (§4, 15 sep 2026): `shared_lower_division` loopt de "
        "`TIER2`-keten onder de Premier League af — één schakel, de Championship — en geen van "
        "beide ploegen staat daarin. Beide spelen op het ACHTSTE niveau van Engeland, in twee "
        "verschillende groepen van de Southern League Premier Division, dus er is niet alleen "
        "geen gemeten divisiefactor maar ook geen gedeelde divisie. Een gepoolde factor erop "
        "zetten zou het gat dichten met een getal zonder onderbouwing (§2, §4). NUL BETS, en dat "
        "is de uitkomst van de kalender en niet van een poort: er is geen enkele selectie "
        "doorgerekend die een poort kon halen of missen. "
        "NUL CREDITS UITGEGEVEN op een plafond van 441, en DE MARKTBALANS-CONTROLE VAN §1a "
        "SLAAGT NIET: nul competities met een doelpuntenmarkt en nul met een uitkomstmarkt. De "
        "oorzaak is niet het plafond maar dat `soccer_england_fa_cup` niet bij de 21 actieve "
        "sportkeys staat. Wat er gratis wél is: het BetExplorer-marktgemiddelde over zestien "
        "boeken (2,07 / 3,63 / 3,09). "
        "DE ACHTDAAGSE UNDERSTAT-STORING IS GEDIAGNOSTICEERD en het is niet wat er acht dagen "
        "stond: de 26.719 bytes zijn Understats EIGEN ONDERHOUDSPAGINA, 'We will come back soon', "
        "HTTP 200 van nginx, geen Cloudflare en geen verhuisde route. Vandaag kost dat nul duels "
        "(geen van de vijf competities speelt). "
        "AFWIKKELING: 11 picks van 7 en 8 november, 5 gewonnen en 6 verloren, plus 70 "
        "schaduwrijen (28 gewonnen, 41 verloren, 1 void). ZES VERLIEZERS IS DE GRENS WAARBOVEN §7 "
        "ervan wil horen, dus het staat in de notificatie — maar elf picks op één dag is geen "
        "reeks (§6d) en er is niets op aangepast. Drie van de zes verliezers stonden op de "
        "Under-kant, de kant waarvan §6g de scheefstand al meet. "
        "DE POORT-9-REEKS (`doelpunten_onder`) HAALT DE ~30 EN STAAT OP 41 GEVALLEN MET −31,5% — "
        "de rem doet zijn werk, het teken is niet gedraaid, en er wordt dus niets voorgelegd en "
        "niets verzet (§1h punt 3). `recalibrate.load_fit().fitted_through` staat op 2026-11-08, "
        "de vorige rundag, zoals §6b-5c eist."
    ),
    "matches_in_window": 1,
    "analysed": 0,
    "truncated": 0,
    "truncated_cost_real_analyses": 0,
    "bets": 0,
    "qualified_not_published": 0,
    "credits": "0 van een plafond van 441 (nul inkoopbare competities); 19.444 over",
    "samenvatting": ("0 bets: interlandvenster, 1 duel in het venster en dat op NONE "
                     "(non-league tegen non-league); Understat-storing eindelijk "
                     "gediagnosticeerd als onderhoudspagina"),
}
json.dump(h, open(H, "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt:", len(S), "bronnen")
