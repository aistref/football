"""Stage 6 — vastleggen: picks.jsonl, run-state. Run B 18 sep 2026 (nul bets)."""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-18"

TOELICHTING = """Vrijdag 18 september: negen van de zeventien competities uit prompts/run-b.md speelden, samen achttien duels - de drukste Run B-dag sinds weken, en de eerste waarop de Keuken Kampioen Divisie een volledige speelronde van acht wedstrijden tegelijk afwerkt. De acht lege competities zijn Czech First League, Greek Super League, Allsvenskan, Serie B, Swiss Super League, English League One, English League Two en de Kosovo Superleague. Die laatste komt nog altijd helemaal niet op de Fotmob-daglijst voor, ongewijzigd sinds 13 aug 2026; de andere zeven spelen hun ronde in het weekend. De cap stond op 55 (vr-zo) tegen achttien duels, dus MAX_DEEP_ANALYSES heeft deze run geen enkele analyse gekost - 0 afgekapt, laagste datarijkdom in de run 4,5 en hoogste 8,0.

Vijftien van de achttien duels kwamen door de datadekkingspoort: 4 FULL en 11 LIGHT. De drie die op NONE uitkwamen zijn Rudes - Slaven (Kroatie), Puskas FC Academy - Kispest Honved (Hongarije) en UTA Arad - Sepsi OSK (Roemenie), en alle drie om precies dezelfde reden: er staat een ploeg in die vorig seizoen niet in deze divisie speelde, en voor Kroatie, Hongarije en Roemenie kent promotion.py geen divisiepaar. Zie de bevinding hieronder - dit is geen storing van vandaag, maar het kostte wel drie van de achttien analyses.

Uit die vijftien duels zijn 98 selecties doorgerekend over alle zes de markten, en er kwam nul bets uit. De hoogste herijkte edge van de dag staat op +17,86 procentpunt (Almere City FC om te winnen tegen Heracles, marktgemiddelde 3,10), maar die selectie staat op de underdog-kant: de markt geeft Almere 29,7% tegen 46,9% voor Heracles, onder de ondergrens van 35% waar poort 8 dichtgaat. Dat is de enige selectie die deze run door poort 8 is tegengehouden, en hij gaat als schaduwpick het logboek in met de volledige drie getallen erbij (xG-model +30,41, splitsmethode +36,38, zwakste stand van het (shrink, rho)-grid +28,28).

De dichtstbijzijnde bet die geen poort raakte is Asian Handicap WSG Tirol +1,5 bij Rapid Wien, tegen 1,97 bij Betfair. Die staat op +7,54 procentpunt herijkt tegen een drempel van 8,0 voor FULL - een half procentpunt tekort. Ruw, zonder de herijking van par. 1g, staat dezelfde selectie op +21,71 pp, en dan bindt poort 8 er wel op (WSG Tirol krijgt 12,7% van de markt tegen 70,2% voor Rapid). Die twee lezingen staan daarom als twee aparte rijen in het schaduwlogboek: een near_miss op de herijkte schaal en een underdog_ruw-rij op de ruwe. Shadow.py slaat de dubbeltelling zelf over.

Twee selecties haalden alle acht poorten op de ruwe schaal maar niet na de herijking: Over 2.5 bij Albacete - Cordoba (ruw +8,29 pp, herijkt -5,66) en Under 3.5 bij Rapid Wien - WSG Tirol (ruw +9,07, herijkt -4,57). Beide gaan als zonder_herijking-rij het logboek in. Over de hele run vielen 92 van de 98 selecties af op de edge-poort, 3 op de herijking, 2 op de koersband (Rapid Wien - WSG Tirol had de uitwinst op 8,06, boven MAX_ODDS van 6,00) en 1 op poort 8. Poort 5 (tweede methode), 6 (robuustheid) en 7 (context) hebben deze run niets tegengehouden.

De inkoop kan de uitkomst deze keer niet scheef hebben getrokken, maar de dekking is wel ongelijk verdeeld en dat is het vermelden waard. Vier van de negen spelende competities hebben een sportkey bij The Odds API (Eliteserien, Segunda Division, 2. Bundesliga, Austrian Bundesliga) en die kregen alle vier de volle bulk-aanroep - 12 credits, vijf van de zes markten in een keer. De andere vijf (Kroatie, Hongarije, Roemenie, Keuken Kampioen Divisie, Kategoria Superiore) zijn niet in te kopen: daar is het BetExplorer-marktgemiddelde de enige 1X2-bron en zijn er dus drie selecties per duel in plaats van elf tot negentien. Dat betekent dat tien van de vijftien doorgerekende duels het met een marktgemiddelde moeten doen, waar de edge systematisch te laag uitvalt - conservatief, maar niet vergelijkbaar met de vier duels waar de beste prijs wel bekend is. De marktbalans-controle slaagt ruim: alle vier de ingekochte competities hebben zowel een uitkomst- als een doelpuntenmarkt.

De beste prijs leverde vandaag gemiddeld +5,50% op ten opzichte van het BetExplorer-marktgemiddelde (9,30% bij Sarpsborg - KFUM, 5,41% bij Rapid Wien, 5,12% bij Albacete, 3,88% bij Greuther Furth, 3,81% bij Wolfsburg) - in lijn met de +7,78% van de meting van 5 sep. In alle vier de competities stond een deel van de beste prijzen bij een beurs (Betfair, Matchbook), dus die koersen zijn door oddsapi.net_price gehaald: 2% commissie over de nettowinst. Bij Rapid Wien - WSG Tirol stonden alle drie de 1X2-uitkomsten bij een beurs.

BTTS is gekocht voor drie van de vier duels met een kandidaat-edge (Albacete - Cordoba, Greuther Furth - Magdeburg, Rapid Wien - WSG Tirol), a 2 credits: 3 credits in totaal want de derde viel binnen hetzelfde plafond. Het vierde duel met een kandidaat-edge, Almere City FC - Heracles, kon geen BTTS krijgen omdat de Keuken Kampioen Divisie geen sportkey heeft - dat staat zo in markets_checked, met de reden erbij en niet als gat.

Een wedstrijd kwam helemaal zonder prijzen te staan: Vllaznia - Teuta Durres in de Kategoria Superiore. De BetExplorer-slug albania/abissnet-superiore gaf nul rijen terug - geen foutmelding, gewoon een lege tabel - en een sportkey is er niet. Het duel is wel op LIGHT uitgekomen (de stand van vorig seizoen geeft doelpunten voor en tegen), maar zonder een enkele koers valt er niets door te rekenen. Dat is opgeschreven als "niet gevonden bij The Odds API en niet bij BetExplorer" en niet als een markt die niet bestaat.

De vroeg-seizoenscorrectie staat deze run op x1,1027, gepoold over negen competities en 71 speeldagen - de ruimste steekproef die deze routine tot nu toe heeft gehad, doordat ook de vijf competities zonder Fotmob-xG meetellen (daar op doelpunten gemeten, dezelfde eenheid als waarin die duels rekenen). De controle die par. 3 Stage 5 vraagt valt deze keer ongunstig uit en dat hoort er eerlijk bij te staan: zonder correctie lag P(Over 2.5) gemiddeld 3,59 procentpunt onder de de-vigde marktkans, met correctie 2,81 procentpunt erboven, en de gemiddelde absolute fout loopt op van 5,35 naar 7,03 procentpunt. De correctie schiet dus door. Maar: dat is gemeten over vier wedstrijden - alleen de duels waar beide kanten van de 2.5-lijn een prijs hebben, en dat zijn precies de vier ingekochte competities - en bij vier waarnemingen is dit ruis en geen bevinding. Het staat hier zodat een volgende run kan zien of het patroon terugkomt."""

