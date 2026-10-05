"""Copies every page in tools/urls.txt, the WordPress JSON API data, and every
referenced image from rhodenroofing.com into ./scrape (run on GitHub Actions)."""
import json, os, re, sys, hashlib
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
import requests
from PIL import Image

OUT = "scrape"
UA = {"User-Agent": "Mozilla/5.0 (compatible; RhodenStagingBuild/1.0)"}
S = requests.Session(); S.headers.update(UA)
os.makedirs(f"{OUT}/html", exist_ok=True); os.makedirs(f"{OUT}/api", exist_ok=True)

import time, threading
LOCK = threading.Lock(); NEXT = [0.0]
def get(url, gap=1.2, **kw):
    """Polite GET: global spacing between requests, honours 429/503 Retry-After."""
    err = None
    for attempt in range(8):
        with LOCK:
            wait = NEXT[0] - time.time()
            if wait > 0: time.sleep(wait)
            NEXT[0] = time.time() + gap
        try:
            r = S.get(url, timeout=40, **kw)
            if r.status_code in (429, 503):
                ra = r.headers.get("Retry-After", "")
                delay = int(ra) if ra.isdigit() else min(15 * (attempt + 1), 120)
                print("429 wait", delay, url, flush=True)
                with LOCK: NEXT[0] = max(NEXT[0], time.time() + delay)
                continue
            return r
        except Exception as e:
            err = e; time.sleep(5)
    print("FAIL", url, err, flush=True); return None

def slug_of(url):
    p = urlparse(url).path.strip("/")
    return p or "index"

# ---------- 1. HTML pages ----------
urls = [u.strip() for u in open("tools/urls.txt") if u.strip()]
urls = ["https://rhodenroofing.com/"] + [u for u in urls if u != "https://rhodenroofing.com/"]
status = {}
def fetch_page(u):
    if os.path.exists(f"{OUT}/html/{slug_of(u)}.html"):
        status[u] = 200; return
    r = get(u)
    if r is None: status[u] = "error"; return
    status[u] = r.status_code
    if r.ok and "text/html" in r.headers.get("content-type", ""):
        path = f"{OUT}/html/{slug_of(r.url)}.html"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(r.text)
        if r.url.rstrip("/") != u.rstrip("/"): status[u] = f"redirect:{r.url}"
with ThreadPoolExecutor(2) as ex: list(ex.map(fetch_page, urls))
json.dump(status, open(f"{OUT}/status.json", "w"), indent=1)
missing = [u for u, v in status.items() if v != 200 and not str(v).startswith("redirect")]
print("missing pages:", len(missing), missing[:20])
print("pages:", sum(1 for v in status.values() if v == 200), "/", len(urls))

# ---------- 2. WordPress REST API ----------
def api_all(route):
    out, page = [], 1
    while True:
        r = get(f"https://rhodenroofing.com/wp-json/wp/v2/{route}", params={"per_page": 100, "page": page})
        if r is None or not r.ok: break
        try: batch = r.json()
        except Exception: break
        if not isinstance(batch, list) or not batch: break
        out += batch
        if page >= int(r.headers.get("X-WP-TotalPages", 1)): break
        page += 1
    return out
types = get("https://rhodenroofing.com/wp-json/wp/v2/types")
routes = ["posts", "pages", "categories", "tags", "media"]
if types is not None and types.ok:
    try:
        for k, v in types.json().items():
            rb = v.get("rest_base")
            if rb and rb not in routes and k not in ("attachment", "nav_menu_item", "wp_block", "wp_template", "wp_template_part", "wp_navigation", "wp_global_styles", "wp_font_family", "wp_font_face"):
                routes.append(rb)
    except Exception: pass
tax = get("https://rhodenroofing.com/wp-json/wp/v2/taxonomies")
if tax is not None and tax.ok:
    try:
        for k, v in tax.json().items():
            rb = v.get("rest_base")
            if rb and rb not in routes: routes.append(rb)
    except Exception: pass
for rt in routes:
    fn = f"{OUT}/api/{rt.replace('/', '_')}.json"
    if os.path.exists(fn) and json.load(open(fn)): print("api cached", rt); continue
    data = api_all(rt)
    if rt == "media":
        data = [{k: d.get(k) for k in ("id", "source_url", "alt_text", "media_details")} for d in data]
    json.dump(data, open(f"{OUT}/api/{rt.replace('/', '_')}.json", "w"))
    print("api", rt, len(data))

# ---------- 3. Images ----------
IMG_RE = re.compile(r'rhodenroofing\.com/wp-content/uploads/[^\s"\'()<>,]+?\.(?:jpe?g|png|gif|webp|svg)', re.I)
found = set()
for root, _, files in os.walk(OUT):
    if "/img" in root: continue
    for f in files:
        if f.endswith((".html", ".json")):
            txt = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read().replace("\\/", "/")
            found.update("https://" + m for m in IMG_RE.findall(txt))
# Drop WordPress resized variants when the original is also referenced, keep everything else.
def base_of(u): return re.sub(r'-\d{2,4}x\d{2,4}(?=\.\w+$)', '', u)
originals = {u for u in found if base_of(u) == u}
want = sorted(u for u in found if base_of(u) == u or base_of(u) not in originals)
print("images referenced:", len(found), "downloading:", len(want))
imgmap = {}
def fetch_img(u):
    rel = urlparse(u).path.split("/wp-content/uploads/", 1)[1]
    dest = f"{OUT}/img/{rel}"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        imgmap[u] = rel; return
    r = get(u, gap=0.35)
    if r is None or not r.ok: return
    open(dest, "wb").write(r.content)
    try:
        if dest.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            im = Image.open(dest)
            if im.width > 1800:
                im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
                if dest.lower().endswith((".jpg", ".jpeg")):
                    im.convert("RGB").save(dest, quality=82, optimize=True, progressive=True)
                else:
                    im.save(dest, optimize=True)
            elif dest.lower().endswith((".jpg", ".jpeg")) and os.path.getsize(dest) > 400_000:
                im.convert("RGB").save(dest, quality=82, optimize=True, progressive=True)
    except Exception as e:
        print("img process", u, e)
    imgmap[u] = rel
with ThreadPoolExecutor(4) as ex: list(ex.map(fetch_img, want))
json.dump(imgmap, open(f"{OUT}/images.json", "w"), indent=0)
print("images saved:", len(imgmap))
