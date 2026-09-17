"""Stage 6 — vastleggen: picks.jsonl, run-state. Run A 17 sep 2026 (nul bets)."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-17"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-17T04:12:00+02:00"

TOELICHTING = """Donderdag 17 september: 12 wedstrijden op de runlijst, in 3 van de 21 competities. La Liga speelde de restanten van zijn midweekse speelronde (2 duels), de Europa League had zijn eerste volle speelronde van de competitiefase (9 duels) en de League Cup had een uitgestelde derderondewedstrijd (1 duel). De achttien andere competities hadden niets op de kalender - Premier League, Serie A, Bundesliga, Ligue 1, Championship, Eredivisie, Primeira Liga, de Belgische Pro League, de Super Lig, de Schotse Premiership, de Deense Superliga, de Ekstraklasa, de Champions League, de Conference League, de FA Cup, de Coppa Italia, de KNVB Beker en de DFB Pokal. Dat is GEEN WEDSTRIJD, geen storing. De cap van 40 (donderdag) kwam niet in de buurt: nul duels afgekapt, de hele kalender is doorgerekend. Tien duels kwamen door de datadekkingspoort - een FULL en negen LIGHT - en twee kwamen op NONE uit. Samen 141 doorgerekende selecties over alle zes de markten, en nul bets.

Negen van de tien doorgerekende duels zijn LIGHT, en dat is bijna de hele verklaring van vandaag. Zeven Europa League-duels zijn met scripts/interleague.py naar de Europese schaal omgerekend, en twee binnenlandse duels leunen op een promovendus-omrekening (Malaga in La Liga, Norwich City in de League Cup). Een omgerekende ploeg is nooit FULL, en LIGHT betekent een drempel van 16.0 procentpunt in plaats van 8.0 - met de herijking van par. 1g daar nog overheen. Alleen Real Betis - Getafe is FULL; dat is het enige duel vandaag waar de drempel van 8.0 geldt.

Twee Europese duels haalden de omrekening niet en kwamen op NONE. OFI Crete - Hoffenheim: de omgerekende verdediging van OFI komt op 1.685 uit en het gemeten bereik loopt tot 1.446, dus buiten het bereik waarin de factor is waargenomen - dat is de poort van par. 4 (in_range), geen storing. Lillestrom - Torreense: Torreense speelt in de Liga Portugal 2 en niet in de hoogste divisie waarop de Portugese factor is gemeten, dus er is geen gemeten niveau om de ploeg vandaan te halen.

De inkoop kon vandaag geen scheve uitkomst veroorzaken. Alle drie de competities hebben een sportkey, alle drie kregen de volle bulk-aanroep (h2h + spreads + totals), en de drie duels met een kandidaat-edge kregen daarbovenop BTTS: 12 van 682 credits. De marktbalans-controle slaagt volledig, 3 op 3 met zowel een uitkomst- als een doelpuntenmarkt.

Van de 141 selecties vielen er op de herijkte schaal 130 af op poort 1 (edge) en 11 op poort 2 (koers buiten de band 1.30-6.00). Geen enkele selectie viel alleen op de herijking af, dus er is vandaag geen rij zonder_herijking. Op de ruwe schaal ziet dezelfde verdeling er anders uit: 120 op edge, 11 op de koers en 10 op poort 8 (underdog). Poort 5 (tweede methode), poort 6 (robuustheid) en poort 7 (context) hielden deze run niets tegen.

Zestien selecties hebben een positieve herijkte edge. De hoogste staat op +12.99 pp - Marseille wint bij Besiktas @4.33 - tegen een LIGHT-drempel van 16.0. Daarna Ferencvaros wint bij Celtic @4.63 met +8.00 pp, ook LIGHT. Beide zouden bij een FULL-drempel van 8.0 wel zijn gepubliceerd; dat ze LIGHT zijn is geen formaliteit maar het gevolg van een omrekening die de systematische fout eruit haalt en de onzekerheid niet.

Op de ruwe schaal zijn er 62 positieve edges, en daar zit de bevinding van vandaag. Nul selecties haalden alle acht de poorten op de ruwe schaal - maar tien werden er op die schaal door poort 8 tegengehouden, en ze komen alle tien uit dezelfde drie duels: Besiktas - Marseille, Celtic - Ferencvaros en Levski Sofia - Salzburg. Het zijn alle tien de uitploeg, alle tien door de markt als de mindere ploeg gezien, en de hoogste staat op ruw +23.86 pp. Dat is exact het patroon waar par. 1e voor is gebouwd: de grootste geclaimde edge staat op de kant waar het model aantoonbaar te hoog schat. Drie rijen (een per wedstrijd) gaan als underdog_ruw het schaduwlogboek in.

