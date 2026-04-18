#!/usr/bin/env python3
"""Fetch photos for the canonical catdef reference bundle.

Reads PEXELS_API_KEY and UNSPLASH_ACCESS_KEY from the environment.
Downloads each photo into canonical/photos/ (skipping any already present)
and writes canonical/photos_manifest.json with per-photo attribution.

Run: PEXELS_API_KEY=... UNSPLASH_ACCESS_KEY=... python canonical/fetch_photos.py
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHOTOS = HERE / "photos"
MANIFEST = HERE / "photos_manifest.json"

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

UA = "catdef-canonical-fetch/1.0 (+https://catdef.org)"

# Each entry: (filename, provider, query, orientation)
# provider is "pexels" or "unsplash" — we spread across both to be a good citizen
# and so attribution is meaningfully mixed.
TARGETS = [
    ("item01_tin_locomotive_front.jpg", "pexels",   "vintage tin toy train", "landscape"),
    ("item01_tin_locomotive_side.jpg",  "unsplash", "antique metal toy train", "landscape"),
    ("item01_tin_locomotive_mark.jpg",  "pexels",   "vintage tin toy closeup", "landscape"),
    ("item02_flower_album_cover.jpg",   "unsplash", "antique leather book cover", "landscape"),
    ("item02_flower_album_page.jpg",    "pexels",   "pressed flowers herbarium", "landscape"),
    ("item03_plane_overview.jpg",       "pexels",   "vintage wood plane", "landscape"),
    ("item03_plane_mark.jpg",           "unsplash", "stanley tool stamp vintage", "landscape"),
    ("item04_map_scan.jpg",             "pexels",   "antique hand drawn map", "landscape"),
    ("item05_phone_front.jpg",          "pexels",   "vintage rotary telephone", "landscape"),
    ("item05_phone_base.jpg",           "unsplash", "old bakelite telephone detail", "landscape"),
    ("item05_phone_handset.jpg",        "pexels",   "vintage phone receiver", "landscape"),
    ("item06_lullaby_sheet.jpg",        "pexels",   "handwritten sheet music antique", "landscape"),
    ("item07_milk_bottle.jpg",          "pexels",   "vintage glass milk bottle", "landscape"),
    ("item08_quilt_overview.jpg",       "pexels",   "patchwork quilt antique", "landscape"),
    ("item08_quilt_detail.jpg",         "unsplash", "quilt embroidery detail", "landscape"),
    ("item09_campaign_button.jpg",      "pexels",   "vintage enamel pin badge", "landscape"),
    ("item10_ice_pick.jpg",             "pexels",   "ice axe tool antique", "landscape"),
    ("item11_letter.jpg",               "pexels",   "handwritten letter old paper", "landscape"),
    ("item12_playbill_front.jpg",       "pexels",   "vintage handbill paper print", "landscape"),
    ("item12_playbill_back.jpg",        "unsplash", "old paper document aged", "landscape"),
    ("loc_opera_house.jpg",             "pexels",   "small town historic theatre building", "landscape"),
    ("loc_van_bergen_schoolhouse.jpg",  "pexels",   "old one room schoolhouse", "landscape"),
]


def http_get_json(url, headers):
    req = urllib.request.Request(url, headers={**headers, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def http_get_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch_pexels(query, orientation):
    if not PEXELS_KEY:
        raise RuntimeError("PEXELS_API_KEY not set")
    url = (
        "https://api.pexels.com/v1/search?"
        + urllib.parse.urlencode({"query": query, "per_page": 5, "orientation": orientation})
    )
    data = http_get_json(url, {"Authorization": PEXELS_KEY})
    photos = data.get("photos", [])
    if not photos:
        return None
    photo = photos[0]
    img_url = photo["src"]["large"]
    img_bytes = http_get_bytes(img_url)
    return {
        "provider": "pexels",
        "provider_id": str(photo["id"]),
        "photographer": photo["photographer"],
        "photographer_url": photo["photographer_url"],
        "source_url": photo["url"],
        "image_url": img_url,
        "width": photo["width"],
        "height": photo["height"],
        "query": query,
        "license": "Pexels License (https://www.pexels.com/license/)",
        "bytes": img_bytes,
    }


def fetch_unsplash(query, orientation):
    if not UNSPLASH_KEY:
        raise RuntimeError("UNSPLASH_ACCESS_KEY not set")
    url = (
        "https://api.unsplash.com/search/photos?"
        + urllib.parse.urlencode({"query": query, "per_page": 5, "orientation": orientation})
    )
    data = http_get_json(url, {"Authorization": f"Client-ID {UNSPLASH_KEY}"})
    results = data.get("results", [])
    if not results:
        return None
    photo = results[0]
    img_url = photo["urls"]["regular"]
    img_bytes = http_get_bytes(img_url)
    # Trigger an Unsplash download endpoint per their API guidelines.
    try:
        http_get_json(
            photo["links"]["download_location"],
            {"Authorization": f"Client-ID {UNSPLASH_KEY}"},
        )
    except Exception:
        pass
    return {
        "provider": "unsplash",
        "provider_id": photo["id"],
        "photographer": photo["user"]["name"],
        "photographer_url": photo["user"]["links"]["html"],
        "source_url": photo["links"]["html"],
        "image_url": img_url,
        "width": photo["width"],
        "height": photo["height"],
        "query": query,
        "license": "Unsplash License (https://unsplash.com/license)",
        "bytes": img_bytes,
    }


def generate_stanley_placeholder(dest_path):
    """Generate the Stanley trademark placeholder image.

    The Stanley Rule & Level Co. entry in the Maker subcat is the one real-brand
    reference in the canonical. Rather than fetch a random photo to stand in for
    the trademark (which would misrepresent a real company's brand), this
    function renders a neutral typeset card clearly labelled PLACEHOLDER.
    """
    from PIL import Image, ImageDraw, ImageFont

    W, H = 480, 240
    img = Image.new("RGB", (W, H), color=(245, 239, 226))
    draw = ImageDraw.Draw(img)

    font_lg = font_sm = font_tiny = None
    for candidate in ("C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/georgia.ttf",
                      "C:/Windows/Fonts/timesbd.ttf", "C:/Windows/Fonts/times.ttf"):
        if os.path.exists(candidate):
            font_lg = ImageFont.truetype(candidate, 30)
            break
    for candidate in ("C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf"):
        if os.path.exists(candidate):
            font_sm = ImageFont.truetype(candidate, 14)
            font_tiny = ImageFont.truetype(candidate, 10)
            break
    if not font_lg:
        font_lg = ImageFont.load_default()
    if not font_sm:
        font_sm = ImageFont.load_default()
    if not font_tiny:
        font_tiny = ImageFont.load_default()

    ink = (42, 31, 18)
    muted = (122, 106, 82)

    def centered(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, y), text, font=font, fill=fill)

    draw.rectangle([(12, 12), (W - 12, H - 12)], outline=ink, width=2)
    draw.rectangle([(20, 20), (W - 20, H - 20)], outline=ink, width=1)
    centered(38, "STANLEY", font_lg, ink)
    centered(76, "RULE & LEVEL CO.", font_lg, ink)
    draw.line([(W // 2 - 90, 124), (W // 2 + 90, 124)], fill=muted, width=1)
    centered(132, "NEW BRITAIN, CONN.", font_sm, muted)
    centered(154, "EST. 1857", font_sm, muted)
    centered(205, "PLACEHOLDER — catdef canonical reference bundle", font_tiny, muted)

    img.save(dest_path, quality=88, optimize=True)
    return {
        "provider": "generated",
        "provider_id": "placeholder-stanley-v1",
        "photographer": "catdef-maintainer (generated placeholder)",
        "photographer_url": "https://catdef.org",
        "source_url": "canonical/fetch_photos.py (generate_stanley_placeholder)",
        "image_url": "",
        "width": W,
        "height": H,
        "query": None,
        "license": "MIT (part of the canonical bundle authored by catdef-maintainer)",
        "note": "Generated via PIL. Typeset reproduction of STANLEY RULE & LEVEL CO. on the bundle theme background; clearly labelled PLACEHOLDER so it cannot be mistaken for an authentic Stanley trademark.",
    }


def main():
    PHOTOS.mkdir(parents=True, exist_ok=True)

    manifest = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Generated placeholder (no API needed).
    placeholder_dest = PHOTOS / "maker_stanley_logo.jpg"
    if not placeholder_dest.exists() or "maker_stanley_logo.jpg" not in manifest:
        print("  generate maker_stanley_logo.jpg [placeholder]")
        manifest["maker_stanley_logo.jpg"] = generate_stanley_placeholder(placeholder_dest)
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    errors = []
    for filename, provider, query, orientation in TARGETS:
        dest = PHOTOS / filename
        if dest.exists() and filename in manifest:
            print(f"  skip {filename} (cached)")
            continue

        print(f"  fetch {filename} [{provider}] {query!r}")
        try:
            if provider == "pexels":
                result = fetch_pexels(query, orientation)
            elif provider == "unsplash":
                result = fetch_unsplash(query, orientation)
            else:
                raise ValueError(f"unknown provider {provider}")
            if not result:
                raise RuntimeError(f"no results for {query!r} on {provider}")
            dest.write_bytes(result.pop("bytes"))
            manifest[filename] = result
            MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.5)
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"    ERROR: {e}")

    print(f"\nDone. {len(manifest)} photos in manifest.")
    if errors:
        print(f"{len(errors)} errors:")
        for f, e in errors:
            print(f"  {f}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
