"""Wat als we niet op de underdog-kant hadden gezeten? — analyse over alle afgewikkelde picks.

Aanleiding (4 sep 2026, vraag van de gebruiker): drie van de drie bets van vandaag stonden op de
underdog-kant (Real Betis +1.5, Basaksehir +1.5) of op een promovendus, en dat is al weken het
patroon. De vraag is niet of die kant vaker verliest — dat weten we — maar of de **spiegelbet**
(dezelfde markt, dezelfde wedstrijd, de favorietenkant) het wél had gehaald.

Werkwijze in drie stappen:

1. Parseer uit elke pick de markt, de gespeelde kant en de lijn.
2. **Controle:** reken de ORIGINELE bet na op de eindstand en vergelijk met het vastgelegde
   resultaat. Zolang die twee niet op alle 207 picks overeenkomen, is de spiegelberekening
   niets waard.
3. Reken de spiegelbet na op diezelfde eindstand.

Underdog/favoriet wordt bepaald in deze volgorde:
  a. Asian Handicap: het teken van de lijn. Een plus-lijn is per definitie de kant die de markt
     zwakker vindt; dat is geen schatting maar de definitie van de markt.
  b. 1X2 / DNB / Double Chance: de de-vigde marktkansen uit `calibration` in data/run-state/
     (beschikbaar vanaf 22 aug 2026), of anders de 1X2-koersen uit `markets_checked`.
  c. Lukt geen van beide, dan blijft de pick op "onbekend" staan en telt hij apart mee. Er wordt
     niet geraden.
"""
import json, glob, re, sys, unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, "tmp-run")


# ---------- naamvergelijking -------------------------------------------------------------------
def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("Ø", "o").replace("ł", "l").replace("ß", "ss")
    s = (s.replace("ı", "i").replace("İ", "i").replace("ş", "s").replace("Ş", "s")
          .replace("ğ", "g").replace("Ğ", "g").replace("ç", "c").replace("Ç", "c")
          .replace("đ", "d").replace("ð", "d").replace("þ", "th"))
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()


def toks(s):
    drop = {"fc", "afc", "cf", "sc", "ac", "as", "sv", "vfl", "vfb", "tsv", "bsc", "se", "if",
            "ff", "town", "city", "united", "utd", "athletic", "wanderers", "rovers", "county",
            "ks", "kf", "cd", "ad", "ud", "sd", "us", "club", "calcio", "ii", "b"}
    return {t for t in norm(s).split() if t not in drop} or set(norm(s).split())


def which_side(text, home, away):
    """Slaat `text` op de thuis- of de uitploeg? None als het niet uit te maken is."""
    t = norm(text)
    for label, name in (("home", home), ("away", away)):
        if norm(name) and norm(name) in t:
            return label
    th, ta, tt = toks(home), toks(away), set(norm(text).split())
    hit_h, hit_a = th & tt, ta & tt
    if hit_h and not hit_a:
        return "home"
    if hit_a and not hit_h:
        return "away"
    return None


# ---------- afrekenen --------------------------------------------------------------------------
def asian(margin, line):
    """Uitkomst van een Aziatische handicap in eenheden winst bij 1u inzet tegen koers 1.0.

    Geeft een fractie van de inzet terug: 1 = vol gewonnen, 0.5 = half gewonnen, 0 = push,
    -0.5 = half verloren, -1 = vol verloren.
    """
    m = margin + line
    if m >= 0.5:
        return 1.0
    if abs(m - 0.25) < 1e-9:
        return 0.5
    if abs(m) < 1e-9:
        return 0.0
    if abs(m + 0.25) < 1e-9:
        return -0.5
    return -1.0


def settle(kind, side, line, gh, ga):
    """Uitkomst als fractie: 1 gewonnen, 0.5 half, 0 push, -0.5 half verloren, -1 verloren."""
    margin = (gh - ga) if side == "home" else (ga - gh)
    if kind == "1x2":
        if side == "draw":
            return 1.0 if gh == ga else -1.0
        return 1.0 if margin > 0 else -1.0
    if kind == "dnb":
        return 0.0 if gh == ga else (1.0 if margin > 0 else -1.0)
    if kind == "dc":
        return 1.0 if margin >= 0 else -1.0
    if kind == "ah":
        return asian(margin, line)
    if kind == "ou":
        total = gh + ga
        # `line` is de doelpuntenlijn, `side` is "over" of "under"
        diff = total - line
        if side == "under":
            diff = -diff
        if diff >= 0.5:
            return 1.0
        if abs(diff - 0.25) < 1e-9:
            return 0.5
        if abs(diff) < 1e-9:
            return 0.0
        if abs(diff + 0.25) < 1e-9:
            return -0.5
        return -1.0
    if kind == "btts":
        yes = gh > 0 and ga > 0
        return 1.0 if (yes == (side == "yes")) else -1.0
    raise ValueError(kind)