En twee duels werden niet gespeeld waar Fotmob het eigen stadion van de thuisploeg noteert. Real Betis - Getafe stond in Estadio Benito Villamarin terwijl Fotmob La Cartuja als thuisbasis van Betis heeft, en Levski Sofia - Salzburg stond in het nationale Vasil Levski-stadion in plaats van Georgi Asparuhov. check_venue zag beide en zette relocated. In geen van beide gevallen sluit de poort - hij houdt alleen tegen, en beide ploegen spelen gewoon in hun eigen stad - maar thuisvoordeel is de aanname waar het model het zwaarst op leunt, dus het hoort in het rapport te staan."""

OMREKENINGEN = {
    "aanleiding": (
        "Twee soorten omrekening vandaag. Kruis-grens (par. 4, 8 sep 2026): negen Europa "
        "League-duels, waarvan er zeven zijn omgerekend naar de Europese schaal met "
        "scripts/interleague.py en twee niet. Geslaagd zijn Levski Sofia - Salzburg, Besiktas - "
        "Marseille, Celtic - Ferencvaros, Crystal Palace - Lech Poznan, Juventus - NEC Nijmegen, "
        "Real Sociedad - AFC Bournemouth en Viktoria Plzen - Union St.Gilloise; alle veertien "
        "ploegen vielen binnen het gemeten bereik van de omgerekende aanval en verdediging. "
        "Geweigerd zijn OFI Crete (GRE) en Torreense (POR), elk om een eigen reden: de "
        "omgerekende verdediging van OFI komt op 1.685 uit tegen een gemeten bereik tot 1.446, "
        "en Torreense speelt in de Liga Portugal 2 en niet in de hoogste divisie waarop de "
        "Portugese factor is gemeten. OFI Crete - Hoffenheim en Lillestrom - Torreense komen "
        "daarmee op NONE. Binnenlands (par. 4, promovendi): twee geslaagde omrekeningen - Malaga "
        "uit LaLiga2 naar La Liga (x0.661/1.498, gemeten paar SP1/SP2) en Norwich City uit de "
        "Championship naar de Premier League-basis van de League Cup (x0.541/1.783, gemeten paar "
        "E0/E1). Allebei binnen het gemeten bereik, en allebei LIGHT: een omgerekende ploeg is "
        "nooit FULL."),
    "toegepast_op": ["Málaga", "Norwich City",
                     "Levski Sofia", "Salzburg", "Beşiktaş", "Marseille", "Celtic",
                     "Ferencváros", "Crystal Palace", "Lech Poznań", "Juventus", "NEC Nijmegen",
                     "Real Sociedad", "AFC Bournemouth", "Viktoria Plzeň", "Union St.Gilloise"],
    "geweigerd": ["OFI Crete (GRE, omgerekende verdediging 1.685 buiten het bereik 0.388-1.446)",
                  "Torreense (POR, speelt in Liga Portugal 2, niet in de hoogste divisie)"],
}

CREDITBRON = (
    "suggest_cap(19134, 14) = 682 - 19.134 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 866 gebruikt deze maand), 14 dagen tot de maandwissel, 2 runs per dag. "
    "split_budget(682, 3) gaf 3 spreads / 3 totals, oftewel alle drie de inkoopbare competities "
    "kregen allebei. Het plafond is ruim genoeg voor 3 credits per competitie, dus de "
    "bulk-aanroep (h2h + spreads + totals, par. 1a) is voor alle drie gedaan: vijf van de zes "
    "markten in een keer, en 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Dat leverde over de negen duels met beide prijzen gemiddeld +6.68% betere "
    "koers op (bereik +2.57% tot +15.88%). BTTS is daarna in een tweede ronde gekocht voor de "
    "drie duels met een kandidaat-edge - zie par. 1a stap 2. Totaal 9 credits aan de bulk plus "
    "3 aan BTTS = 12 van 682; 19.122 over."
)

res = json.load(open("tmp-run/ra17_results.json"))
odds = json.load(open("tmp-run/ra17_odds.json"))
s3 = json.load(open("tmp-run/ra17_stage3.json"))
uplift = json.load(open("tmp-run/ra17_uplift.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
bets = [m for m in matches if m.get("bet")]
assert not bets, "deze emit is geschreven voor een run met nul bets"
print("bets:", len(bets), "- niets toe te voegen aan picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["duur"]["gestart"] = "2026-09-17T02:08:00+00:00"   # tijdstempel van de sessiemap
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
    "POORT_8_UNDERDOG": "licht sinds 5 sep 2026 — sides.UNDERDOG_FLOOR = 0.35",
    "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
    "HERIJKING": "recalibrate.apply, fit op uitslagen", "SETTLE_FALLBACK_HOURS": 2.0,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": TOELICHTING,
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
             "per_market": m.get("per_market"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "kruis_grens", "understat", "verplaatst", "poort8_geblokkeerd",
                  "poort8_ruw", "basis_per_wedstrijd",
                  "afgekapt", "seizoensweging", "odds_1x2", "odds_1x2_best",
                  "beste_prijs_winst_pct", "zonder_herijking", "kandidaat_edge"):
            if m.get(k): e[k] = m[k]
        if m.get("reason"): e["reden"] = m["reason"]
        if m.get("near_miss"): e["near_miss"] = m["near_miss"]
        if m.get("calibration"): e["calibration"] = m["calibration"]
        entry["matches"].append(e)
    mark(state, comp, entry)
for comp, v in fx.items():
    if not v["matches"]:
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": [],
                           "reden": "niets op de kalender vandaag (Fotmob-daglijst)"})
save(state)
print("run-state weggeschreven:", len(state["competitions"]), "competities")
