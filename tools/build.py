#!/usr/bin/env python3
"""Rhoden Roofing staging site generator.

Reads the copy of rhodenroofing.com in ../scrape (html/, api/, img/) and writes the
redesigned static site into the repository root.

    python3 tools/build.py --scrape ../scrape --base /rhoden-roofing/

For the live domain, rebuild with --base / and --live (drops the noindex tags).
"""
import argparse, base64, html as htmlmod, json, math, os, re, shutil, sys
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "tools", "templates")
ap = argparse.ArgumentParser()
ap.add_argument("--scrape", default=os.path.join(os.path.dirname(ROOT), "scrape"))
ap.add_argument("--base", default="/rhoden-roofing/")
ap.add_argument("--live", action="store_true")
ap.add_argument("--out", default=ROOT)
A = ap.parse_args()
BASE = A.base if A.base.endswith("/") else A.base + "/"
SCRAPE, OUT = A.scrape, A.out
SITE = "https://rhodenroofing.com"
PHONE, PHONE_TEL = "(316) 927-2233", "3169272233"
ADDRESS = "6601 E Kellogg Dr, Wichita, KS 67207"
MAPS = "https://google.com/maps?cid=6212979081897534887"

def log(*a): print(*a, file=sys.stderr)

# ------------------------------------------------------------------ inputs
def slug_of(url):
    p = urlparse(url).path if url.startswith("http") else url
    p = unquote(p).split("#")[0].split("?")[0].strip("/")
    return p or "index"

HTML = {}
for root, _, files in os.walk(os.path.join(SCRAPE, "html")):
    for f in files:
        if f.endswith(".html"):
            full = os.path.join(root, f)
            HTML[os.path.relpath(full, os.path.join(SCRAPE, "html"))[:-5]] = full
log("html pages:", len(HTML))

def api(name):
    p = os.path.join(SCRAPE, "api", name + ".json")
    try: return json.load(open(p))
    except Exception: return []
API_POSTS, API_PAGES, API_CATS, API_MEDIA = api("posts"), api("pages"), api("categories"), api("media")
API_GLOSS = api("glossary")
API_GCATS = api("glossary-cat") or api("glossary_cat") or api("glossary-cats")
MEDIA = {m["id"]: m.get("source_url") for m in API_MEDIA if m.get("id")}
CAT_BY_ID = {c["id"]: c for c in API_CATS}
log("api posts/pages/cats/gloss:", len(API_POSTS), len(API_PAGES), len(API_CATS), len(API_GLOSS))

POST_SLUGS = set()
for line in open(os.path.join(ROOT, "tools", "posts.txt")):
    if line.strip(): POST_SLUGS.add(slug_of(line.strip()))
for p in API_POSTS:
    POST_SLUGS.add(slug_of(p.get("link", "")))

# images available locally
IMG_DIR = os.path.join(SCRAPE, "img")
IMGS = set()
for root, _, files in os.walk(IMG_DIR):
    for f in files:
        IMGS.add(os.path.relpath(os.path.join(root, f), IMG_DIR))
IMGS_LOWER = {i.lower(): i for i in IMGS}
STEMS, STEMS_W = {}, {}
MISSES = set()
for i in sorted(IMGS):
    m = re.match(r'(.+?)-(\d{2,4})x(\d{2,4})\.\w+$', i) or re.match(r'(.+?)-scaled\.\w+$', i)
    if m:
        k = m.group(1).lower(); w = int(m.group(2)) if m.lastindex and m.lastindex >= 2 else 99999
        if k not in STEMS or w > STEMS_W.get(k, 0): STEMS[k] = i; STEMS_W[k] = w
log("images:", len(IMGS))

UP_RE = re.compile(r'wp-content/uploads/(.+?\.(?:jpe?g|png|gif|webp|svg))', re.I)
def local_img(url):
    """Map any original / optimizer image URL to a local asset URL (or None)."""
    if not url: return None
    m = UP_RE.search(url)
    if not m: return None
    rel = unquote(m.group(1))
    cands = [rel, re.sub(r'-\d{2,4}x\d{2,4}(?=\.\w+$)', '', rel), re.sub(r'(-\d{2,4}x\d{2,4})?(?=\.\w+$)', '-scaled', rel)]
    base_noext = re.sub(r'-\d{2,4}x\d{2,4}(?=\.\w+$)', '', rel)
    for c in cands:
        hit = c if c in IMGS else IMGS_LOWER.get(c.lower())
        if hit: return BASE + "assets/img/" + hit
    # any sized variant of the same original (largest available)
    stem = re.sub(r'\.\w+$', '', base_noext).lower()
    if stem in STEMS: return BASE + "assets/img/" + STEMS[stem]
    MISSES.add("https://rhodenroofing.com/wp-content/uploads/" + rel)
    return None

# ------------------------------------------------------------------ classify
def kind_of(slug):
    if slug == "index": return "home"
    if slug == "glossary": return "glossary-index"
    if slug.startswith("glossary/"): return "term"
    if slug.startswith("glossary-cat/"): return "gcat"
    if slug.startswith("category/"): return "category"
    if slug == "learning-center": return "learning"
    if slug in POST_SLUGS or slug.startswith("learning-center/"): return "article"
    if slug == "service-areas": return "areas-index"
    if slug.startswith("service-areas/") or re.search(r'-(ks|kansas)(-|/|$)', slug.split("/")[-1]) and "roof" in slug: return "area"
    if slug in POST_SLUGS or slug.startswith("learning-center/"): return "article"
    return "page"

SKIP = {"confirmation", "sitemap"}
PAGES = {s: {"slug": s, "kind": kind_of(s)} for s in HTML if s not in SKIP}
def url_for(slug):
    return BASE if slug == "index" else BASE + slug + "/"
def exists(slug): return slug in PAGES

