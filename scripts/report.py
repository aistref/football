#!/usr/bin/env python3
"""Leesbaar dagrapport als HTML-pagina, naast het technische runrapport in markdown.

Waarom dit bestaat: het markdown-runrapport is geschreven voor iemand die de repo kent. Het
opent met bronstatus, gebruikt edge_pp, de-viggen en Brier zonder uitleg, en de bets staan als
twee regels in een tabel tussen alle andere wedstrijden. De gebruiker die de routine alleen
leest heeft daar niets aan. Deze pagina bevat dezelfde cijfers in een andere volgorde: eerst de
bets met prijs en tijd, dan wat de gebruiker zelf moet beslissen, dan de dekking, dan het
logboek, dan een woordenlijst.

    python3 scripts/report.py --run a --date 2026-08-09

Structurele data komt automatisch uit `data/picks.jsonl` en `data/run-state/`. De leesbare tekst
per run komt uit een prosebestand, `runs/<datum>-run-<id>.prose.json`; ontbreekt dat, dan levert
het script een pagina zonder de verhalende stukken en zegt het dat erbij. Werkt zo voor Run A en
Run B: de competitielijst komt uit het voortgangsbestand, niet uit dit script.

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import argparse
import html
import json
from datetime import date, datetime
from pathlib import Path

import ledger

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"
STATE_DIR = ROOT / "data" / "run-state"

DISCLAIMER = ("Beslissingsondersteuning, geen winnend systeem. "
              "Na de bookmakermarge is de verwachtingswaarde negatief.")

MONTHS = ["januari", "februari", "maart", "april", "mei", "juni",
          "juli", "augustus", "september", "oktober", "november", "december"]
DAYS = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]

STATUS_CHIP = {
    "GEANALYSEERD": ("ok", "geanalyseerd"),
    "GEEN WEDSTRIJD": ("none", "geen wedstrijd"),
    "BUITEN DATADEKKING": ("gap", "geen cijfers"),
    "AFGEKAPT": ("gap", "afgekapt"),
}

GLOSSARY = [
    ("Koers / odds",
     "Wat je terugkrijgt per ingezette euro als je wint. Koers 2.48 betekent: 1 euro inzet "
     "levert 2,48 euro terug, dus 1,48 winst."),
    ("Kans van de bookmaker",
     "De koers omgerekend naar een percentage. Koers 2.48 komt neer op 40,3% — zo vaak moet het "
     "gebeuren voordat die prijs eerlijk is. <em>In de repo heet dit “implied prob”.</em>"),
    ("Voordeel in procentpunten",
     "Het verschil tussen mijn schatting en die van de bookmaker. Zeg ik 48,2% en hij 40,3%, dan "
     "is dat +7,9. Onder de 8 wordt er niets gepubliceerd — 16 als de cijfers zwakker zijn. "
     "<em>In de repo: “edge_pp”.</em>"),
    ("Kansenkwaliteit (xG)",
     "Hoeveel doelpunten een ploeg had “moeten” maken op basis van de kwaliteit van hun kansen. "
     "Betrouwbaarder dan de echte score, omdat geluk er grotendeels uit is."),
    ("De robuustheidstoets",
     "Elke bet wordt zes keer doorgerekend met andere instellingen. Blijft het voordeel alleen "
     "bestaan bij één toevallige instelling, dan is het een rekenartefact en gaat de bet eruit."),
    ("De tweede methode",
     "Naast het xG-model rekent een tweede berekening dezelfde wedstrijd door op wat de ploegen "
     "thuis en uit werkelijk scoorden. Alleen wat beide methodes bevestigen wordt gepubliceerd."),
    ("Marge eruit rekenen",
     "Elke bookmaker rekent zijn winst in de koersen. Om eerlijk te vergelijken gaat die marge er "
     "eerst uit — anders lijkt elke bet slecht. <em>In de repo: “de-viggen”.</em>"),
    ("Volledig / beperkt / geen data",
     "Hoeveel er bekend is over een wedstrijd. Bij “geen data” — meestal een net gepromoveerde "
     "club zonder historie — komt er per definitie geen bet, hoe mooi de koers ook is."),
    ("De kalibratiescore",
     "Meet of iemands percentages op de lange duur kloppen. Lager is beter. Het punt is de "
     "vergelijking: is die van mij lager dan die van de bookmaker, dan voegt de analyse iets toe."),
]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def nl_date(day: date) -> str:
    return f"{DAYS[day.weekday()]} {day.day} {MONTHS[day.month - 1]} {day.year}"


def pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}".replace(".", ",") + "%"


def signed(value: float, digits: int = 1) -> str:
    return f"{value:+.{digits}f}".replace(".", ",")


def kickoff_time(pick: dict) -> str:
    try:
        return datetime.fromisoformat(pick["kickoff"]).strftime("%H:%M")
    except (ValueError, KeyError):
        return "tijd onbekend"


def short_competition(name: str, labels: dict) -> str:
    if name in labels:
        return labels[name]
    return name.split(" (")[0]


RISK_LEVELS = {"low": "low", "laag": "low",
               "med": "med", "medium": "med", "gemiddeld": "med", "mid": "med",
               "high": "high", "hoog": "high"}


def normalise_risk(level: str, pick: dict) -> str:
    """Breng een risk_level uit een prosebestand terug tot low/med/high.

    Nodig sinds 22 aug 2026: Run A schreef "med" en Run B "medium" voor hetzelfde niveau. Dat
    bleef onopgemerkt zolang de waarde alleen als CSS-klasse werd gebruikt — een onbekende klasse
    geeft geen fout, alleen een chip zonder kleur. Zodra er ook een label uit moest komen, klapte
    het rapport eruit. Een onbekende waarde valt hier terug op de kans in plaats van te falen.
    """
    return RISK_LEVELS.get(str(level).strip().lower(),
                           "high" if pick["my_prob"] < 0.35 else "med")


def risk_class(pick: dict, prose: dict) -> tuple[str, str]:
    """(css-klasse, zin). Prosebestand wint; anders afgeleid van de kans."""
    given = prose.get("risk")
    if given:
        return normalise_risk(prose.get("risk_level", ""), pick), given
    if pick["my_prob"] >= 0.45:
        return "med", "Middelmatig risico — kans rond de helft, geen gok op een stunt"
    if pick["my_prob"] >= 0.30:
        return "med", f"Verhoogd risico — dit lukt ongeveer {pick['my_prob'] * 100:.0f} keer per 100"
    return "high", (f"Hoog risico — dit lukt ongeveer {pick['my_prob'] * 100:.0f} keer per 100, "
                    "en de markt is het stevig oneens")


def max_shortlist(day: date) -> int:
    """3 op ma-do, 5 op vr-zo — `MAX_SHORTLIST` uit _shared-rules.md §0."""
    return 5 if day.weekday() >= 4 else 3


def selection_score(pick: dict) -> float:
    """edge_pp x my_prob x (FULL 1.0 | LIGHT 0.5) — dezelfde formule als model.selection_score.

    Hier opnieuw uitgeschreven in plaats van geimporteerd, omdat dit script alleen uit
    picks.jsonl leest en niet uit de rekenkern; de velden die de formule nodig heeft staan
    allemaal in de pick zelf.
    """
    weight = 1.0 if pick.get("data_tier") == "FULL" else 0.5
    return pick["edge_pp"] * pick["my_prob"] * weight


def rank_picks(picks: list[dict], day: date) -> tuple[list[dict], list[dict]]:
    """(topselectie, rest), gesorteerd op selection_score.

    Bestaansreden (22 aug 2026, op verzoek van de gebruiker). §5 schrijft een topselectie voor en
    `picks.jsonl` heeft er een `shortlisted`-veld voor, maar deze pagina deed er niets mee: alle
    bets stonden ongeordend onder elkaar. Op een dag met dertien bets is dat precies de vraag die
    onbeantwoord blijft — welke zou ik nou spelen. De rangschikking is die van §5 en §1, zodat de
    volgorde hier niet kan afwijken van die in het markdown-runrapport.

    Het opgeslagen `shortlisted`-veld is leidend, want dat is het besluit van de run zelf
    (inclusief `MAX_LIGHT_IN_SHORTLIST`). Staat het nergens aan — oudere runs — dan valt dit
    terug op de bovenste `max_shortlist(day)` op score.
    """
    order = sorted(picks, key=selection_score, reverse=True)
    flagged = [p for p in order if p.get("shortlisted")]
    if not flagged:
        flagged = order[:max_shortlist(day)]
    rest = [p for p in order if p not in flagged]
    return flagged, rest


def ledger_summary(picks: list[dict]) -> dict:
    settled = [p for p in picks if p.get("result") in ("won", "lost")]
    won = [p for p in settled if p["result"] == "won"]
    profit = sum(ledger.pick_units(p) for p in settled)
    own = ledger.brier([(p["my_prob"], 1 if p["result"] == "won" else 0) for p in settled])
    market = ledger.brier([(p["implied_prob"], 1 if p["result"] == "won" else 0) for p in settled])
    return {"settled": len(settled), "won": len(won), "profit": profit,
            "brier_own": own, "brier_market": market}


# --------------------------------------------------------------------------- rendering

def render_bets(picks: list[dict], prose: dict, labels: dict) -> str:
    if not picks:
        return ('<div class="callout"><p class="prose"><strong>Geen bets vandaag.</strong> '
                'Geen enkele wedstrijd haalde alle drempels. Dat is een geldige uitkomst, geen '
                'mislukte run — de lijst wordt niet aangevuld om hem voller te laten lijken.</p>'
                '</div>')
    blocks = []
    for pick in picks:
        text = prose.get(pick["id"], {})
        level, sentence = risk_class(pick, text)
        why = text.get("why") or ("Onderbouwing niet in het prosebestand gezet; de technische "
                                  "redenering staat in het markdown-runrapport.")
        blocks.append(f'''<div class="bet">
    <div class="bet-top">
      <div class="bet-id">
        <span class="bet-meta">{esc(short_competition(pick["competition"], labels))} · aftrap {esc(kickoff_time(pick))}</span>
        <span class="bet-match">{esc(pick["home"])} – {esc(pick["away"])}</span>
        <span class="bet-pick">{esc(pick["selection"])}</span>
      </div>
      <div class="price">
        <span class="odds num">{pick["odds"]:.2f}</span>
        <span class="book">bij {esc(text.get("book") or pick["odds_source"].split(" (")[0])}</span>
      </div>
    </div>
    <div class="probrow">
      <div class="prob"><span class="l">De bookmaker zegt</span><span class="v num">{pct(pick["implied_prob"])}</span></div>
      <div class="prob"><span class="l">Ik schat</span><span class="v num">{pct(pick["my_prob"])}</span></div>
      <div class="prob hl"><span class="l">Verschil in mijn voordeel</span><span class="v num">{signed(pick["edge_pp"])}</span></div>
    </div>
    <div class="why">
      <h4>Waarom</h4>
      <p class="prose">{esc(why)}</p>
      <span class="risk"><span class="dot {level}"></span>{esc(sentence)}</span>
    </div>
  </div>''')
    return "\n".join(blocks)


def normalise_competitions(state: dict) -> dict:
    """Maak van elke competitiewaarde een dict, ook als een run er een platte string van maakte.

    `progress.mark()` documenteert {"status": ..., "matches": [...]}, maar Run B van 10 aug 2026
    schreef "GEANALYSEERD (FULL, 2 van 2; 0 bets - ...)" als kale string. Dit script klapte daar
    op stuk, en een rapportgenerator die omvalt op de invoer van een andere run is zelf het
    probleem: de status staat vooraan, de rest is toelichting, dus dat is prima te lezen.
    """
    out = {}
    for name, value in state.get("competitions", {}).items():
        if isinstance(value, dict):
            out[name] = value
            continue
        text = str(value)
        status = next((s for s in ("GEANALYSEERD", "BUITEN DATADEKKING", "AFGEKAPT",
                                    "GEEN WEDSTRIJD") if text.startswith(s)), text)
        note = text[len(status):].strip(" ()") or None
        out[name] = {"status": status, "matches": [], **({"note": note} if note else {})}
    return out


def render_shortlist(picks: list[dict], prose: dict, labels: dict, day: date) -> str:
    """De topselectie als tabel: welke bets zou je spelen als je er maar een paar speelt."""
    if not picks:
        return ""
    top, rest = rank_picks(picks, day)
    cap = max_shortlist(day)
    dagsoort = "vrijdag t/m zondag" if day.weekday() >= 4 else "maandag t/m donderdag"

    rows = []
    for i, pick in enumerate(top, 1):
        text = prose.get(pick["id"], {})
        level, _ = risk_class(pick, text)
        risk_label = {"low": "laag", "med": "gemiddeld", "high": "hoog"}[level]
        rows.append(f'''<tr>
          <td class="num rank">{i}</td>
          <td>
            <span class="sl-match">{esc(pick["home"])} – {esc(pick["away"])}</span>
            <span class="sl-pick">{esc(pick["selection"])} · {esc(short_competition(pick["competition"], labels))} · aftrap {esc(kickoff_time(pick))}</span>
          </td>
          <td class="num">{pick["odds"]:.2f}</td>
          <td class="num">{pct(pick["my_prob"])}</td>
          <td class="num">+{pick["edge_pp"]:.1f}</td>
          <td class="num">{selection_score(pick):.2f}</td>
          <td><span class="chip {level}">{risk_label}</span></td>
        </tr>''')

    if len(top) < cap:
        tail = (f'<p class="prose measure" style="margin-top:18px">Er waren maar {len(top)} '
                f'{"bet" if len(top) == 1 else "bets"}, dus de lijst is korter dan de {cap} plekken '
                f'die er op {dagsoort} zijn. Hij wordt niet aangevuld om hem voller te laten lijken.</p>')
    elif rest:
        nxt = rest[0]
        tail = (f'<p class="prose measure" style="margin-top:18px">Er staan er {len(rest)} '
                f'buiten deze lijst. De eerste die net afviel is '
                f'<strong>{esc(nxt["home"])} – {esc(nxt["away"])}</strong> '
                f'({esc(nxt["selection"])}, score {selection_score(nxt):.2f}).</p>')
    else:
        tail = ""

    return f'''<section>
  <div class="sectionhead">
    <span class="eyebrow">Topselectie</span>
    <h2>{"De bet" if len(top) == 1 else f"De beste {len(top)}"} als u er maar een paar speelt</h2>
  </div>

  <p class="prose measure" style="margin-bottom:22px">Op {dagsoort} houd ik maximaal
  <strong>{cap}</strong> bets in de topselectie. De volgorde is die van de score hieronder: het
  voordeel in procentpunten maal de kans dat het lukt, en gehalveerd als de cijfers zwakker zijn.
  Dat weegt een hogere trefkans dus zwaarder dan een paar procentpunt extra voordeel.
  <strong>De score rangschikt, het risico waarschuwt</strong> — een bet kan bovenaan staan én hoog
  risico zijn.</p>

  <div class="tablewrap">
    <table class="shortlist">
      <thead><tr>
        <th class="num">#</th><th>Bet</th><th class="num">Koers</th>
        <th class="num">Mijn kans</th><th class="num">Voordeel</th>
        <th class="num">Score</th><th>Risico</th>
      </tr></thead>
      <tbody>
        {"".join(rows)}
      </tbody>
    </table>
  </div>
  {tail}
</section>'''


def render_coverage(state: dict, notes: dict, labels: dict) -> str:
    order = {"GEANALYSEERD": 0, "BUITEN DATADEKKING": 1, "AFGEKAPT": 2, "GEEN WEDSTRIJD": 3}
    rows = sorted(normalise_competitions(state).items(),
                  key=lambda kv: (order.get(kv[1].get("status"), 9), kv[0]))
    out = []
    for name, result in rows:
        css, label = STATUS_CHIP.get(result.get("status"), ("none", result.get("status", "?")))
        note = notes.get(name) or result.get("note")
        if note is None:
            count = len(result.get("matches", []))
            note = (f"{count} wedstrijd{'en' if count != 1 else ''} bekeken" if count
                    else "niets op de kalender")
        out.append(f'<tr><td class="comp">{esc(short_competition(name, labels))}</td>'
                   f'<td><span class="chip {css}">{esc(label)}</span></td>'
                   f'<td class="note">{note}</td></tr>')
    return "\n        ".join(out)


GATE_LABEL = {
    "edge": "voordeel te klein",
    "robuustheid": "verdwijnt bij andere rekeninstellingen",
    "tweede_methode": "tweede rekenmethode is het oneens",
    "odds": "koers buiten de toegestane band",
    "data": "te weinig onafhankelijke cijfers",
}


def render_near_misses(state: dict, labels: dict) -> str:
    """De afgewezen kandidaten, met per poort het cijfer waarop ze sneuvelden.

    Toegevoegd 10 aug 2026 op verzoek van de gebruiker. Zonder dit leest een run met nul bets als
    "er was niets", terwijl het verschil tussen "geen enkele wedstrijd kwam in de buurt" en "drie
    kandidaten vielen op een haar af" precies is wat je over meerdere dagen wilt kunnen zien —
    onder meer om te merken of één poort structureel alles wegvangt.

    De cijfers komen uit `data/run-state/`, niet uit het prosebestand: overtypen is precies hoe
    twee rapporten van dezelfde run uiteen gaan lopen.
    """
    rows = []
    for comp, result in sorted(normalise_competitions(state).items()):
        for match in result.get("matches", []):
            nm = match.get("near_miss")
            if not nm:
                continue
            gate = GATE_LABEL.get(nm.get("failed_gate"), nm.get("failed_gate", "—"))
            cells = []
            for key, head in (("edge_xg", "xG-model"), ("edge_split", "2e methode"),
                              ("edge_robust_min", "zwakste stand")):
                v = nm.get(key)
                cls = "num" + (" below" if isinstance(v, (int, float)) and v < 3.0 else "")
                cells.append(f'<td class="{cls}">{signed(v) + " pp" if isinstance(v, (int, float)) else "—"}</td>')
            odds = nm.get("odds")
            price = (f'<br><span class="note">koers {odds:.2f}</span>'
                     if isinstance(odds, (int, float)) else "")
            rows.append(
                f'<tr><td class="comp">{esc(match.get("match", "?"))}<br>'
                f'<span class="note">{esc(short_competition(comp, labels))}</span></td>'
                f'<td>{esc(nm.get("market", "—"))}{price}</td>'
                + "".join(cells)
                + f'<td><span class="chip gap">{esc(gate)}</span></td></tr>')
    if not rows:
        return ""
    return f'''
<section>
  <div class="sectionhead">
    <span class="eyebrow">Net niet</span>
    <h2>Wat er wél in beeld was</h2>
  </div>

  <p class="prose measure" style="margin-bottom:22px">Kandidaten die een echt voordeel lieten zien
  en alsnog zijn afgewezen. De grens ligt sinds 31 augustus op <strong>8,0 procentpunt</strong>
  (16,0 als de cijfers zwakker zijn), verhoogd van 3,0 omdat alles daaronder over 179 afgerekende
  weddenschappen geld bleek te kosten.
  Staat er in één rij een hoog én een laag getal, dan zijn twee rekenmethodes het oneens over
  dezelfde wedstrijd — en dan hoort er geen bet uit te komen.</p>

  <div class="tablewrap">
    <table>
      <thead><tr><th>Wedstrijd</th><th>Markt</th><th>xG-model</th><th>2e methode</th>
        <th>zwakste stand</th><th>Valt af op</th></tr></thead>
      <tbody>
        {chr(10).join(rows)}
      </tbody>
    </table>
  </div>
</section>'''


def render_finding(finding) -> str:
    """Rendert één bevinding, of een lijst bevindingen achter elkaar.

    De lijstvorm is toegevoegd op 18 aug 2026: die dag had de run twee losstaande dingen uit te
    leggen (waarom een bet met voldoende voordeel toch niet is aanbevolen, en wat het kost dat een
    databron definitief geblokkeerd is). Die in één blok proppen maakt beide verhalen slechter, en
    ze in `todo` zetten is fout — het zijn geen handelingen voor de gebruiker maar uitleg.
    """
    if isinstance(finding, list):
        items = [f for f in finding if f]
        # Alleen de eerste is "de belangrijkste bevinding"; die kop twee keer op één pagina zetten
        # is niet waar. Een bevinding mag zijn eigen `eyebrow` meegeven.
        for i, f in enumerate(items):
            f.setdefault("eyebrow", "De belangrijkste bevinding" if i == 0 else "Ook uit deze run")
        return "\n".join(render_finding(f) for f in items)
    if not finding:
        return ""
    paragraphs = "\n    ".join(f'<p class="prose">{p}</p>' for p in finding.get("paragraphs", []))
    table = ""
    if finding.get("table"):
        head = "".join(f"<th>{esc(h)}</th>" for h in finding["table"]["head"])
        body = "\n        ".join(
            "<tr>" + "".join(
                f'<td class="{"comp" if i == 0 else "num"}">{cell}</td>' if i < len(row) - 1
                else f"<td>{cell}</td>"
                for i, cell in enumerate(row)) + "</tr>"
            for row in finding["table"]["rows"])
        table = f'''
  <div class="tablewrap" style="margin-top:24px">
    <table>
      <thead><tr>{head}</tr></thead>
      <tbody>
        {body}
      </tbody>
    </table>
  </div>'''
    return f'''
<section>
  <div class="sectionhead">
    <span class="eyebrow">{esc(finding.get("eyebrow", "De belangrijkste bevinding"))}</span>
    <h2>{esc(finding.get("title", "Wat deze run opleverde"))}</h2>
  </div>
  <div class="stack g16 measure">
    {paragraphs}
  </div>{table}
</section>'''


def render_todo(items: list[dict]) -> str:
    if not items:
        return ""
    blocks = []
    for i, item in enumerate(items, 1):
        done = item.get("done")
        mark = "✓" if done else str(i)
        when = f'<span class="when">{esc(item["when"])}</span>' if item.get("when") else ""
        blocks.append(f'''<div class="task">
      <span class="tick{' done' if done else ''}">{mark}</span>
      <span class="body">
        <span class="t">{esc(item["title"])}</span>
        <span class="d">{esc(item.get("detail", ""))}</span>
        {when}
      </span>
    </div>''')
    return f'''
<section>
  <div class="sectionhead">
    <span class="eyebrow">Actie</span>
    <h2>Wat jij nog moet doen</h2>
  </div>
  <div class="todo">
    {"".join(blocks)}
  </div>
</section>'''


def render_settled(entries: list[dict], stats: dict) -> str:
    # Een push (inzet terug) is geen verlies. Tot 31 aug 2026 rendeerde elke uitkomst die niet
    # 'won' was als "verloren", en dat maakte van een teruggegeven inzet stilzwijgend een nederlaag.
    chip = {"won": ("ok", "gewonnen"), "lost": ("gap", "verloren"), "void": ("", "inzet terug")}
    rows = "\n        ".join(
        f'<tr><td class="comp">{esc(e["label"])}</td><td class="num">{esc(e["score"])}</td>'
        f'<td><span class="chip {chip.get(e.get("result"), ("gap", "verloren"))[0]}">'
        f'{chip.get(e.get("result"), ("gap", "verloren"))[1]}</span></td></tr>'
        for e in entries)
    table = f'''
  <div class="tablewrap" style="margin-bottom:22px">
    <table>
      <thead><tr><th>Afgewikkelde bet</th><th>Uitslag</th><th>Resultaat</th></tr></thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>''' if entries else ""

    if not stats["settled"]:
        verdict = ('<p class="prose">Er is nog geen enkele bet afgewikkeld, dus over de kwaliteit '
                   'valt nog niets te zeggen.</p>')
    else:
        own, market = stats["brier_own"], stats["brier_market"]
        if own is None or market is None:
            verdict = ""
        elif own < market:
            verdict = (f'<div class="callout"><p class="prose"><strong>De cijferregel om op te '
                       f'letten.</strong> Er is één getal dat op termijn zegt of dit werkt: of mijn '
                       f'kansinschatting scherper is dan die van de bookmaker. Op dit moment is die '
                       f'van mij beter ({own:.3f} tegen {market:.3f} — lager is beter). Bij '
                       f'{stats["settled"]} wedstrijden is dat nog geen bewijs, maar het staat de '
                       f'goede kant op.</p></div>')
        else:
            verdict = (f'<div class="callout warn"><p class="prose"><strong>De cijferregel om op te '
                       f'letten.</strong> Er is één getal dat op termijn zegt of dit werkt: of mijn '
                       f'kansinschatting scherper is dan die van de bookmaker. Op dit moment is die '
                       f'van de bookmaker beter ({market:.3f} tegen mijn {own:.3f} — lager is beter). '
                       f'Bij {stats["settled"]} wedstrijden is dat ruis, maar het is de goede meter, '
                       f'en hij staat nu in het rood.</p></div>')
    return f'''
<section>
  <div class="sectionhead">
    <span class="eyebrow">Eerlijke stand</span>
    <h2>Hoe het tot nu toe gaat</h2>
  </div>{table}
  <div class="stack g16 measure">
    {verdict}
  </div>
</section>'''


def render(run_id: str, day: date, picks: list[dict], all_picks: list[dict],
           state: dict, prose: dict) -> str:
    labels = prose.get("coverage_labels", {})
    stats = ledger_summary(all_picks)
    comps = normalise_competitions(state)
    active = sum(1 for r in comps.values() if r.get("status") != "GEEN WEDSTRIJD")
    matches = sum(len(r.get("matches", [])) for r in comps.values())
    # De bets zelf ook op score tonen, zodat de volgorde daar niet afwijkt van de topselectie.
    ranked_picks = [p for group in rank_picks(picks, day) for p in group] if picks else picks
    record = f'{stats["won"]}/{stats["settled"]}' if stats["settled"] else "–"
    record_colour = ' style="color:var(--neg)"' if stats["settled"] and not stats["won"] else ""
    started = prose.get("started")
    verdict = prose.get("verdict") or (
        f'Van <b>{matches} wedstrijden</b> in <b>{active} competities</b> '
        f'{"blijft er <b>1 bet</b> over" if len(picks) == 1 else f"blijven er <b>{len(picks)} bets</b> over"}.')

    gloss = "\n    ".join(
        f'<div class="term"><dt>{esc(t)}</dt><dd>{d}</dd></div>' for t, d in GLOSSARY)

    truncated = prose.get("truncated", 0)
    trunc_line = (f'<p class="prose measure" style="margin-top:20px">Er is <strong>niets weggelaten '
                  f'wegens tijdgebrek</strong>: er mogen er 30 per run diep worden bekeken en het '
                  f'waren er {matches}.</p>') if not truncated else (
        f'<p class="prose measure" style="margin-top:20px"><strong>{truncated} wedstrijden zijn '
        f'afgekapt</strong> omdat er per run maximaal 30 diep bekeken kunnen worden.</p>')

    return f'''<title>Run {run_id.upper()} — {nl_date(day)}</title>
<style>{CSS}</style>

<div class="wrap">

<header>
  <div class="masthead">
    <h1>Run {run_id.upper()}</h1>
    <span class="date">{nl_date(day)}{f" · gedraaid om {esc(started)}" if started else ""}</span>
  </div>

  <p class="verdict">{verdict}</p>

  <div class="facts">
    <div class="fact"><span class="v num">{len(picks)}</span><span class="l">bets gepubliceerd</span></div>
    <div class="fact"><span class="v num">{matches}</span><span class="l">wedstrijden bekeken</span></div>
    <div class="fact"><span class="v num">{active}</span><span class="l">competities actief</span></div>
    <div class="fact"><span class="v num">{truncated}</span><span class="l">wedstrijden afgekapt</span></div>
    <div class="fact"><span class="v num"{record_colour}>{record}</span><span class="l">record tot nu toe</span></div>
  </div>
</header>

<section>
  <div class="sectionhead">
    <span class="eyebrow">Het antwoord</span>
    <h2>{"De bet" if len(picks) == 1 else f"De {len(picks)} bets" if picks else "Geen bets vandaag"}</h2>
  </div>
  {render_bets(ranked_picks, prose.get("bets", {}), labels)}
</section>
{render_shortlist(picks, prose.get("bets", {}), labels, day)}
{f'<div class="wrap-callout"><div class="callout"><p class="prose">{prose["next_best"]}</p></div></div>' if prose.get("next_best") else ""}
{render_near_misses(state, labels)}
{render_todo(prose.get("todo", []))}
{render_finding(prose.get("finding"))}
<section>
  <div class="sectionhead">
    <span class="eyebrow">Dekkingsrapportage</span>
    <h2>Wat er is bekeken, en wat niet</h2>
  </div>

  <p class="prose measure" style="margin-bottom:22px">Alle {len(comps)} competities uit de opdracht, elk met één status.</p>

  <div class="tablewrap">
    <table>
      <thead><tr><th>Competitie</th><th>Status</th><th>Toelichting</th></tr></thead>
      <tbody>
        {render_coverage(state, prose.get("coverage_notes", {}), labels)}
      </tbody>
    </table>
  </div>
  {trunc_line}
</section>
{render_settled(prose.get("settled", []), stats)}
<section>
  <div class="sectionhead">
    <span class="eyebrow">De termen</span>
    <h2>Wat al dat jargon betekent</h2>
  </div>
  <dl class="gloss">
    {gloss}
  </dl>
</section>

<footer>
  <p class="disc">{DISCLAIMER}</p>
  <p class="meta">Run {run_id.upper()} · {nl_date(day)} · {len(picks)} bets uit {matches} wedstrijden{f" · {esc(prose['sources'])}" if prose.get("sources") else ""}</p>
</footer>

</div>
'''


CSS = """
:root{
  --ground:#EBEEF2; --surface:#FFFFFF; --surface-2:#F4F6F9;
  --ink:#141A21; --ink-2:#3D4854; --muted:#68737F; --line:#D3DAE2; --line-soft:#E3E8EE;
  --accent:#96620F; --accent-ink:#7A4F0B; --accent-wash:#F6EDDC;
  --pos:#256B4E; --pos-wash:#E2EFE8;
  --neg:#9E3B33; --neg-wash:#F6E5E3;
  --hold:#5C6672; --hold-wash:#E7EBEF;
  --shadow:0 1px 2px rgba(20,26,33,.06), 0 8px 24px -12px rgba(20,26,33,.18);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0C1117; --surface:#141B23; --surface-2:#1A222B;
    --ink:#E6EBF1; --ink-2:#B9C3CE; --muted:#8593A2; --line:#2A343F; --line-soft:#212A34;
    --accent:#D6A44B; --accent-ink:#E8BC6C; --accent-wash:#2A2313;
    --pos:#5FB48C; --pos-wash:#16281F;
    --neg:#D77A70; --neg-wash:#2B1917;
    --hold:#8B98A6; --hold-wash:#1D252E;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --ground:#0C1117; --surface:#141B23; --surface-2:#1A222B;
  --ink:#E6EBF1; --ink-2:#B9C3CE; --muted:#8593A2; --line:#2A343F; --line-soft:#212A34;
  --accent:#D6A44B; --accent-ink:#E8BC6C; --accent-wash:#2A2313;
  --pos:#5FB48C; --pos-wash:#16281F;
  --neg:#D77A70; --neg-wash:#2B1917;
  --hold:#8B98A6; --hold-wash:#1D252E;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.7);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  font-size:17px; line-height:1.5; -webkit-font-smoothing:antialiased;
}
.prose{font-family:ui-serif,Georgia,"Iowan Old Style","Times New Roman",serif; font-size:1.02rem; line-height:1.62; color:var(--ink-2)}
.num{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace; font-variant-numeric:tabular-nums}

