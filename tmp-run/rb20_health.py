"""Stage 3 vastleggen: `data/source-health.json` en `data/coverage.json` bijwerken (§6b-3).

`run-b.md` vroeg expliciet om dit: veertien van de zeventien competities in deze runlijst stonden
daar als "nog niet getest", met de waarschuwing dat Fotmob-dekking van een competitie in hetzelfde
land niets zegt over een andere. Vandaag speelden er dertien, dus die vraag is voor elk van hen
beantwoord — en het antwoord hoort in `coverage.json` en niet alleen in het runrapport.
"""
import json
from datetime import date

DAG = "2026-09-20"
s3 = json.load(open("tmp-run/rb20_stage3.json"))
res = json.load(open("tmp-run/rb20_results.json"))
odds = json.load(open("tmp-run/rb20_odds.json"))

# ---------------- coverage.json ----------------
cov = json.load(open("data/coverage.json"))
comps = cov["competitions"]

SPORTKEY = {n: v.get("sportkey") for n, v in s3["fixtures"].items() if v.get("sportkey")}
LEAGUE_ID = {n: v.get("primaryId") for n, v in s3["fixtures"].items() if v.get("primaryId")}

n_new = n_upd = 0
for name, st in s3["stats"].items():
    if "error" in st:
        continue
    has_xg = st["prev"]["has_xg"]
    key = SPORTKEY.get(name)
    lid = LEAGUE_ID.get(name)
    duels = len(s3["fixtures"][name]["matches"])
    zin = (f"Run B {DAG}: Fotmob-id {lid}, seizoen {s3['fixtures'][name]['s_prev']} "
           f"({st['prev']['teams']} ploegen) — xG "
           f"{'AANWEZIG' if has_xg else 'AFWEZIG'}"
           + (f", competitiegemiddelde {st['prev']['avg_xg']:.3f} xG/duel" if has_xg else "")
           + f"; lopend seizoen {st['cur']['played']} speeldagen, xG "
           + f"{'aanwezig' if st['cur']['has_xg'] else 'afwezig'}. "
           + f"{duels} duel(s) vandaag, doorgerekend als "
           + f"{'FULL' if has_xg else 'LIGHT (doelpunten als sterktemaat, categorie 2)'}. "
           + (f"The Odds API-sportkey: {key}, volle bulk gekocht (h2h+spreads+totals)."
              if key else
              "Geen sportkey bij The Odds API — BetExplorer-marktgemiddelde is de enige "
              "1X2-bron, en er zijn dus geen handicap- en doelpuntenmarkten."))

    if name not in comps:
        comps[name] = {
            "prob_sources": ["fotmob"] + ([] if has_xg else []),
            "notes": zin,
        }
        n_new += 1
    else:
        comps[name]["notes"] = (comps[name].get("notes", "").rstrip() + " " + zin).strip()
        n_upd += 1

