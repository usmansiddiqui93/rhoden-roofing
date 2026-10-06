# Rhoden Roofing – staging site

Redesigned Rhoden Roofing, LLC website (Wichita, KS): 479 pages covering services, roof types, service areas, the Learning Center (209 articles, 34 topic pages) and the roofing glossary (53 terms, 10 categories). Published with GitHub Pages.

**Staging:** every page carries `noindex, nofollow` and `robots.txt` blocks all crawlers.

## How it is built
- `tools/scrape.py` (GitHub Actions) copies the live site's pages, content data and images to the `scrape` branch.
- `tools/build.py` turns that copy into this static site using the templates in `tools/templates/`, rewriting every internal link and image to the staging copy.

Rebuild locally:

    git clone -b scrape <repo> ../scrape
    python3 tools/build.py --scrape ../scrape --base /rhoden-roofing/

For the live domain: `python3 tools/build.py --scrape ../scrape --base / --live` (removes noindex, allows crawlers).
