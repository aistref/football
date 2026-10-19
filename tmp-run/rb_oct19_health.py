"""Run B, 19 okt 2026 — bronprobe voor source-health.json.

Acht duels over vijf competities: de kleinste Run B-lijst van de maand, en dat hoort bij een
maandag. Beide bronkanten zijn deze run werkelijk gebruikt — Fotmob voor de standen, de context,
de daglijsten, de marktvorm- en voorbeschouwingsblokken; The Odds API voor drie bulk-aanroepen en
twee BTTS-aanroepen; BetExplorer voor het gratis 1X2-marktgemiddelde en voor de bevestiging door
een tweede bron op alle zeventien competities — dus de statusregels komen hier uit echte
aanroepen en niet uit een probe.
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
     "19 okt (run B): daglijsten 19 en 20 okt opgehaald (111 competities, 272 duels samen); "
     "idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode "
     "0), ook voor de twaalf competities van deze runlijst die vandaag niet spelen — en juist "
     "daar moet die controle kijken, want een fout id geeft nul wedstrijden en dat leest als GEEN "
     "WEDSTRIJD. Standen van alle vijf spelende competities geleverd — drie met xG (Allsvenskan "
     "67, Segunda División 140, Série A BRA 268) en twee zonder (Romanian SuperLiga 189, Keuken "
     "Kampioen Divisie 111) — en context opgehaald voor alle 8 duels in het inzetvenster; de cap "
     "(40 op maandag) kapte niets af. Stadioncontrole: NUL alarmen op 8 duels. Geen enkel duel "
     "had om 05:10 NL een bevestigde opstelling (alle 8 op lineupType = lastStarting11), dezelfde "
     "klokbevinding als de voorgaande weken. DE SQUAD_VALUE-LACUNE VAN 18 OKT KOMT HIER TERUG EN "
     "IS VANDAAG GROTER: vier van de acht duels hebben aan minstens één kant squad_value = 0 — de "
     "drie beloftenelftallen van de Keuken Kampioen Divisie (Jong Ajax, Jong FC Utrecht, Jong "
     "PSV) en Celta Fortuna. context.check gaat daar terecht open (hij eist squad_value > 0 aan "
     "beide kanten) maar ctxlog.out_share geeft None, dus het contextlogboek kreeg 4 van de 8 "
     "rijen. Geen van de vier werd een gepubliceerde bet. Ook geleverd: de marktvorm-blokken van "
     "alle 8 doorgerekende duels (§6b-5h, nul fouten) en het voorbeschouwingsblok van de enige "
     "gepubliceerde bet.")

note("the_odds_api", "ok",
     "19 okt (run B): api_check.py meldt 49 actieve voetbalcompetities en een quotum van 19.102 "
     "over / 898 verbruikt deze maand. Drie van de vijf spelende competities hebben een sportkey "
     "en kregen alle drie de bulk-aanroep (h2h + spreads + totals, 3 credits per stuk, 9 totaal): "
     "Allsvenskan 9 events, Segunda División 11, Série A BRA 16. Daarna 2 BTTS-aanroepen à 1 "
     "credit voor 2 van de 3 duels met een kandidaat-edge; het derde (Jong PSV – FC Dordrecht) "
     "speelt in een competitie zónder sportkey. Totaal 11 van een plafond van 733, 19.091 over. "
     "Marktbalans: drie van de drie inkoopbare competities kregen álle zes de markten. Pinnacle "
     "leverde 1X2 voor 25 events (marge 3,8 tot 4,8% op de drie duels van deze runlijst) en "
     "totalen voor 25 events; de gepubliceerde koers staat op Matchbook, met net_price toegepast "
     "(1,81 bruto / 1,7938 netto). Geen enkele aanroep faalde.")

note("betexplorer", "ok",
     "19 okt (run B): fetch_league_fixtures voor alle zeventien competities van de runlijst, "
     "inclusief de twaalf die vandaag niet spelen. Gratis 1X2-marktgemiddelde voor alle vijf "
     "spelende competities (9 tot 18 rijen per competitie, 8 duels gedekt) en de bevestiging door "
     "een tweede bron: 17 van 17 competities eens met Fotmob, 8 duels tegen 8, en per competitie "
     "gelijk — ook de nullen van de twaalf competities zonder speelronde. Geen HTTP-fout, geen "
     "lege respons, geen verhuisde slug; de op 16 okt gerepareerde Série A-slug levert weer "
     "gewoon rijen. De is_today-vlag is zoals sinds 7 okt genegeerd in de exacte naamkoppeling en "
     "sinds 17 okt ook in de soepele terugval; dat bond vandaag bij Corinthians – Vitória, dat om "
     "01:00 NL op 20 okt aftrapt en door BetExplorer dus niet als 'vandaag' wordt gelabeld.")

note("understat", "n/a",
     "19 okt (run B): niet aangeroepen en dat is geen storing. Understat dekt alleen Premier "
     "League, La Liga, Bundesliga, Serie A en Ligue 1 en geen van die vijf staat op de runlijst "
     "van Run B. Voor deze runlijst is Fotmob dus de enige xG-bron, en dat is precies waarom §3 "
     "voorschrijft dat een omgevallen Fotmob vooraan in de notificatie hoort.")

note("api_football", "plan_limited",
     "19 okt (run B): API_FOOTBALL_KEY niet gezet. Dat is het besluit van de gebruiker van 27 sep "
     "2026 en geen storing; api_check.py meldt het en dringt er niet op aan. Boekhouding, geen "
     "actiepunt.")

H["last_run"] = {"date": "2026-10-19", "run": "B", "checked_at": now,
                 "summary": ("8 duels in het inzetvenster over 5 van de 17 competities, 0 "
                             "afgekapt (cap 40), 1 gepubliceerde regel — een Under op "
                             "LIGHT-data, op rangorde en onder zijn eigen lat. Alle bronnen ok; "
                             "geen sleutel afgewezen.")}
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt")
