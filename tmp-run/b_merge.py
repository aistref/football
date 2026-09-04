"""Fotmob levert de xG-rijen en de standenrijen soms onder verschillend geaccentueerde namen
(gemeten 4 sep 2026 op LaLiga2 2025/2026: 30 'ploegen' voor een competitie van 22, waarvan er
acht in twee halve rijen uiteenvielen — de ene met xg/xga/mp, de andere met gf/ga/played/home/away).
Zonder samenvoegen krijgt zo'n ploeg xg=None of splits=None en valt hij ten onrechte op NONE."""
import unicodedata

def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in s if ch.isalnum())

def merge_teams(teams):
    """Voeg rijen met dezelfde genormaliseerde naam samen. Geeft (nieuwe dict, lijst samengevoegd)."""
    buckets = {}
    for name, row in teams.items():
        buckets.setdefault(_norm(name), []).append((name, row))
    out, merged = {}, []
    for _, rows in buckets.items():
        if len(rows) == 1:
            out[rows[0][0]] = rows[0][1]
            continue
        # naam met de meeste velden wint als sleutel; velden vullen elkaar aan
        rows.sort(key=lambda nr: -len(nr[1]))
        combined = {}
        for _, row in rows:
            for k, v in row.items():
                if v is not None and (k not in combined or combined[k] is None):
                    combined[k] = v
        name = max((n for n, _ in rows), key=len)
        out[name] = combined
        merged.append([n for n, _ in rows])
    return out, merged
