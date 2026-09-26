#!/usr/bin/env python3
"""Behutsamer, fortsetzbarer Abruf fehlender Wowhead-Forever-Itemseiten.

Ersetzt fetch-wowhead-items.ps1. Laeuft lokal, nur Standardbibliothek.

  check   Validator am vorhandenen Cache pruefen, Fortschritt gegen die CSV zeigen
  fetch   fehlende Seiten sequenziell laden; globaler Stopp bei 403/429/5xx/Challenge
  ingest  manuell im Browser gespeicherte Itemseiten pruefen und als <ID>.html uebernehmen

Standardpfade gelten relativ zum Repository-Root (work/forever-beta-quality-of-life).
Der Importer tools/import_wowhead_drops.py bleibt die massgebliche Pruefung;
dieses Skript sorgt nur dafuer, dass kein Challenge- oder Fremdinhalt als <ID>.html landet.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

USER_AGENT = "BetaQoL-DropResearch/0.9.7 (personal addon dataset; sequential, low rate)"
FOREVER_ENV = 16
DEFAULT_BASE = "https://www.wowhead.com"
DEFAULT_CSV = "../../outputs/Questitem-Downloadliste.csv"
DEFAULT_CACHE = "../quest-drop-research/wowhead-items"
DEFAULT_STATE = "../quest-drop-research/wowhead-fetch-state.json"
DEFAULT_REJECTED = "../quest-drop-research/wowhead-rejected"

BLOCK_CODES = {401, 403, 407, 429}
CHALLENGE_MARKERS = (
    "cf-chl", "cf_chl_opt", "challenge-platform", "/cdn-cgi/challenge",
    "Just a moment", "Attention Required", "px-captcha", "Request blocked",
)
# Ergebnisse, bei denen die Seite fuer diesen Datensatz endgueltig nichts liefert.
TERMINAL_SKIP = {"not_found", "not_in_forever", "wrong_env"}
ID_KEYS = ("id", "typeId", "entityId", "itemId", "pageId")
DROPPED_BY_RE = re.compile(r"""id\s*:\s*['"]dropped-by['"]""")


# ---------------------------------------------------------------- Validierung

def parse_page_meta(html: str) -> Optional[dict]:
    """Erstes JSON-Objekt nach 'data.pageMeta', das nach Seitenmetadaten aussieht."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"data\.pageMeta", html):
        brace = html.find("{", m.end())
        if brace == -1 or brace - m.end() > 200:
            continue
        try:
            obj, _ = dec.raw_decode(html, brace)
        except ValueError:
            continue
        if isinstance(obj, dict) and ("page" in obj or "dataEnv" in obj):
            return obj
    return None


def meta_item_id(meta: dict) -> Optional[int]:
    for key in ID_KEYS:
        val = meta.get(key)
        if isinstance(val, dict):
            val = val.get("id")
        if isinstance(val, bool):
            continue
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)
    return None


def meta_env(meta: dict) -> Optional[int]:
    env = meta.get("dataEnv")
    if isinstance(env, dict):
        env = env.get("env")
    if env is None:
        env = meta.get("env")
    try:
        return int(env)
    except (TypeError, ValueError):
        return None


def canonical_item_id(html: str) -> Optional[int]:
    """Item-ID aus <link rel=canonical> oder og:url (nicht aus beliebigen Links der Seite)."""
    for tag in re.finditer(r"<(?:link|meta)\b[^>]*>", html[:200000], re.I):
        text = tag.group(0)
        if re.search(r"""rel=["']canonical["']|property=["']og:url["']""", text, re.I):
            found = re.search(r"/forever/item=(\d+)", text)
            if found:
                return int(found.group(1))
    return None


def classify(html: str, expected_id: Optional[int]) -> Tuple[str, Optional[int], Optional[dict]]:
    """Liefert (Urteil, Item-ID, pageMeta). Urteil 'ok' heisst: echte Forever-Itemseite."""
    meta = parse_page_meta(html)
    if meta is None:
        if any(marker in html for marker in CHALLENGE_MARKERS):
            return "challenge", None, None
        return "no_meta", None, None
    if meta.get("page") not in (None, "item"):
        return "not_item", None, meta
    item_id = meta_item_id(meta)
    if item_id is None:
        item_id = canonical_item_id(html)
    if item_id is None:
        return "id_unknown", None, meta
    if expected_id is not None and item_id != expected_id:
        return "id_mismatch", item_id, meta
    if meta_env(meta) != FOREVER_ENV:
        return "wrong_env", item_id, meta
    return "ok", item_id, meta