.wrap{max-width:920px; margin:0 auto; padding:0 20px 80px}
section{margin-top:56px}
h1,h2,h3{text-wrap:balance; margin:0}
h2{font-size:1.5rem; font-weight:750; letter-spacing:-.018em}
p{margin:0}
.stack{display:flex; flex-direction:column}
.g16{gap:16px}
.measure{max-width:64ch}

.eyebrow{font-size:.7rem; font-weight:700; letter-spacing:.13em; text-transform:uppercase; color:var(--accent)}
.sectionhead{display:flex; flex-direction:column; gap:6px; padding-bottom:16px; border-bottom:2px solid var(--ink); margin-bottom:24px}

header{padding:44px 0 0}
.masthead{display:flex; flex-wrap:wrap; align-items:baseline; gap:12px 18px; padding-bottom:20px; border-bottom:1px solid var(--line)}
.masthead h1{font-size:clamp(1.9rem,5vw,2.6rem); font-weight:800; letter-spacing:-.032em; line-height:1.05}
.masthead .date{font-size:.95rem; color:var(--muted); font-weight:500}
.verdict{margin-top:22px; font-size:clamp(1.15rem,2.9vw,1.42rem); line-height:1.42; font-weight:600; letter-spacing:-.014em; max-width:34ch}
.verdict b{color:var(--accent-ink); font-weight:800}

