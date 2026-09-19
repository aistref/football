"""Stage 6 — vastleggen: picks.jsonl, run-state. Run B 19 sep 2026 (nul bets)."""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-19"

TOELICHTING = """Zaterdag 19 september: vijftien van de zeventien competities uit prompts/run-b.md speelden, samen 57 duels - veruit de drukste Run B-dag tot nu toe, en de eerste waarop English League One (11 duels) en English League Two (12 duels) allebei een volledige speelronde afwerken. De twee lege competities zijn Serie B (ITA), dat dit weekend niet speelt, en de Kosovo Superleague, die nog altijd helemaal niet op de Fotmob-daglijst voorkomt - ongewijzigd sinds 13 aug 2026. De cap stond op 55 (vr-zo) tegen 57 duels, dus MAX_DEEP_ANALYSES heeft deze run voor het eerst sinds lange tijd werkelijk iets gekost: 2 duels afgekapt (Debrecen - Vasas Budapest en FC Dinamo City - Laci). Allebei kwamen ze hoe dan ook op NONE uit, dus de afkapping heeft geen analyse gekost die er een had kunnen worden. De laagste datarijkdom die het nog haalde is 4,5 (Vora - Skenderbeu) en de hoogste die afviel is eveneens 4,5 (Debrecen - Vasas Budapest): de cap sneed dwars door een gelijkspel in de rangschikking, en de aftraptijd gaf de doorslag. Dat is precies het beeld dat par. 3 Stage 4 beschrijft - de datarijkdom-score scheidt niet.

Van de 57 duels kwamen er 42 door de datadekkingspoort: 24 FULL en 18 LIGHT. De vijftien op NONE vallen in drie groepen van precies vijf, en die driedeling is de bevinding van vandaag. Vijf duels stranden omdat promotion.TIER2 geen divisiepaar kent voor dat land (Griekenland, Hongarije, Oostenrijk en twee keer Albanie). Vijf duels stranden omdat de ploeg uit een divisie komt waar de TIER2-ketting niet meer bij kan: Tenerife en Eldense promoveerden naar de Segunda Division en Rochdale en York City naar League Two, en onder LaLiga2 en League Two houdt de ketting op. En vijf duels stranden op conversion_in_range - de omrekening lukte wel, maar kwam buiten het gemeten bereik uit.

Uit die 42 duels zijn 460 selecties doorgerekend over alle zes de markten, en er kwam nul bets uit. Van die 460 vielen er 438 af op de edge-poort, 17 op de koersband (MIN_ODDS/MAX_ODDS) en 5 op de herijking. Poort 5 (tweede methode), 6 (robuustheid), 7 (context) en 8 (underdog) hebben op de herijkte schaal deze run niets tegengehouden.

De dichtstbijzijnde bet is Asian Handicap Kristiansund BK +1,25 tegen Rosenborg, 1,89 bij de beste prijs. Die staat op +5,99 procentpunt herijkt tegen een drempel van 8,0 voor FULL - twee procentpunt tekort. Ruw, zonder de herijking van par. 1g, staat dezelfde selectie op +19,98 pp, en dan bindt poort 8 er wel op: Kristiansund krijgt van de markt minder dan de ondergrens van 35%. Die twee lezingen staan als twee aparte rijen in het schaduwlogboek, een near_miss op de herijkte schaal en een underdog_ruw-rij op de ruwe; shadow.py slaat de dubbeltelling zelf over.

Drie selecties werden op de ruwe schaal door poort 8 tegengehouden (Kifisia FC om te winnen bij Atromitos tegen 4,04, Kristiansund +1,25 en Bromley +1 tegen Huddersfield), en drie andere haalden alle acht poorten ruw maar niet na de herijking: Over 3.5 bij Luzern - Grasshopper (ruw +13,00 pp, herijkt -0,47), Over 2.75 bij Blackpool - Plymouth (ruw +9,57, herijkt -4,12) en Over 2.5 bij Gillingham - Bristol Rovers (ruw +8,74, herijkt -4,49). Die laatste drie gaan als zonder_herijking-rij het logboek in. Het patroon is het bekende: alle drie zijn het doelpuntenmarkten aan de Over-kant, en alle drie draait de herijking ze van ruim positief naar negatief.

De inkoop kan de uitkomst deze keer niet scheef hebben getrokken. Negen van de vijftien spelende competities hebben een sportkey bij The Odds API en die kregen alle negen de volle bulk-aanroep - 27 credits, vijf van de zes markten in een keer, 1X2 op de beste prijs. De marktbalans-controle slaagt daarmee zo ruim als hij kan: 9 van de 9 ingekochte competities hebben zowel een uitkomst- als een doelpuntenmarkt. Van de 42 doorgerekende duels staan er 32 op de beste prijs en 10 op het BetExplorer-marktgemiddelde (Tsjechie, Kroatie, Hongarije, Roemenie en de Keuken Kampioen Divisie, geen van alle in te kopen). Daar valt de edge systematisch te laag uit - conservatief, maar niet vergelijkbaar met de duels waar de beste prijs wel bekend is.

De beste prijs leverde vandaag gemiddeld +6,74% op ten opzichte van het BetExplorer-marktgemiddelde (mediaan +6,41%), over 32 duels waar beide bronnen een prijs gaven. Dat is de ruimste steekproef die deze meting tot nu toe heeft gehad en ze ligt netjes in lijn met de +7,78% van 5 sep. Waar de beste prijs bij een beurs stond (Betfair, Matchbook) is hij door oddsapi.net_price gehaald: 2% commissie over de nettowinst.

BTTS is in de tweede ronde gekocht voor alle acht duels met een kandidaat-edge, a 2 credits, samen 8 credits. Totaal 35 van een plafond van 791; 18.977 credits over.

De vroeg-seizoenscorrectie staat deze run op x1,0904, gepoold over vijftien competities en 134 speeldagen - opnieuw de ruimste steekproef die deze routine heeft gehad, doordat ook de zes competities zonder Fotmob-xG meetellen (daar op doelpunten gemeten, dezelfde eenheid als waarin die duels rekenen). De controle die par. 3 Stage 5 vraagt valt voor de tweede Run B op rij ongunstig uit, en nu over een steekproef die wel wat zegt: zonder correctie lag P(Over 2.5) gemiddeld 2,19 procentpunt onder de de-vigde marktkans, met correctie 3,42 procentpunt erboven, en de gemiddelde absolute fout loopt op van 4,29 naar 4,80 procentpunt. De correctie schiet dus door - ze haalt een onderschatting weg en zet er een overschatting van vergelijkbare omvang voor terug. Dat is gemeten over 23 wedstrijden, tegen vier op 18 sep, en daarmee is het geen ruis meer maar nog steeds een diagnose: par. 1d en par. 6e verbieden uitdrukkelijk om deze factor op de markt af te regelen. Wat het wel is, is een tweede waarneming in dezelfde richting; komt hij een derde keer terug, dan hoort early_season_uplift op uitkomsten te worden nagerekend in plaats van op de markt."""

