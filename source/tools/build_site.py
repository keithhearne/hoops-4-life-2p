"""Turn the game page into an installable web app (PWA) folder for GitHub Pages."""
import json, os, re, sys
from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
game = open(src).read()
SUB = sys.argv[6] if len(sys.argv) > 6 else ""   # optional second line on the icon

# --- icon: a shaded basketball on the arena navy, with "H4L" ---
def icon(size, path, maskable=False):
    S = size * 4  # draw big, then shrink for smooth edges
    im = Image.new("RGBA", (S, S), (16, 21, 43, 255))
    d = ImageDraw.Draw(im)
    pad = int(S * (0.2 if maskable else 0.1))
    r = (S - 2 * pad) // 2
    cx = cy = S // 2
    # ball with a simple light-to-dark shading
    for i in range(r, 0, -1):
        t = i / r
        col = (int(169 + (255 - 169) * (1 - t) * 0.9), int(65 + (164 - 65) * (1 - t) * 0.9), int(12 + (92 - 12) * (1 - t) * 0.9))
        ox = int((1 - t) * -r * 0.25)
        d.ellipse([cx - i + ox, cy - i + ox, cx + i + ox, cy + i + ox], fill=col)
    seam = (42, 18, 6)
    w = max(4, S // 70)
    d.line([cx - r, cy, cx + r, cy], fill=seam, width=w)
    d.line([cx, cy - r, cx, cy + r], fill=seam, width=w)
    d.arc([cx - int(r * 1.55), cy - r, cx - int(r * 0.25), cy + r], -60, 60, fill=seam, width=w)
    d.arc([cx + int(r * 0.25), cy - r, cx + int(r * 1.55), cy + r], 120, 240, fill=seam, width=w)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(110, 42, 6), width=w)
    # label
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(r * 0.62))
    except OSError:
        font = ImageFont.load_default()
    def label(txt, f, mid, col):
        bb = d.textbbox((0, 0), txt, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text((cx - tw // 2 - bb[0], mid - th // 2 - bb[1]), txt, font=f, fill=col, stroke_width=w * 2, stroke_fill=(27, 35, 64))
    if SUB:   # a second line under "H4L", e.g. "2P" for the 2 Player app
        label("H4L", font, cy - int(r * 0.24), (255, 201, 60))
        try: small = ImageFont.truetype("DejaVuSans-Bold.ttf", int(r * 0.46))
        except OSError: small = font
        label(SUB, small, cy + int(r * 0.42), (255, 255, 255))
    else:
        label("H4L", font, cy, (255, 201, 60))
    im.resize((size, size), Image.LANCZOS).save(path)

icon(192, os.path.join(out, "icon-192.png"))
icon(512, os.path.join(out, "icon-512.png"))
icon(512, os.path.join(out, "icon-maskable-512.png"), maskable=True)
icon(180, os.path.join(out, "apple-touch-icon.png"))

manifest = {
    "name": "__APP__",
    "short_name": "__APP__",
    "description": "Zackie vs Keelan: 1 v 1 basketball.",
    "start_url": "./",
    "scope": "./",
    "display": "fullscreen",
    "orientation": "landscape",
    "background_color": "#10152B",
    "theme_color": "#10152B",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

# bump this when the game changes so phones fetch the new version
version = sys.argv[3] if len(sys.argv) > 3 else "1"
APP = sys.argv[4] if len(sys.argv) > 4 else "Hoops 4 Life"
SLUG = sys.argv[5] if len(sys.argv) > 5 else "hoops4life"
manifest["name"] = manifest["short_name"] = APP
json.dump(manifest, open(os.path.join(out, "manifest.webmanifest"), "w"), indent=2)
open(os.path.join(out, "sw.js"), "w").write(f"""// Offline support: keep the game files on the phone so it opens without internet.
const CACHE = "{SLUG}-{version}";
const FILES = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png",
  "./icon-maskable-512.png", "./apple-touch-icon.png"];
self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
}});
// only clear this game's own old copies: other games on the same site keep theirs
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith("{SLUG}-") && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});
// game files: use the network when online so updates arrive, fall back to the saved copy offline
self.addEventListener("fetch", e => {{
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request).then(res => {{
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return res;
    }}).catch(() => caches.match(e.request).then(r => r || caches.match("./index.html")))
  );
}});
""")

# --- full HTML document around the game ---
title_end = game.index("</title>") + len("</title>")
body = game[title_end:]
head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<title>__APP__</title>
<meta name="theme-color" content="#10152B">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<style>
*,*::before,*::after{box-sizing:border-box}
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
html,body{height:100%;margin:0}
body{overscroll-behavior:none;touch-action:none}
[hidden]{display:none!important}
</style>
"""
body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", body)
tail = """
<script>
// install support: register the offline worker
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
}
</script>
</body>
</html>
"""
open(os.path.join(out, "index.html"), "w").write(head.replace("__APP__", APP) + "</head>\n<body>\n" + body.lstrip() + tail)
print("built", out)