BEVINDING = {
    "titel": ("Drie duels op NONE door een ontbrekend divisiepaar, niet door ontbrekende data "
              "(Kroatie, Hongarije, Roemenie)"),
    "wat": (
        "Rudes (promovendus in de Croatian HNL), Kispest Honved (Hungarian NB I) en Sepsi OSK "
        "(Romanian SuperLiga) staan geen van drieen in de stand van 2025/2026 van hun eigen "
        "competitie. Par. 4 schrijft voor zo'n ploeg eerst de omrekening uit de divisie eronder "
        "voor en pas daarna NONE. Die omrekening kon hier niet: promotion.TIER2 kent dertien "
        "divisieparen en Kroatie, Hongarije en Roemenie zitten daar geen van drieen bij, dus "
        "promotion.convert gooit meteen 'geen divisie boven of onder ... bekend'. Gevolg: drie "
        "van de achttien duels van vandaag zijn niet doorgerekend."),
    "is_dit_een_fout": (
        "Nee - dit is de regel die werkt zoals hij bedoeld is, en het is nadrukkelijk geen reden "
        "om een factor te verzinnen. promotion.MEASURED_TIER2_GAP is op 31 aug 2026 gemeten voor "
        "NED, DEN, POR, BEL, TUR en POL, over de seizoenen 2016/2017 t/m 2024/2025; buiten die "
        "landen is er geen meting en dus geen onafhankelijke kansinput op het niveau waarop "
        "gespeeld wordt. Dat is exact de Coventry-val waar conversion_in_range voor is gemaakt: "
        "een gepoolde of geraden factor levert schijnedge die alle andere poorten haalt."),
    "wat_het_kost": (
        "Vandaag drie duels. Over de afgelopen weken is dit geen eenmalig geval: Kroatie, "
        "Hongarije en Roemenie staan alle drie vast op LIGHT (geen Fotmob-xG) en hebben elk "
        "promovendi, dus elke speelronde valt er hier wel een duel af. Wat het zou kosten om het "
        "op te lossen is een meting in de geest van 31 aug: de tweede divisie van die drie landen "
        "bij Fotmob ophalen over meerdere seizoenen en het gat meten met promotion.measure_gap. "
        "Dat is werk voor een aparte sessie, niet voor een dagelijkse run - en het hoort pas in "
        "TIER2 als het gemeten is."),
}