# ------------------------------------------------------------------ links
def rewrite_href(href):
    if not href: return href
    h = href.strip()
    if h.startswith(("mailto:", "tel:", "sms:", "#", "javascript:")): return h
    if h.startswith("//"): h = "https:" + h
    host = urlparse(h).netloc.lower() if h.startswith("http") else "rhodenroofing.com"
    if host.endswith("rhodenroofing.com"):
        li = local_img(h)
        if li: return li
        path = urlparse(h).path
        frag = ("#" + urlparse(h).fragment) if urlparse(h).fragment else ""
        s = slug_of(path)
        if s in PAGES: return url_for(s) + frag
        if s in REDIRECTS and REDIRECTS[s] in PAGES: return url_for(REDIRECTS[s]) + frag
        if s.startswith(("free-estimate", "contact")): return url_for("free-estimate") if exists("free-estimate") else BASE + "#contact"
        return SITE + path + frag   # not part of the staging copy: send to live site
    return h

REDIRECTS = {}
try:
    for u, v in json.load(open(os.path.join(SCRAPE, "status.json"))).items():
        if isinstance(v, str) and v.startswith("redirect:"):
            REDIRECTS[slug_of(u)] = slug_of(v[9:])
except Exception: pass

# ------------------------------------------------------------------ content cleaning
YT_RE = re.compile(r'(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|vi(?:_webp)?/)|youtu\.be/)([\w-]{11})')
KEEP_ATTR = {"a": {"href"}, "img": {"src", "alt", "width", "height"}, "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan"},
             "ol": {"start"}}
DROP_SEL = [".et_pb_blog_grid_wrapper", ".et_pb_blog_grid", ".et_pb_posts", ".et_pb_comments_module", ".et_pb_post_nav",
            ".et_pb_social_media_follow", ".et_pb_contact_form_container", ".everest-forms", ".evf-container", ".gform_wrapper",
            ".wpforms-container", ".et_pb_map_container", ".et_pb_signup", ".et_pb_search", ".et_pb_sidebar_0", ".widget_search",
            ".et_pb_post_title", ".et_pb_menu", ".et_pb_fullwidth_menu", ".ti-widget", ".trustindex", ".sharedaddy", ".et_pb_countdown_timer",
            ".et_pb_login", ".et_pb_shop", ".breadcrumbs", ".yoast-breadcrumbs", "#breadcrumbs", ".rank-math-breadcrumb", ".et_pb_bar_counters"]
def img_src(el):
    for a in ("nitro-lazy-src", "data-src", "data-lazy-src", "src"):
        v = el.get(a)
        if v and not v.startswith("data:"): return v
    ss = el.get("nitro-lazy-srcset") or el.get("srcset") or ""
    if ss: return ss.split(",")[-1].strip().split(" ")[0]
    return None

def yt_id_of(el):
    blob = " ".join(str(v) for v in el.attrs.values())
    for a in ("nitro-lazy-src", "src", "data-src"):
        v = el.get(a) or ""
        if v.startswith("data:text/html;base64,"):
            try: blob += base64.b64decode(v.split(",", 1)[1] + "==").decode("utf-8", "ignore")
            except Exception: pass
    m = YT_RE.search(blob)
    return m.group(1) if m else None

def video_html(soup, vid, title="Video"):
    """Placeholder; expanded to the full facade after cleaning (see finish_videos)."""
    t = soup.new_tag("p"); t.string = f"@@VIDEO:{vid}@@"
    return t

