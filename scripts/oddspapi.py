#!/usr/bin/env python3
"""OddsPapi — **reservebron** voor odds. Staat standaard uit en draait nooit vanzelf.

WAAROM DIT BESTAAT (15 aug 2026, op verzoek van de gebruiker)
-------------------------------------------------------------
The Odds API is de gratis Starter: 500 credits per maand. OddsPapi komt daar naast te staan met
**250 verzoeken per maand** — dat is krap, ongeveer vier per run bij twee runs per dag. Het is dus
uitdrukkelijk een noodvoorraad voor als de credits van The Odds API op zijn, en geen tweede bron
die elke ochtend meedraait.

DE TWEE SLOTEN
--------------
De gebruiker vroeg expliciet: reserve, en niet automatisch draaien. Daarom moeten er **twee**
onafhankelijke voorwaarden waar zijn voordat er ook maar één verzoek uitgaat:

1. `data/odds-fallback.json` staat op `"armed": true`. Dat bestand is versiebeheerd en de run
   **mag hem nooit zelf omzetten** — anders kan een run zichzelf toestemming geven en is de
   voorraad in één ochtend weg. Alleen een mens zet hem aan.
2. The Odds API is werkelijk (bijna) op: `remaining <= threshold` uit datzelfde bestand.

Ontbreekt `ODDSPAPI_KEY`, dan gebeurt er sowieso niets. De sleutel mag dus rustig in de omgeving
staan zonder dat er iets verandert — dat was precies de vraag.

WAT HIER NOG NIET VASTSTAAT
---------------------------
Basis-URL en authenticatie zijn wél nagetrokken op 15 aug 2026 uit hun documentatie:

    https://v5.oddspapi.io/{taal}/...?apiKey=...        (taal: en, es, fr, pt, de, it, ru, zh)
    fout zonder sleutel: {"error":401,"message":"missing apiKey","code":"missing_api_key"}

De **exacte fixture- en odds-paden niet**. OddsPapi controleert de sleutel vóór de routering, dus
zonder sleutel geeft élk pad 401 — ook een verzonnen pad. Bestaande en niet-bestaande endpoints zijn
daardoor niet te onderscheiden zolang er geen sleutel is. `discover()` lost dat op zodra hij er wel
is: die probeert de kandidaten één voor één en onthoudt wat werkt in `data/odds-fallback.json`, zodat
het maar één keer hoeft.

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data" / "odds-fallback.json"

BASE = "https://v5.oddspapi.io"
LANG = "en"
TIMEOUT = 35

# Kandidaatpaden uit de endpointlijst in hun documentatie-index ("Fixtures Today", "Fixtures
# Filtered", "Fixture Odds"). Welke spelling het werkelijk is, wijst `discover()` uit.
FIXTURE_PATH_CANDIDATES = ("/fixtures/today", "/fixtures", "/fixtures/filtered")
ODDS_PATH_CANDIDATES = ("/fixtures/odds", "/fixture-odds", "/odds")


class OddsPapiError(RuntimeError):
    pass


class NotArmed(RuntimeError):
    """Geen fout: de reservebron staat uit, of is niet nodig. Ga gewoon verder zonder."""


@dataclass
class FallbackState:
    armed: bool = False
    threshold: int = 20
    monthly_quota: int = 250
    used_this_month: int = 0
    period: str = ""
    endpoints: dict = field(default_factory=dict)
    #: Kenmerk (sha256[:12]/lengte) van de sleutel waarmee `discover()` het laatst getest heeft.
    #: Zo is een run die een oude omgevingswaarde testte te onderscheiden van een nieuwe sleutel
    #: die ook wordt afgewezen. Zie `api_key_fingerprint`.
    key_fingerprint: str = ""
    notes: str = ""

    @classmethod
    def load(cls) -> "FallbackState":
        if not STATE.exists():
            return cls()
        raw = json.loads(STATE.read_text())
        known = {k: v for k, v in raw.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def save(self) -> None:
        current = json.loads(STATE.read_text()) if STATE.exists() else {}
        current.update({k: getattr(self, k) for k in self.__dataclass_fields__})
        STATE.write_text(json.dumps(current, ensure_ascii=False, indent=1) + "\n")


#: Namen waaronder de sleutel in de omgeving kan staan. Nodig sinds 18 aug 2026: de gebruiker had
#: hem al dagen gezet als `ODDSPapi_API_Key`, terwijl deze code alleen naar `ODDSPAPI_KEY` keek.
#: Namen van omgevingsvariabelen zijn hoofdlettergevoelig, dus vier runs lang meldde de routine
#: "ODDSPAPI_KEY niet gezet" terwijl de sleutel er gewoon was. Dat is precies de stille storing die
#: §1b wilde voorkomen — vandaar dat er nu hoofdletterongevoelig op een handvol spellingen wordt
#: gezocht in plaats van op één exacte naam.
KEY_ENV_NAMES: tuple[str, ...] = ("ODDSPAPI_KEY", "ODDSPAPI_API_KEY", "ODDS_PAPI_KEY",
                                   "ODDSPAPI_APIKEY", "ODDSPAPI")


def api_key() -> str | None:
    for name in KEY_ENV_NAMES:
        value = os.environ.get(name)
        if value:
            return value
    wanted = {n.replace("_", "").lower() for n in KEY_ENV_NAMES}
    for name, value in os.environ.items():
        if value and name.replace("_", "").lower() in wanted:
            return value
    return None


def api_key_fingerprint() -> str | None:
    """Onomkeerbaar kenmerk van de sleutel: `sha256[:12]/lengte`. Nooit de sleutel zelf.

    Nodig sinds 18 aug 2026. De sleutel werd die dag vernieuwd, maar een draaiende container houdt
    de omgeving die hij bij het starten meekreeg — dus een run kan een oude waarde testen en
    `invalid_api_key` melden zonder dat er iets mis is met de nieuwe. Zonder kenmerk is dat
    achteraf niet te onderscheiden van een nieuwe sleutel die ook wordt afgewezen, en dat zijn twee
    heel verschillende problemen met twee heel verschillende oplossingen. Twaalf hex-tekens uit een
    sha256 zijn niet terug te rekenen naar de sleutel; ze mogen dus in de repo.
    """
    key = api_key()
    if not key:
        return None
    return f"{hashlib.sha256(key.encode()).hexdigest()[:12]}/{len(key)}"


def api_key_source() -> str | None:
    """Onder welke naam de sleutel gevonden is — voor het runrapport en `api_check.py`."""
    for name in KEY_ENV_NAMES:
        if os.environ.get(name):
            return name
    wanted = {n.replace("_", "").lower() for n in KEY_ENV_NAMES}
    for name, value in os.environ.items():
        if value and name.replace("_", "").lower() in wanted:
            return name
    return None


def should_use(odds_api_remaining: int | None) -> tuple[bool, str]:
    """Mag de reservebron deze run aan? Geeft (ja/nee, reden) — de reden gaat in het runrapport.

    Beide sloten moeten open: handmatig gewapend, én The Odds API daadwerkelijk (bijna) op.
    """
    state = FallbackState.load()
    if not api_key():
        return False, "ODDSPAPI_KEY niet gezet"
    if not state.armed:
        return False, "reservebron staat uit (armed=false in data/odds-fallback.json)"
    if state.used_this_month >= state.monthly_quota:
        return False, (f"maandquotum op ({state.used_this_month}/{state.monthly_quota}); "
                       f"periode {state.period or 'onbekend'}")
    if odds_api_remaining is None:
        return False, "credits van The Odds API onbekend — bij twijfel de reserve niet aanspreken"
    if odds_api_remaining > state.threshold:
        return False, (f"niet nodig: The Odds API heeft nog {odds_api_remaining} credits "
                       f"(drempel {state.threshold})")
    return True, (f"The Odds API staat op {odds_api_remaining} credits (drempel {state.threshold}) "
                  f"en de reserve is gewapend; nog "
                  f"{state.monthly_quota - state.used_this_month} verzoeken over deze maand")


def _get(path: str, params: dict | None = None) -> tuple[int, dict, bytes]:
    key = api_key()
    if not key:
        raise OddsPapiError("ODDSPAPI_KEY niet gezet")
    query = dict(params or {})
    query["apiKey"] = key
    url = f"{BASE}/{LANG}{path}?{urllib.parse.urlencode(query)}"
    try:
        with urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}), timeout=TIMEOUT) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), exc.read() or b""


def request(path: str, params: dict | None = None, *, count: bool = True) -> dict | list:
    """Eén verzoek, en tel hem mee tegen het maandquotum.

    Zelf tellen is hier nodig: OddsPapi geeft `X-RateLimit-*` voor verzoeken per seconde en per
    minuut, maar geen teller voor het maandquotum. Zonder eigen boekhouding merk je pas dat de 250
    op zijn wanneer hij op is.
    """
    status, headers, body = _get(path, params)
    if count:
        state = FallbackState.load()
        state.used_this_month += 1
        state.save()
    if status != 200:
        raise OddsPapiError(f"HTTP {status} op {path}: {body[:200].decode(errors='replace')}")
    return json.loads(body)


def discover() -> dict:
    """Zoek eenmalig uit welke paden echt bestaan en leg ze vast.

    Hoe de statuscodes gelezen worden — dit is de kern, en het ligt niet voor de hand:

    | Status | Betekenis | Actie |
    |---|---|---|
    | 200 | pad bestaat en gaf meteen data | gevonden |
    | 400 | pad **bestaat**, maar mist verplichte parameters | **ook gevonden** |
    | 404 | pad bestaat niet | volgende kandidaat |
    | 401/403 | sleutelprobleem, niet een padprobleem | afbreken, verder zoeken heeft geen zin |
    | 429 | rate limit | afbreken |

    Dat 400 als tréffer telt is geen detail: een fixture-endpoint eist vrijwel zeker een datum of
    een competitie, dus de kans is groot dat het juiste pad 400 geeft in plaats van 200. Wie 400
    als "bestaat niet" leest, zoekt de hele lijst af en concludeert dat er niets werkt.

    Kost hooguit een handvol verzoeken en hoeft maar één keer; daarna staat het resultaat in
    `data/odds-fallback.json` onder `endpoints`.
    """
    state = FallbackState.load()
    found = dict(state.endpoints)
    log: list[str] = []
    for naam, kandidaten in (("fixtures", FIXTURE_PATH_CANDIDATES), ("odds", ODDS_PATH_CANDIDATES)):
        # Alleen een echt pad telt als "al gevonden". Een mislukte poging laat hier
        # "onbepaald (HTTP 401: ...)" achter, en dat is óók een niet-lege string — die als treffer
        # lezen betekent dat `discover()` daarna nooit meer een verzoek doet en stil de oude
        # mislukking blijft terugmelden, alsof hij het opnieuw geprobeerd had. `ensure_discovered`
        # hanteerde die "/"-controle al; hier ontbrak hij, waardoor de hertest na de eerste 401
        # dood was. Gevonden op 18 aug 2026, nadat de sleutel vernieuwd werd en de controle
        # onveranderd 401 bleef melden zonder het net te hebben geprobeerd.
        if str(found.get(naam, "")).startswith("/"):
            continue
        for pad in kandidaten:
            status, _, body = _get(pad)
            state.used_this_month += 1
            snippet = body[:120].decode(errors="replace").replace("\n", " ")
            log.append(f"{pad} -> HTTP {status} {snippet}")
            if status in (200, 400):
                found[naam] = pad
                break
            if status == 404:
                continue
            found[naam] = f"onbepaald (HTTP {status}: {snippet})"
            break
        else:
            found[naam] = "geen van de kandidaten bestaat — zoek het juiste pad in hun documentatie"
    state.endpoints = found
    state.key_fingerprint = api_key_fingerprint() or ""
    state.notes = ("discover gedraaid op " + (state.period or "onbekende datum")
                   + f" met sleutel {state.key_fingerprint or 'onbekend'}; "
                   + " | ".join(log))[:1500]
    state.save()
    return found


def ensure_discovered() -> tuple[bool, str]:
    """Eén keer per omgeving: controleer dat de reserve werkt, vóórdat je hem nodig hebt.

    Draait alleen als de sleutel er is en de paden nog onbekend zijn, en is verder een no-op.
    Dit staat los van `armed`: het testen van een noodaggregaat hoort niet te wachten tot de
    stroom uitvalt. Kosten: een handvol van de 250, één keer.
    """
    if not api_key():
        return False, "ODDSPAPI_KEY niet gezet — niets te ontdekken"
    state = FallbackState.load()
    # Alleen een pad dat met "/" begint telt als gevonden. Een mislukte poging laat hier
    # "onbepaald (HTTP 401: ...)" achter, en dát mag een nieuwe poging niet blokkeren: anders
    # blijft een verkeerd getypte sleutel voor altijd staan als "al ontdekt".
    if any(str(v).startswith("/") for v in state.endpoints.values()):
        return False, f"paden al bekend: {state.endpoints}"
    found = discover()
    werkt = [k for k, v in found.items() if v.startswith("/")]
    return True, (f"discover gedraaid, {len(werkt)} van {len(found)} paden gevonden: {found}")


if __name__ == "__main__":
    import sys
    state = FallbackState.load()
    ok, reden = should_use(odds_api_remaining=None)
    print("OddsPapi — reservebron")
    print(f"  sleutel gezet   : {'ja' if api_key() else 'nee'}")
    print(f"  gewapend        : {state.armed}")
    print(f"  drempel         : The Odds API <= {state.threshold} credits")
    print(f"  maandquotum     : {state.used_this_month}/{state.monthly_quota} gebruikt"
          f"{' — periode ' + state.period if state.period else ''}")
    print(f"  bekende paden   : {state.endpoints or 'nog niet ontdekt (draai: discover)'}")
    print(f"  nu inzetbaar    : {ok} — {reden}")
    if len(sys.argv) > 1 and sys.argv[1] == "discover":
        if not api_key():
            raise SystemExit("ODDSPAPI_KEY niet gezet — niets te ontdekken.")
        print("\nontdekken...", discover())