# ---------- parsen -----------------------------------------------------------------------------
NUM = re.compile(r"([+-]?\d+(?:\.\d+)?)")


def parse(pick):
    """(kind, side, line) of None als het niet te parsen valt."""
    m, sel, home, away = pick["market"], pick["selection"], pick["home"], pick["away"]
    low = norm(sel)
    if m == "Over/Under":
        side = "over" if low.startswith("over") else "under"
        return "ou", side, float(NUM.search(sel).group(1))
    if m == "BTTS":
        neg = (" nee" in low) or low.strip() in ("nee",) or low.endswith("nee")
        return "btts", ("no" if neg else "yes"), None
    if m == "1X2":
        if "gelijkspel" in low and "of gelijk" not in low:
            return "1x2", "draw", None
        if re.match(r"^1 ", sel) or low.startswith("1 "):
            return "1x2", "home", None
        if re.match(r"^2 ", sel) or low.startswith("2 "):
            return "1x2", "away", None
        s = which_side(sel, home, away)
        return ("1x2", s, None) if s else None
    if m == "Draw No Bet":
        s = which_side(sel, home, away)
        return ("dnb", s, None) if s else None
    if m == "Double Chance":
        s = which_side(sel, home, away)
        if s is None and low.startswith("1x"):
            s = "home"
        if s is None and ("x2" in low):
            s = "away"
        return ("dc", s, None) if s else None
    if m == "Asian Handicap":
        n = NUM.search(sel.replace("−", "-"))
        if not n:
            return None
        line = float(n.group(1))
        # de teamnaam is de rest van de tekst, zonder het getal en zonder "AH"/"Asian Handicap"
        rest = sel.replace(n.group(1), " ")
        rest = re.sub(r"(?i)asian handicap|\bah\b|@|\(|\)", " ", rest)
        s = which_side(rest, home, away)
        if s is None and "uit" in norm(rest):
            s = "away"
        if s is None and "thuis" in norm(rest):
            s = "home"
        return ("ah", s, line) if s else None
    return None


def mirror(kind, side, line):
    """De spiegelbet: dezelfde markt, de andere kant."""
    flip = {"home": "away", "away": "home"}
    if kind in ("1x2", "dnb", "dc", "ah"):
        if side not in flip:
            return None
        return (kind, flip[side], (-line if line is not None else None))
    return None


# ---------- marktbeeld uit run-state ------------------------------------------------------------
def market_index():
    """(datum, thuis, uit) -> de-vigde 1X2-marktkansen, uit data/run-state/."""
    idx = {}
    odds_pats = [re.compile(r"1 @([\d.]+).*?X @([\d.]+).*?2 @([\d.]+)"),
                 # oudere schrijfwijze (t/m 21 aug 2026): "1.18 / 7.38 / 15.00"
                 re.compile(r"(\d+\.\d+)\s*/\s*(\d+\.\d+)\s*/\s*(\d+\.\d+)")]
    for f in sorted(glob.glob("data/run-state/*.json")):
        d = json.load(open(f))
        day = d.get("date")
        for comp, v in (d.get("competitions") or {}).items():
            if not isinstance(v, dict):
                continue
            for mm in v.get("matches") or []:
                if not isinstance(mm, dict):
                    continue
                name = mm.get("match") or ""
                probs = None
                cal = mm.get("calibration") or {}
                if cal.get("market") and len(cal["market"]) == 3:
                    probs = cal["market"]
                else:
                    s = (mm.get("markets_checked") or {}).get("1X2")
                    hit = None
                    for pat in odds_pats:
                        hit = pat.search(s) if isinstance(s, str) else None
                        if hit:
                            break
                    if hit:
                        inv = [1 / float(x) for x in hit.groups()]
                        tot = sum(inv)
                        probs = [x / tot for x in inv]
                if probs:
                    parts = re.split(r"\s+[–-]\s+", name)
                    if len(parts) == 2:
                        key = (day, frozenset(toks(parts[0])), frozenset(toks(parts[1])))
                        idx.setdefault(key, probs)
    return idx


IDX = market_index()


