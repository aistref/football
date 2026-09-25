import json, sys, urllib.request, re
sys.path.insert(0,'.')
from scripts import betexplorer as bx

HEADERS = bx.HEADERS

def raw(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u, headers=HEADERS), timeout=30).read().decode(errors='replace')
    except Exception as e:
        return f"ERROR {e}"

# check concacaf page for team mentions
u = "https://www.betexplorer.com/football/north-central-america/concacaf-nations-league/fixtures/"
text = raw(u)
print(len(text))
for team in ["Bermuda","Guadeloupe","Grenada","Cuba","Barbados","Saint Lucia","Bonaire","St. Kitts","Kitts"]:
    print(team, team in text)

print("---")
for slug in [
  "https://www.betexplorer.com/football/asia/",
]:
    t = raw(slug)
    # search for asean/aff mentions
    for m in re.finditer(r'href="(/football/asia/[a-z0-9\-]+/)"[^>]*>([^<]{0,60})<', t):
        if 'asean' in m.group(1).lower() or 'aff' in m.group(1).lower() or 'champ' in m.group(1).lower():
            print(m.group(1), m.group(2))
