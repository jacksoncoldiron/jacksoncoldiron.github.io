"""
Build the photography map from folders of exported photos.

Workflow
--------
1. Export your favourite photos from Google Photos / iCloud (keep location data on!)
   into one folder per place, inside `photos-inbox/` (which is git-ignored):

       photos-inbox/
         zambia-lusaka/
           place.yml          <- optional: title, region, date, blurb, lat/lng override
           captions.yml       <- optional: {filename: caption}
           IMG_0412.HEIC
           IMG_0419.jpg
         new-zealand-whakatane/
           ...

2. Run:   python3 scripts/build_photos.py
3. Re-render the site:  quarto render

What it does
------------
* Converts HEIC -> JPEG (macOS `sips`), fixes rotation, resizes to web sizes (WebP),
  and strips ALL metadata from the published copies (so precise GPS never ships).
* Places each folder on the map at the median GPS location of its photos
  (or at `lat`/`lng` from place.yml if you want to override / photos lack GPS).
* Writes `data/places.json`, which photography.qmd reads.

`python3 scripts/build_photos.py --demo` regenerates the sample placeholder gallery.
"""

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from PIL.ExifTags import GPSTAGS, TAGS

try:
    import yaml
except ImportError:  # tiny fallback for flat "key: value" files
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "photos-inbox"
OUT_MEDIA = ROOT / "media" / "photos"
OUT_JSON = ROOT / "data" / "places.json"

FULL_PX = 1800      # long edge of carousel images
THUMB_PX = 520      # long edge of thumbnails
QUALITY = 78
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}


# ---------------------------------------------------------------- helpers
def read_yaml(path):
    if not path.exists():
        return {}
    text = path.read_text()
    if yaml:
        return yaml.safe_load(text) or {}
    out = {}
    for line in text.splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def to_degrees(value, ref):
    d, m, s = (float(x) for x in value)
    deg = d + m / 60 + s / 3600
    return -deg if ref in ("S", "W") else deg


def exif_info(img):
    """Return (lat, lng, datetime) from EXIF if present."""
    lat = lng = when = None
    try:
        exif = img.getexif()
        for tag_id, val in exif.items():
            if TAGS.get(tag_id) == "DateTime":
                when = val
        sub = exif.get_ifd(0x8769)  # Exif IFD
        if sub.get(36867):
            when = sub.get(36867)  # DateTimeOriginal
        gps_raw = exif.get_ifd(0x8825)
        gps = {GPSTAGS.get(k, k): v for k, v in gps_raw.items()}
        if "GPSLatitude" in gps and "GPSLongitude" in gps:
            lat = to_degrees(gps["GPSLatitude"], gps.get("GPSLatitudeRef", "N"))
            lng = to_degrees(gps["GPSLongitude"], gps.get("GPSLongitudeRef", "E"))
    except Exception:
        pass
    if when:
        try:
            when = datetime.strptime(str(when), "%Y:%m:%d %H:%M:%S").date().isoformat()
        except ValueError:
            when = None
    return lat, lng, when


def open_image(path, tmpdir):
    """Open an image, converting HEIC with macOS sips if Pillow can't read it."""
    if path.suffix.lower() in (".heic", ".heif"):
        out = Path(tmpdir) / (path.stem + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", str(path), "--out", str(out)],
                       check=True, capture_output=True)
        return Image.open(out)
    return Image.open(path)


def save_resized(img, dest, long_edge):
    im = img.copy()
    im.thumbnail((long_edge, long_edge), Image.LANCZOS)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    im.save(dest, "WEBP", quality=QUALITY, method=6)  # no exif= -> metadata stripped
    return im.size