.facts{display:grid; grid-template-columns:repeat(auto-fit,minmax(132px,1fr)); gap:1px; background:var(--line-soft); border:1px solid var(--line-soft); border-radius:10px; overflow:hidden; margin-top:30px}
.fact{background:var(--surface); padding:14px 16px; display:flex; flex-direction:column; gap:3px}
.fact .v{font-size:1.5rem; font-weight:780; letter-spacing:-.03em}
.fact .l{font-size:.74rem; color:var(--muted); font-weight:600; letter-spacing:.02em}

.bet{background:var(--surface); border:1px solid var(--line); border-radius:12px; box-shadow:var(--shadow); overflow:hidden}
.bet + .bet{margin-top:20px}
.bet-top{padding:20px 22px 18px; display:flex; flex-wrap:wrap; gap:14px 20px; align-items:flex-start; justify-content:space-between}
.bet-id{display:flex; flex-direction:column; gap:5px; min-width:min(100%,260px)}
.bet-meta{font-size:.78rem; color:var(--muted); font-weight:600; letter-spacing:.03em; text-transform:uppercase}
.bet-match{font-size:1.22rem; font-weight:760; letter-spacing:-.02em; line-height:1.25}
.bet-pick{display:inline-flex; align-items:center; gap:8px; align-self:flex-start; margin-top:4px;
  background:var(--accent-wash); color:var(--accent-ink); border:1px solid color-mix(in srgb,var(--accent) 30%,transparent);
  padding:5px 11px; border-radius:6px; font-size:.9rem; font-weight:700}
