"""Bouwt de mechanische secties van runs/2026-08-30-run-b.md."""
import json, sys
sys.path.insert(0, "tmp-run")

res = json.load(open("tmp-run/rb_results.json"))
odds = json.load(open("tmp-run/rb_odds.json"))
fx = json.load(open("tmp-run/rb_fixtures.json"))
stats = json.load(open("tmp-run/rb_stats.json"))
matches = res["matches"]
state = json.load(open("data/run-state/2026-08-30-run-b.json"))
picks = [json.loads(l) for l in open("data/picks.jsonl") if '"run_date": "2026-08-30"' in l and '"run": "B"' in l]
pick_by_id = {pk["id"]: pk for pk in picks}
meta = {}
for comp, e in state["competitions"].items():
    for mm in e.get("matches", []):
        if mm.get("pick_id"):
            meta[mm["match"]] = {"risk": mm.get("risico"), "short": mm.get("shortlisted"),
                                 "conf": pick_by_id[mm["pick_id"]]["confidence"]}
for m in matches:
    if m.get("bet"):
        m["_risk"] = meta[m["match"]]["risk"]
        m["_shortlisted"] = meta[m["match"]]["short"]
        m["_confidence"] = meta[m["match"]]["conf"]

RUNLIJST = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
            "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
            "Romanian SuperLiga (ROU)", "Segunda División (ESP)", "Serie B (ITA)",
            "2. Bundesliga (GER)", "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
            "Keuken Kampioen Divisie (NED)", "English League One (ENG)", "English League Two (ENG)",
            "Kategoria Superiore (ALB)", "Kosovo Superleague (KOS)"]

out = []
out.append("| Competitie | Status | Toelichting |\n|---|---|---|")
for comp in RUNLIJST:
    ms = [m for m in matches if m["competition"] == comp]
    if not ms:
        reden = {"English League Two (ENG)": "niets op de Fotmob-daglijst; League Two speelde gisteren",
                 "Kosovo Superleague (KOS)": "niet op de Fotmob-daglijst — dekkingsgat sinds 13 aug ongewijzigd"}[comp]
        out.append(f"| {comp} | GEEN WEDSTRIJD | {reden} |"); continue
    n = len(ms)
    done = [m for m in ms if not m.get("afgekapt") and m["tier"] != "NONE"]
    none_ = [m for m in ms if m["tier"] == "NONE"]
    cut = [m for m in ms if m.get("afgekapt")]
    b = sum(1 for m in ms if m.get("bet"))
    tier = "FULL" if any(m["tier"] == "FULL" for m in ms) else "LIGHT"
    bits = [f"{n} wedstrijd" + ("en" if n > 1 else ""), f"{len(done)} doorgerekend ({tier})"]
    if none_: bits.append(f"{len(none_)} op tier NONE")
    if cut: bits.append(f"{len(cut)} afgekapt")
    bits.append(f"{b} bet" + ("s" if b != 1 else "") if b else "geen bet")
    status = "GEANALYSEERD" if done else ("AFGEKAPT" if cut else "BUITEN DATADEKKING")
    out.append(f"| {comp} | {status} | {' · '.join(bits)} |")
print("\n".join(out)); print()

print("## Marktbalans\n")
print("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |\n|---|---|---|---|")
fam = {"1X2": 0, "Asian Handicap": 0, "Draw No Bet": 0, "Double Chance": 0, "Over/Under": 0, "BTTS": 0}
bets_fam = dict(fam)
comps_fam = {k: set() for k in fam}
for m in matches:
    if m.get("afgekapt") or m["tier"] == "NONE":
        continue
    for c in m.get("all_candidates", []):
        pass
    for c in m.get("all_candidates", []):
        fam[c["market"]] += 1
        comps_fam[c["market"]].add(m["competition"])
    if m.get("bet"):
        bets_fam[m["pick"]["market"]] += 1
# all_candidates is afgetopt op 12; tel echt door via candidates_evaluated per markt niet mogelijk -> meld
print("<!-- let op: all_candidates is per wedstrijd afgetopt op 12 -->")
for k in fam:
    print(f"| {k} | {len(comps_fam[k])} | {fam[k]} | {bets_fam[k]} |")
print()

print("## Topselectie\n")
bets = sorted([m for m in matches if m.get("bet")], key=lambda m: -m["pick"]["score"])
print("| # | Bet | My prob | Edge | Score | Risicoklasse | Data |\n|---|---|---|---|---|---|---|")
for i, m in enumerate(bets, 1):
    p = m["pick"]
    tag = " **(topselectie)**" if m.get("_shortlisted") else ""
    print(f"| {i} | {m['match']} — {p['market']}: {p['selection']} @ {p['odds']}{tag} | "
          f"{p['my_prob']*100:.1f}% | {p['edge_pp']:+.1f} pp | {p['score']} | {m.get('_risk','')} | {m['tier']} |")
print()

print("## Net niet\n")
print("| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |\n|---|---|---|---|---|---|")
for m in matches:
    nm = m.get("near_miss")
    if not nm: continue
    rb = nm["edge_robust_min"]
    print(f"| {m['match']} | {nm['market']} @ {nm['odds']} | {nm['edge_xg']:+.2f} pp | "
          f"{nm['edge_split']:+.2f} pp | {(f'{rb:+.2f} pp' if rb is not None else 'niet berekend')} | {nm['failed_gate']} |")
print()

print("## Wedstrijden (compact)\n")
for comp in RUNLIJST:
    ms = [m for m in matches if m["competition"] == comp]
    if not ms: continue
    print(f"### {comp}\n")
    for m in sorted(ms, key=lambda m: m["kickoff_utc"]):
        head = f"**{m['match']}** · {m['kickoff_nl']} · {m['tier']}"
        if m.get("bet"):
            p = m["pick"]
            print(f"- {head}\n  - **Bet:** {p['market']} — {p['selection']} — odds **{p['odds']}** ({p['odds_source']})\n"
                  f"  - Implied {p['implied']*100:.1f}% • My prob {p['my_prob']*100:.1f}% • Edge {p['edge_pp']:+.1f} pp "
                  f"(xG {p['edge_xg']:+.1f} / splits {p['edge_split']:+.1f} / zwakste stand {p['edge_robust_min']:+.1f}) "
                  f"• Confidence {m['_confidence']}\n"
                  f"  - Datarijkdom {m['richness']}/10 · {m['candidates_evaluated']} selecties doorgerekend"
                  + (f" · tweede: {m['runner_up']['selection']} (score {m['runner_up']['score']})" if m.get("runner_up") else " · geen tweede door alle poorten"))
        else:
            print(f"- {head} — **GEEN BET** — {m.get('reason','')}")
    print()
