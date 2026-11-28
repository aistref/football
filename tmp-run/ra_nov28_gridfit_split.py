"""§6g punt 4 — de niveaucorrectie apart meten op de duels van ná 3 nov 2026.

`gridfit.py measure` draait op alle homogene duels sinds de shrink-overstap, en dat is sinds
3 november geen homogene populatie meer op het NIVEAU: de lambdas van ná die datum dragen
`model.LEVEL_SCALE` = 1.032 al in zich. §6g punt 4 eist daarom dat de vraag "werkt de correctie"
op alléén die duels wordt gelezen. Dit script knipt de reeks op `gridfit.LEVEL_SWITCH` en meet
beide helften apart, met dezelfde `gridfit.measure` als de gewone meting.
"""
from scripts import gridfit

rows = gridfit.load()
na = [r for r in rows if r["date"] >= gridfit.LEVEL_SWITCH]
voor = [r for r in rows if r["date"] < gridfit.LEVEL_SWITCH]
print(f"na {gridfit.LEVEL_SWITCH}: {len(na)}  tussen {gridfit.SHRINK_SWITCH} en {gridfit.LEVEL_SWITCH}: {len(voor)}")
gridfit.measure(na, f"ALLEEN DE DUELS MET DE NIVEAUCORRECTIE (vanaf {gridfit.LEVEL_SWITCH})")
gridfit.measure(voor, f"VERGELIJKING: {gridfit.SHRINK_SWITCH} t/m 2026-11-02, zonder de correctie")
