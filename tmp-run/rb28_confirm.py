"""Tweede methode: per competitie de eigen Fotmob-competitiepagina (leagues?id=),
in plaats van de daglijst (matches?date=). Twee verschillende endpoints, dus een echte
onafhankelijke bevestiging van de kalender."""
import json, urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
NL = ZoneInfo("Europe/Amsterdam")
DAY = date(2026, 9, 28)
start = datetime.combine(DAY, datetime.min.time(), NL).replace(hour=8)
end = start + timedelta(days=1)
RUNLIST = json.load(open("tmp-run/rb28_runlist_ids.json"))

HDRS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
def get(url):
    import gzip
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)

tot = 0
for name, lid in RUNLIST.items():
    try:
        d = get(f"https://www.fotmob.com/api/data/leagues?id={lid}")
    except Exception as exc:
        print(f"{name}: FOUT {type(exc).__name__}: {exc}")
        continue
    fixtures = (d.get("fixtures") or {}).get("allMatches") or []
    hits = []
    for m in fixtures:
        ut = m.get("status", {}).get("utcTime") or m.get("utcTime")
        if not ut:
            continue
        t = ut[:-1] + "+00:00" if ut.endswith("Z") else ut
        try:
            k = datetime.fromisoformat(t)
        except ValueError:
            continue
        if k.tzinfo is None:
            k = k.replace(tzinfo=timezone.utc)
        if start <= k < end and not m.get("status", {}).get("cancelled"):
            hits.append((m.get("home", {}).get("name"), m.get("away", {}).get("name"),
                         k.astimezone(NL).strftime("%H:%M")))
    tot += len(hits)
    print(f"{name}: {len(hits)} duels in het venster" + (f" -> {hits}" if hits else ""))
print("\nTOTAAL via competitiepagina's:", tot)
