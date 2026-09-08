"""Dataset voor de inter-competitiemeting: Europese uitslagen + binnenlandse standen.

Waarom dit bestaat: het model normaliseert elke ploeg op het gemiddelde van zijn EIGEN
competitie, en kent daardoor het krachtsverschil tussen twee nationale competities niet.
Bij een kruis-grensduel (UCL/UEL/UECL) komt dat gat er als schijn-edge uit, en daarom staan
die duels sinds 18 aug 2026 op data_tier NONE.

Voor divisies binnen één land is dat gat gemeten omdat ploegen daar fysiek tussen bewegen
(promotion.MEASURED_TIER2_GAP). Tussen twee landen gebeurt dat niet: de enige brug is de
Europese wedstrijd zelf. Dit script haalt die brug op.

Per Europese wedstrijd wordt de BINNENLANDSE stand van het VORIGE afgeronde seizoen gebruikt,
precies zoals de live-pijplijn dat doet. Dat voorkomt dat de meting cijfers gebruikt die op de
speeldag nog niet bestonden.
"""
import json, sys, time, urllib.parse
from pathlib import Path
sys.path.insert(0, ".")
from scripts.fotmob import _get_json, _pick_table, FotmobError

CACHE = Path("data/cache/interleague")
OUT = Path("tmp-run/il_dataset.json")

# Europese topdivisies, handmatig gekozen uit /api/data/allLeagues (de eerste competitie van een
# land is niet altijd de hoogste — bij Litouwen staat de kwalificatie bovenaan, bij Armenië de
# beker). ccode -> (fotmob_id, naam).
LEAGUES = {
    "ALB": (260, "Kategoria Superiore"),   "ARM": (118, "Armenian Premier League"),
    "AUT": (38,  "Austrian Bundesliga"),   "AZE": (262, "Azerbaijan Premier League"),
    "BLR": (263, "Belarus Premier League"),"BEL": (40,  "Belgian Pro League"),
    "BIH": (267, "Bosnia Premier League"), "BUL": (270, "Bulgaria First League"),
    "CRO": (252, "Croatian HNL"),          "CYP": (136, "Cyprus 1. Division"),
    "CZE": (122, "Czech First League"),    "DEN": (46,  "Danish Superliga"),
    "ENG": (47,  "Premier League"),        "EST": (248, "Meistriliiga"),
    "FRO": (250, "Faroe Premier League"),  "FIN": (51,  "Veikkausliiga"),
    "FRA": (53,  "Ligue 1"),               "GEO": (439, "Erovnuli Liga"),
    "GER": (54,  "Bundesliga"),            "GRE": (135, "Greek Super League"),
    "HUN": (212, "Hungarian NB I"),        "ISL": (215, "Besta deildin"),
    "IRL": (126, "Irish Premier Division"),"ISR": (127, "Ligat ha'Al"),
    "ITA": (55,  "Serie A"),               "KAZ": (225, "Kazakhstan Premier League"),
    "LVA": (226, "Latvia Virsliga"),       "LTU": (228, "Lithuania Toplyga"),
    "LUX": (229, "Luxembourg National"),   "MKD": (249, "Macedonia Prva Liga"),
    "MDA": (231, "Moldova National"),      "MNE": (232, "Montenegro 1. CFL"),
    "NED": (57,  "Eredivisie"),            "NIR": (129, "NIR Premiership"),
    "NOR": (59,  "Eliteserien"),           "POL": (196, "Ekstraklasa"),
    "POR": (61,  "Primeira Liga"),         "ROU": (189, "Romanian Liga I"),
    "SCO": (64,  "Scottish Premiership"),  "SRB": (182, "Serbia Super Liga"),
    "SVK": (176, "Slovakia 1. liga"),      "SVN": (173, "Slovenia Prva Liga"),
    "ESP": (87,  "La Liga"),               "SWE": (67,  "Allsvenskan"),
    "SUI": (69,  "Swiss Super League"),    "TUR": (71,  "Süper Lig"),
    "UKR": (441, "Ukraine Premier League"),"WAL": (116, "Cymru Premier"),
}

