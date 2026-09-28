"""§5b-opruiming: een op rangorde gepubliceerde bet mag niet ook als schaduwpick tellen.

Het analysescript toetst de edge-drempel nog als poort en schrijft een `near_miss` op `edge` voor
elke selectie die eronder blijft. Onder §5b (20 sep 2026) is die drempel géén poort meer maar een
afkapping: staan er minder selecties boven de drempel dan er regels in de lijst passen, dan bepaalt
de rangorde de lijst en gaat de drempel per regel mee als label. Vandaag haalde één selectie haar
drempel en zijn er vier gepubliceerd — dus drie gepubliceerde bets hadden óók een `near_miss` op
`edge`, en `shadow.py collect` heeft ze als schaduwpick weggeschreven.

Dat is precies de dubbeltelling die §1e en §5a verbieden ("nooit dezelfde selectie twee keer"):
dezelfde selectie zou dan zowel in `picks.jsonl` als in `shadow.jsonl` worden afgerekend, en de
reeks `viel af op: edge` zou winnaars gaan bevatten die in werkelijkheid gewoon gespeeld zijn.
"""
import json

DAG = "2026-09-27"
picks = [json.loads(l) for l in open("data/picks.jsonl") if l.strip()]
vandaag = {(p["home"] + " – " + p["away"], p["market"], round(p["odds"], 4))
           for p in picks if p["run_date"] == DAG and p["run"] == "B"}
print("gepubliceerde bets vandaag:", len(vandaag))

# 1. schaduwrijen van vandaag die een gepubliceerde bet beschrijven eruit halen
rows, weg = [], []
for l in open("data/shadow.jsonl"):
    l = l.strip()
    if not l:
        continue
    o = json.loads(l)
    if o.get("date") == DAG and o.get("run") == "B":
        markt = (o.get("market") or "").split(" — ")[0]
        sleutel = (o["match"], markt, round(o.get("odds") or 0, 4))
        if sleutel in vandaag:
            weg.append(o["id"]); continue
    rows.append(o)
with open("data/shadow.jsonl", "w") as f:
    for o in rows:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print("schaduwrijen verwijderd:", len(weg))
for i in weg:
    print("   ", i)

# 2. run-state: die drie zijn bets, geen afgewezen kandidaten
pad = f"data/run-state/{DAG}-run-b.json"
st = json.load(open(pad))
namen = {k[0] for k in vandaag}
n = 0
for comp in st["competitions"].values():
    for m in comp.get("matches", []):
        if m.get("match") in namen and not m.get("bet"):
            nm = m.get("near_miss")
            m["bet"] = True
            m["gepubliceerd_op_rangorde"] = {
                "waarom": ("§5b: deze selectie blijft onder haar edge-drempel maar haalt alle acht "
                           "poorten, en er stonden minder selecties boven de drempel dan er regels "
                           "in de lijst passen. De rangorde bepaalt dan de lijst en de drempel gaat "
                           "mee als label."),
                "poortcijfers": nm,
            }
            m["near_miss"] = None
            m["reason"] = ("gepubliceerd op rangorde (§5b), onder de drempel van "
                           f"{8.0 if m.get('tier') == 'FULL' else 16.0} pp")
            n += 1
json.dump(st, open(pad, "w"), ensure_ascii=False, indent=1)
print("run-state: near_miss omgezet naar gepubliceerd_op_rangorde voor", n, "wedstrijd(en)")
