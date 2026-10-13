#!/usr/bin/env python3
"""Image optimizer for PaviaRacing.com.

  python3 scripts/optimize-images.py ingest FILE [FILE ...] --dest public/uploads/2026/10
      Resize (long edge <= 2000px), apply EXIF rotation, strip metadata, write
      WebP (photos/screenshots) into --dest, and write a gallery/list thumbnail
      to public/thumbs/<same path>.webp. Prints the site path to use in posts.

  python3 scripts/optimize-images.py thumbs
      Create any missing thumbnails for public/uploads and public/galleries.

Animated GIFs are left alone (no thumbnail is made, originals are served).
"""
import os, sys, argparse
from PIL import Image, ImageOps

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
PUBLIC = os.path.normpath(PUBLIC)
MAX_EDGE = 2000
THUMB_W, THUMB_H = 320, 240          # covers the 160x120 gallery cell at 2x
THUMB_MIN_SOURCE = 40_000            # don't thumbnail files already tiny
EXTS = ('.jpg', '.jpeg', '.png', '.webp')

def thumb_path(site_path):
    return os.path.join(PUBLIC, 'thumbs', site_path.lstrip('/') + '.webp')

def make_thumb(src_file, site_path):
    out = thumb_path(site_path)
    if os.path.exists(out): return None
    if os.path.getsize(src_file) < THUMB_MIN_SOURCE: return None
    im = Image.open(src_file)
    if getattr(im, 'is_animated', False): return None
    im = ImageOps.exif_transpose(im)
    if im.mode not in ('RGB', 'RGBA'): im = im.convert('RGBA' if 'transparency' in im.info else 'RGB')
    w, h = im.size
    s = max(THUMB_W / w, THUMB_H / h)
    if s < 1: im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, 'WEBP', quality=78, method=6)
    if os.path.getsize(out) >= os.path.getsize(src_file) * 0.7:
        os.remove(out); return None
    return out

def ingest(files, dest):
    dest_abs = os.path.abspath(dest)
    for f in files:
        im = ImageOps.exif_transpose(Image.open(f))
        has_alpha = im.mode in ('RGBA', 'LA') or 'transparency' in im.info
        im = im.convert('RGBA' if has_alpha else 'RGB')
        w, h = im.size
        s = MAX_EDGE / max(w, h)
        if s < 1: im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
        name = os.path.splitext(os.path.basename(f))[0] + '.webp'
        out = os.path.join(dest_abs, name)
        os.makedirs(dest_abs, exist_ok=True)
        im.save(out, 'WEBP', quality=82, method=6)
        site = '/' + os.path.relpath(out, PUBLIC).replace(os.sep, '/')
        make_thumb(out, site)
        print(f'{os.path.getsize(f)//1024} KB -> {os.path.getsize(out)//1024} KB  {site}')

def thumbs():
    n = 0
    for top in ('uploads', 'galleries'):
        for r, _, fs in os.walk(os.path.join(PUBLIC, top)):
            for f in fs:
                if f.lower().endswith(EXTS):
                    p = os.path.join(r, f)
                    site = '/' + os.path.relpath(p, PUBLIC).replace(os.sep, '/')
                    if make_thumb(p, site): n += 1
    print('thumbnails created:', n)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['ingest', 'thumbs'])
    ap.add_argument('files', nargs='*')
    ap.add_argument('--dest')
    a = ap.parse_args()
    if a.cmd == 'ingest':
        if not a.files or not a.dest: ap.error('ingest needs FILEs and --dest')
        ingest(a.files, a.dest)
    else: thumbs()