.price{text-align:right; display:flex; flex-direction:column; gap:2px; margin-left:auto}
.price .odds{font-size:2.1rem; font-weight:800; letter-spacing:-.04em; line-height:1}
.price .book{font-size:.8rem; color:var(--muted); font-weight:600}

.probrow{display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--line-soft); border-top:1px solid var(--line-soft); border-bottom:1px solid var(--line-soft)}
.prob{background:var(--surface-2); padding:13px 16px; display:flex; flex-direction:column; gap:2px}
.prob .l{font-size:.72rem; color:var(--muted); font-weight:650; letter-spacing:.02em}
.prob .v{font-size:1.28rem; font-weight:750; letter-spacing:-.025em}
.prob.hl .v{color:var(--accent-ink)}

.why{padding:18px 22px 22px; display:flex; flex-direction:column; gap:12px}
.why h4{margin:0; font-size:.72rem; font-weight:700; letter-spacing:.13em; text-transform:uppercase; color:var(--muted)}
.risk{display:inline-flex; align-items:center; gap:7px; font-size:.82rem; font-weight:650; color:var(--ink-2)}
.dot{width:8px; height:8px; border-radius:50%; flex:none}
.dot.med{background:var(--accent)} .dot.high{background:var(--neg)}

.chip{display:inline-block; padding:3px 9px; border-radius:5px; font-size:.73rem; font-weight:700; white-space:nowrap}
.chip.ok{background:var(--pos-wash); color:var(--pos)}
.chip.none{background:var(--hold-wash); color:var(--hold)}
.chip.gap{background:var(--neg-wash); color:var(--neg)}
.chip.low{background:var(--pos-wash); color:var(--pos)}
.chip.med{background:var(--accent-wash); color:var(--accent-ink)}
.chip.high{background:var(--neg-wash); color:var(--neg)}
/* een getal onder de drempel: de reden dat de bet er niet is, dus visueel te vinden */
.num.below{color:var(--neg); font-weight:600}