BEVINDING = {
    "titel": ("Vijf duels op NONE doordat de conversion_in_range-poort net dichtvalt - "
              "alle vijf binnen 0,03 van het gemeten bereik"),
    "wat": (
        "Vijf van de vijftien NONE-duels van vandaag hadden een geslaagde omrekening en "
        "stranden op conversion_in_range: de omgerekende relatieve sterkte valt net buiten "
        "het bereik waarover het divisiegat is gemeten. Wat opvalt is hoe krap dat 'net' is. "
        "Girona (La Liga -> Segunda): verdediging 1,074 tegen een ondergrens van 1,078 - een "
        "verschil van 0,004. Cambridge United (League Two -> League One): 0,557 tegen 0,565, "
        "een verschil van 0,008. Port Vale en Exeter City (League One -> League Two): allebei "
        "1,008 tegen 1,033, een verschil van 0,025. Leicester City (Championship -> League "
        "One): aanval 0,968 tegen een bovengrens van 0,939, een verschil van 0,029. Alle vijf "
        "dus binnen drie honderdsten van de grens, en geen van de vijf een uitschieter zoals "
        "de Coventry-val beschrijft."),
    "is_dit_een_fout": (
        "Nee, en het is nadrukkelijk geen reden om het bereik op te rekken. conversion_in_range "
        "is een poort en geen aantekening (par. 4): buiten het waargenomen bereik is er geen "
        "meting, en 'het scheelt maar 0,004' is precies het soort redenering waarmee schijnedge "
        "binnenkomt die alle andere poorten haalt. De grens zelf is bovendien een waarneming uit "
        "een eindige steekproef (n=33 tot n=43 per paar), dus hem met de hand verschuiven is de "
        "steekproef overschrijven met een wens. Wat hier gebeurt is de regel die werkt zoals hij "
        "hoort."),
    "wat_het_kost": (
        "Vandaag vijf van de 57 duels, en dat is niet het hele verhaal: nog eens vijf duels "
        "vallen af doordat de TIER2-ketting onder LaLiga2 en League Two ophoudt (Tenerife, "
        "Eldense, Rochdale, York City) of geen paar voor dat land kent. Voor Run B weegt dat "
        "zwaarder dan voor Run A, want deze runlijst zit per definitie aan de onderkant van de "
        "ladder: waar Run A een ploeg nog een divisie omlaag kan volgen, staat Run B daar al. "
        "Wat het zou kosten om het op te lossen is een meting in de geest van 31 aug 2026: het "
        "bereik per divisiepaar over meer seizoenen opnieuw vaststellen, zodat de grenzen op "
        "meer waarnemingen rusten dan de huidige 33 a 43. Dat is werk voor een aparte sessie, "
        "niet voor een dagelijkse run - en het verruimt het bereik alleen als de data dat zegt."),
}

