"""Run A 9 nov 2026 onder §5b: run-state en logboeken. NUL BETS, en wel om een reden die
niets met de poorten te maken heeft.

HET INTERLANDVENSTER IS BEGONNEN EN TWINTIG VAN DE EENENTWINTIG COMPETITIES VAN DE RUNLIJST
SPELEN NIET. Er is precies één wedstrijd in het inzetvenster: FA Cup, Plymouth Parkway -
Berkhamsted, 20:30 NL. Zie HET_INTERLANDVENSTER_LEGT_DE_HELE_RUNLIJST_STIL.

DAT ENE DUEL KOMT OP `NONE` UIT, en dat is een gemeten antwoord en geen gat. Zie
HET_ENE_DUEL_IS_NON_LEAGUE_TEGEN_NON_LEAGUE_EN_DAAROM_NONE.

ER IS NUL CREDIT UITGEGEVEN EN DE MARKTBALANS-CONTROLE VAN §1a KAN NIET SLAGEN. Dat komt
vandaag niet van een krap plafond maar van een lege runlijst. Zie
NUL_CREDITS_EN_DE_MARKTBALANS_CONTROLE_SLAAGT_NIET.

DE AFWIKKELING VAN GISTEREN GAF ZES VERLIEZERS OP ELF PICKS. Zie
ZES_VERLIEZERS_OP_ELF_PICKS_EN_WAT_DAT_NIET_BETEKENT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.progress import load_or_start, mark, save

DAG = "2026-11-09"
RUN = "A"
res = json.load(open("tmp-run/ra_nov09_results.json"))
odds = json.load(open("tmp-run/ra_nov09_odds.json"))

st = {"date": DAG, "run": RUN, "competitions": {}}
for m in res["matches"]:
    st["competitions"].setdefault(m["competition"],
                                 {"status": "GEANALYSEERD", "matches": []})["matches"].append(m)
top = toplist.build(st)

state = load_or_start(RUN.lower(), date.fromisoformat(DAG))
state["parameters"] = {
    "HET_INTERLANDVENSTER_LEGT_DE_HELE_RUNLIJST_STIL": (
        "TWINTIG VAN DE EENENTWINTIG COMPETITIES VAN DE RUNLIJST HEBBEN VANDAAG GEEN WEDSTRIJD "
        "IN HET INZETVENSTER, en de eenentwintigste heeft er één. Dat is `GEEN WEDSTRIJD` en "
        "geen storing (§5): het FIFA-interlandvenster van november is begonnen, dus de dertien "
        "clubcompetities liggen stil, de drie Europese toernooien spelen niet en vier van de vijf "
        "bekers hebben hun eerstvolgende ronde pas in december. "
        "DIT IS BIJ TWEE BRONNEN NAGETROKKEN EN NIET AAN DE DAGLIJST ALLEEN OVERGELATEN. De "
        "Fotmob-daglijst geeft voor League Cup (id 133), DFB Pokal (209) en KNVB Beker (235) nul "
        "duels in het venster, en BetExplorer noemt de eerstvolgende ronde erbij: Coppa Italia "
        "1 dec, KNVB Beker 1 dec, DFB Pokal 1 dec, League Cup 15 dec. Twee bronnen, hetzelfde "
        "antwoord. Dat die controle er is, is geen formaliteit: 'niet in de daglijst' mag nooit "
        "als `GEEN WEDSTRIJD` worden opgeschreven zonder tweede bron, en dat is het gat dat Run A "
        "op 6 oktober 2026 vijf duels kostte. "
        "DE CAP BINDT DAARMEE NIET EN HEEFT 39 PLEKKEN OVER (`MAX_DEEP_ANALYSES` = 40 op een "
        "maandag, §0). Dat is de ruimste marge van deze reeks en de spiegel van gisteren, toen "
        "55 duels op een zondagcap van 55 uitkwamen — nul marge. Er is nul duel afgekapt."),
    "HET_ENE_DUEL_IS_NON_LEAGUE_TEGEN_NON_LEAGUE_EN_DAAROM_NONE": (
        "PLYMOUTH PARKWAY - BERKHAMSTED (FA Cup, 20:30 NL) KOMT OP `data_tier = NONE` UIT, en dat "
        "is een gemeten antwoord en geen ontbrekende bron. "
        "In een beker ligt de basis per WEDSTRIJD en niet per toernooi (§4, 15 sep 2026): "
        "`promotion.CUP_BASE` hangt de FA Cup aan de Premier League, en staan beide ploegen daar "
        "niet in, dan loopt `promotion.shared_lower_division` de `TIER2`-keten af op zoek naar een "
        "divisie waarin ze BEIDE staan. Die keten is onder de Premier League één schakel lang — "
        "Championship (id 48) — en geen van beide ploegen staat in de stand van 2025/2026. "
        "`shared_lower_division` geeft daarom `None`, en de omrekening geeft "
        "`PromotionError: 'Plymouth Parkway' staat niet in de stand van Championship (ENG) "
        "2025/2026`. "
        "DAT IS GEEN TEKORT IN DE ADMINISTRATIE. Beide ploegen spelen in de Southern League "
        "Premier Division, het achtste niveau van Engeland: Plymouth Parkway in de zuidelijke "
        "groep, Berkhamsted in de centrale. Er is dus niet alleen geen gemeten divisiefactor tot "
        "dat niveau, er is ook geen gedeelde divisie, want ze spelen in twee verschillende "
        "groepen. Een gepoolde factor erop zetten zou het gat dichten met een getal zonder "
        "onderbouwing, en dat is precies wat §2 en §4 verbieden. "
        "WAT DE BRON WEL HEEFT, IS DE CONTEXT, en die is netjes gelogd: vorm WLWLW thuis tegen "
        "WWLDD uit, zes dagen rust tegen negen, gespeeld in Manadon Sports Hub — het eigen "
        "stadion van de thuisploeg, dus niet verplaatst. Wat er niet is: selectiewaarde, "
        "uitvallers en opstelling (`squad_value` 0, `team_id` 0, `lineup_type` leeg). Dat is bij "
        "een achtste-niveauclub te verwachten en het is de reden dat de datarijkdom op 3,5 "
        "uitkomt — ontbrekende metingen krijgen het middenpunt en nooit nul (§3, Stage 4). "
        "ER IS GEEN MARKT DOORGEREKEND en dat hoort zo: §6b-5b slaat wedstrijden met `tier = "
        "NONE` over in `progress.py verify`, want daar valt geen markt door te rekenen. "
        "`markets_checked` is daarom met opzet leeg en niet half gevuld."),
    "NUL_CREDITS_EN_DE_MARKTBALANS_CONTROLE_SLAAGT_NIET": (
        "ER IS VANDAAG NUL CREDIT UITGEGEVEN, op een plafond van 441 (`suggest_cap(19444, 22)`, "
        "twee runs per dag). Niet omdat het plafond krap is — het is het ruimste van de maand — "
        "maar omdat er niets inkoopbaar is: de enige competitie die speelt is de FA Cup, en "
        "`soccer_england_fa_cup` staat niet bij de 21 actieve sportkeys van `api_check.py` van "
        "deze run. `split_budget(441, 0)` geeft dus (0, 0) en `CreditGuard` doet nul aanroepen. "
        "DE MARKTBALANS-CONTROLE VAN §1a SLAAGT DAARMEE NIET, en dat moet er staan in plaats van "
        "stil te worden overgeslagen. Die controle eist dat er minstens één competitie met een "
        "doelpuntenmarkt EN minstens één met een uitkomstmarkt in de run zit. Vandaag zijn het er "
        "nul van elk. §1a schrijft voor dat je dan meldt dat het plafond te krap is voor deze "
        "runlijst; DAT IS HIER NIET DE OORZAAK, en dat onderscheid is het hele punt van die "
        "controle: ze is er om te zien wanneer een scheve uitkomst uit de portemonnee komt in "
        "plaats van uit de data. Vandaag komt ze uit de kalender. "
        "WAT ER WEL IS OPGEHAALD, GRATIS: het BetExplorer-marktgemiddelde voor de FA Cup, één rij "
        "over zestien boeken — Plymouth Parkway 2,07 / gelijk 3,63 / Berkhamsted 3,09. Dat is "
        "het marktoordeel, niet de beste prijs, en het is hier alleen boekhouding: met `tier = "
        "NONE` is er geen `my_prob` om ertegen af te zetten en dus geen edge, geen "
        "kalibratierij en geen poort 8. Gemiddelde om te meten, beste prijs om te spelen (§1a) — "
        "en vandaag valt er geen van beide te doen."),
    "ZES_VERLIEZERS_OP_ELF_PICKS_EN_WAT_DAT_NIET_BETEKENT": (
        "DE ELF OPENSTAANDE PICKS VAN 7 EN 8 NOVEMBER ZIJN AFGEWIKKELD: VIJF GEWONNEN, ZES "
        "VERLOREN. Daarnaast zijn er zeventig schaduwrijen afgerekend (28 gewonnen, 41 verloren, "
        "1 void), en `calibration.py settle` en `ctxlog.py settle` zijn gedraaid — 258 "
        "kalibratiewaarnemingen en 94 contextwedstrijden. `recalibrate.load_fit().fitted_through` "
        "staat daarmee op 2026-11-08, de vorige rundag, zoals §6b-5c eist. "
        "ZES VERLIEZERS OP EEN DAG IS DE GRENS WAARBOVEN §7 ERVAN WIL HOREN (een "
        "afwikkelingsreeks die opvalt, 5+ verliezers), dus hij staat in de notificatie. "
        "WAT HET NIET IS: een reeks. §6d eist ~30 gevallen voordat een reeks gelezen mag worden, "
        "en elf picks op één dag is dat niet. Vijf van de elf stonden bovendien op een Over/Under "
        "op de Under-kant en drie daarvan verloren — precies de kant waarvan §6g de scheefstand "
        "al meet, dus dat is geen nieuwe bevinding maar dezelfde. Er wordt vandaag op grond "
        "hiervan geen drempel, gewicht of poort aangeraakt."),
    "DE_REFLECTIE_OP_DE_UITSLAGEN_VAN_GISTEREN": (
        "§3 Stage 0 (12 okt 2026) vraagt bij elke afgewikkelde pick of de REDENERING klopte en "
        "niet alleen de uitkomst. De vier vragen, met de aantallen erbij: "
        "1. KLOPTE DE REDENERING? Twee van de vijf winnaars zijn gewonnen op een wedstrijd die "
        "ongeveer liep zoals voorgerekend (Napoli - Lazio 1-1 onder de 3, Tromso - Bodo/Glimt "
        "0-2 onder de 3,5). Twee van de zes verliezers liepen juist volledig uit de hand: Viking "
        "- KFUM werd 5-1 en Sandefjord - Molde 5-5, samen zestien doelpunten in twee duels waar "
        "er zes à zeven waren verwacht. Dat zijn verloren bets op een verkeerd ingeschatte "
        "wedstrijd. Sunderland - Chelsea 1-0 is het omgekeerde: een Over 2.5 die verliest op een "
        "duel dat met één doelpunt eindigde, dus ook daar zat de schatting ernaast. Villarreal - "
        "Getafe 2-0 (BTTS nee) is gewonnen én goed ingeschat. "
        "2. DEDEN DE POORTEN HUN WERK? De zeventig schaduwrijen staan op 28 gewonnen en 41 "
        "verloren, dus de poorten hielden gisteren overwegend verliezers tegen. Twee rijen vallen "
        "op in de andere richting: Union St.Gilloise - Genk (BTTS nee, de `lijstlengte`-rij van "
        "gisteren) WON, en Besiktas - Genclerbirligi staat met twee rijen in het logboek waarvan "
        "de Under 2.5 verloor en de Under 3.5 won — dezelfde mening op twee lijnen, en de lijn "
        "maakte het verschil. "
        "3. ZAT ER EEN PATROON IN? Ja, en het is er een die al in de boeken staat: van de vijf "
        "gespeelde Unders verloren er drie, en twee daarvan op een duel met tien of zes "
        "doelpunten. Dat is de Under-scheefstand van §6g, nu met vijf gevallen erbij. Daarnaast "
        "vielen er in de Eliteserien van gisteren in drie duels samen achttien doelpunten. "
        "4. WAT BETEKENT DIT NIET? Eén dag is geen reeks, en vijf Unders zijn geen meting. De "
        "`doelpunten_onder`-reeks van poort 9 is de meting die hierover gaat en die wordt niet "
        "gelezen onder ~30 afgewikkelde gevallen (§1h, §6d). De niveaucorrectie "
        "`model.LEVEL_SCALE` = 1.032 bindt sinds 3 november en is juist bedoeld om dit te "
        "verkleinen; of dat lukt is pas te zien als er genoeg duels van ná die datum liggen, en "
        "zes dagen is dat niet."),
    "DE_HERIJKING_EN_DE_VROEG_SEIZOENSCORRECTIE_ZIJN_GEDRAAID_MAAR_RAKEN_NIETS": (
        "`recalibrate.load_fit()` geeft a=1.0319, b=0.0206 over 7734 waarnemingen, gefit t/m "
        "2026-11-08. De vroeg-seizoenscorrectie komt op factor 1.0253 uit (gepoold 1.0455 over "
        "10 speeldagen, één competitie in de pool, nul overgeslagen), en `model.league_level` "
        "koos voor de FA Cup-basis de route `vorig+uplift` — Premier League op 10 van 38 "
        "speeldagen, 26%, onder de helft. "
        "ALLEBEI ZIJN ZE GEDRAAID EN ALLEBEI RAKEN ZE VANDAAG NIETS, want het enige duel komt op "
        "`NONE` uit voordat er een kans wordt berekend. Ze staan hier omdat §6e en §1g een reeks "
        "willen die over dagen heen vergelijkbaar is, en een dag waarop de getallen niet zijn "
        "opgeschreven is een gat in die reeks. "
        "LET OP DE POOL: hij bestaat vandaag uit ÉÉN competitie (de Premier League, als basis van "
        "de FA Cup). Een gepoolde factor over één waarneming is geen pool, en hij is hier dan ook "
        "niet op een bet toegepast. Lees de 1,0253 van vandaag dus niet als een meting naast die "
        "van gisteren, toen er twaalf competities in zaten."),
    "WAT_ER_VANDAAG_NIET_IS_GELOGD_EN_WAAROM_DAT_KLOPT": (
        "NUL near_miss-rijen, nul schaduwrijen, nul kalibratierijen, nul marktvormblokken en nul "
        "voorbeschouwingen — en dat is bij één duel op `NONE` het juiste antwoord, geen "
        "vergeetachtigheid. "
        "`shadow.py collect` heeft geen kandidaat om te boeken, want er is geen selectie "
        "doorgerekend die een poort kon halen of missen. `calibration.py collect` eist een "
        "doorgerekend duel met een de-vigde marktkans EN modelkansen; de modelkansen bestaan niet. "
        "`marketform.match_block` wordt per DOORGEREKEND duel gevraagd (§4, 17 okt 2026: 'dus niet "
        "bij tier = NONE, daar valt niets te tellen'). `preview.py` draait per GEPUBLICEERDE bet "
        "en er zijn er nul, dus `prosecheck.py` heeft ook niets te meten (§6b-5j zegt dat "
        "zelf: bij nul bets zijn er geen voorbeschouwingen). "
        "EN `ctxlog.py collect` VOEGT VANDAAG OOK NUL RIJEN TOE, maar om een andere reden dan "
        "de rest, en die hoort opgeschreven. De context IS opgehaald en staat in het "
        "`context`-blok van het duel — vorm, rust, stadion. Wat ontbreekt is de "
        "selectiewaarde: `squad_value` en `out_value` zijn beide 0, dus `ctxlog.out_share` "
        "(= out / (basis + out)) geeft `None` en `_rows_from_state` slaat de rij over. Dat is "
        "CORRECT en geen gemiste meting: die reeks bestaat om ooit te kunnen zeggen hoeveel "
        "ontbrekende spelers waard zijn (§1c), en bij een achtste-niveauclub zonder "
        "marktwaardes is er geen beschikbaarheidsverschil om te loggen. Een nul boeken waar "
        "niets is gemeten zou precies de fout zijn die §1c bij de datarijkdom verbiedt: een "
        "meting die er niet is, is geen bewijs van een probleem. Het logboek blijft daarmee "
        "op 2278 rijen staan."),
}
state["vroeg_seizoen"] = res.get("vroeg_seizoen")
state["niveau"] = res.get("niveau")
state["selectie_5b"] = top
state["credits"] = {
    "plafond": odds.get("cap"), "split_budget": odds.get("split"),
    "verbruikt": 0, "aanroepen": 0, "guard": odds.get("guard"),
    "markten_gekocht": {"h2h": [], "spreads": [], "totals": [], "btts": []},
    "gratis": {"betexplorer_1x2": ["FA Cup (ENG)"]},
    "marktbalans": ("SLAAGT NIET: nul competities met een doelpuntenmarkt en nul met een "
                    "uitkomstmarkt. De oorzaak is niet het plafond (441 credits, nul gebruikt) "
                    "maar dat de enige competitie die vandaag speelt geen actieve sportkey heeft "
                    "(soccer_england_fa_cup staat niet bij de 21 actieve keys van api_check.py). "
                    "Zie §1a en het runrapport."),
}

for comp, blok in st["competitions"].items():
    entry = {"status": "GEANALYSEERD", "matches": []}
    for m in blok["matches"]:
        entry["matches"].append({**m, "bet": False})
    mark(state, comp, entry)

s3 = json.load(open("tmp-run/ra_nov09_stage3.json"))
for comp, v in s3["fixtures"].items():
    if comp in state["competitions"]:
        continue
    mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})

cups = json.load(open("tmp-run/ra_nov09_cups.json"))["cups"]
for comp, v in cups.items():
    if comp in state["competitions"]:
        continue
    bxv = v.get("betexplorer") or {}
    mark(state, comp, {"status": v["status"], "matches": [],
                       "bron": v.get("bron", "BetExplorer (§5)") + " + BetExplorer",
                       "eerstvolgende_ronde": bxv.get("eerste_ronde"),
                       "teamparen_op_de_fixturepagina": bxv.get("teamparen")})

save(state)
print(f"run-state Run {RUN} weggeschreven ({len(state['competitions'])} competities)")
print("regels in de dagranglijst (herijkt):", len(top["herijkt"]), "ruw:", len(top["ruw"]))
print("picks toegevoegd aan data/picks.jsonl: 0 (nul bets)")