.tablewrap{overflow-x:auto; border:1px solid var(--line); border-radius:10px; background:var(--surface)}
table{border-collapse:collapse; width:100%; font-size:.9rem; min-width:520px}
th{text-align:left; font-size:.7rem; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); font-weight:700;
   padding:11px 16px; background:var(--surface-2); border-bottom:1px solid var(--line); white-space:nowrap}
td{padding:11px 16px; border-bottom:1px solid var(--line-soft); vertical-align:top}
tr:last-child td{border-bottom:0}
td.comp{font-weight:640; white-space:nowrap}
td.note{color:var(--ink-2); font-size:.86rem}

/* Topselectie: de rangschikking van §5, zodat "welke zou ik spelen" een antwoord krijgt. */
table.shortlist{min-width:640px}
table.shortlist td{vertical-align:middle}
td.rank{font-size:1.05rem; font-weight:700; color:var(--accent-ink); width:1%}
.sl-match{display:block; font-weight:660; letter-spacing:-.01em}
.sl-pick{display:block; font-size:.82rem; color:var(--muted); margin-top:3px}
.wrap-callout{max-width:var(--measure, 68ch); margin:24px auto 0}

.todo{display:flex; flex-direction:column; gap:1px; background:var(--line-soft); border:1px solid var(--line-soft); border-radius:10px; overflow:hidden}
.task{background:var(--surface); padding:16px 18px; display:flex; gap:14px; align-items:flex-start}
.tick{width:22px; height:22px; border-radius:5px; border:2px solid var(--line); flex:none; margin-top:1px; display:grid; place-items:center; color:var(--muted); font-size:.72rem; font-weight:800}
.tick.done{background:var(--pos-wash); border-color:var(--pos); color:var(--pos)}
.task .body{display:flex; flex-direction:column; gap:4px}
.task .t{font-weight:680; letter-spacing:-.008em}
.task .d{font-size:.88rem; color:var(--ink-2)}
.when{font-size:.74rem; font-weight:700; color:var(--accent-ink); background:var(--accent-wash); padding:2px 8px; border-radius:4px; align-self:flex-start; margin-top:2px}