OMREKENINGEN = {
    "aanleiding": (
        "25 van de 57 duels hadden minstens een ploeg die niet in de stand van vorig seizoen "
        "van de eigen competitie staat, en par. 4 schrijft voor die eerst om te rekenen en pas "
        "daarna NONE te geven. Voor tien van die 25 lukte dat en kwam het duel op LIGHT uit; "
        "vijftien stranden, in drie groepen van vijf: geen divisiepaar voor dat land, een "
        "divisie onder de onderkant van de TIER2-ketting, of conversion_in_range. Zie de "
        "bevinding hierboven."),
    "geweigerd_geen_paar": [
        "Iraklis (Greek Super League) - geen divisiepaar voor Griekenland in promotion.TIER2",
        "Vasas Budapest (Hungarian NB I) - geen divisiepaar voor Hongarije",
        "Austria Lustenau (Austrian Bundesliga) - geen divisiepaar voor Oostenrijk",
        "Skenderbeu en Laci (Kategoria Superiore) - geen divisiepaar voor Albanie",
    ],
    "geweigerd_onder_de_ketting": [
        "Tenerife en Eldense - gepromoveerd naar de Segunda Division; onder LaLiga2 kent "
        "promotion.TIER2 geen divisie",
        "Rochdale en York City - gepromoveerd naar League Two; onder League Two houdt de "
        "ketting op",
        "VfL Osnabruck - staat niet in de stand van de 2. Bundesliga en evenmin in die van de "
        "Bundesliga erboven",
    ],
    "geweigerd_buiten_bereik": [
        "Girona - verdediging 1,074 tegen ondergrens 1,078 (SP1/SP2 down, n=33)",
        "Cambridge United - verdediging 0,557 tegen ondergrens 0,565 (E2/E3 up, n=43)",
        "Port Vale en Exeter City - verdediging 1,008 tegen ondergrens 1,033 (E2/E3 down, n=43)",
        "Leicester City - aanval 0,968 tegen bovengrens 0,939 (E1/E2 down, n=33)",
    ],
    "let_op": (
        "Geen van de tien geslaagde omrekeningen kwam vandaag in de buurt van een bet, en dat "
        "hoort ook zo: een omgerekende ploeg is nooit FULL, dus de drempel staat daar op 16,0 "
        "procentpunt en daar gaat de herijking van par. 1g nog overheen."),
}

