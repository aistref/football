#!/usr/bin/env python3
"""xGscore-ophaalcode: gepubliceerde 1X2-modelkansen, server-side gerenderd.

Bevestigd werkend op 8 aug 2026: geen Cloudflare, geen JS-only leeg schaaltje — de voorspelling
staat leesbaar in de HTML (Angular Universal, server-side gerenderd). Onafhankelijk in de zin van
§2: de site rekent zelf met xG, niet met odds (in tegenstelling tot prognosist.com, dat expliciet
"odds and market movement" als invoer noemt — zie coverage.json en _shared-rules.md §2).

**Dekking is beperkt en wisselt per dag.** De dagpagina toont niet alle wedstrijden wereldwijd,
maar een door de site gekozen selectie competities (op 8 aug 2026: Eredivisie, Primeira Liga,
Argentinië, Brazilië, Noorwegen, Zweden — geen Ekstraklasa, Belgian Pro League of Scottish
Premiership, die dezelfde dag wél op de kalender stonden). Neem dus niet aan dat een competitie
hier ontbreekt omdat er geen wedstrijd is; het kan ook zijn dat xGscore hem niet toont.

    from scripts.xgscore import fetch_today, fetch_week

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass

TIMEOUT = 35
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
}

_BLOCK_SPLIT = "<xgs-category-forecast-fixture "
_TIME_RE = re.compile(r'<div class="text-muted">\s*([\d:]+)\s*</div>')
_LINK_RE = re.compile(
    r'href="/([^/"]+)/([^/"]+)/preview"><span>([^<]+)</span>.*?<span>([^<]+)</span>', re.S)
_MARK_RE = re.compile(
    r'<mark class="xgs-category-forecast-fixture_mark xgs-mark -medium( xgs-highlight-\w+)?"'
    r'[^>]*><strong[^>]*>\s*(\w+)\s*</strong>')
_PROB_RE = re.compile(r'mr-6 mr-xxl-2[^"]*"[^>]*><strong[^>]*>\s*(\d+)%\s*</strong>')
_ODDS_RE = re.compile(r'xgs-odds-format-decimal"><strong[^>]*>\s*([\d.]+)\s*</strong>')
_CONF_RE = re.compile(r'class="text-xs-tiny">(\d+)</small>')


class XgscoreError(RuntimeError):
    pass


@dataclass
class Prediction:
    competition_slug: str
    match_slug: str
    home: str
    away: str
    time: str  # zoals getoond op de site — bevestigd UTC op 8 aug 2026, controleer bij twijfel
    pick: str  # "1" | "X" | "2" — de uitkomst waar xGscore op inzet
    probability: float  # 0..1, kans van xGscore op `pick` (dus niet per se de thuiszege)
    reference_odds: float
    confidence: int | None  # 0..100, xGscore's eigen "quality"-score; betekenis niet officieel gedocumenteerd


def _fetch(url: str) -> str:
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=TIMEOUT).read().decode(
            errors="replace")
    except urllib.error.HTTPError as exc:
        raise XgscoreError(f"HTTP {exc.code} op {url}") from exc


def _parse(html: str) -> list[Prediction]:
    predictions = []
    for block in html.split(_BLOCK_SPLIT)[1:]:
        time_m = _TIME_RE.search(block)
        link_m = _LINK_RE.search(block)
        prob_m = _PROB_RE.search(block)
        odds_m = _ODDS_RE.search(block)
        conf_m = _CONF_RE.search(block)
        pick = next((label for highlight, label in _MARK_RE.findall(block) if highlight), None)
        if not (time_m and link_m and prob_m and odds_m and pick):
            continue  # onvolledige rij overslaan i.p.v. gokken — dit gaat om betrouwbaarheid, niet volledigheid
        predictions.append(Prediction(
            competition_slug=link_m.group(1),
            match_slug=link_m.group(2),
            home=link_m.group(3).strip(),
            away=link_m.group(4).strip(),
            time=time_m.group(1),
            pick=pick,
            probability=int(prob_m.group(1)) / 100,
            reference_odds=float(odds_m.group(1)),
            confidence=int(conf_m.group(1)) if conf_m else None,
        ))
    return predictions


def fetch_today() -> list[Prediction]:
    return _parse(_fetch("https://xgscore.io/predictions/today"))


def fetch_week() -> list[Prediction]:
    """Bredere selectie dan `fetch_today` — zelfde beperking: geen volledige wereldwijde dekking."""
    return _parse(_fetch("https://xgscore.io/predictions/week"))


# Competitie-slugs bevestigd op 8 aug 2026 (uit de link-structuur zelf, niet geraden).
# Vul aan zodra een nieuwe competitie in `fetch_today()`/`fetch_week()` opduikt.
KNOWN_COMPETITION_SLUGS: dict[str, str] = {
    "eredivisie": "Eredivisie (NED)",
    "primeira-liga": "Primeira Liga (POR)",
}


if __name__ == "__main__":
    # Zelftest: bevat vandaag minstens de bevestigde Eredivisie/Primeira Liga-wedstrijden en
    # heeft elke rij een geldige kans (0-1) en positieve referentie-odds.
    preds = fetch_today()
    print(f"{len(preds)} voorspellingen gevonden")
    slugs = sorted({p.competition_slug for p in preds})
    print("competities vandaag:", slugs)
    for p in preds:
        print(f"  {p.time}  {p.competition_slug:16s} {p.home} - {p.away}  "
              f"pick {p.pick} @ {p.probability * 100:.0f}%  odds {p.reference_odds}  conf {p.confidence}")
    assert preds, "geen voorspellingen gevonden — pagina-structuur kan gewijzigd zijn"
    assert all(0 < p.probability <= 1 for p in preds), "kans buiten (0,1] — parser klopt niet"
    assert all(p.reference_odds > 1.0 for p in preds), "odds <= 1.0 is onmogelijk — parser klopt niet"
    assert any(p.competition_slug == "eredivisie" for p in preds), "Eredivisie niet gevonden vandaag"
    print("Zelftest geslaagd.")