def market_probs_for(pick):
    """De-vigde 1X2-marktkansen voor deze wedstrijd, of None."""
    th, ta = frozenset(toks(pick["home"])), frozenset(toks(pick["away"]))
    probs = IDX.get((pick["run_date"], th, ta))
    if probs is None:
        for (day, kh, ka), p in IDX.items():
            if day == pick["run_date"] and (kh & th) and (ka & ta):
                return p
    return probs


def favourite_side(pick, kind, side, line):
    """"underdog" | "favoriet" | "gelijk" | "geen kant" | None."""
    if kind in ("ou", "btts") or side == "draw":
        return "geen kant"                  # Over/Under, BTTS en het gelijkspel kennen geen kant
    if kind == "ah" and line is not None:
        if line > 0:
            return "underdog"
        if line < 0:
            return "favoriet"
        return "gelijk"
    th, ta = frozenset(toks(pick["home"])), frozenset(toks(pick["away"]))
    probs = IDX.get((pick["run_date"], th, ta))
    if probs is None:                       # losser koppelen: overlappende tokens volstaan
        for (day, kh, ka), p in IDX.items():
            if day == pick["run_date"] and (kh & th) and (ka & ta):
                probs = p
                break
    if probs is None:
        # Laatste redmiddel: de eigen koers van de pick. Bij een 1X2-zege ligt het omslagpunt
        # rond een impliciete kans van 0.395 — dat is (overround 1.06 minus een gelijkspel van
        # ~0.27) gedeeld door twee. Onder 0.37 is de tegenstander met zekerheid favoriet, boven
        # 0.42 zijn wij dat; daartussen valt het uit één koers niet uit te maken. Bij Draw No Bet
        # ligt het omslagpunt op 0.5 (het gelijkspel is eruit), bij Double Chance op 0.5 gemeten
        # op de tegenkant. Deze gevallen worden apart geteld, nooit stilzwijgend meegerekend.
        imp = pick["implied_prob"]
        if kind == "1x2":
            if imp <= 0.37:
                return "underdog?"
            if imp >= 0.42:
                return "favoriet?"
            return "onbeslist?"
        if kind == "dnb":
            if imp <= 0.48:
                return "underdog?"
            if imp >= 0.53:
                return "favoriet?"
            return "onbeslist?"
        if kind == "dc":
            return "underdog?" if imp >= 0.35 else "favoriet?"
        return None
    ph, pa = probs[0], probs[2]
    if abs(ph - pa) < 0.03:
        return "gelijk"
    strong = "home" if ph > pa else "away"
    return "favoriet" if side == strong else "underdog"


# ---------- doorrekenen -------------------------------------------------------------------------
rows = [json.loads(l) for l in open("data/picks.jsonl") if l.strip()]
settled = [r for r in rows if r["result"] in ("won", "lost") and r.get("settled_score")]
print(f"afgewikkelde picks met eindstand: {len(settled)}")

recorded = {"won": 1.0, "lost": -1.0}
out, problems = [], []
for p in settled:
    parsed = parse(p)
    gh, ga = (int(x) for x in re.match(r"(\d+)\D+(\d+)", p["settled_score"]).groups())
    if parsed is None:
        problems.append((p["id"], p["market"], p["selection"], "niet te parsen"))
        continue
    kind, side, line = parsed
    got = settle(kind, side, line, gh, ga)
    # controle: klopt onze narekening met wat er in het logboek staat?
    ok = (got > 0) == (p["result"] == "won") or abs(got) == 0.5 or got == 0.0
    if not ok:
        problems.append((p["id"], p["market"], p["selection"], p["settled_score"],
                         f"berekend {got} vs vastgelegd {p['result']}"))
    row = dict(p)
    row.update(kind=kind, side=side, line=line, gh=gh, ga=ga, calc=got,
               kant=favourite_side(p, kind, side, line),
               market_probs=market_probs_for(p))
    mir = mirror(kind, side, line)
    row["mirror"] = None if mir is None else settle(mir[0], mir[1], mir[2], gh, ga)
    out.append(row)

print(f"geparsed: {len(out)}, niet geparsed of afwijkend: {len(problems)}")
for pr in problems[:25]:
    print("   ", pr)
json.dump(out, open("tmp-run/underdog_mirror.json", "w"), ensure_ascii=False, indent=1)
print("\nkanten:", Counter(r["kant"] for r in out))
print("markten met spiegel:", Counter(r["market"] for r in out if r["mirror"] is not None))
