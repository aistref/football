import json, inspect
from scripts import fotmob
print(inspect.signature(fotmob.fetch_league_stats))
print(fotmob.fetch_league_stats.__doc__)