# ---------------------------------------------------------------- build
def build():
    if not INBOX.exists():
        sys.exit(f"No {INBOX.relative_to(ROOT)}/ folder yet. Create it and add one folder per place.")

    places = []
    if OUT_MEDIA.exists():
        shutil.rmtree(OUT_MEDIA)
    OUT_MEDIA.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        for folder in sorted(p for p in INBOX.iterdir() if p.is_dir()):
            slug = folder.name.lower().replace(" ", "-").replace("_", "-")
            meta = read_yaml(folder / "place.yml")
            captions = read_yaml(folder / "captions.yml")
            # include images in subfolders (e.g. an unzipped Google Photos export); zips are ignored
            files = sorted((f for f in folder.rglob("*") if f.suffix.lower() in IMAGE_EXT and not f.name.startswith(".")),
                           key=lambda f: f.name.lower())
            if not files:
                continue
            (OUT_MEDIA / slug).mkdir()
            photos, lats, lngs, dates = [], [], [], []

            for i, f in enumerate(files, 1):
                try:
                    img = open_image(f, tmp)
                except Exception as e:
                    print(f"  ! skipped {f.name}: {e}")
                    continue
                lat, lng, when = exif_info(img)
                img = ImageOps.exif_transpose(img)
                if lat is not None:
                    lats.append(lat)
                    lngs.append(lng)
                if when:
                    dates.append(when)
                name = f"{i:02d}"
                w, h = save_resized(img, OUT_MEDIA / slug / f"{name}.webp", FULL_PX)
                save_resized(img, OUT_MEDIA / slug / f"{name}-thumb.webp", THUMB_PX)
                photos.append({
                    "src": f"media/photos/{slug}/{name}.webp",
                    "thumb": f"media/photos/{slug}/{name}-thumb.webp",
                    "w": w, "h": h,
                    "caption": str(captions.get(f.name, captions.get(f.stem, ""))),
                    "date": when,
                })

            lat = meta.get("lat", statistics.median(lats) if lats else None)
            lng = meta.get("lng", statistics.median(lngs) if lngs else None)
            if lat is None or lng is None:
                print(f"  ! {folder.name}: no GPS in photos and no lat/lng in place.yml; skipped")
                shutil.rmtree(OUT_MEDIA / slug)
                continue

            cover = int(meta.get("cover", 1)) - 1
            if 0 < cover < len(photos):
                photos.insert(0, photos.pop(cover))

            places.append({
                "slug": slug,
                "title": meta.get("title", folder.name.replace("-", " ").title()),
                "region": meta.get("region", ""),
                "date": str(meta.get("date", (min(dates)[:7] if dates else ""))),
                "blurb": meta.get("blurb", ""),
                "category": meta.get("category", "travel"),  # travel | field | nature
                "lat": round(float(lat), 3),   # ~100 m precision is plenty for a map
                "lng": round(float(lng), 3),
                "photos": photos,
            })
            print(f"  ✓ {slug}: {len(photos)} photos")

    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(places, indent=1, ensure_ascii=False))
    print(f"wrote {OUT_JSON.relative_to(ROOT)} with {len(places)} places")


# ---------------------------------------------------------------- demo data
DEMO = [
    ("santa-barbara", "Santa Barbara & the Gaviota Coast", "California, USA", "2025", 34.42, -119.70, "field",
     "Home base for grad school: chaparral ridgelines, oak woodland, and the Dangermond Preserve.", 6),
    ("los-padres", "Los Padres National Forest", "California, USA", "2025", 34.69, -119.55, "field",
     "Fieldwork and hikes through the backcountry I mapped with Los Padres ForestWatch.", 4),
    ("lusaka", "Lusaka & the Zambian countryside", "Zambia", "2025-07", -15.42, 28.28, "field",
     "A summer with the University of Zambia, visiting irrigated plots I had only seen from space.", 7),
    ("whakatane", "Whakatāne", "Bay of Plenty, New Zealand", "2024-08", -37.95, 176.99, "nature",
     "Tracking kiwi chicks through the native bush.", 5),
    ("colombia", "Andes of Boyacá", "Colombia", "2023-09", 5.53, -73.36, "travel",
     "Farming in the Andes with WWOOF.", 5),
    ("bryce", "Bryce Canyon", "Utah, USA", "2024", 37.59, -112.19, "nature",
     "Hoodoos at sunrise.", 3),
]
DEMO_COLORS = [("#A8D5CF", "#83A1C3"), ("#CEB5C8", "#83A1C3"), ("#FAC898", "#CEB5C8"),
               ("#9DB8A6", "#A8D5CF"), ("#83A1C3", "#3F5671"), ("#FAC898", "#B17776")]


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def demo_image(w, h, c1, c2, seed):
    import math
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    a, b = hex_rgb(c1), hex_rgb(c2)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    for k in range(14):
        base = h * (k + 1) / 15
        pts = [(x, base + 26 * math.sin(x / (170 + seed * 9) + k * 0.4 + seed)) for x in range(0, w + 20, 20)]
        d.line(pts, fill=(255, 255, 255), width=2)
    return img


def build_demo():
    if OUT_MEDIA.exists():
        shutil.rmtree(OUT_MEDIA)
    places = []
    for p_i, (slug, title, region, date, lat, lng, cat, blurb, n) in enumerate(DEMO):
        (OUT_MEDIA / slug).mkdir(parents=True)
        photos = []
        for i in range(1, n + 1):
            c1, c2 = DEMO_COLORS[(p_i + i) % len(DEMO_COLORS)]
            w, h = (1600, 1067) if i % 3 else (1067, 1500)
            img = demo_image(w, h, c1, c2, p_i * 3 + i)
            img.save(OUT_MEDIA / slug / f"{i:02d}.webp", "WEBP", quality=70)
            img.thumbnail((THUMB_PX, THUMB_PX))
            img.save(OUT_MEDIA / slug / f"{i:02d}-thumb.webp", "WEBP", quality=70)
            photos.append({"src": f"media/photos/{slug}/{i:02d}.webp",
                           "thumb": f"media/photos/{slug}/{i:02d}-thumb.webp",
                           "w": w, "h": h, "caption": f"Sample photo {i} (replace with your own)",
                           "date": None})
        places.append({"slug": slug, "title": title, "region": region, "date": date, "blurb": blurb,
                       "category": cat, "lat": lat, "lng": lng, "photos": photos, "sample": True})
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(places, indent=1, ensure_ascii=False))
    print(f"wrote demo gallery: {len(places)} places")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="generate sample placeholder gallery")
    args = ap.parse_args()
    build_demo() if args.demo else build()