CREDITBRON = (
    "suggest_cap(19012, 12) = 791 - 19.012 credits over volgens api_check.py van deze run "
    "(20K-plan, 988 gebruikt deze maand), 12 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(791, 9) gaf 9 spreads / 9 totals: negen van de vijftien spelende competities "
    "hebben een sportkey. Het plafond laat 3 credits per competitie ruimschoots toe, dus alle "
    "negen kregen de bulk-aanroep (h2h + spreads + totals, par. 1a) - vijf van de zes markten "
    "in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-marktgemiddelde. "
    "Dat leverde gemiddeld +6,74% betere koers op over de 32 duels waar beide bronnen een "
    "prijs gaven (mediaan +6,41%). BTTS is in de tweede ronde gekocht voor alle acht duels met "
    "een kandidaat-edge, a 2 credits. Totaal 35 van 791 credits; 18.977 over. "
    "Marktbalans-controle: 9 van 9 ingekochte competities hebben zowel een uitkomst- als een "
    "doelpuntenmarkt - hij slaagt zo ruim als hij kan. Wat hij niet laat zien en wat hier wel "
    "hoort: zes van de vijftien spelende competities zijn helemaal niet in te kopen "
    "(Tsjechie, Kroatie, Hongarije, Roemenie, de Keuken Kampioen Divisie en Albanie), en die "
    "tien doorgerekende duels staan daarom op een 1X2-marktgemiddelde zonder handicap-, "
    "doelpunten- of BTTS-markt."
)

res = json.load(open("tmp-run/rb19_results.json"))
odds = json.load(open("tmp-run/rb19_odds.json"))
s3 = json.load(open("tmp-run/rb19_stage3.json"))
uplift = json.load(open("tmp-run/rb19_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
state["duur"]["start"] = "2026-09-19T03:08:06+00:00"   # containerstart (uptime -s)
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
    "POORT_8_UNDERDOG": "licht sinds 5 sep 2026 — sides.UNDERDOG_FLOOR = 0.35",
    "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
    "HERIJKING": "recalibrate.apply, fit op uitslagen", "SETTLE_FALLBACK_HOURS": 2.0,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": TOELICHTING,
    "bevinding": BEVINDING,
    "omrekeningen": OMREKENINGEN,
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = {**vs, "controle_tegen_de_markt": uplift}
state["credits"] = {
    "plafond": odds["cap"], "gebruikt": odds.get("guard_totaal"),
    "split_budget": odds["split"],
    "bron": CREDITBRON,
    "markten_gekocht": {"bulk_h2h_spreads_totals": odds["bought"]["spreads"],
                        "h2h": odds["bought"]["h2h"], "totals": odds["bought"]["totals"],
                        "btts": odds["bought"]["btts"]},
    "geen_sportkey": odds.get("geen_sportkey"),
    "btts_kandidaat_edge": odds.get("btts_kandidaat_edge"),
    "guard_report": odds["guard"], "guard_report_btts": odds.get("guard_btts"),
}
by_comp = {}
for m in matches:
    by_comp.setdefault(m["competition"], []).append(m)
for comp, ms in by_comp.items():
    doorgerekend = [m for m in ms if m["tier"] != "NONE"]
    entry = {"status": "GEANALYSEERD" if doorgerekend else "BUITEN DATADEKKING", "matches": []}
    if not doorgerekend:
        entry["reden"] = (f"{len(ms)} wedstrijd(en) vandaag, geen enkele met een bruikbare "
                          f"onafhankelijke kansinput op het niveau waarop gespeeld wordt")
    for m in ms:
        e = {"match": m["match"], "match_id": m["match_id"], "tier": m["tier"],
             "bet": bool(m.get("bet")), "kickoff_nl": m["kickoff_nl"], "kickoff_utc": m["kickoff_utc"],
             "markets_checked": m["markets_checked"], "lambdas": m.get("lambdas"),
             "per_market": m.get("per_market"), "eenheid": m.get("eenheid"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "kruis_grens", "understat", "verplaatst", "poort8_geblokkeerd",
                  "poort8_ruw", "basis_per_wedstrijd",
                  "afgekapt", "buiten_cap", "seizoensweging", "odds_1x2", "odds_1x2_best",
                  "beste_prijs_winst_pct", "zonder_herijking", "kandidaat_edge"):
            if m.get(k):
                e[k] = m[k]
        if m.get("reason"):
            e["reden"] = m["reason"]
        if m.get("near_miss"):
            e["near_miss"] = m["near_miss"]
        if m.get("calibration"):
            e["calibration"] = m["calibration"]
        entry["matches"].append(e)
    mark(state, comp, entry)
for comp, v in fx.items():
    if not v["matches"]:
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": [],
                           "reden": "niets op de kalender vandaag (Fotmob-daglijst)"})
save(state)
print("run-state weggeschreven:", len(state["competitions"]), "competities")
