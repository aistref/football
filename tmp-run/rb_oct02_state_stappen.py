"""Stage 5 stap 1 en 2 vastleggen in `data/run-state/` (§3 Stage 5, 20 sep 2026).

Overgenomen van `rb_oct01_state_stappen.py`, maar nu voor **alle drie** de duels van de run in
plaats van voor het enige duel van 1 oktober — ook voor Eldense – Real Oviedo, dat op NONE
uitkomt. Dat laatste is geen verspilling: het dossier is gratis (Fotmob) en §1c eist dat de
context van élke wedstrijd waarvoor hij is opgehaald wordt vastgelegd, ook als het duel niet is
doorgerekend. Het dossier hoort bij diezelfde steekproef.

Stap 2 blijft wat §3 Stage 5 ervan meet: geschreven voorspellingen zijn grotendeels niet te
halen, en wat er wél is, is de de-vigde 1X2 van Pinnacle plus de `insights` van Fotmob. Alles
daaruit is marktafgeleid en blijft buiten `my_prob` en `prob_sources` (§2).
"""
import dataclasses, json
from datetime import date
from scripts import calibration, dossier
from scripts.progress import load_or_start, mark, save

odds = json.load(open("tmp-run/rb_oct02_odds.json"))
res = json.load(open("tmp-run/rb_oct02_results.json"))

GEEN_PRIJSBRON = (
    "Niet gehaald, en dat is de gemeten stand van §3 Stage 5 sinds 20 sep 2026: Pinnacle 404, "
    "Matchbook 530, Betfair/Forebet 403 achter Cloudflare, voetbalwedden.net 200 maar zonder de "
    "wedstrijden van de dag, xgscore 0 regels. Er is dus geen enkele externe modelkans of "
    "geschreven tip in deze run meegewogen.")


def boeken_van(comp, home_hint, away_hint):
    """{boek: {odds, marge, devig}} uit de h2h-respons van The Odds API, of {}."""
    evs = (odds["raw"].get("h2h") or {}).get(comp) or []
    ev = next((e for e in evs
               if home_hint.lower() in e["home_team"].lower()
               and away_hint.lower() in e["away_team"].lower()), None)
    if ev is None:
        return {}
    uit = {}
    for b in ev["bookmakers"]:
        for m in b["markets"]:
            if m["key"] != "h2h":
                continue
            d = {x["name"]: x["price"] for x in m["outcomes"]}
            tri = [d.get(ev["home_team"]), d.get("Draw"), d.get(ev["away_team"])]
            if all(tri):
                uit[b["title"]] = {"odds": tri,
                                   "marge": round(sum(1 / x for x in tri) - 1, 4),
                                   "devig": [round(x, 4) for x in calibration.devig(tri)]}
    return uit


HINTS = {5103566: ("Sao Paulo", "Santos"),
         5868475: ("Eldense", "Oviedo"),
         5832887: ("Helmond", "Heracles")}

state = load_or_start("b", date(2026, 10, 2))
blokken = state.get("done") or state.get("competitions")

for m in res["matches"]:
    mid = m["match_id"]
    try:
        dos = dataclasses.asdict(dossier.build(mid))
    except Exception as e:
        dos = {"error": f"{type(e).__name__}: {e}"}
    hh, ha = HINTS.get(mid, (m["home"], m["away"]))
    boeken = boeken_van(m["competition"], hh, ha)
    stap2 = {
        "geschreven_voorspellingen": GEEN_PRIJSBRON,
        "pinnacle_devig": boeken.get("Pinnacle"),
        "scherpste_marges": sorted(
            ({"boek": k, "marge_pct": round(v["marge"] * 100, 2), "devig": v["devig"]}
             for k, v in boeken.items()), key=lambda r: r["marge_pct"])[:6],
        "n_boeken": len(boeken),
        "fotmob_insights": dos.get("insights"),
        "let_op": ("Marktafgeleid — buiten `my_prob` en buiten `prob_sources` gehouden (§2). Dit "
                   "is de meetlat waaraan de eigen kans wordt getoetst, niet een invoer ervoor."),
    }
    if boeken:
        stap2["consensus_thuis"] = {
            "min": round(min(v["devig"][0] for v in boeken.values()), 4),
            "max": round(max(v["devig"][0] for v in boeken.values()), 4),
            "mediaan": round(sorted(v["devig"][0] for v in boeken.values())[len(boeken) // 2], 4)}
    else:
        stap2["consensus_thuis"] = None
        stap2["n_boeken_reden"] = (
            "geen h2h-respons bij The Odds API voor deze competitie (geen sportkey) — het "
            "marktoordeel komt hier van het BetExplorer-gemiddelde, niet per boek"
            if not (odds["raw"].get("h2h") or {}).get(m["competition"])
            else "deze wedstrijd stond niet in de h2h-respons")

    comp = m["competition"]
    blok = blokken[comp]
    for mm in blok["matches"]:
        if mm["match_id"] == mid:
            mm["dossier"] = ({k: dos[k] for k in
                              ("h2h_summary", "h2h_matches", "insights", "form", "unavailable",
                               "lineup_type", "weather", "table_note", "notes") if k in dos}
                             or dos)
            mm["stap2_wat_anderen_voorspellen"] = stap2
    mark(state, comp, blok)
    print(f"{m['match'][:34]:34s} boeken={len(boeken):3d} pinnacle="
          f"{(stap2['pinnacle_devig'] or {}).get('devig')} insights={len(dos.get('insights') or [])}")

save(state)
print("stap 1 en 2 vastgelegd voor", len(res["matches"]), "wedstrijden")