cov["updated"] = DAG
json.dump(cov, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print(f"coverage.json: {n_new} nieuwe competitie(s), {n_upd} bijgewerkt")

# ---------------- source-health.json ----------------
sh = json.load(open("data/source-health.json"))
src = sh["sources"]

n_full = sum(1 for m in res["matches"] if m.get("tier") == "FULL")
n_light = sum(1 for m in res["matches"] if m.get("tier") == "LIGHT")
n_none = sum(1 for m in res["matches"] if m.get("tier") == "NONE")
n_sel = sum(m.get("candidates_evaluated", 0) for m in res["matches"])
n_bets = 5

def add(bron, tekst, status=None):
    e = src.setdefault(bron, {"status": "untested", "role": "?", "detail": ""})
    e["last_checked"] = DAG
    if status:
        e["status"] = status
    e["detail"] = (e.get("detail", "").rstrip() + " " + tekst).strip()

add("the_odds_api",
    f"Run B {DAG}: api_check.py gaf 42 actieve voetbalcompetities en 18.805 credits over van "
    f"20.000 (1.195 gebruikt deze maand). Plafond suggest_cap(18805, 11) = 853; "
    f"split_budget(853, 7) = 7 spreads / 7 totals, dus de volle bulk (3 credits) paste voor alle "
    f"zeven inkoopbare competities. Uitgegeven: 21 credits aan de bulk + 21 aan BTTS "
    f"(21 van de 26 duels met een kandidaat-edge; 5 vielen af omdat hun competitie geen sportkey "
    f"heeft) = 42 van 853. Geen enkele fout. Marktbalans gehaald met ruime marge: alle zeven "
    f"gekochte competities kregen h2h, spreads én totals in dezelfde aanroep, dus 7 van 7 met "
    f"een doelpuntenmarkt en 7 van 7 met een uitkomstmarkt.",
    status="ok")

add("api_football",
    f"Run B {DAG}: API_FOOTBALL_KEY nog steeds niet gezet in de omgeving van de geplande taak. "
    f"Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder HTTP-verzoek. Gevolg "
    f"deze run: geen, Fotmob dekte alle dertien competities. Wél relevant dat dit de enige "
    f"statistiekbron blijft: zes van de dertien competities van vandaag hebben géén xG bij "
    f"Fotmob, en een tweede bron zou daar het verschil tussen LIGHT en FULL kunnen maken.",
    status="key_missing")

add("fotmob",
    f"Run B {DAG}: daglijst plus standen 2025/2026 en 2026/2027 (respectievelijk 2025/2026 voor "
    f"de twee kalenderjaarcompetities) voor dertien competities, wedstrijdcontext voor alle 43 "
    f"duels en de stadioncontrole. Geen enkele fout, geen enkele ctx-fout. Dit is de eerste run "
    f"die de xG-vraag uit run-b.md voor de hele runlijst beantwoordt: xG AANWEZIG bij Greek Super "
    f"League (135), Eliteserien (59), Allsvenskan (67), Segunda División (140), 2. Bundesliga "
    f"(146), Swiss Super League (69) en Austrian Bundesliga (38); xG AFWEZIG bij Czech First "
    f"League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189), Keuken "
    f"Kampioen Divisie (111) en Kategoria Superiore (260). Serie B, English League One en League "
    f"Two speelden niet. Kosovo Superleague stond niet in de daglijst en heeft dus nog steeds "
    f"geen geverifieerde Fotmob-id.",
    status="ok")

add("betexplorer",
    f"Run B {DAG}: dertien slugs opgehaald, alle dertien raak — samen 77 rijen waarvan 39 van "
    f"vandaag. Kosovo Superleague heeft geen slug in KNOWN_LEAGUE_URLS, maar speelde ook niet. "
    f"Eén naamkoppeling gerepareerd: BetExplorer kort Dinamo Zagreb af tot 'Din. Zagreb' en er "
    f"stond alleen een alias voor 'NK Lokomotiva'; `find_1x2` eist beide ploegen, dus Dinamo "
    f"Zagreb – NK Lokomotiva kwam op nul doorgerekende selecties uit terwijl de rij met vijf "
    f"boeken gewoon bij BetExplorer stond. Alias toegevoegd in tmp-run/ra_names.py.",
    status="ok")

add("understat",
    f"Run B {DAG}: niet aangeroepen. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue 1 "
    f"en geen van die vijf staat op de Run B-runlijst. Het tweede xG-model van §4 is voor deze "
    f"run dus per definitie niet beschikbaar — bekende grens van de bron, geen storing.")

sh["last_run"] = {
    "run": "B",
    "date": DAG,
    "note": (
        f"Run B {DAG} — zondag. Dertien van de zeventien competities uit de runlijst speelden "
        f"(43 duels); Serie B, English League One, English League Two en Kosovo Superleague niet. "
        f"Cap 55 tegen 43 duels, dus 0 afgekapt. {n_full + n_light} van de 43 door de "
        f"datadekkingspoort: {n_full} FULL en {n_light} LIGHT; de {n_none} op NONE vallen allemaal "
        f"op een ontbrekende divisie-omrekening (Kalamata en FC Voluntari: geen TIER1/TIER2 voor "
        f"Griekenland en Roemenië; Sabadell, Celta Fortuna en Energie Cottbus: gepromoveerd uit "
        f"een divisie die niet in promotion.py staat) en niet op een datagat. {n_sel} selecties "
        f"over alle zes de markten, {n_bets} bets — drie boven hun drempel, twee op rangorde "
        f"(§5b). Stage 0: niets af te wikkelen, de tien openstaande picks van vandaag hadden nog "
        f"niet gespeeld. Zeven van de zeven inkoopbare competities kregen de volle bulk; 21 "
        f"credits daarvoor plus 21 aan BTTS = 42 van een plafond van 853, 18.763 van 20.000 over. "
        f"Dit is de eerste run die de xG-vraag uit run-b.md voor de hele runlijst beantwoordt: "
        f"zeven competities mét xG, zes zonder. Twee reparaties: `p_xg_shrink08` wordt nu "
        f"vastgelegd zoals §6e sinds 19 sep eist (Run A deed dat vandaag niet, waardoor de "
        f"shrink-arm met zichzelf werd vergeleken), en de Segunda División stond onder een andere "
        f"naam in promotion.TIER1 waardoor de degradantenomrekening 'geen divisie bekend' meldde. "
        f"Derde en zwaarste bevinding: `oddsapi.net_price` werd alleen op de 1X2-tak toegepast, "
        f"zodat spreads, totals en BTTS met de BRUTO beurskoers rekenden — 125 van de 403 "
        f"selecties van vandaag stonden bij een beurs. Gerepareerd vóór publicatie; het "
        f"veranderde twee van de vijf bets."
    ),
}
sh["updated"] = DAG
json.dump(sh, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