def read_html(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def scan_cache(cache: Path) -> Dict[int, Tuple[str, bool]]:
    """{item_id: (urteil, hat_dropped_by)} fuer alle <ID>.html im Cache."""
    result = {}
    if not cache.is_dir():
        return result
    for path in cache.glob("*.html"):
        if not path.stem.isdigit():
            continue
        html = read_html(path)
        verdict, _, _ = classify(html, int(path.stem))
        result[int(path.stem)] = (verdict, bool(DROPPED_BY_RE.search(html)))
    return result


# ---------------------------------------------------------------- Dateien und Zustand

def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def load_csv(path: Path) -> List[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["item_id"] = int(row["item_id"])
        row["priority"] = int(row["priority"])
    rows.sort(key=lambda r: r["priority"])  # stabil: CSV-Reihenfolge innerhalb der Prioritaet bleibt
    return rows


def load_state(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"items": {}, "stop": None, "runs": []}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_bytes(text.encode("utf-8"))
    os.replace(tmp, path)


# ---------------------------------------------------------------- HTTP

class Response:
    def __init__(self, status: int, url: str, headers, text: str):
        self.status, self.url, self.headers, self.text = status, url, headers, text


def http_get(url: str, timeout: float) -> Response:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
        "Accept-Language": "en-US,en;q=0.8",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, final, headers, body = resp.status, resp.geturl(), resp.headers, resp.read()
    except urllib.error.HTTPError as err:
        status, final, headers = err.code, err.geturl() or url, err.headers
        body = err.read() or b""
    encoding = (headers.get("Content-Encoding") or "").lower()
    if encoding == "gzip" and body:
        body = gzip.decompress(body)
    elif encoding == "deflate" and body:
        body = zlib.decompress(body)
    charset = headers.get_content_charset() or "utf-8"
    return Response(status, final, headers, body.decode(charset, errors="replace"))


# ---------------------------------------------------------------- Kommandos

def cmd_check(args) -> int:
    rows = load_csv(Path(args.csv))
    cache = scan_cache(Path(args.cache))
    state = load_state(Path(args.state))

    verdicts: Dict[str, int] = {}
    for verdict, _ in cache.values():
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
    ok_ids = {i for i, (v, _) in cache.items() if v == "ok"}
    print(f"Cache {args.cache}: {len(cache)} <ID>.html-Dateien, Urteile: {verdicts or '-'}")
    bad = sorted(i for i, (v, _) in cache.items() if v != "ok")
    if bad:
        print(f"  Nicht bestanden (Auszug): {bad[:15]}")
    if ok_ids:
        sample = Path(args.cache) / f"{min(ok_ids)}.html"
        meta = parse_page_meta(read_html(sample)) or {}
        print(f"  pageMeta-Schluessel am Beispiel {sample.name}: {sorted(meta)}")
        dropped = sum(1 for i in ok_ids if cache[i][1])
        print(f"  davon mit 'dropped-by'-Tabelle: {dropped}")

    print(f"\nDownloadliste {args.csv}: {len(rows)} Items")
    for prio in sorted({r['priority'] for r in rows}):
        part = [r for r in rows if r["priority"] == prio]
        done = sum(1 for r in part if r["item_id"] in ok_ids)
        skipped = sum(1 for r in part if r["item_id"] not in ok_ids
                      and state["items"].get(str(r["item_id"]), {}).get("result") in TERMINAL_SKIP)
        print(f"  Prioritaet {prio} ({part[0]['status']}): {done}/{len(part)} im Cache, "
              f"{skipped} endgueltig ohne Seite, {len(part) - done - skipped} offen")

    stop = state.get("stop")
    if stop:
        print(f"\nLetzter Stopp: {stop['reason']} (HTTP {stop.get('http')}) bei Item {stop.get('item_id')} "
              f"am {stop['at']}; Cooldown bis {stop.get('until') or '-'}")
    if cache and not ok_ids:
        print("\nFEHLER: Keine einzige Cache-Datei besteht die Pruefung. Validator passt nicht zum "
              "Seitenformat; bitte vor dem Abruf anpassen.")
        return 1
    return 0


def cmd_fetch(args) -> int:
    csv_path, cache_dir, state_path = Path(args.csv), Path(args.cache), Path(args.state)
    rejected_dir = Path(args.rejected)
    rows = load_csv(csv_path)
    state = load_state(state_path)
    cache_dir.mkdir(parents=True, exist_ok=True)

    stop = state.get("stop")
    if stop and stop.get("until") and not args.ignore_cooldown:
        until = dt.datetime.fromisoformat(stop["until"])
        if until > now_utc():
            print(f"Abbruch: Cooldown nach '{stop['reason']}' (HTTP {stop.get('http')}) laeuft bis "
                  f"{until.astimezone().strftime('%d.%m.%Y %H:%M')}. Kein erneuter Abruf vorher.")
            return 3

    cache = scan_cache(cache_dir)
    if cache and not any(v == "ok" for v, _ in cache.values()):
        print("Abbruch: Keine vorhandene Cache-Datei besteht den Validator. Erst 'check' ausfuehren.")
        return 1
    ok_ids = {i for i, (v, _) in cache.items() if v == "ok"}

    wanted = set(args.priority) if args.priority else None
    queue = []
    for row in rows:
        iid = row["item_id"]
        if wanted and row["priority"] not in wanted:
            continue
        if iid in ok_ids:
            continue
        prior = state["items"].get(str(iid), {}).get("result")
        if prior in TERMINAL_SKIP and not args.retry_skipped:
            continue
        queue.append(row)
    queue = queue[: args.max]
    if not queue:
        print("Nichts zu tun: alle ausgewaehlten Items sind im Cache oder endgueltig ohne Seite.")
        return 0

    minutes = (len(queue) * args.delay + (len(queue) // args.batch) * args.batch_pause) / 60
    print(f"{len(queue)} Seiten geplant (Prioritaeten {sorted({r['priority'] for r in queue})}), "
          f"Abstand {args.delay}s, Pause {args.batch_pause}s alle {args.batch}; ca. {minutes:.0f} min.")
    if args.dry_run:
        for row in queue[:20]:
            print(f"  {row['priority']} {row['item_id']} {row['name']}")
        return 0

    run = {"started": now_utc().isoformat(), "planned": len(queue), "ok": 0, "results": {}}
    state["runs"].append(run)
    state["stop"] = None

    def halt(reason: str, http: Optional[int], item_id: Optional[int], retry_after=None, cooldown=True) -> int:
        state["stop"] = {
            "reason": reason, "http": http, "item_id": item_id, "at": now_utc().isoformat(),
            "retry_after": retry_after,
            "until": (now_utc() + dt.timedelta(hours=args.cooldown_hours)).isoformat() if cooldown else None,
        }
        run["finished"] = now_utc().isoformat()
        save_state(state_path, state)
        print(f"\nSTOPP: {reason} (HTTP {http}) bei Item {item_id}. Fortschritt gesichert.")
        if retry_after:
            print(f"  Server nennt Retry-After: {retry_after}")
        if cooldown:
            print(f"  Kein weiterer Abruf fuer {args.cooldown_hours} h. Alternativ die restlichen Seiten im "
                  f"Browser speichern und mit 'ingest' uebernehmen.")
        return 2

    # robots.txt mit derselben Kennung holen: zugleich Probe, ob der Block noch besteht.
    try:
        robots = http_get(args.base_url.rstrip("/") + "/robots.txt", args.timeout)
    except (urllib.error.URLError, OSError) as err:
        return halt(f"Netzwerkfehler bei robots.txt: {err}", None, None, cooldown=False)
    if robots.status in BLOCK_CODES or robots.status >= 500:
        return halt("robots.txt blockiert", robots.status, None, robots.headers.get("Retry-After"))
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(robots.text.splitlines())
    probe_url = f"{args.base_url.rstrip('/')}/forever/item={queue[0]['item_id']}"
    if robots.status == 200 and not parser.can_fetch(USER_AGENT, probe_url):
        return halt("robots.txt verbietet /forever/item= fuer diese Kennung; Abruf nicht zulaessig",
                    200, None, cooldown=False)

    try:
        for n, row in enumerate(queue):
            iid = row["item_id"]
            if n:
                time.sleep(args.batch_pause if n % args.batch == 0 else args.delay)
            url = f"{args.base_url.rstrip('/')}/forever/item={iid}"
            try:
                resp = http_get(url, args.timeout)
            except (urllib.error.URLError, OSError) as err:
                return halt(f"Netzwerkfehler: {err}", None, iid, cooldown=False)

            entry = {"at": now_utc().isoformat(), "http": resp.status, "final_url": resp.url}
            if resp.status in BLOCK_CODES or resp.status >= 500:
                entry["result"] = "blocked"
                state["items"][str(iid)] = entry
                return halt("Server blockiert oder ueberlastet", resp.status, iid, resp.headers.get("Retry-After"))
            if resp.status == 404:
                entry["result"] = "not_found"
            elif resp.status != 200:
                entry["result"] = f"http_{resp.status}"
                state["items"][str(iid)] = entry
                return halt("Unerwarteter HTTP-Status", resp.status, iid)
            elif "/forever/" not in resp.url:
                entry["result"] = "not_in_forever"
            else:
                verdict, _, _ = classify(resp.text, iid)
                entry["result"] = verdict
                if verdict == "ok":
                    write_atomic(cache_dir / f"{iid}.html", resp.text)
                    entry["dropped_by"] = bool(DROPPED_BY_RE.search(resp.text))
                    run["ok"] += 1
                elif verdict != "wrong_env":
                    rejected_dir.mkdir(parents=True, exist_ok=True)
                    write_atomic(rejected_dir / f"{iid}.{verdict}.html", resp.text)
                    state["items"][str(iid)] = entry
                    reason = "Challenge-Seite erkannt" if verdict == "challenge" else f"Unerwarteter Seiteninhalt ({verdict})"
                    return halt(reason, resp.status, iid, cooldown=(verdict == "challenge"))

            state["items"][str(iid)] = entry
            run["results"][entry["result"]] = run["results"].get(entry["result"], 0) + 1
            save_state(state_path, state)
            mark = "+" if entry["result"] == "ok" else "-"
            drop = " dropped-by" if entry.get("dropped_by") else ""
            print(f"[{n + 1}/{len(queue)}] {mark} {iid} {row['name']}: {entry['result']}{drop}", flush=True)
    except KeyboardInterrupt:
        run["finished"] = now_utc().isoformat()
        save_state(state_path, state)
        print("\nAbgebrochen; Fortschritt gesichert.")
        return 130

    run["finished"] = now_utc().isoformat()
    save_state(state_path, state)
    print(f"\nFertig: {run['ok']} neue Seiten gespeichert, Ergebnisse {run['results']}.")
    return 0


def cmd_ingest(args) -> int:
    rows = {r["item_id"]: r for r in load_csv(Path(args.csv))}
    cache_dir, state_path = Path(args.cache), Path(args.state)
    cache_dir.mkdir(parents=True, exist_ok=True)
    state = load_state(state_path)
    cache = scan_cache(cache_dir)
    counts: Dict[str, int] = {}
    for folder in args.folders:
        for path in sorted(Path(folder).rglob("*.htm*")):
            if path.suffix.lower() not in (".html", ".htm") or path.resolve().parent == cache_dir.resolve():
                continue
            html = read_html(path)
            verdict, iid, _ = classify(html, None)
            if verdict == "ok" and iid not in rows and not args.any_item:
                verdict = "not_in_list"
            if verdict == "ok" and cache.get(iid, ("",))[0] == "ok" and not args.overwrite:
                verdict = "already_cached"
            if verdict == "ok":
                write_atomic(cache_dir / f"{iid}.html", html)
                state["items"][str(iid)] = {"at": now_utc().isoformat(), "result": "ok",
                                            "source": "ingest", "file": path.name,
                                            "dropped_by": bool(DROPPED_BY_RE.search(html))}
            counts[verdict] = counts.get(verdict, 0) + 1
            print(f"{verdict:15} {iid or '-':>7} {path.name}")
    save_state(state_path, state)
    print(f"\nUebernommen: {counts.get('ok', 0)}; alle Urteile: {counts}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", default=DEFAULT_CSV)
    p.add_argument("--cache", default=DEFAULT_CACHE)
    p.add_argument("--state", default=DEFAULT_STATE)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Validator kalibrieren und Fortschritt zeigen")

    f = sub.add_parser("fetch", help="fehlende Seiten behutsam laden")
    f.add_argument("--priority", type=lambda s: [int(x) for x in s.split(",")], default=None,
                   help="z. B. 1,2 (Standard: alle)")
    f.add_argument("--max", type=int, default=250, help="Seiten pro Lauf (Standard 250)")
    f.add_argument("--delay", type=float, default=10.0, help="Sekunden zwischen Seiten (Standard 10)")
    f.add_argument("--batch", type=int, default=25, help="Seiten je Batch (Standard 25)")
    f.add_argument("--batch-pause", type=float, default=120.0, help="Pause nach jedem Batch in s (Standard 120)")
    f.add_argument("--cooldown-hours", type=float, default=12.0, help="Sperrfrist nach Block (Standard 12)")
    f.add_argument("--timeout", type=float, default=30.0)
    f.add_argument("--retry-skipped", action="store_true", help="404/Nicht-Forever-Items erneut versuchen")
    f.add_argument("--ignore-cooldown", action="store_true")
    f.add_argument("--dry-run", action="store_true")
    f.add_argument("--rejected", default=DEFAULT_REJECTED, help=argparse.SUPPRESS)
    f.add_argument("--base-url", default=DEFAULT_BASE, help=argparse.SUPPRESS)

    i = sub.add_parser("ingest", help="im Browser gespeicherte Seiten uebernehmen")
    i.add_argument("folders", nargs="+")
    i.add_argument("--any-item", action="store_true", help="auch Items ausserhalb der Downloadliste")
    i.add_argument("--overwrite", action="store_true")
    return p


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    args = build_parser().parse_args(argv)
    return {"check": cmd_check, "fetch": cmd_fetch, "ingest": cmd_ingest}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
