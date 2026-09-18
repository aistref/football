"""Hulpstuk: dekkingstabel en wedstrijdsecties voor runs/2026-09-18-run-b.md uit run-state.

Overtypen is de fout die §5 en §6c allebei benoemen — dit leest dezelfde bron als report.py.
"""
import json
from datetime import date

ST = json.load(open("data/run-state/2026-09-18-run-b.json"))
RES = {m["match"]: m for m in json.load(open("tmp-run/rb18_results.json"))["matches"]}

pp = lambda x: f"{x:+.2f}".replace(".", ",") + " pp"

cov, secs = [], []
cov.append("| Competitie | Status | Toelichting |")
cov.append("|---|---|---|")
for comp, b in ST["competitions"].items():
    st = b["status"]
    if st == "GEEN WEDSTRIJD":
        toel = "niets op de kalender vandaag (Fotmob-daglijst)"
    else:
        n = len(b["matches"])
        tiers = {}
        for m in b["matches"]:
            tiers[m["tier"]] = tiers.get(m["tier"], 0) + 1
        toel = f"{n} wedstrijd(en) — " + ", ".join(f"{v}× `{k}`" for k, v in sorted(tiers.items()))
        sel = sum(m.get("candidates_evaluated", 0) for m in b["matches"])
        toel += f"; {sel} selecties doorgerekend, 0 bets"
    cov.append(f"| {comp} | `{st}` | {toel} |")

for comp, b in ST["competitions"].items():
    if b["status"] == "GEEN WEDSTRIJD":
        continue
    for m in sorted(b["matches"], key=lambda x: x["kickoff_utc"]):
        secs.append(f'### {m["match"]} · {m["kickoff_nl"]} · {comp}\n')
        if m["tier"] == "NONE":
            secs.append("Data: `NONE`\n")
            secs.append(f'**GEEN BET** — {m.get("reden")}\n')
            secs.append("")
            continue
        secs.append(f'Data: `{m["tier"]}` · datarijkdom {m["datarijkdom"]["score"]} · '
                    f'{m.get("candidates_evaluated", 0)} selecties doorgerekend\n')
        secs.append(f'**GEEN BET** — {m.get("reden")}\n')
        nm = m.get("near_miss")
        if nm:
            secs.append(f'Net niet: {nm["market"]} @ {nm["odds"]:.2f} — xG-model {pp(nm["edge_xg"])}, '
                        f'2e methode {pp(nm["edge_split"])}, zwakste stand {nm["edge_robust_min"]:.2f}, '
                        f'herijkt {pp(nm["edge_pp"])} (valt af op `{nm["failed_gate"]}`).\n')
        for row in (m.get("poort8_geblokkeerd") or []):
            secs.append(f'Poort 8 hield tegen: {row["market"]} @ {row["odds"]:.2f} — '
                        f'xG-model {pp(row["edge_xg"])}, 2e methode {pp(row["edge_split"])}, '
                        f'zwakste stand {row["edge_robust_min"]:.2f}, herijkt {pp(row["edge_pp"])}; '
                        f'{row["reden"]}\n')
        for row in (m.get("zonder_herijking") or []):
            secs.append(f'Zonder de herijking een bet: {row["market"]} @ {row["odds"]:.2f} — '
                        f'ruw {pp(row["edge_pp"])}, herijkt {pp(row["edge_pp_herijkt"])}, '
                        f'zwakste stand {row["edge_robust_min"]:.2f}.\n')
        for row in (m.get("poort8_ruw") or []):
            secs.append(f'Poort 8 op de ruwe schaal: {row["market"]} @ {row["odds"]:.2f} — '
                        f'ruw {pp(row["edge_pp"])}, herijkt {pp(row["edge_pp_herijkt"])}; '
                        f'{row["reden"]}\n')
        if m.get("verplaatst"):
            secs.append(f'Verplaatst: {m["verplaatst"].get("note")}\n')
        if m.get("beste_prijs_winst_pct"):
            secs.append(f'Beste prijs t.o.v. het marktgemiddelde: +{m["beste_prijs_winst_pct"]:.2f}%.\n')
        secs.append("")

open("tmp-run/rb18_coverage.md", "w").write("\n".join(cov))
open("tmp-run/rb18_matches.md", "w").write("\n".join(secs))
print("\n".join(cov))
print()
print("\n".join(secs))