.gloss{display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr)); gap:1px; background:var(--line-soft); border:1px solid var(--line-soft); border-radius:10px; overflow:hidden}
.term{background:var(--surface); padding:16px 18px; display:flex; flex-direction:column; gap:6px}
.term dt{font-weight:720; font-size:.95rem; letter-spacing:-.01em}
.term dd{margin:0; font-size:.88rem; color:var(--ink-2); line-height:1.55}
.term dd em{color:var(--muted); font-style:normal}

.callout{border-left:3px solid var(--accent); background:var(--surface); padding:18px 20px; border-radius:0 10px 10px 0; display:flex; flex-direction:column; gap:10px}
.callout.warn{border-left-color:var(--neg)}

footer{margin-top:64px; padding-top:24px; border-top:1px solid var(--line); display:flex; flex-direction:column; gap:10px}
footer .disc{font-size:.92rem; color:var(--ink-2); font-style:italic; max-width:62ch}
footer .meta{font-size:.78rem; color:var(--muted)}
a{color:var(--accent-ink)}
:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--run", required=True, choices=["A", "B", "a", "b"])
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("-o", "--output", help="standaard runs/<datum>-run-<id>.html")
    args = parser.parse_args()

    run_id = args.run.lower()
    day = date.fromisoformat(args.date)

    state_path = STATE_DIR / f"{day.isoformat()}-run-{run_id}.json"
    if not state_path.exists():
        raise SystemExit(f"Geen voortgangsbestand: {state_path}. Draai eerst de run.")
    state = json.loads(state_path.read_text())

    all_picks = ledger.load_picks()
    # `void` staat voor een pick die is teruggetrokken vóór aftrap (10 aug 2026: een bet die was
    # gepubliceerd onder een regelset waar poort 5 nog uit ontbrak). Zo'n regel blijft in het
    # logboek staan omdat hij wél is verstuurd, maar hij mag niet als speelbare bet op de pagina
    # komen — dan leest de lezer een advies dat is ingetrokken.
    picks = [p for p in all_picks
             if p.get("run", "").lower() == run_id and p.get("run_date") == day.isoformat()
             and p.get("result") != "void"]

    prose_path = RUNS_DIR / f"{day.isoformat()}-run-{run_id}.prose.json"
    if prose_path.exists():
        prose = json.loads(prose_path.read_text())
    else:
        prose = {}
        print(f"Let op: geen {prose_path.name} — de pagina komt zonder de verhalende stukken.")

    out = Path(args.output) if args.output else RUNS_DIR / f"{day.isoformat()}-run-{run_id}.html"
    out.write_text(render(run_id, day, picks, all_picks, state, prose))
    print(f"{out} geschreven — {len(picks)} bet(s), "
          f"{len(state.get('competitions', {}))} competities.")
    print("Publiceer hem daarna als Artifact en zet de link in de notificatie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
