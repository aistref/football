# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0,'.')
ST=json.load(open("data/run-state/2026-09-05-run-b.json"))
A=json.load(open("tmp-run/c_analysis.json"))
out=[]
# dekkingstabel
out.append("| Competitie | Status | Toelichting |")
out.append("|---|---|---|")
for comp,b in ST["competitions"].items():
    out.append(f'| {comp} | `{b["status"]}` | {b["toelichting"]} |')
open("tmp-run/c_coverage.md","w").write("\n".join(out))

# wedstrijden
sec=[]
for comp,b in ST["competitions"].items():
    ms=[m for m in b["matches"] if not m.get("afgekapt")]
    if not ms: continue
    sec.append(f"\n### {comp}\n")
    for m in sorted(ms,key=lambda x:x["kickoff_utc"]):
        k=m["match"]; r=A.get(k,{})
        sec.append(f'#### {k} · {m["kickoff_nl"]} · {comp}')
        if m["tier"]=="NONE":
            sec.append(f'- **Data:** NONE')
            sec.append(f'- **GEEN BET** — {m["reden"]}\n')
            continue
        if m.get("pick"):
            p=m["pick"]
            sec.append(f'- **Data:** {m["tier"]}')
            sec.append(f'- **Bet:** {p["market"]} — {p["selection"]} — Odds: best {p["odds"]:.2f} ({p["odds_source"]})')
            sec.append(f'- **Implied prob:** {p["implied"]*100:.1f}% • **My prob:** {p["my_prob"]*100:.1f}%')
            sec.append(f'- **Edge:** {p["edge_pp"]:+.2f} pp (xG-methode {p["edge_xg"]:+.2f}, splitsmethode {p["edge_split"]:+.2f}, zwakste stand van het grid {p["edge_robust_min"]:+.2f}) • **selection_score:** {p["score"]:.2f}')
            s=m.get("second")
            sec.append(f'- **Tweede selectie:** {s["market"]} — {s["selection"]} (score {s["score"]:.2f}, ook gekwalificeerd)' if s else '- **Tweede selectie:** geen andere selectie haalde alle acht de poorten')
            sec.append(f'- **Inputs:** {m["inputs"]["home"]} · {m["inputs"]["away"]}')
            sec.append(f'- **Context:** {m["context"]["lineup_type"]} — thuis {m["context"]["home_summary"]}; uit {m["context"]["away_summary"]}\n')
        else:
            sec.append(f'- **Data:** {m["tier"]}')
            sec.append(f'- **GEEN BET** — {m["reden"]}\n')
open("tmp-run/c_matches.md","w").write("\n".join(sec))

# net niet
nm=[]
for comp,b in ST["competitions"].items():
    for m in b["matches"]:
        if m.get("near_miss"): nm.append((comp,m["match"],m["near_miss"]))
nm.sort(key=lambda t:-t[2]["edge_pp"])
t=["| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |","|---|---|---|---|---|---|"]
for comp,k,x in nm:
    rb=f'{x["edge_robust_min"]:+.2f} pp' if isinstance(x["edge_robust_min"],(int,float)) else "—"
    t.append(f'| {k} | {x["market"]} @ {x["odds"]:.2f} | {x["edge_xg"]:+.2f} pp | {x["edge_split"]:+.2f} pp | {rb} | `{x["failed_gate"]}` |')
open("tmp-run/c_nearmiss.md","w").write("\n".join(t))

# topselectie
bets=[(c,m) for c,b in ST["competitions"].items() for m in b["matches"] if m.get("pick")]
bets.sort(key=lambda t:-t[1]["pick"]["score"])
tl=["| # | Bet | Probability | Edge | Score | Risicoklasse | Waarom deze |","|---|---|---|---|---|---|---|"]
open("tmp-run/c_top.md","w").write("\n".join(tl))
for i,(c,m) in enumerate(bets,1):
    p=m["pick"]; print(i, m["match"], p["market"], p["selection"], p["odds"], f'{p["my_prob"]*100:.1f}%', f'{p["edge_pp"]:+.2f}', f'{p["score"]:.2f}')
print("secties geschreven")
