import json
from scripts import fotmob
FIX=json.load(open('tmp-run/rb_fixtures.json'))
BASE={"Greek Super League (GRE)":(135,"2025/2026"), "Allsvenskan (SWE)":(67,"2026"),
      "Croatian HNL (CRO)":(252,"2025/2026"), "Romanian SuperLiga (ROU)":(189,"2025/2026"),
      "Segunda Division (ESP)":(140,"2025/2026"), "Keuken Kampioen Divisie (NED)":(111,"2025/2026"),
      "Kategoria Superiore (ALB)":(260,"2025/2026")}
cache={}
for comp,(lid,s) in BASE.items():
    cache[comp]=fotmob.fetch_league_stats(lid,s)
    print(f"== {comp} [{s}] ==")
    print("   ", sorted(cache[comp]['teams'].keys()))
print()
print("=== ONTBREKENDE PLOEGEN ===")
for f in FIX:
    t=cache[f['comp']]['teams']
    for side in ('home','away'):
        if f[side] not in t:
            print(f"  {f['comp']:30} {f[side]!r} NIET in tabel")
