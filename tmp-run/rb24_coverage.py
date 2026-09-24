import json
from pathlib import Path
P = Path("data/coverage.json")
d = json.loads(P.read_text())
c = d["competitions"]["MLS (USA)"]
c["notes"] += (
 " Run B 24 sep 2026, eerste keer dat deze competitie werkelijk is doorgerekend: xG opnieuw "
 "bevestigd voor 2025 (30 ploegen, avg 1.492, thuis 1.639 / uit 1.361 doelpunten per duel) en 2026 "
 "(30 ploegen, 27 speeldagen, avg 1.537, thuis 1.820 / uit 1.389). Tier FULL. TWEE DINGEN OM VAST "
 "TE HOUDEN. (1) Het competitieNIVEAU is hier uit het LOPENDE seizoen genomen en niet uit "
 "early_season_uplift: met 27 van de ~34 speeldagen gespeeld is de verhouding lopend/vorig (1.0301) "
 "een echt niveauverschil en geen vroeg-seizoenseffect, en de correctie is gebouwd om uit te doven. "
 "Dat is openstaand punt 3 van runs/2026-09-20-run-b.md, hier voor het eerst zo uitgevoerd; "
 "hetzelfde geldt voor Eliteserien, Allsvenskan en Série A. (2) De aftraptijd maakt deze competitie "
 "voor Run B structureel lastig: een MLS-duel dat in UTC op de rundag valt, trapt af tussen 00:00 "
 "en 05:00 NL en is dus al gespeeld of onderweg als de run om 05:15 draait. Op 24 sep stond het "
 "enige duel op 89' (2-0). Dat is geen dekkingsgat maar het betekent dat een MLS-duel alleen "
 "speelbaar is als de run het ophaalt op de kalenderdag VOOR zijn UTC-datum."
)
d["updated"] = "2026-09-24"
P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("coverage.json bijgewerkt")
