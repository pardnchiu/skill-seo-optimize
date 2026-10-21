#!/usr/bin/env python3
import argparse
import http.cookiejar
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://trends.google.com/trends/api"


def opener(hl):
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/126 Safari/537.36"),
        ("Accept-Language", hl),
    ]
    try:
        op.open("https://trends.google.com/?geo=US", timeout=20).read()
    except (urllib.error.URLError, TimeoutError):
        pass
    return op


def fetch(op, url, retries=5):
    last = None
    for i in range(retries):
        try:
            body = op.open(url, timeout=30).read().decode()
            return json.loads(body[body.find("{"):])
        except urllib.error.HTTPError as e:
            last = f"[Unavailable] trends: HTTP {e.code}" if e.code == 429 else f"[Upstream] trends: HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            last = f"[Timeout] trends: {e}"
        except json.JSONDecodeError as e:
            last = f"[Upstream] trends: unparsable response: {e}"
        time.sleep(6 * (i + 1))
    raise RuntimeError(f"[Limit] trends: retries exhausted: {last}")


def compare(op, terms, geo, timeframe, hl):
    req = {"comparisonItem": [{"keyword": t, "geo": "" if geo == "WW" else geo, "time": timeframe} for t in terms], "category": 0, "property": ""}
    explore = fetch(op, f"{BASE}/explore?hl={hl}&tz=0&req={urllib.parse.quote(json.dumps(req))}")
    widget = next((w for w in explore.get("widgets", []) if w.get("id") == "TIMESERIES"), None)
    if widget is None:
        raise RuntimeError(f"[Upstream] trends: no TIMESERIES widget for {terms}")
    data = fetch(op, f"{BASE}/widgetdata/multiline?hl={hl}&tz=0&req={urllib.parse.quote(json.dumps(widget['request']))}&token={widget['token']}")
    points = data["default"]["timelineData"]
    if not points:
        raise RuntimeError(f"[Not found] trends: empty timeline for {terms}")
    windows = [points, points[-12:], points[-4:]]
    return {t: tuple(sum(p["value"][i] for p in w) / len(w) for w in windows) for i, t in enumerate(terms)}


def main():
    ap = argparse.ArgumentParser(description="Google Trends relative interest, normalized to one anchor term across batches")
    ap.add_argument("terms", nargs="+")
    ap.add_argument("--anchor", required=True)
    ap.add_argument("--geo", default="US")
    ap.add_argument("--time", default="today 12-m")
    ap.add_argument("--hl", default="en-US")
    args = ap.parse_args()

    terms = [t for t in dict.fromkeys(args.terms) if t != args.anchor]
    if not terms:
        sys.exit("[Invalid] terms: at least one term other than the anchor is required")
    op = opener(args.hl)
    out = {}
    for geo in [g.strip() for g in args.geo.split(",") if g.strip()]:
        rows, ref, errors = {}, None, []
        for i in range(0, len(terms), 4):
            batch = [args.anchor] + terms[i:i + 4]
            try:
                res = compare(op, batch, geo, args.time, args.hl)
            except RuntimeError as e:
                errors.append(f"{batch[1:]}: {e}")
                continue
            a = res[args.anchor]
            if ref is None:
                ref = a
                rows[args.anchor] = a
            for t in batch[1:]:
                v = res[t]
                rows[t] = tuple(v[k] * ref[k] / a[k] if a[k] else 0.0 for k in range(3))
            time.sleep(4)
        out[geo] = {
            "rows": sorted(([t, *(round(x, 2) for x in v)] for t, v in rows.items()), key=lambda r: -r[1]),
            "errors": errors,
        }
    print(json.dumps({"anchor": args.anchor, "time": args.time, "columns": ["term", "avg", "recent12w", "recent4w"], "geo": out}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
