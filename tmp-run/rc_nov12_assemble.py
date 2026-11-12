import json, copy
from scripts import toplist
DAY = "2026-11-12"
P = "data/run-state/2026-11-12-run-c.json"
state = json.load(open(P))
res = json.load(open("tmp-run/rc_nov12_pass.json"))
REN = {"AFCON-kwalificatie (id 10608)": "CAF Afrika Cup-kwalificatie (id 10608)"}
ORDER = ["Vriendschappelijke interlands (id 114)", "UEFA Nations League A (id 9806)", "UEFA Nations League B (id 9807)",
         "UEFA Nations League C (id 9808)", "UEFA Nations League D (id 9809)", "CONCACAF Nations League (id 9821)",
         "CAF Afrika Cup-kwalificatie (id 10608)", "Arabian Gulf Cup (id 329)", "FIFA ASEAN Cup (id 13287)",
         "SAFF Championship (id 9876)"]
MK = ["1X2", "DC", "DNB", "AH", "OU", "BTTS"]; KIND = {"1X2": "1x2", "DC": "dc", "DNB": "dnb", "AH": "ah", "OU": "ou", "BTTS": "btts"}
comps = {k: {"status": "GEEN WEDSTRIJD", "matches": []} for k in ORDER}
for comp, rs in res.items():
    cid = REN.get(comp, comp); out = []
    for r in rs:
        r = copy.deepcopy(r); r["competition"] = cid
        if r["tier"] == "NONE":
            r.update(bet=False, reden=f"national.in_range faalt: {r['data_reason']}",
                     markets_checked={m: f"NONE — landenrating buiten bereik ({r['data_reason'].split(':')[0]})" for m in MK})
        elif r.get("buiten_datadekking"):
            r.update(tier="BUITEN_DATADEKKING", bet=False,
                     reden="geen prijsbron: geen sportkey bij The Odds API voor de CONCACAF Nations League en het duel staat niet op BetExplorers CONCACAF NL-pagina",
                     markets_checked={m: "BUITEN DATADEKKING — geen prijsbron voor dit duel" for m in MK})
        else:
            kinds = {c["kind"] for c in r["all_candidates"]}; src = r["odds_source_kind"]; mc = {}
            for m in MK:
                k = KIND[m]
                if k in kinds:
                    mc[m] = ("doorgerekend — The Odds API (beste prijs, netto)" + (" — per-wedstrijdmarkt btts (1 credit, kandidaat-edge)" if k == "btts" else "")) if src == "oddsapi" else "doorgerekend — BetExplorer marktgemiddelde"
                elif src == "oddsapi":
                    mc[m] = ("niet opgevraagd — geen kandidaat-edge in dit duel" if k == "btts" and not r.get("kandidaat_edge_voor_btts")
                             else f"niet beschikbaar — geen {m}-lijn bij The Odds API voor dit duel")
                else:
                    mc[m] = "niet opgevraagd — geen sportkey bij The Odds API voor deze competitie (alleen BetExplorer 1X2)"
            r["markets_checked"] = mc
            r["odds_source"] = ("The Odds API (beste prijs, netto)" if src == "oddsapi" else r["all_candidates"][0]["odds_source"])
            ps = ["scripts/national.py — landenrating (7086 interlands, herfit 12 nov 2026; scale=1.0)"]
            ps.append("scripts/squadform.py — selectiewaarde (tweede methode, 0.30; selecties opgehaald 12 nov 2026)" if not r["poort5_niet_gemeten"]
                      else "scripts/squadform.py — selectiewaarde NIET bruikbaar bij een of beide ploegen: poort 5 niet gemeten")
            r["prob_sources"] = ps
            wb = [c for c in r["all_candidates"] if c["would_block_underdog"]]
            if wb: r["poort8_vervallen"] = [{"market": c["market"], "selection": c["selection"], "odds": c["odds"], "underdog_reason": c["underdog_reason"], "gepubliceerd": False} for c in wb]
            r["bet"] = False
        out.append(r)
    comps[cid] = {"status": "GEANALYSEERD", "matches": out}
state["competitions"] = comps
state["parameters"] = {"MAX_DEEP_ANALYSES": 40, "MAX_SHORTLIST": 3, "dag_type": "doordeweeks (donderdag)",
                       "EDGE_THRESHOLD_LIGHT": 16.0, "NEAR_LIGHT": 6.0, "MAX_LIGHT_IN_SHORTLIST": "n.v.t. voor Run C", "scale": 1.0}
state["credits"] = {"markten_gekocht": {"soccer_uefa_nations_league": "bulk h2h+spreads+totals (3 credits); btts per duel voor 5 kandidaat-duels (5 credits)"},
                    "totaal_credits": 8, "plafond": 539, "over_na_run": 19430}
state["uitgesloten_competities"] = {"10437": "EURO U21 Qualification Playoff — U21 (1 duel op 12 nov, 3 op 13 nov)",
    "344": "Friendlies U21 — U21 (2 op 12 nov, 4 op 13 nov)", "9375": "Women's Champions League — Women (2)",
    "11129": "UEFA Women's Europa Cup - 8th Finals — Women (1)", "489": "Club Friendlies — clubteams, niet gebruiken (4)",
    "BetExplorer": "op de oefenpagina U19/U20/U21/U23-duels (Thailand U23 – Qatar U23, Scotland U21 – Ukraine U21 e.a.) geweerd"}
state["onderhoud"] = {"national.py build+fit": "7086 duels (was 6784, t/m 18 sep); verify OK", "squadform.py build": "213 selecties, 118 bruikbaar; verify OK (was 24 sep)"}
# toplijst bepaalt de bets (§5b)
tl = toplist.build(state)
bets = {(r["match"], r["market"], r["selection"]) for r in tl["herijkt"]}
for comp in comps.values():
    for m in comp["matches"]:
        for c in m.get("all_candidates", []):
            if (m["match"], c["market"], c["selection"]) in bets:
                m["bet"] = True; m["_bet"] = c
json.dump(state, open(P, "w"), indent=1, ensure_ascii=False)
print(json.dumps(tl["herijkt"], ensure_ascii=False, indent=1)); print("ruw:", [(r["match"], r["selection"], r["edge_pp"], r["status"]) for r in tl["ruw"]])
