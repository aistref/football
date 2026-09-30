"""Stage 5 stap 1 en 2 vastleggen in `data/run-state/` (§3 Stage 5, 20 sep 2026).

De analyse begint bij de wedstrijd en niet bij de koers: stap 1 is het wedstrijddossier
(`scripts/dossier.py`), stap 2 is wat anderen voorspellen. Van stap 2 is in de praktijk vrijwel
niets te halen (§3 Stage 5, de tabel met 404/403/530) — wat er wél is, is de **de-vigde 1X2 van
Pinnacle** als het scherpste publieke expertoordeel, plus de `insights` van Fotmob. Die horen
vastgelegd naast de eigen kans, en uitdrukkelijk NIET erin: alles uit stap 2 en 3 is
marktafgeleid en mag `my_prob` of `prob_sources` niet raken (§2).
"""
import dataclasses, json
from datetime import date
from scripts import calibration, dossier
from scripts.progress import load_or_start, mark, save

MATCH_ID = 5071384
odds = json.load(open("tmp-run/rb30_odds.json"))
ev = [e for e in odds["raw"]["h2h"]["MLS (USA)"]
      if "Red Bulls" in e["home_team"] and "Louis" in e["away_team"]][0]

boeken = {}
for b in ev["bookmakers"]:
    for m in b["markets"]:
        if m["key"] != "h2h":
            continue
        d = {x["name"]: x["price"] for x in m["outcomes"]}
        tri = [d.get("New York Red Bulls"), d.get("Draw"), d.get("St. Louis City SC")]
        if all(tri):
            boeken[b["title"]] = {"odds": tri, "marge": round(sum(1 / x for x in tri) - 1, 4),
                                  "devig": [round(x, 4) for x in calibration.devig(tri)]}

dos = dataclasses.asdict(dossier.build(MATCH_ID))
stap2 = {
    "geschreven_voorspellingen": (
        "Niet gehaald, en dat is de gemeten stand van §3 Stage 5 sinds 20 sep 2026: Pinnacle "
        "404, Matchbook 530, Betfair/Forebet 403 achter Cloudflare, voetbalwedden.net 200 maar "
        "zonder de wedstrijden van de dag, xgscore 0 regels. Voor een MLS-duel om 01:30 NL is "
        "er bovendien geen Nederlandstalige tipwebsite die er iets over schrijft. Er is dus "
        "geen enkele externe modelkans of geschreven tip in deze run meegewogen."),
    "pinnacle_devig": boeken.get("Pinnacle"),
    "scherpste_marges": sorted(
        ({"boek": k, "marge_pct": round(v["marge"] * 100, 2), "devig": v["devig"]}
         for k, v in boeken.items()), key=lambda r: r["marge_pct"])[:6],
    "n_boeken": len(boeken),
    "consensus_thuis": {
        "min": round(min(v["devig"][0] for v in boeken.values()), 4),
        "max": round(max(v["devig"][0] for v in boeken.values()), 4),
        "mediaan": round(sorted(v["devig"][0] for v in boeken.values())[len(boeken) // 2], 4)},
    "fotmob_insights": dos["insights"],
    "let_op": ("Marktafgeleid — buiten `my_prob` en buiten `prob_sources` gehouden (§2). Dit is "
               "de meetlat waaraan de eigen kans wordt getoetst, niet een invoer ervoor."),
}

state = load_or_start("b", date(2026, 9, 30))
blok = state["done"]["MLS (USA)"] if "done" in state else state["competitions"]["MLS (USA)"]
for m in blok["matches"]:
    if m["match_id"] == MATCH_ID:
        m["dossier"] = {k: dos[k] for k in
                        ("h2h_summary", "h2h_matches", "insights", "form", "unavailable",
                         "lineup_type", "weather", "table_note", "notes")}
        m["stap2_wat_anderen_voorspellen"] = stap2
mark(state, "MLS (USA)", blok)
save(state)
print("Pinnacle de-vig:", stap2["pinnacle_devig"])
print("consensus thuis:", stap2["consensus_thuis"], f"over {stap2['n_boeken']} boeken")
print("dossier-notes:", dos["notes"])