EURO = {42: "UEFA Champions League", 73: "UEFA Europa League", 10216: "UEFA Conference League"}

# Europese seizoenen die de meting gebruikt. 2021/2022 is het eerste volledige seizoen na corona
# (2019/2020 en 2020/2021 werden deels zonder publiek en in afwijkende formats gespeeld), en
# 2025/2026 is het laatst afgeronde seizoen.
EURO_SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"]


def _fetch(league_id: int, season: str) -> dict:
    """Ruwe league-respons, gecached op schijf. Eén HTTP-verzoek per (competitie, seizoen)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{league_id}_{season.replace('/', '-')}.json"
    if path.exists():
        return json.loads(path.read_text())
    url = ("https://www.fotmob.com/api/data/leagues?id=" + str(league_id)
           + "&season=" + urllib.parse.quote(season, safe=""))
    data = _get_json(url)
    slim = {"table": data.get("table"), "allAvailableSeasons": data.get("allAvailableSeasons"),
            "fixtures": {"allMatches": (data.get("fixtures") or {}).get("allMatches")}}
    path.write_text(json.dumps(slim, ensure_ascii=False))
    time.sleep(0.3)
    return slim


def domestic_season(ccode: str, euro_season: str, available: list[str]) -> str | None:
    """Het laatst AFGERONDE binnenlandse seizoen vóór een Europees seizoen `YYYY/YYYY+1`.

    Najaar-voorjaarcompetities schrijven "2024/2025"; kalenderjaarcompetities (Scandinavië,
    de Baltische staten, Ierland, Kazachstan, Wit-Rusland, IJsland, Faeröer) schrijven "2024".
    Welke van de twee het is, blijkt uit de seizoenslijst van de competitie zelf — niet uit een
    lijst die hier wordt bijgehouden en die stilzwijgend kan verouderen.
    """
    start = int(euro_season[:4])
    for cand in (f"{start - 1}/{start}", str(start - 1)):
        if cand in available:
            return cand
    return None


def league_table(league_id: int, season: str) -> dict | None:
    """{team_id: {"gf","ga","played","home":{...},"away":{...},"name"}} plus competitiegemiddelden."""
    try:
        raw = _fetch(league_id, season)
    except FotmobError:
        return None
    table = _pick_table(raw.get("table") or [])
    if table is None:
        return None
    teams: dict[str, dict] = {}
    for side in ("home", "away"):
        for row in table.get(side, []):
            gf, ga = (int(x) for x in row["scoresStr"].split("-"))
            teams.setdefault(str(row["id"]), {"name": row["name"]})[side] = {
                "played": row["played"], "gf": gf, "ga": ga}
    tot_gf = tot_played = 0
    for row in table.get("all", []):
        gf, ga = (int(x) for x in row["scoresStr"].split("-"))
        t = teams.setdefault(str(row["id"]), {"name": row["name"]})
        t.update(gf=gf, ga=ga, played=row["played"], name=row["name"])
        tot_gf += gf
        tot_played += row["played"]
    teams = {k: v for k, v in teams.items() if v.get("played")}
    if not teams or not tot_played:
        return None
    return {"teams": teams, "goals_per_team_per_match": tot_gf / tot_played, "n_teams": len(teams)}


def main() -> int:
    # 1. seizoenslijsten ophalen (één verzoek per competitie, op een seizoen dat zeker bestaat)
    available: dict[str, list[str]] = {}
    for cc, (lid, name) in LEAGUES.items():
        try:
            raw = _fetch(lid, "2024/2025")
            av = raw.get("allAvailableSeasons") or []
            if not av:  # kalenderjaarcompetitie: 2024/2025 bestaat daar niet
                raw = _fetch(lid, "2024")
                av = raw.get("allAvailableSeasons") or []
            available[cc] = av
            print(f"  {cc} {name[:28]:28s} {len(av)} seizoenen, nieuwste {av[0] if av else '-'}")
        except FotmobError as exc:
            available[cc] = []
            print(f"  {cc} {name[:28]:28s} FOUT {exc}")

    # 2. binnenlandse standen per (competitie, benodigd seizoen)
    tables: dict[str, dict] = {}          # f"{cc}|{season}" -> league_table
    team_league: dict[str, dict] = {}     # f"{team_id}|{season}" -> cc
    for es in EURO_SEASONS:
        for cc, (lid, name) in LEAGUES.items():
            ds = domestic_season(cc, es, available.get(cc) or [])
            if ds is None or f"{cc}|{ds}" in tables:
                continue
            tbl = league_table(lid, ds)
            if tbl is None:
                print(f"  geen stand: {cc} {ds}")
                continue
            tables[f"{cc}|{ds}"] = tbl
            for tid in tbl["teams"]:
                team_league[f"{tid}|{ds}"] = cc
    print(f"\nbinnenlandse standen: {len(tables)} (competitie, seizoen)-combinaties, "
          f"{len(team_league)} ploegvermeldingen")

    # 3. Europese wedstrijden
    season_pool = {es: {s for s in (domestic_season(cc, es, available.get(cc) or [])
                                    for cc in LEAGUES) if s} for es in EURO_SEASONS}
    matches = []
    unmatched: dict[str, int] = {}
    for es in EURO_SEASONS:
        for lid, cname in EURO.items():
            try:
                raw = _fetch(lid, es)
            except FotmobError as exc:
                print(f"  {cname} {es}: FOUT {exc}")
                continue
            for m in (raw.get("fixtures") or {}).get("allMatches") or []:
                st = m.get("status") or {}
                if not st.get("finished") or st.get("cancelled") or st.get("awarded"):
                    continue
                score = (st.get("scoreStr") or "").replace(" ", "")
                if "-" not in score:
                    continue
                try:
                    hg, ag = (int(x) for x in score.split("-"))
                except ValueError:
                    continue
                hid, aid = str(m["home"].get("id")), str(m["away"].get("id"))
                rec = {"euro_season": es, "competition": cname, "round": m.get("roundName"),
                       "utc": st.get("utcTime"), "match_id": m.get("id"),
                       # scoreStr is de EINDstand: bij een knock-outduel zit verlenging erin
                       # (en soms strafschoppen). §6d rekent af op 90 minuten, dus de meting
                       # gebruikt alleen duels die op "FT" staan. De code wordt hier vastgelegd
                       # zodat het filter in de fit zit en het aantal te rapporteren is.
                       "reason": ((st.get("reason") or {}).get("short") or "").upper(),
                       "home_id": hid, "away_id": aid,
                       "home": m["home"]["name"], "away": m["away"]["name"],
                       "hg": hg, "ag": ag}
                matches.append(rec)
                ds_any = season_pool[es]
                for tid, nm in ((hid, rec["home"]), (aid, rec["away"])):
                    if not any(f"{tid}|{s}" in team_league for s in ds_any):
                        unmatched[nm] = unmatched.get(nm, 0) + 1
    print(f"Europese wedstrijden met uitslag: {len(matches)}")
    top = sorted(unmatched.items(), key=lambda kv: -kv[1])[:15]
    print(f"ploegen zonder binnenlandse stand: {len(unmatched)} — grootste: {top}")

    OUT.write_text(json.dumps({"leagues": {cc: {"id": v[0], "name": v[1]} for cc, v in LEAGUES.items()},
                               "available": available, "tables": tables,
                               "team_league": team_league, "matches": matches},
                              ensure_ascii=False))
    print(f"\n{OUT} geschreven ({OUT.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
