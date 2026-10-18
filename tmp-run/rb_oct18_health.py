"""Run B, 18 okt 2026 — bronprobe voor source-health.json.

45 duels over veertien competities. Beide bronkanten zijn deze run werkelijk gebruikt — Fotmob
voor de standen, de context, de daglijsten, de marktvorm- en voorbeschouwingsblokken; The Odds
API voor negen bulk-aanroepen en 23 BTTS-aanroepen; BetExplorer voor het gratis
1X2-marktgemiddelde en voor de bevestiging door een tweede bron op alle zeventien competities —
dus de statusregels komen hier uit echte aanroepen en niet uit een probe.
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
     "18 okt (run B): daglijsten 18 en 19 okt opgehaald (238 competities, 690 duels samen); "
     "idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode "
     "0), ook voor de drie competities van deze runlijst die vandaag niet spelen. Standen van "
     "alle veertien spelende competities geleverd — negen met xG (Greek Super League 135, "
     "Eliteserien 59, Allsvenskan 67, Segunda División 140, Serie B 86, 2. Bundesliga 146, "
     "Austrian Bundesliga 38, MLS 130, Série A BRA 268) en vijf zonder (Czech First League 122, "
     "Croatian HNL 252, Hungarian NB I 212, Romanian SuperLiga 189, Keuken Kampioen Divisie 111) "
     "— en context opgehaald voor alle 45 duels in het inzetvenster, ook de 5 op tier NONE; de "
     "cap kapte vandaag niets af. Stadioncontrole: NUL alarmen op 45 duels. Geen enkel duel had "
     "om 05:15 NL een bevestigde opstelling (alle 45 op lineupType = lastStarting11), dezelfde "
     "klokbevinding als de voorgaande weken. NIEUW GEMETEN EN HET VERDIENT EEN REGEL: voor AD "
     "Ceuta FC, Eldense en Sabadell geeft Fotmob squad_value = 0 bij een wel gevulde "
     "uitvallerslijst, dus het beschikbaarheidsverschil is daar niet te berekenen. context.check "
     "gaat dan terecht open (hij eist squad_value > 0 aan beide kanten) maar ctxlog.out_share "
     "geeft None, waardoor het contextlogboek 42 van de 45 rijen kreeg. Geen van de drie werd een "
     "gepubliceerde bet. Ook geleverd: de marktvorm-blokken van alle 40 doorgerekende duels "
     "(§6b-5h, voor het eerst in de pipeline in plaats van als naschrift) en de "
     "voorbeschouwingsblokken van alle vijf de gepubliceerde bets.")

note("the_odds_api", "ok",
     "18 okt (run B): api_check.py meldt 49 actieve voetbalcompetities en een quotum van 19.181 "
     "over / 819 verbruikt deze maand. Negen van de veertien spelende competities hebben een "
     "sportkey en kregen alle negen de bulk-aanroep (h2h + spreads + totals, 3 credits per stuk, "
     "27 totaal): Greek Super League 12 events, Eliteserien 7, Allsvenskan 12, Segunda División "
     "12, Serie B 11, 2. Bundesliga 9, Austrian Bundesliga 9, MLS 20, Série A BRA 15. Daarna 23 "
     "BTTS-aanroepen à 1 credit voor 23 van de 26 duels met een kandidaat-edge; de drie die er "
     "geen kregen spelen in een competitie zónder sportkey. Totaal 50 van een plafond van 684, "
     "19.131 over. Marktbalans: negen van de negen inkoopbare competities kregen álle zes de "
     "markten. Pinnacle leverde 1X2 voor 29 duels (marge 2,8 tot 4,3%) en totalen voor 64 events; "
     "Matchbook en Betfair zaten in de respons en drie van de vijf gepubliceerde koersen staan op "
     "Matchbook, met net_price toegepast. Geen enkele aanroep faalde.")

note("betexplorer", "ok",
     "18 okt (run B): fetch_league_fixtures voor alle zeventien competities van de runlijst, "
     "inclusief de drie die vandaag niet spelen. Gratis 1X2-marktgemiddelde voor alle veertien "
     "spelende competities (3 tot 17 rijen per competitie, 45 duels gedekt) en de bevestiging "
     "door een tweede bron: 17 van 17 competities eens met Fotmob, 45 duels tegen 45, en per "
     "competitie gelijk — ook de nullen van Swiss Super League, English League One en English "
     "League Two. Geen HTTP-fout, geen lege respons, geen verhuisde slug. De is_today-vlag is "
     "zoals sinds 7 okt genegeerd in de exacte naamkoppeling en sinds 17 okt ook in de soepele "
     "terugval; vandaag gaf dat geen enkel duel zonder marktgemiddelde.")

note("understat", "n/a",
     "18 okt (run B): niet aangeroepen en dat is geen storing. Understat dekt alleen Premier "
     "League, La Liga, Bundesliga, Serie A en Ligue 1 en geen van die vijf staat op de runlijst "
     "van Run B. Voor deze runlijst is Fotmob dus de enige xG-bron, en dat is precies waarom §3 "
     "voorschrijft dat een omgevallen Fotmob vooraan in de notificatie hoort.")

note("api_football", "plan_limited",
     "18 okt (run B): API_FOOTBALL_KEY niet gezet. Dat is het besluit van de gebruiker van 27 sep "
     "2026 en geen storing; api_check.py meldt het en dringt er niet op aan. Boekhouding, geen "
     "actiepunt.")

H["last_run"] = {"date": "2026-10-18", "run": "B", "checked_at": now,
                 "summary": ("45 duels in het inzetvenster over 14 van de 17 competities, 0 "
                             "afgekapt (cap 55), 5 gepubliceerde regels — alle vijf een Under op "
                             "FULL-data. Alle bronnen ok; geen sleutel afgewezen.")}
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt")