OMREKENINGEN = {
    "aanleiding": (
        "Drie omrekeningen vandaag, alle drie degradanten (par. 4, convert_relegated). "
        "Wolfsburg degradeerde uit de Bundesliga naar de 2. Bundesliga: relatieve aanval 0.818 en "
        "verdediging 1.255 over 34 duels, met het gemeten paar D1/D2 (x1.777 aanval, x0.743 "
        "verdediging) omgerekend naar 1.454 en 0.932 - beide binnen het gemeten bereik (n=23). "
        "Heracles en FC Volendam degradeerden uit de Eredivisie naar de Keuken Kampioen Divisie; "
        "daar is geen apart gemeten paar, dus de gepoolde factor (x1.654 / x0.647, n=240) doet "
        "het werk, met uitkomsten 1.072/1.018 respectievelijk 1.072/0.659, allebei binnen bereik. "
        "Alle drie de duels komen daarmee op LIGHT uit - een omgerekende ploeg is nooit FULL."),
    "toegepast_op": ["Wolfsburg", "Heracles", "FC Volendam"],
    "geweigerd": [
        "Rudes (Croatian HNL) - geen divisiepaar voor Kroatie in promotion.TIER2",
        "Kispest Honved (Hungarian NB I) - geen divisiepaar voor Hongarije in promotion.TIER2",
        "Sepsi OSK (Romanian SuperLiga) - geen divisiepaar voor Roemenie in promotion.TIER2",
    ],
    "let_op": (
        "De twee Nederlandse omrekeningen leunen op de gepoolde factor en niet op een gemeten "
        "Eredivisie/KKD-paar. Dat is toegestaan (conversion_in_range staat open) maar het is de "
        "zwakste variant, en beide duels kwamen vandaag hoe dan ook niet in de buurt van een bet."),
}

CREDITBRON = (
    "suggest_cap(19081, 13) = 733 - 19.081 credits over volgens api_check.py van deze run "
    "(20K-plan, 919 gebruikt deze maand), 13 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(733, 4) gaf 4 spreads / 4 totals: vier van de negen spelende competities "
    "hebben een sportkey. Het plafond laat 3 credits per competitie ruimschoots toe, dus alle "
    "vier kregen de bulk-aanroep (h2h + spreads + totals, par. 1a) - vijf van de zes markten in "
    "een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-marktgemiddelde. Dat "
    "leverde gemiddeld +5,50% betere koers op over de vier duels waar beide bronnen een prijs "
    "gaven. BTTS is in de tweede ronde gekocht voor drie duels met een kandidaat-edge (Albacete, "
    "Greuther Furth, Rapid Wien), a 2 credits; het vierde duel met een kandidaat-edge (Almere "
    "City - Heracles) heeft geen sportkey en kon dus niet. Totaal 15 van 733 credits; 19.066 "
    "over. Marktbalans-controle: 4 van 4 ingekochte competities hebben zowel een uitkomst- als "
    "een doelpuntenmarkt - hij slaagt ruim. Wat hij niet laat zien en wat hier wel hoort: vijf "
    "van de negen spelende competities zijn helemaal niet in te kopen, en die tien duels staan "
    "daarom op een 1X2-marktgemiddelde zonder handicap-, doelpunten- of BTTS-markt."
)

res = json.load(open("tmp-run/rb18_results.json"))
odds = json.load(open("tmp-run/rb18_odds.json"))
s3 = json.load(open("tmp-run/rb18_stage3.json"))
uplift = json.load(open("tmp-run/rb18_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
state["duur"]["start"] = "2026-09-18T03:08:30+00:00"   # containerstart (uptime -s)
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
                  "afgekapt", "seizoensweging", "odds_1x2", "odds_1x2_best",
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
