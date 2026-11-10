"""Run A, 10 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Vier dingen die hier vastgelegd moeten worden en die een volgende run anders opnieuw moet
uitzoeken:

1. **De runlijst is vandaag VOLLEDIG leeg** — nul van 21, waar het gisteren één van 21 was. Bij
   twee bronnen nagetrokken.
2. **De Understat-storing loopt door op dag negen**, met exact dezelfde respons als de
   onderhoudspagina die op 9 november is gediagnosticeerd. Geen nieuwe diagnose nodig.
3. **De bevinding van deze run is een FOUT in het runrapport van gisteren**: de Copa del Rey
   staat niet in de runlijst van Run B, en het punt is daarmee ten onrechte doorgeschoven.
4. **Nul credits uitgegeven en de marktbalans-controle van §1a slaagt niet** — en vandaag komt
   dat van een lege kalender, niet van een krap plafond.
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
    S[key]["last_checked"] = "2026-11-10"
    if status:
        S[key]["status"] = status
    if role:
        S[key]["role"] = role


hist("understat",
     "10 nov (run A): NEGENDE dag onbruikbaar, en de diagnose van gisteren houdt stand zonder "
     "dat er iets bij te zoeken valt. Alle vijf de competitiecodes (EPL, La_liga, Bundesliga, "
     "Serie_A, Ligue_1) geven opnieuw `UnderstatError: geen JSON terug van "
     "https://understat.com/getLeagueData/<code>/2025 (26719 bytes)` — EXACT hetzelfde aantal "
     "bytes als de acht dagen ervoor, en dat is precies wat een statische onderhoudspagina doet. "
     "GEEN NIEUWE MEETPOGING GEDAAN EN DAT IS MET OPZET. Op 9 november is die respons uitgepakt "
     "en bleek het Understats EIGEN onderhoudspagina te zijn (`<title>Understat.com</title>`, "
     "'We will come back soon', HTTP 200 van nginx/1.24.0, geen Cloudflare, geen verhuisde "
     "route). Er is dus niets om langs te werken (§3, 'Niet doen'), en een tiende meting van "
     "dezelfde 26.719 bytes voegt niets toe. Hij komt terug als de beheerder hem terugzet; de "
     "dagcache van `understat.fetch_league` pakt dat automatisch op. "
     "WAT HET VANDAAG KOST: NIETS, en voor de tweede dag op rij om dezelfde reden. Geen van de "
     "vijf Understat-competities speelt vandaag — het interlandvenster — en er is geen enkele "
     "doorgerekende wedstrijd die een `p_xg_understat`-arm had kunnen krijgen. Gisteren nul van "
     "nul, vandaag nul van nul; op 8 november kostte het nog 24 van de 55 duels hun tweede "
     "xG-arm. "
     "WAT HET WEL BLIJFT KOSTEN: de REDUNDANTIE waarvoor Understat op 31 augustus is toegevoegd. "
     "Fotmob is nu voor vrijwel elke competitie de enige xG-bron. §3 (27 sep 2026) schrijft voor "
     "dat de kanskant pas VOORAAN in de notificatie hoort zodra FOTMOB wegvalt; dat is niet "
     "gebeurd — Fotmob leverde vandaag twee volledige daglijsten (33 competities / 73 duels en "
     "24 / 48), drie bekerid's en alle 33 standen van `idcheck.py`, zonder één fout.",
     status="onderhoudspagina")

hist("the_odds_api",
     "10 nov (run A): OK, en voor de tweede dag op rij niet gebruikt. `api_check.py`: 42 actieve "
     "voetbalcompetities, quota 19.438 over en 562 verbruikt deze maand, 31 van de 34 sportkeys "
     "van de repo actief. GEEN ENKELE SLEUTEL IS AFGEWEZEN. "
     "DRIE SPORTKEYS STAAN OP NIET ACTIEF: Coppa Italia, Eliteserien (NOR) en de Conference "
     "League. Dat is het interlandvenster plus een winterstop en geen storing — The Odds API zet "
     "een key op inactief zolang er geen wedstrijden zijn. Let op de beweging: gisteren stonden "
     "er dertien van de 34 op inactief en waren er 30 actieve competities, vandaag drie en 42. "
     "De markt loopt dus al weer op terwijl de clubcompetities nog stilliggen; dat zijn de "
     "interlands zelf, die in geen van de drie runlijsten van vandaag zitten (Run C draait niet "
     "dagelijks, §9 besluit 2). "
     "ER IS NUL CREDIT UITGEGEVEN en dat is geen plafondkwestie: `suggest_cap(19438, 21)` geeft "
     "462 credits — RUIMER dan de 441 van gisteren — en `split_budget(462, 0)` geeft (0, 0) omdat "
     "er nul inkoopbare competitie in de run zit. "
     "DE MARKTBALANS-CONTROLE VAN §1a SLAAGT DAARMEE NIET: nul competities met een "
     "doelpuntenmarkt en nul met een uitkomstmarkt. §1a schrijft voor dat je dan meldt dat het "
     "plafond te krap is voor de runlijst; DAT IS HIER DE OORZAAK NIET. Dat onderscheid is het "
     "hele punt van die controle: ze bestaat om te zien wanneer een scheve uitkomst uit de "
     "PORTEMONNEE komt in plaats van uit de data. Vandaag komt ze uit de KALENDER, en er is zelfs "
     "geen uitkomst om scheef te zijn. "
     "ZES ACTIEVE KEYS KENT DE REPO NIET (Brazil Série B, 3. Liga, Copa del Rey, Superettan, "
     "UCL Women, Nations League). Daarvan valt er GEEN ENKELE binnen een runlijst — zie "
     "`copa_del_rey_buiten_alle_runlijsten` hieronder, want het runrapport van gisteren zei iets "
     "anders.",
     status="ok")

hist("fotmob",
     "10 nov (run A): OK, en opnieuw de enige bron die iets inhoudelijks heeft geleverd. Twee "
     "daglijsten (10 nov: 33 competities / 73 duels; 11 nov: 24 / 48), de drie bekerid's uit de "
     "daglijst (League Cup 133, DFB Pokal 209, KNVB Beker 235) en alle 33 standen van "
     "`scripts/idcheck.py` groen. Geen enkele fout. "
     "DAT DE BRON LEVERT IS HIER DE BEPALENDE WAARNEMING, want ze onderscheidt een lege runlijst "
     "van een omgevallen bron. Er staan 73 wedstrijden in de daglijst van vandaag — zeven Copa "
     "del Rey, veertien groepsduels EFL Trophy, de Engelse zesde en zevende niveaus, de Women's "
     "Champions League, Liga II (ROU) en vijf Zuid-Amerikaanse competities — en geen enkele "
     "daarvan staat in de runlijst van Run A. Was Fotmob omgevallen, dan had de daglijst leeg "
     "geweest en niet vol.",
     status="ok")

hist("betexplorer",
     "10 nov (run A): OK, en vandaag UITSLUITEND als tweede bron voor de bekerronde — geen "
     "enkele koers opgehaald. De vijf fixturepagina's zijn gelezen en bevestigen de "
     "Fotmob-daglijst, met de eerstvolgende ronde erbij: FA Cup 20 teamparen / 5 dec, League Cup "
     "4 / 15 dec, Coppa Italia 8 / 1 dec, KNVB Beker 16 / 1 dec, DFB Pokal 8 / 1 dec. Twee "
     "bronnen, hetzelfde antwoord, en bij alle vijf een datum die het antwoord verklaart. "
     "DAT IS DE CONTROLE DIE RUN A OP 6 OKTOBER 2026 VIJF DUELS KOSTTE toen ze er niet was: de "
     "FA Cup-kwalificatie stond toen niet in de Fotmob-daglijst en wel bij BetExplorer. 'Niet in "
     "de daglijst' mag nooit als `GEEN WEDSTRIJD` worden opgeschreven zonder tweede bron. "
     "Anders dan gisteren is er geen marktgemiddelde gelezen: dat gaat per wedstrijd en er is "
     "geen wedstrijd. Een fixturepagina is een kalender, geen koers.",
     status="ok")

hist("copa_del_rey_buiten_alle_runlijsten",
     "10 nov (run A): RECHTGEZET, en dit is de bevinding van deze run. "
     "`runs/2026-11-09-run-a.md` schrijft: 'daarvan valt alleen de Copa del Rey binnen een "
     "runlijst (Run B), en die speelt 10 november — dat is een punt voor Run B en niet voor deze "
     "run.' DAT IS ONWAAR. `prompts/run-b.md` noemt zeventien competities en geen enkele beker; "
     "`grep -i copa prompts/run-a.md prompts/run-b.md prompts/run-c.md` geeft nul treffers. Het "
     "rapport van 8 NOVEMBER had het wél goed ('de Copa del Rey staat niet in run-a.md, "
     "run-b.md of run-c.md') en die juiste formulering is op 9 november vervangen door een "
     "onjuiste. "
     "DIT IS DE FAALVORM WAARVOOR §4 BIJ DE GEPOOLDE PROMOTIEFACTOR WAARSCHUWT: een "
     "samenvattende zin die onwaar is en ongemerkt wordt overgenomen. Daar duurde het drie "
     "runrapporten; hier is het binnen één dag gevonden, en wel doordat de Copa del Rey vandaag "
     "ECHT speelt. "
     "WAT HET GEVOLG WAS GEWEEST: het punt is doorgeschoven naar een run die het niet in zijn "
     "opdracht heeft. Run B van 10 november zou vandaag naar de Copa del Rey hebben gekeken, hem "
     "niet in zijn eigen runlijst hebben gevonden en het punt hebben teruggelegd — of, erger, hem "
     "hebben toegevoegd, terwijl `prompts/run-a.md` met zoveel woorden zegt 'niets toevoegen of "
     "raden'. "
     "DE STAND: zeven Copa del Rey-duels in het inzetvenster van vandaag, `soccer_spain_copa_del_"
     "rey` actief bij The Odds API, geen `fotmob_id` in `coverage.json`, en geen van de drie "
     "runlijsten die hem dekt. Openstaand sinds 1 november. EEN RUN VOEGT GEEN COMPETITIE TOE — "
     "dat is een besluit van de gebruiker (§1a, §1e, §6g), en het staat als één punt met "
     "`owner = besluit` in het dagrapport. Het wordt niet elke dag opnieuw gesteld (§9 besluit 3).",
     status="onwaarheid_rechtgezet")

hist("max_deep_analyses",
     "10 nov (run A): NUL WEDSTRIJDEN OP EEN DINSDAGCAP VAN 40, dus alle veertig plekken over en "
     "nul afgekapt. Dat is nog een stap ruimer dan gisteren (één duel op 40) en de spiegel van "
     "8 november, toen 55 duels op een zondagcap van 55 uitkwamen — nul marge. "
     "DE TWEE GETALLEN DIE §3 STAGE 4 EIST BESTAAN VANDAAG NIET: de datarijkdom van de laagste "
     "wedstrijd die het nog haalde en van de hoogste die afviel. Dat is iets anders dan nul — een "
     "lijst van nul heeft geen onderkant — en het hoort zo te worden opgeschreven in plaats van "
     "met twee nullen te worden gevuld. De cap is een TIJDSgrens en geen creditgrens (§0); "
     "vandaag bindt geen van beide.",
     status="nul_duels_in_de_cap")

hist("poort_9_doelpunten_onder",
     "10 nov (run A): ONVERANDERD op 41 afgewikkelde gevallen — 15 winnaars, 36,6% trefkans, "
     "−12,92u, −31,5% rendement. Er is vandaag geen kandidaat bij gekomen, want er is geen "
     "wedstrijd doorgerekend. "
     "DE REM DOET ZIJN WERK en het teken is niet gedraaid. §1h noemt twee aanleidingen om de "
     "vraag opnieuw voor te leggen — de reeks draait van teken, of de vormfout van §6g is "
     "gerepareerd — en geen van beide is ingetreden (keuze (a) is op 28 oktober gemeten en "
     "afgewezen). ER WORDT DUS NIETS VOORGELEGD EN NIETS VERZET; dit staat hier als boekhouding, "
     "zoals §1h punt 3 voorschrijft. "
     "WAT ER WEL BEWEEGT, IS DE OORZAAKKANT: `margins.py goalbias` zet de regel 'Under gespeeld' "
     "vandaag op 136 duels met +0,658 doelpunt per duel en z = +4,62, de hoogste z van deze reeks. "
     "De scheefstand die poort 9 afdekt is dus niet kleiner geworden. De niveaucorrectie "
     "`model.LEVEL_SCALE` = 1.032 bindt sinds 3 november en `gridfit.py measure` meldt zelf dat "
     "263 van de 1436 duels haar al in zich dragen — te weinig om te zien wat ze doet (§6d).",
     status="reeks_leesbaar_rem_werkt")

h["updated"] = "2026-11-10"
h["last_run"] = {
    "run": "A",
    "date": "2026-11-10",
    "note": (
        "DE RUNLIJST IS VANDAAG VOLLEDIG LEEG: EENENTWINTIG VAN DE EENENTWINTIG COMPETITIES EN "
        "TOERNOOIEN HEBBEN GEEN WEDSTRIJD IN HET INZETVENSTER [08:00 NL 10 nov, 08:00 NL "
        "11 nov). Gisteren was er nog één duel (FA Cup, op `NONE`); vandaag nul. Dat is "
        "`GEEN WEDSTRIJD` en geen storing (§5, Stage 2): het FIFA-interlandvenster van november "
        "loopt, dus de dertien clubcompetities liggen stil, de drie Europese toernooien spelen "
        "niet en de vijf bekers hebben hun eerstvolgende ronde pas in december. "
        "BIJ TWEE BRONNEN NAGETROKKEN. De Fotmob-daglijst geeft voor alle zestien gefilterde "
        "id's nul duels en voor de drie bekers met een id (League Cup 133, DFB Pokal 209, KNVB "
        "Beker 235) ook nul; BetExplorer noemt de eerstvolgende ronde erbij voor alle vijf de "
        "bekers (FA Cup 5 dec, League Cup 15 dec, Coppa Italia 1 dec, KNVB Beker 1 dec, DFB "
        "Pokal 1 dec). Twee bronnen, hetzelfde antwoord. "
        "DE BRON LEVERT WEL, en dat onderscheidt dit van een storing: er staan 73 wedstrijden in "
        "de daglijst van vandaag, verdeeld over 33 competities. Er speelt volop voetbal, het "
        "staat alleen niet in deze runlijst. "
        "NUL BETS, EN DAT IS DE UITKOMST VAN DE KALENDER EN NIET VAN EEN POORT: er is geen enkele "
        "selectie doorgerekend die een poort kon halen of missen. Nul near_miss-rijen, nul "
        "schaduwrijen, nul kalibratierijen, nul contextrijen, nul regels in beide dagranglijsten "
        "van §5a en nul voorbeschouwingen — bij een lege runlijst het juiste antwoord. "
        "`progress.py verify` is groen. "
        "NUL CREDITS UITGEGEVEN op een plafond van 462 (ruimer dan de 441 van gisteren), en DE "
        "MARKTBALANS-CONTROLE VAN §1a SLAAGT NIET: nul competities met een doelpuntenmarkt en nul "
        "met een uitkomstmarkt. De oorzaak is niet het plafond maar de kalender. Geen enkele "
        "sleutel is afgewezen; `API_FOOTBALL_KEY` ontbreekt met opzet (besluit 27 sep 2026, geen "
        "gat en geen actiepunt). "
        "AFWIKKELING: GEEN ENKELE ECHTE PICK STOND OPEN. Twee schaduwrijen van Run B van "
        "9 november zijn afgewikkeld — Botosani – Otelul Galati 1-1 (1X2 thuiszege, poort 5, "
        "VERLOREN) en Sabadell – Real Sociedad B 0-0 (AH +1 op de uitploeg, poort 8, GEWONNEN). "
        "In BEIDE duels vielen er minder doelpunten dan voorgerekend (2 tegen 2,64 en 0 tegen "
        "2,70); twee rijen zijn geen reeks (§6d) en er is niets op aangepast. "
        "DE BEVINDING VAN DEZE RUN IS EEN FOUT IN HET RUNRAPPORT VAN GISTEREN. Dat schreef dat de "
        "Copa del Rey 'binnen een runlijst (Run B)' valt; dat is onwaar — hij staat in geen van "
        "de drie runlijsten, en het rapport van 8 november had dat nog goed. Het punt was daarmee "
        "doorgeschoven naar een run die het niet in zijn opdracht heeft, op precies de dag dat de "
        "Copa del Rey zeven duels speelt. Rechtgezet; toevoegen is een besluit van de gebruiker "
        "en geen handeling van een run. "
        "UNDERSTAT LIGT ER NEGEN DAGEN UIT, met dezelfde 26.719 bytes als de acht dagen ervoor — "
        "op 9 november gediagnosticeerd als Understats eigen onderhoudspagina. Kost vandaag nul "
        "duels. Fotmob levert, dus §2 blijft gedekt en de uitzonderingsregel van §3 punt 3 is "
        "niet in beeld. "
        "`recalibrate.load_fit().fitted_through` staat op 2026-11-09, de vorige rundag, zoals "
        "§6b-5c eist."
    ),
    "matches_in_window": 0,
    "analysed": 0,
    "truncated": 0,
    "truncated_cost_real_analyses": 0,
    "bets": 0,
    "qualified_not_published": 0,
    "credits": "0 van een plafond van 462 (nul inkoopbare competities); 19.438 over",
    "samenvatting": ("0 bets: het interlandvenster legt de hele runlijst stil — 21 van 21 op "
                     "GEEN WEDSTRIJD, bij twee bronnen nagetrokken; bevinding: de Copa del Rey "
                     "staat in geen enkele runlijst, anders dan het rapport van gisteren schreef"),
}
json.dump(h, open(H, "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt:", len(S), "bronnen")
