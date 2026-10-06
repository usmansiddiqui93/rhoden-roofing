"""Download the images listed in tools/missing-images.txt into ./extra/img (polite, resumable)."""
import os, time, requests
from urllib.parse import urlparse, unquote
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (compatible; RhodenStagingBuild/1.0)"
ok = 0
for u in [l.strip() for l in open("tools/missing-images.txt") if l.strip()]:
    rel = unquote(urlparse(u).path.split("/wp-content/uploads/", 1)[1])
    d = os.path.join("extra/img", rel)
    if os.path.exists(d): ok += 1; continue
    for attempt in range(6):
        try:
            r = S.get(u, timeout=40)
        except Exception as e:
            time.sleep(5); continue
        if r.status_code in (429, 503):
            ra = r.headers.get("Retry-After", ""); time.sleep(int(ra) if ra.isdigit() else 20 * (attempt + 1)); continue
        if r.ok:
            os.makedirs(os.path.dirname(d), exist_ok=True); open(d, "wb").write(r.content); ok += 1
        else:
            print(r.status_code, u)
        break
    time.sleep(0.6)
print("downloaded", ok)