def finish_videos(html, title):
    seen = set()
    def rep(m):
        vid = m.group(1)
        if vid in seen: return ""
        seen.add(vid)
        t = htmlmod.escape(title, quote=True)
        return (f'<div class="video-wrap"><button class="video" type="button" data-yt="{vid}" aria-label="Play video: {t}">'
                f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy"><span class="play"><i></i></span></button></div>')
    html = re.sub(r'(?:<p>\s*)+@@VIDEO:([\w-]{11})@@(?:\s*</p>)+', rep, html)
    html = re.sub(r'@@VIDEO:([\w-]{11})@@', rep, html)
    return re.sub(r'<p>\s*</p>', '', html)

def clean_content(root, soup, page_title=""):
    """Turn a Divi content tree into clean semantic HTML for .prose."""
    for t in root.find_all(["script", "style", "noscript", "template", "form", "link", "meta", "button", "input", "select", "textarea", "svg", "canvas", "object", "embed"]):
        if t.name == "script" and t.get("type") == "application/ld+json":
            m = YT_RE.search(t.string or "")
            if m: t.replace_with(video_html(soup, m.group(1), page_title)); continue
        t.decompose()
    for c in root.find_all(string=lambda x: isinstance(x, Comment)): c.extract()
    for sel in DROP_SEL:
        for t in root.select(sel): t.decompose()
    # de-duplicate video blocks (ld+json + iframe for same id)
    # iframes -> video facade
    for fr in root.find_all("iframe"):
        vid = yt_id_of(fr)
        if vid: fr.replace_with(video_html(soup, vid, page_title))
        else: fr.decompose()
    # glossary tooltips -> term links
    for sp in root.select(".glossary-tooltip"):
        a = sp.select_one(".glossary-link a")
        tip = sp.select_one(".glossary-tooltip-text")
        txt = a.get_text() if a else sp.get_text()
        new = soup.new_tag("a", attrs={"class": "term", "href": a.get("href") if a else "#"})
        new.string = txt
        if tip:
            for more in tip.find_all("a"): more.decompose()
            new["data-tip"] = re.sub(r"\s+", " ", tip.get_text(" ", strip=True))
        sp.replace_with(new)
    # toggles / accordions
    for tg in root.select(".et_pb_toggle"):
        ttl = tg.select_one(".et_pb_toggle_title")
        body = tg.select_one(".et_pb_toggle_content")
        d = soup.new_tag("details"); s = soup.new_tag("summary"); s.string = ttl.get_text(" ", strip=True) if ttl else "Details"
        d.append(s); inner = soup.new_tag("div", attrs={"class": "dbody"})
        if body:
            for ch in list(body.children): inner.append(ch.extract())
        d.append(inner); tg.replace_with(d)
    # tabs -> headings + content
    for tabs in root.select(".et_pb_tabs"):
        names = [li.get_text(" ", strip=True) for li in tabs.select(".et_pb_tabs_controls li")]
        panes = tabs.select(".et_pb_tab")
        wrap = soup.new_tag("div")
        for i, p in enumerate(panes):
            h = soup.new_tag("h3"); h.string = names[i] if i < len(names) else f"Part {i+1}"
            wrap.append(h)
            for ch in list(p.children): wrap.append(ch.extract())
        tabs.replace_with(wrap)
    # buttons
    for b in root.select("a.et_pb_button, .et_pb_button_module_wrapper a, a.et_pb_more_button, a.et_pb_promo_button"):
        b.attrs = {"href": b.get("href", "#"), "class": "btn btn-copper"}
    # blurbs
    for bl in root.select(".et_pb_blurb"):
        bl["data-kind"] = "blurb"
    for cta in root.select(".et_pb_promo"):
        cta["data-kind"] = "callout"
    for t in root.select(".et_pb_testimonial"):
        q = soup.new_tag("blockquote")
        for ch in list(t.select_one(".et_pb_testimonial_content") or t): q.append(ch.extract() if isinstance(ch, Tag) else NavigableString(str(ch)))
        t.replace_with(q)
    # galleries
    for g in root.select(".et_pb_gallery, .gallery"):
        g["data-kind"] = "gallery"
    # images
    for im in root.find_all("img"):
        src = img_src(im)
        loc = local_img(src) if src else None
        if not loc:
            im.decompose(); continue
        alt = im.get("alt", "") or ""
        w, h = im.get("width"), im.get("height")
        im.attrs = {"src": loc, "alt": alt, "loading": "lazy", "decoding": "async"}
        if w and str(w).isdigit(): im["width"] = w
        if h and str(h).isdigit(): im["height"] = h
    # background images on sections/rows -> keep as figure at top of block if no other image (skip, handled by hero)
    # links
    for a in root.find_all("a"):
        if a.get("class") == ["term"] or "term" in (a.get("class") or []):
            a["href"] = rewrite_href(a.get("href"))
            continue
        href = rewrite_href(a.get("href"))
        if not href:
            a.unwrap(); continue
        keep = {"href": href}
        if "btn" in (a.get("class") or []): keep["class"] = "btn btn-copper"
        if href.startswith("http") and not href.startswith(SITE + "/wp-content"):
            keep["target"] = "_blank"; keep["rel"] = "noopener"
        a.attrs = keep
    # structure: rows/columns
    for row in root.select(".et_pb_row, .et_pb_row_inner"):
        cols = [c for c in row.find_all(class_=re.compile(r"^et_pb_column"), recursive=False)
                if c.get_text(strip=True) or c.find(["img", "button"])]
        if len(cols) > 1:
            row.attrs = {"class": "row", "style": f"--cols:{min(len(cols), 4)}"}
            for c in row.find_all(class_=re.compile(r"^et_pb_column"), recursive=False):
                if c in cols: c.attrs = {"class": "col"}
                else: c.decompose()
        else:
            row["data-unwrap"] = "1"
    # convert marked blocks
    for el in root.find_all(attrs={"data-kind": True}):
        k = el["data-kind"]
        el.attrs = {"class": {"blurb": "blurb", "callout": "callout", "gallery": "gal"}[k]}
        el.name = "div"
    # unwrap generic wrappers
    keep_div = {"row", "col", "blurb", "callout", "gal", "video-wrap", "dbody"}
    for el in list(root.find_all(["div", "span", "section", "article", "font", "center", "main", "header", "footer", "aside"])):
        if el.decomposed if hasattr(el, "decomposed") else False: continue
        cls = el.get("class") or []
        if isinstance(cls, str): cls = cls.split()
        if el.name == "div" and set(cls) & keep_div:
            el.attrs = {k: v for k, v in el.attrs.items() if k in ("class", "style")}
            if "style" in el.attrs and not el.attrs["style"].startswith("--cols"): del el.attrs["style"]
            continue
        el.unwrap()
    # strip attributes everywhere else
    for el in root.find_all(True):
        if el.name in ("div", "button", "img", "a", "i") and el.get("class"):
            if el.name == "img": pass
            else: continue
        allowed = KEEP_ATTR.get(el.name, set())
        if el.name == "img": allowed = {"src", "alt", "width", "height", "loading", "decoding"}
        el.attrs = {k: v for k, v in el.attrs.items() if k in allowed}
    for d in root.find_all("details"):
        for b in d.find_all("div"):
            if "dbody" in (b.get("class") or []): b.attrs = {}
    # remove h1 (page title is in hero)
    for h in root.find_all("h1"):
        h.name = "h2"
        if page_title and h.get_text(" ", strip=True).lower().strip(" .:") == page_title.lower().strip(" .:"):
            h.decompose()
    # underline tags look like links on the web
    for u in root.find_all("u"): u.unwrap()
    # flatten <li><ul>…</ul></li> wrappers that create double bullets
    for li in list(root.find_all("li")):
        kids = [c for c in li.children if not (isinstance(c, NavigableString) and not c.strip())]
        if len(kids) == 1 and isinstance(kids[0], Tag) and kids[0].name in ("ul", "ol"):
            inner = kids[0]
            for sub in list(inner.find_all("li", recursive=False)): li.insert_before(sub.extract())
            li.decompose()
    # tables wrap
    for t in root.find_all("table"):
        if not (t.parent and t.parent.name == "div" and "tbl" in (t.parent.get("class") or [])):
            w = soup.new_tag("div", attrs={"class": "tbl"}); t.wrap(w)
    # empty cleanup (repeat for nesting)
    for _ in range(3):
        for el in root.find_all(["p", "h2", "h3", "h4", "h5", "h6", "li", "strong", "em", "b", "i", "u", "ul", "ol", "div", "figure", "blockquote"]):
            if el.find(["img", "button", "iframe", "table", "details"]): continue
            if el.name == "div" and (el.get("class") or []) and ("video-wrap" in el.get("class")): continue
            if not el.get_text(strip=True).replace("\xa0", ""): el.decompose()
    # strip leading "by X | date" leftovers
    return root

def inner_html(el):
    s = el.decode_contents() if el else ""
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()

def text_of(el, n=None):
    t = re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else ""
    return t if n is None or len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"

# ------------------------------------------------------------------ parse every page
def parse(slug):
    raw = open(HTML[slug], encoding="utf-8", errors="ignore").read()
    soup = BeautifulSoup(raw, "lxml")
    P = PAGES[slug]
    title_tag = (soup.title.get_text() if soup.title else "").strip()
    P["seo_title"] = re.sub(r"\s*[-|–]\s*Rhoden Roofing.*$", "", title_tag).strip() or title_tag
    md = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    P["description"] = (md.get("content") or "").strip() if md else ""
    h1 = soup.find("h1")
    P["title"] = text_of(h1) if h1 and text_of(h1) else P["seo_title"]
    ogi = soup.find("meta", attrs={"property": "og:image"})
    P["og_image"] = local_img(ogi.get("content")) if ogi else None
    pub = soup.select_one(".et_pb_title_meta_container .published, .published, time.entry-date")
    P["date"] = text_of(pub) if pub else ""
    sec = soup.find("meta", attrs={"property": "article:section"})
    P["section"] = sec.get("content") if sec else ""
    P["ld_sections"] = []
    for sc in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(sc.string or "{}")
            nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
            for n in nodes if isinstance(nodes, list) else []:
                if isinstance(n, dict) and n.get("articleSection"):
                    v = n["articleSection"]; P["ld_sections"] += v if isinstance(v, list) else [v]
                if isinstance(n, dict) and n.get("datePublished") and not P.get("iso"):
                    P["iso"] = n["datePublished"]
                if isinstance(n, dict) and n.get("@type") in ("Article", "BlogPosting") and n.get("image") and not P["og_image"]:
                    im = n["image"]; im = im.get("url") if isinstance(im, dict) else (im[0] if isinstance(im, list) and im else im)
                    P["og_image"] = local_img(im) if isinstance(im, str) else None
        except Exception:
            pass
    # links to glossary categories / categories (for membership)
    body = soup.select_one(".et_pb_post_content") if P["kind"] == "article" else None
    if body is None:
        body = soup.select_one(".et-l--body") or soup.select_one("#main-content") or soup.select_one("#et-main-area") or soup.body
    # background images in sections: take first as hero candidate
    bg = None
    for st in soup.find_all("style"):
        m = re.search(r'\.et_pb_section_[01](?:\.et_pb_section)?[^{]*\{[^}]*background-image:[^;]*url\(([^)]+)\)', st.string or "")
        if m: bg = local_img(m.group(1).strip("'\"")); break
    for el in body.find_all(attrs={"nitro-lazy-bg": True}) if body else []:
        bg = bg or local_img(el.get("nitro-lazy-bg")); break
    P["bg"] = bg
    # glossary category links (term pages + archive pages)
    P["gcat_links"] = sorted({slug_of(a["href"]) for a in soup.find_all("a", href=True) if "/glossary-cat/" in a["href"]})
    P["cat_links_in_body"] = sorted({slug_of(a["href"]) for a in (body.find_all("a", href=True) if body else []) if "/category/" in a["href"]})
    # archive membership: posts linked from archive bodies
    if P["kind"] in ("category", "gcat", "learning", "glossary-index", "areas-index"):
        P["listed"] = []
        for a in (body.find_all("a", href=True) if body else []):
            s = slug_of(a["href"]) if "rhodenroofing.com" in a["href"] or a["href"].startswith("/") else None
            if s and s in PAGES and s not in P["listed"] and s != slug: P["listed"].append(s)
    # first-section lede for builder pages
    lede = ""
    if P["kind"] in ("page", "area", "areas-index") and body is not None:
        first = body.find(class_=re.compile(r"^et_pb_section"))
        if first is not None and first.find("h1") is not None:
            txt = text_of(first)
            h1t = text_of(first.find("h1"))
            rest = txt.replace(h1t, "", 1).strip()
            if len(rest) < 320:
                lede = rest
                # keep a hero image from that section
                im = first.find("img")
                if im is not None and not P["bg"]: P["bg"] = local_img(img_src(im))
                first.decompose()
    P["lede"] = lede
    content = clean_content(body, soup, P["title"]) if body is not None else None
    html = inner_html(content)
    # drop repeated "by Rhoden Roofing | date" line remnants
    html = re.sub(r'^\s*<p>\s*by\s+Rhoden Roofing.*?</p>', '', html, flags=re.I | re.S)
    html = finish_videos(html, P["title"])
    P["html"] = html
    csoup = BeautifulSoup(html, "lxml")
    P["text"] = text_of(csoup)
    P["words"] = len(P["text"].split())
    P["toc"] = [(text_of(h), re.sub(r"[^a-z0-9]+", "-", text_of(h).lower()).strip("-")[:60]) for h in csoup.find_all("h2")]
    fi = csoup.find("img")
    P["first_img"] = fi["src"] if fi else None
    P["image"] = P["og_image"] or P["bg"] or P["first_img"]
    if not P["description"]:
        p = csoup.find("p")
        P["description"] = text_of(p, 170) if p else text_of(csoup, 170)
    P["excerpt"] = P["description"] if len(P["description"]) < 220 else P["description"][:200].rsplit(" ", 1)[0] + "…"
    return P

for s in sorted(PAGES):
    try: parse(s)
    except Exception as e:
        log("PARSE FAIL", s, repr(e)); PAGES[s]["html"] = ""; PAGES[s].setdefault("title", s); PAGES[s].setdefault("description", "")
        for k in ("seo_title", "image", "excerpt", "date", "toc", "words", "lede", "section", "ld_sections", "gcat_links", "cat_links_in_body", "text"): PAGES[s].setdefault(k, "" if k not in ("toc", "ld_sections", "gcat_links", "cat_links_in_body") else [])
        PAGES[s]["words"] = 0

# add ids to h2s for TOC
for P in PAGES.values():
    if P.get("toc"):
        def add_ids(m, it=iter(P["toc"])):
            try: _, i = next(it)
            except StopIteration: return m.group(0)
            return f'<h2 id="{i}">'
        P["html"] = re.sub(r"<h2>", add_ids, P["html"])

# ------------------------------------------------------------------ taxonomy
def ptitle(s): return PAGES[s]["title"] if s in PAGES else s.split("/")[-1].replace("-", " ").title()
CATS = {s: PAGES[s] for s in PAGES if PAGES[s]["kind"] == "category"}
for s, C in CATS.items():
    C["name"] = re.sub(r"^(Category|Archives?)\s*[:\-]\s*", "", C["title"]).strip() or s.split("/")[-1].replace("-", " ").title()
    C["posts"] = []
NAME_TO_CAT = {C["name"].lower(): s for s, C in CATS.items()}
# from API
api_post_cats = {}
for p in API_POSTS:
    ps = slug_of(p.get("link", ""))
    api_post_cats[ps] = [slug_of(CAT_BY_ID[c]["link"]) for c in p.get("categories", []) if c in CAT_BY_ID]
    if ps in PAGES:
        if p.get("date"): PAGES[ps]["iso"] = p["date"]
        fm = p.get("featured_media")
        if fm and MEDIA.get(fm): PAGES[ps]["image"] = local_img(MEDIA[fm]) or PAGES[ps]["image"]
ARTICLES = [s for s in PAGES if PAGES[s]["kind"] == "article"]
for s in ARTICLES:
    P = PAGES[s]
    cats = set(api_post_cats.get(s, []))
    for nm in [P.get("section")] + P.get("ld_sections", []):
        if nm and nm.lower() in NAME_TO_CAT: cats.add(NAME_TO_CAT[nm.lower()])
    cats |= {c for c in P.get("cat_links_in_body", []) if c in CATS}
    P["cats"] = sorted(c for c in cats if c in CATS)
for s, C in CATS.items():
    for ps in C.get("listed", []):
        if PAGES.get(ps, {}).get("kind") == "article" and s not in PAGES[ps]["cats"]: PAGES[ps]["cats"].append(s)
# parent categories (category/residential-roofing/roof-types/x -> parents)
for s in ARTICLES:
    P = PAGES[s]; extra = set()
    for c in P["cats"]:
        parts = c.split("/")
        for i in range(2, len(parts)):
            par = "/".join(parts[:i])
            if par in CATS: extra.add(par)
    P["cats"] = sorted(set(P["cats"]) | extra)
    for c in P["cats"]: CATS[c]["posts"].append(s)

def sort_key(s):
    P = PAGES[s]
    iso = P.get("iso") or ""
    if not iso and P.get("date"):
        try: iso = datetime.strptime(P["date"], "%b %d, %Y").isoformat()
        except Exception: iso = ""
    P["iso"] = iso
    return iso
ARTICLES.sort(key=sort_key, reverse=True)
for C in CATS.values(): C["posts"].sort(key=lambda s: PAGES[s].get("iso", ""), reverse=True)
for s in ARTICLES:
    P = PAGES[s]
    if not P.get("date") and P.get("iso"):
        try: P["date"] = datetime.fromisoformat(P["iso"][:19]).strftime("%b %d, %Y")
        except Exception: pass
    P["minutes"] = max(1, round(P.get("words", 0) / 230))

# glossary
TERMS = sorted([s for s in PAGES if PAGES[s]["kind"] == "term"], key=lambda s: ptitle(s).lower())
GCATS = {s: PAGES[s] for s in PAGES if PAGES[s]["kind"] == "gcat"}
for s, G in GCATS.items():
    G["name"] = re.sub(r"^(Glossary Category|Archives?)\s*[:\-]\s*", "", G["title"]).strip() or s.split("/")[-1].replace("-", " ").title()
    G["terms"] = [t for t in G.get("listed", []) if t in TERMS]
for t in TERMS:
    PAGES[t]["gcats"] = [g for g in PAGES[t].get("gcat_links", []) if g in GCATS]
for s, G in GCATS.items():
    for t in TERMS:
        if s in PAGES[t]["gcats"] and t not in G["terms"]: G["terms"].append(t)
        if t in G["terms"] and s not in PAGES[t]["gcats"]: PAGES[t]["gcats"].append(s)
    G["terms"].sort(key=lambda t: ptitle(t).lower())
for t in TERMS:
    P = PAGES[t]
    P["short"] = text_of(BeautifulSoup(P["html"], "lxml").find("p"), 170) if P["html"] else P["description"]
    P["short"] = P["short"] or P["description"]
    P["mentions"] = [a for a in ARTICLES if ('/glossary/' + t.split('/', 1)[1] + '/') in PAGES[a]["html"]][:6]

# service areas
AREAS = sorted([s for s in PAGES if PAGES[s]["kind"] == "area"], key=lambda s: ptitle(s))
def area_name(s):
    n = s.split("/")[-1]
    n = re.sub(r"-(ks|kansas)-roofers$|-ks-roofers$|-roofers$", "", n)
    n = re.sub(r"^(residential|commercial)-roofing-", "", n)
    n = re.sub(r"-(ks)$", "", n)
    return n.replace("-", " ").title().replace("Mt ", "Mt. ").replace("County", "County")
for s in AREAS:
    PAGES[s]["area"] = area_name(s)
    PAGES[s]["parent"] = "/".join(s.split("/")[:2]) if s.count("/") >= 2 and "/".join(s.split("/")[:2]) in PAGES else None
TOP_AREAS = [s for s in AREAS if s.count("/") == 1 and s.startswith("service-areas/")]
COUNTIES = [s for s in TOP_AREAS if "county" in s]
CITIES = [s for s in TOP_AREAS if "county" not in s]

# ------------------------------------------------------------------ navigation
def L(slug, label=None):
    return {"href": url_for(slug), "label": label or ptitle(slug), "slug": slug} if exists(slug) else None
def group(items): return [i for i in items if i]
NAV = [
    {"label": "Commercial", "head": L("commercial-roofing-wichita", "Commercial Roofing"), "items": group([
        L("commercial-roofing-wichita/roof-replacement", "Commercial Roof Replacement"), L("commercial-roofing-wichita/roof-repair", "Commercial Roof Repair"),
        L("commercial-roofing-wichita/roof-installation", "Commercial Roof Installation"), L("commercial-roof-maintenance", "Commercial Roof Maintenance"),
        L("commercial-roofing-wichita/schools", "School Partnerships"), L("commercial-metal-roofing", "Commercial Metal Roofing"),
        L("commercial-roofing-wichita/multi-family-roofs", "Multi-Family Roofs"), L("commercial-roofing-wichita/tpo-roofs", "TPO Roofs"),
        L("commercial-roofing-wichita/pvc-roofs", "PVC Roofs"), L("flat-roofing-wichita", "Flat Roofing"), L("roof-coating", "Roof Coatings")])},
    {"label": "Residential", "head": L("residential-roofing", "Residential Roofing"), "items": group([
        L("roof-installation-wichita", "Roof Installation"), L("roof-replacement-wichita", "Roof Replacement"), L("roof-repair-wichita", "Roof Repair"),
        L("emergency-roof-repair", "Emergency Roof Repair"), L("storm-damage-roof-repair", "Storm Damage Repair"), L("hail-damage-roof-inspection", "Hail Damage Inspection"),
        L("residential-roofing/roof-inspections", "Roof Inspections"), L("roof-damage-insurance-claims", "Insurance Claims"), L("gutters", "Gutters"),
        L("residential-roofing/skylight-installation", "Skylight Installation"), L("real-estate-transaction-assistance", "Real Estate Assistance")])},
    {"label": "Roof Types", "head": None, "items": group([
        L("asphalt-shingle-roofing-wichita", "Asphalt Shingles"), L("asphalt-shingle-roofing-wichita/architectural-shingle-roofing", "Architectural Shingles"),
        L("metal-roofing-wichita", "Metal Roofing"), L("metal-roofing-wichita/standing-seam", "Standing Seam Metal"), L("slate-roofing-wichita", "Slate Roofing"),
        L("tile-roofing-wichita", "Tile Roofing"), L("cedar-roofing-wichita", "Cedar Roofing"), L("metal-roofing-wichita/copper", "Copper Roofing"),
        L("asphalt-shingle-roofing-wichita/three-tab-shingle-roofing", "3-Tab Shingles"), L("gutters/seamless", "Seamless Gutters")])},
    {"label": "Learn", "head": L("learning-center", "Learning Center"), "items": group([
        L("learning-center", "All Articles"), L("glossary", "Roofing Glossary"), L("category/costs", "Roofing Costs"),
        L("category/residential-roofing", "Residential Guides"), L("category/commercial-roofing", "Commercial Guides"),
        L("category/residential-roofing/homeowner-insurance", "Insurance Help"), L("category/how-to", "How-To Guides"),
        L("commercial-low-slope-roofing-series", "Low-Slope Roofing Series"), L("learning-resource-library", "Resource Library"), L("financing", "Financing")])},
    {"label": "About", "head": L("about", "About Rhoden Roofing"), "items": group([
        L("about", "What We Do"), L("our-team", "Our Team"), L("about/culture", "Culture & Core Values"), L("lifetime-warranty", "Lifetime Warranty"),
        L("construction-process", "Construction Process"), L("service-areas", "Service Areas"), L("recent-projects", "Recent Projects"), L("gallery", "Gallery"),
        L("customer-reviews", "Reviews"), L("manufacturer-certifications", "Certifications"), L("awards", "Awards"), L("careers", "Careers"),
        L("about/sell-your-business", "Sell Your Business")])},
    {"label": "Giving Back", "head": None, "items": group([
        L("roof-giveaway", "Christmas Roof Giveaway"), L("habitat-for-humanity", "Habitat for Humanity"), L("gaf-roofs-for-troops", "GAF Roofs for Troops"),
        L("wsu-tech-promise-scholarship", "WSU Tech Promise Scholarship"), L("media-room", "Press")])},
]
NAV = [n for n in NAV if n["items"]]
ESTIMATE = url_for("free-estimate") if exists("free-estimate") else BASE + "#contact"
CONTACT = url_for("contact") if exists("contact") else ESTIMATE

SERVICE_SLUGS = [i["slug"] for n in NAV[:3] for i in n["items"]]

# ------------------------------------------------------------------ render
env = Environment(loader=FileSystemLoader(TPL), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
G = dict(BASE=BASE, NAV=NAV, PHONE=PHONE, PHONE_TEL=PHONE_TEL, ADDRESS=ADDRESS, MAPS=MAPS, ESTIMATE=ESTIMATE, CONTACT=CONTACT,
         LIVE=A.live, url_for=url_for, exists=exists, ptitle=ptitle, PAGES=PAGES, YEAR=datetime.now().year,
         LOGO=local_img("wp-content/uploads/2020/12/logo-new.png") or BASE + "images/logo-new.png",
         ICON=local_img("wp-content/uploads/2026/08/cropped-Rhoden-Roofing-Peaks-Real-270x270.png") or BASE + "images/cropped-Rhoden-Roofing-Peaks-Real-270x270.png",
         FALLBACK_HERO=local_img("wp-content/uploads/2020/12/1-4.jpg"), CITIES=CITIES, COUNTIES=COUNTIES)
env.globals.update(G)

def write(slug, html):
    path = os.path.join(OUT, "index.html") if slug == "index" else os.path.join(OUT, slug, "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)

def crumbs_for(slug):
    c = [{"href": BASE, "label": "Home"}]
    k = PAGES[slug]["kind"]
    if k == "article": c.append({"href": url_for("learning-center") if exists("learning-center") else BASE, "label": "Learning Center"})
    elif k == "term": c.append({"href": url_for("glossary"), "label": "Glossary"})
    elif k == "gcat": c.append({"href": url_for("glossary"), "label": "Glossary"})
    elif k == "category": c.append({"href": url_for("learning-center"), "label": "Learning Center"})
    else:
        parts = slug.split("/")
        for i in range(1, len(parts)):
            par = "/".join(parts[:i])
            if exists(par): c.append({"href": url_for(par), "label": ptitle(par)})
    return c

def related_articles(slug, n=3):
    P = PAGES[slug]; cats = set(P.get("cats", []))
    scored = sorted((a for a in ARTICLES if a != slug), key=lambda a: (-len(cats & set(PAGES[a].get("cats", []))), ARTICLES.index(a)))
    return scored[:n]

def card(s):
    P = PAGES[s]
    cat = CATS[P["cats"][-1]]["name"] if P.get("cats") else ""
    return {"href": url_for(s), "title": P["title"], "img": P.get("image"), "excerpt": P.get("excerpt", ""), "date": P.get("date", ""), "cat": cat, "minutes": P.get("minutes")}

def side_links_for(slug):
    for n in NAV:
        if any(i["slug"] == slug for i in n["items"]) or (n["head"] and n["head"]["slug"] == slug):
            return n
    parts = slug.split("/")
    if len(parts) > 1:
        par = "/".join(parts[:-1])
        sib = [L(s) for s in PAGES if s.startswith(par + "/") and s.count("/") == slug.count("/") and PAGES[s]["kind"] in ("page", "area")]
        if exists(par): return {"label": ptitle(par), "head": L(par), "items": group(sib)[:14]}
    return None

def page_ctx(slug, **kw):
    P = PAGES[slug]
    hero = P.get("bg") or P.get("image") or G["FALLBACK_HERO"]
    return dict(P=P, slug=slug, crumbs=crumbs_for(slug), hero=hero, canonical=SITE + "/" + ("" if slug == "index" else slug + "/"), **kw)

counts = defaultdict(int)
T = {n: env.get_template(n + ".html") for n in ("home", "page", "article", "term", "glossary", "learning", "areas", "notfound")}
for slug in sorted(PAGES):
    P = PAGES[slug]; k = P["kind"]
    try:
        if k == "home":
            continue
        elif k == "article":
            prev_next = ARTICLES.index(slug)
            ctx = page_ctx(slug, related=[card(a) for a in related_articles(slug)],
                           cats=[{"href": url_for(c), "label": CATS[c]["name"]} for c in P.get("cats", []) if c.count("/") >= 1][-3:],
                           newer=card(ARTICLES[prev_next - 1]) if prev_next > 0 else None,
                           older=card(ARTICLES[prev_next + 1]) if prev_next + 1 < len(ARTICLES) else None)
            html = T["article"].render(**ctx)
        elif k == "term":
            same = []
            for g in P.get("gcats", []): same += [t for t in GCATS[g]["terms"] if t != slug and t not in same]
            ctx = page_ctx(slug, gcats=[{"href": url_for(g), "label": GCATS[g]["name"]} for g in P.get("gcats", [])],
                           same=[{"href": url_for(t), "title": ptitle(t), "short": PAGES[t]["short"]} for t in same[:8]],
                           mentions=[card(a) for a in P.get("mentions", [])][:3])
            html = T["term"].render(**ctx)
        elif k in ("glossary-index", "gcat"):
            terms = TERMS if k == "glossary-index" else GCATS[slug]["terms"]
            groups = defaultdict(list)
            for t in terms:
                letter = ptitle(t)[:1].upper(); letter = letter if letter.isalpha() else "#"
                groups[letter].append({"href": url_for(t), "title": ptitle(t), "short": PAGES[t]["short"],
                                       "cat": GCATS[PAGES[t]["gcats"][0]]["name"] if PAGES[t].get("gcats") else ""})
            ctx = page_ctx(slug, groups=sorted(groups.items()), letters=[chr(c) for c in range(65, 91)], total=len(terms),
                           gcats=[{"href": url_for(g), "label": GCATS[g]["name"], "n": len(GCATS[g]["terms"]), "current": g == slug} for g in sorted(GCATS, key=lambda g: GCATS[g]["name"])])
            html = T["glossary"].render(**ctx)
        elif k in ("category", "learning"):
            posts = ARTICLES if k == "learning" else CATS[slug]["posts"]
            data = [dict(card(a), cats=[c for c in PAGES[a].get("cats", [])]) for a in posts]
            topcats = sorted([c for c in CATS if CATS[c]["posts"] and c.count("/") == 1], key=lambda c: -len(CATS[c]["posts"]))
            subcats = sorted([c for c in CATS if c.startswith(slug + "/") and CATS[c]["posts"]], key=lambda c: CATS[c]["name"]) if k == "category" else []
            ctx = page_ctx(slug, posts=data, total=len(data), name=CATS[slug]["name"] if k == "category" else "Learning Center",
                           filters=[{"slug": c, "label": CATS[c]["name"], "n": len(CATS[c]["posts"]), "href": url_for(c)} for c in (subcats or topcats)],
                           is_cat=(k == "category"))
            html = T["learning"].render(**ctx)
        elif k == "areas-index":
            ctx = page_ctx(slug, cities=[{"href": url_for(s), "label": PAGES[s]["area"]} for s in CITIES],
                           counties=[{"href": url_for(s), "label": PAGES[s]["area"]} for s in COUNTIES])
            html = T["areas"].render(**ctx)
        else:
            side = side_links_for(slug)
            children = [c for c in PAGES if c.startswith(slug + "/") and c.count("/") == slug.count("/") + 1 and PAGES[c]["kind"] in ("page", "area")]
            is_form = slug in ("free-estimate", "contact")
            ctx = page_ctx(slug, side=side, children=[{"href": url_for(c), "title": ptitle(c), "img": PAGES[c].get("image"), "excerpt": PAGES[c].get("excerpt", "")} for c in sorted(children)],
                           related=[card(a) for a in ARTICLES if any(w in PAGES[a]["title"].lower() for w in (slug.split("/")[-1].split("-")[:1]))][:3] if k == "page" else [],
                           is_form=is_form, gallery=(slug == "gallery"))
            html = T["page"].render(**ctx)
        write(slug, html); counts[k] += 1
    except Exception as e:
        import traceback; traceback.print_exc(); log("RENDER FAIL", slug)

# home
home_main = open(os.path.join(TPL, "_home_main.html"), encoding="utf-8").read()
def home_img(m):
    name = m.group(1)
    for i in IMGS:
        if i.endswith("/" + name): return f'src="{BASE}assets/img/{i}"'
    return f'src="{BASE}images/{name}"'
home_main = re.sub(r'src="images/([^"]+)"', home_img, home_main)
home_main = re.sub(r'href="https://rhodenroofing\.com([^"]*)"', lambda m: f'href="{rewrite_href(SITE + m.group(1))}"', home_main)
svc_map = {"Residential Roofing": "residential-roofing", "Commercial Roofing": "commercial-roofing-wichita", "Multi-family Roofing": "commercial-roofing-wichita/multi-family-roofs",
           "Roof Replacement": "roof-replacement-wichita", "Lifetime Warranty": "lifetime-warranty", "Roof Repairs": "roof-repair-wichita"}
def svc_link(m):
    block = m.group(0)
    for t, s in svc_map.items():
        if f"<h3>{t}</h3>" in block and exists(s): return block.replace('href="#contact"', f'href="{url_for(s)}"', 1).replace('href="#why"', f'href="{url_for(s)}"', 1)
    return block
home_main = re.sub(r'<a class="svc[^"]*"[\s\S]*?</a>', svc_link, home_main)
home_main = home_main.replace('href="#contact">Learn more', f'href="{ESTIMATE}">Learn more')
if exists("hail-damage-roof-inspection"): home_main = home_main.replace('<a class="storm" href="#contact">', f'<a class="storm" href="{url_for("hail-damage-roof-inspection")}">')
latest = [card(a) for a in ARTICLES[:3]]
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(env.get_template("home.html").render(
    P={"title": "Wichita Roofing Contractor", "seo_title": "Wichita Roofing Contractor | Rhoden Roofing, LLC",
       "description": "Rhoden Roofing is Wichita's premier local roofing company. Certified GAF President's Club Contractor providing roof replacements, repairs, & warranties.", "kind": "home"},
    slug="index", home_main=home_main, latest=latest, canonical=SITE + "/"))
counts["home"] += 1

# 404
open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(T["notfound"].render(P={"title": "Page not found", "seo_title": "Page not found", "description": "", "kind": "404"}, slug="404", canonical=SITE + "/"))

# assets: copy only images the generated pages use, web-optimized
from PIL import Image
used = set()
for root, _, files in os.walk(OUT):
    if os.sep + "assets" in root or os.sep + ".git" in root: continue
    for f in files:
        if f.endswith(".html"):
            used.update(re.findall(r'assets/img/([^"\'\s)<>&]+)', open(os.path.join(root, f), encoding="utf-8").read()))
dst = os.path.join(OUT, "assets", "img")
copied = 0
for i in sorted(used):
    i = unquote(i)
    src = os.path.join(IMG_DIR, i); d = os.path.join(dst, i)
    if not os.path.exists(src) or os.path.exists(d): continue
    os.makedirs(os.path.dirname(d), exist_ok=True)
    try:
        if i.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            im = Image.open(src)
            if im.width > 1600:
                im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
            if i.lower().endswith((".jpg", ".jpeg")):
                im.convert("RGB").save(d, quality=80, optimize=True, progressive=True)
            elif i.lower().endswith(".webp"):
                im.save(d, quality=80)
            else:
                im.save(d, optimize=True)
            if os.path.getsize(d) > os.path.getsize(src): shutil.copy2(src, d)
        else:
            shutil.copy2(src, d)
    except Exception as e:
        shutil.copy2(src, d)
    copied += 1
css = open(os.path.join(TPL, "_home_and_base.css")).read() + open(os.path.join(TPL, "_inner.css")).read()
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
open(os.path.join(OUT, "assets", "site.css"), "w").write(css)
shutil.copy2(os.path.join(TPL, "site.js"), os.path.join(OUT, "assets", "site.js"))
# robots + sitemap list for QA
open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n" if not A.live else "User-agent: *\nAllow: /\n")
json.dump({"counts": dict(counts), "pages": len(PAGES), "images": len(IMGS), "copied": copied}, open(os.path.join(ROOT, "tools", "build-report.json"), "w"), indent=1)
open(os.path.join(ROOT, "tools", "missing-images.txt"), "w").write("\n".join(sorted(MISSES)) + "\n")
log("missing images:", len(MISSES))
log("built:", dict(counts), "images copied:", copied)
