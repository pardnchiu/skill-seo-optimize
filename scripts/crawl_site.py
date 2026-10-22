#!/usr/bin/env python3
import argparse
import collections
import concurrent.futures as cf
import json
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_seo as A

UA = "Mozilla/5.0 (compatible; seo-optimize-crawl/1.0)"
LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
MAX_BODY = 3_000_000


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


NO_FOLLOW = urllib.request.build_opener(NoRedirect)


def fetch(url, follow=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        r = (urllib.request.urlopen if follow else NO_FOLLOW.open)(req, timeout=20)
        return {"status": r.status, "url": r.geturl(), "ctype": r.headers.get("Content-Type", ""), "location": "", "body": r.read(MAX_BODY).decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "url": url, "ctype": e.headers.get("Content-Type", ""), "location": e.headers.get("Location", ""), "body": ""}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return {"status": 0, "url": url, "ctype": "", "location": "", "body": "", "error": f"[Unavailable] {url}: {e}"}


def hop(url):
    first = fetch(url, follow=False)
    out = {"url": url, "status": first["status"], "location": urllib.parse.urljoin(url, first["location"]) if first["location"] else ""}
    if first["status"] in (301, 302, 303, 307, 308):
        final = fetch(url)
        out["final"] = final["url"]
        out["final_status"] = final["status"]
        out["to_root"] = urllib.parse.urlparse(final["url"]).path in ("", "/") and urllib.parse.urlparse(url).path not in ("", "/", "/index.html")
    if "error" in first:
        out["error"] = first["error"]
    return out


def sitemap_urls(origin, robots_body):
    host = urllib.parse.urlparse(origin).hostname
    queue = [s.strip() for s in A.SITEMAP_DIRECTIVE_RE.findall(robots_body)] or [f"{origin}/sitemap.xml"]
    seen, urls, foreign, sources = set(), [], collections.Counter(), []
    while queue:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        r = fetch(sm)
        sources.append({"url": sm, "status": r["status"], "priority": "<priority>" in r["body"], "changefreq": "<changefreq>" in r["body"], "lastmod": "<lastmod>" in r["body"]})
        locs = LOC_RE.findall(r["body"])
        if "<sitemapindex" in r["body"]:
            for loc in locs:
                if urllib.parse.urlparse(loc).hostname == host:
                    queue.append(loc)
                else:
                    foreign[urllib.parse.urlparse(loc).hostname] += 1
            continue
        for loc in locs:
            if urllib.parse.urlparse(loc).hostname == host:
                urls.append(loc)
            else:
                foreign[urllib.parse.urlparse(loc).hostname] += 1
    return list(dict.fromkeys(urls)), sources, dict(foreign)


def page(url):
    h = hop(url)
    if h["status"] != 200:
        return h
    r = fetch(url)
    info = asdict(A.parse_html_text(r["body"], url))
    links = [A._attrs(f) for f in A.LINK_RE.findall(r["body"])]
    info.update(h)
    info["x_default"] = any(l.get("hreflang", "").lower() == "x-default" for l in links)
    info["markdown_alternate"] = next((l.get("href", "") for l in links if l.get("type") == "text/markdown"), "")
    info["describedby"] = any(l.get("rel", "").lower() == "describedby" for l in links)
    info["icon"] = [l.get("href", "") for l in links if "icon" in l.get("rel", "").lower()]
    return info


def probes(origin, urls):
    sample = next((u for u in urls if urllib.parse.urlparse(u).path not in ("", "/")), "")
    targets = {
        "missing_page": f"{origin}/__seo-probe-{secrets.token_hex(4)}",
        "http_root": origin.replace("https://", "http://", 1) + "/",
        "index_html": f"{origin}/index.html",
    }
    if sample:
        path = urllib.parse.urlparse(sample).path
        targets["slash_variant"] = sample[:-1] if path.endswith("/") else sample + "/"
        targets["html_variant"] = sample.rstrip("/") + ".html"
    with cf.ThreadPoolExecutor(8) as ex:
        return dict(zip(targets, ex.map(hop, targets.values())))


def composition(urls):
    groups = collections.Counter()
    for u in urls:
        parts = [p for p in urllib.parse.urlparse(u).path.split("/") if p]
        if parts and parts[0] in ("zh", "en", "ja"):
            parts = parts[1:]
        groups["/" + "/".join(parts[:-1][:2])] += 1
    total = len(urls) or 1
    return [{"prefix": k, "count": v, "share": round(v / total, 3)} for k, v in groups.most_common(10)]


def main():
    ap = argparse.ArgumentParser(description="Crawl one live host: sitemap URLs, redirects, head tags, 404/redirect probes and legacy URLs")
    ap.add_argument("origin", help="https://host of the site; other hosts in its sitemaps are counted, not crawled")
    ap.add_argument("--legacy", help="file with one old URL or path per line, e.g. derived from git history")
    ap.add_argument("--limit", type=int, default=2000, help="max sitemap URLs to crawl")
    args = ap.parse_args()

    origin = args.origin.rstrip("/")
    if not origin.startswith(("http://", "https://")):
        print(f"[Invalid] origin: {args.origin!r} must start with https://", file=sys.stderr)
        sys.exit(1)
    robots = fetch(f"{origin}/robots.txt")
    urls, sources, foreign = sitemap_urls(origin, robots["body"])
    crawl = list(dict.fromkeys([f"{origin}/"] + urls))[: args.limit]
    with cf.ThreadPoolExecutor(16) as ex:
        pages = list(ex.map(page, crawl))

    legacy = []
    if args.legacy:
        try:
            lines = [l.strip() for l in Path(args.legacy).read_text(encoding="utf-8").splitlines() if l.strip()]
        except OSError as e:
            print(f"[Not found] legacy: {e}", file=sys.stderr)
            sys.exit(1)
        olds = [l if l.startswith("http") else origin + "/" + l.lstrip("/") for l in lines]
        with cf.ThreadPoolExecutor(16) as ex:
            legacy = list(ex.map(hop, olds))

    status = collections.Counter(p["status"] for p in pages)
    print(json.dumps({
        "origin": origin,
        "robots_txt": {"status": robots["status"], "body": robots["body"][:4000]},
        "sitemaps": sources,
        "sitemap_url_count": len(urls),
        "foreign_hosts_in_sitemaps": foreign,
        "truncated": len(urls) + 1 > args.limit,
        "status_counts": {str(k): v for k, v in status.items()},
        "composition": composition(urls),
        "probes": probes(origin, urls),
        "legacy": legacy,
        "pages": pages,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
