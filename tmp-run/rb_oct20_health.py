"""Run B, 20 okt 2026 — bronprobe voor source-health.json.

23 duels over twee competities: twee complete midweekse rondes van English League One en League
Two op één avond. Beide bronkanten zijn deze run werkelijk gebruikt — Fotmob voor de standen, de
context, de daglijsten, de marktvorm- en voorbeschouwingsblokken en voor de controle op de
National League; The Odds API voor twee bulk-aanroepen en veertien BTTS-aanroepen; BetExplorer
voor het gratis 1X2-marktgemiddelde en voor de bevestiging door een tweede bron op alle zeventien
competities — dus de statusregels komen hier uit echte aanroepen en niet uit een probe.
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
    print(f"{key:18} {status:8} {detail[:110]}...")


note("fotmob", "ok",
     "20 okt (run B): daglijsten 20 en 21 okt opgehaald (47 competities elk, 162 en 141 duels); "
     "idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode "
     "0), ook voor de vijftien competities van deze runlijst die vandaag niet spelen — en juist "
     "daar moet die controle kijken, want een fout id geeft nul wedstrijden en dat leest als GEEN "
     "WEDSTRIJD. Standen van beide spelende competities geleverd, allebei MET xG (English League "
     "One 108, English League Two 109; 24 ploegen en 46 speeldagen in 2025/2026, 11 speeldagen "
     "nu). Context opgehaald voor alle 23 duels in het inzetvenster, nul fouten; de cap (40 op "
     "dinsdag) kapte niets af. Stadioncontrole: NUL alarmen op 23 duels. Geen enkel duel had om "
     "05:10 NL een bevestigde opstelling (alle 23 op lineupType = lastStarting11). DE "
     "BLESSURELACUNE IS HIER HET OPVALLENDST VAN DE MAAND: van de 46 ploegen heeft er PRECIES ÉÉN "
     "een uitvallerslijst bij Fotmob, tegen 41 van de 46 met een squad_value. De blessurepoot van "
     "poort 7 kan op deze twee divisies dus vrijwel niets meten — geen storing maar de dekking "
     "van League One en League Two ruim vijftien uur voor de aftrap, en het is de reden dat poort "
     "7 vandaag nul selecties tegenhield. Ook geleverd: de marktvorm-blokken van alle 17 "
     "doorgerekende duels (§6b-5h, nul fouten) en de voorbeschouwingsblokken van alle drie de "
     "gepubliceerde bets. NIEUW NAGETROKKEN: de National League (ccode ENG, id 117) bestaat bij "
     "Fotmob en geeft per seizoen een EIGEN stand (2018/2019 24 ploegen/46 speeldagen, 2021/2022 "
     "23/44, 2024/2025 24/46, 2025/2026 24/46), dus zonder de stille faalstand van het Hongaarse "
     "id 9117. Dat maakt het paar League Two / National League meetbaar; zie het runrapport.")

note("the_odds_api", "ok",
     "20 okt (run B): api_check.py meldt 49 actieve voetbalcompetities en een quotum van 19.078 "
     "over / 922 verbruikt deze maand. Beide spelende competities hebben een sportkey en kregen "
     "de bulk-aanroep (h2h + spreads + totals, 3 credits per stuk, 6 totaal): English League One "
     "24 events, English League Two 24. Daarna 14 BTTS-aanroepen à 1 credit voor de 14 duels met "
     "een kandidaat-edge. Totaal 20 van een plafond van 866, 19.058 over. Marktbalans: twee van "
     "de twee inkoopbare competities kregen álle zes de markten — de ruimste dekking die deze "
     "runlijst kan hebben. Pinnacle leverde 1X2 voor 24 events (marge 4,4 tot 5,9%) en totalen "
     "voor 24 events; twee van de drie gepubliceerde koersen staan bij Pinnacle zelf. Geen enkele "
     "aanroep faalde en geen sleutel werd afgewezen.")

note("betexplorer", "ok",
     "20 okt (run B): fetch_league_fixtures voor alle zeventien competities van de runlijst, "
     "inclusief de vijftien die vandaag niet spelen. Gratis 1X2-marktgemiddelde voor beide "
     "spelende competities (24 en 22 rijen) en de bevestiging door een tweede bron. ZESTIEN VAN "
     "DE ZEVENTIEN COMPETITIES EENS MET FOTMOB, inclusief alle vijftien nullen. ÉÉN AFWIJKING, EN "
     "ZE IS UITGEZOCHT: de fixturepagina van English League Two toont 13 rijen als 'Today' waar "
     "Fotmob er 12 geeft. De extra rij is 'Northampton - Colchester, Today 20:00 UK', en die "
     "wedstrijd kan niet bestaan — Northampton speelt om 19:45 UK tegen Tranmere en Colchester om "
     "19:45 UK bij Chesterfield, allebei op diezelfde pagina en allebei door Fotmob bevestigd, en "
     "Fotmob kent de combinatie Northampton – Colchester op geen van beide daglijsten en in geen "
     "enkele competitie. Een rij zonder eigen datumlabel die als 'Today' leest, dus een artefact "
     "van de pagina en GEEN gemiste wedstrijd. Geen HTTP-fout, geen lege respons, geen verhuisde "
     "slug.")

note("understat", "n/a",
     "20 okt (run B): niet aangeroepen en dat is geen storing. Understat dekt alleen Premier "
     "League, La Liga, Bundesliga, Serie A en Ligue 1 en geen van die vijf staat op de runlijst "
     "van Run B. Voor deze runlijst is Fotmob dus de enige xG-bron, en dat is precies waarom §3 "
     "voorschrijft dat een omgevallen Fotmob vooraan in de notificatie hoort.")

note("api_football", "plan_limited",
     "20 okt (run B): API_FOOTBALL_KEY niet gezet. Dat is het besluit van de gebruiker van 27 sep "
     "2026 en geen storing; api_check.py meldt het en dringt er niet op aan. Boekhouding, geen "
     "actiepunt.")

H["last_run"] = {"date": "2026-10-20", "run": "B", "checked_at": now,
                 "summary": ("23 duels in het inzetvenster over 2 van de 17 competities, 0 "
                             "afgekapt (cap 40), 3 gepubliceerde regels waarvan 1 zijn eigen lat "
                             "haalt. Alle bronnen ok; geen sleutel afgewezen. Eén BetExplorer-rij "
                             "verworpen als spookwedstrijd (Northampton - Colchester).")}
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt")
