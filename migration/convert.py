"""WordPress (paviaracing.com) -> Astro markdown. Input: export.json + map.json from the server export.
Usage: python3 migration/convert.py SRC_DIR   (SRC_DIR has export.json, map.json, uploads/)"""
import json, re, os, sys, html, shutil, glob
from urllib.parse import urlparse
SRC = sys.argv[1]; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(f'{SRC}/export.json')); MAP = json.load(open(f'{SRC}/map.json'))
DEFAULT = '2026/08/WP-Posts-Default-Image.png'
used = set(); report = {'missing_img': [], 'shortcodes': [], 'noyt': 0}

# TablePress tables (pulled separately from the server)
TABLES = json.load(open(f'{SRC}/tables.json')) if os.path.exists(f'{SRC}/tables.json') else {}
def table_html(tid):
    rows = TABLES.get(str(tid))
    if not rows: return ''
    esc = lambda c: html.escape(c.strip().replace('–', '-') or '-')
    head = ''.join(f'<th>{esc(c)}</th>' for c in rows[0])
    body = ''.join('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in r) + '</tr>' for r in rows[1:])
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'

def upath(u):
    p = urlparse(u).path
    if '/wp-content/uploads/' not in p: return None
    return p.split('/wp-content/uploads/', 1)[1]
def local(u):
    k = upath(u)
    if not k: return None
    base = re.sub(r'^sites/\d+/', '', k)
    for cand in (k, base, re.sub(r'-\d+x\d+(\.\w+)$', r'\1', base), re.sub(r'(\.(?:png|jpe?g|gif))\.(?:png|jpe?g|gif)$', r'\1', base)):
        if cand in MAP: used.add(MAP[cand]); return '/uploads/' + MAP[cand]
        for ext in ('', ):
            if os.path.isfile(f'{SRC}/uploads/{cand}'): used.add(cand); return '/uploads/' + cand
        for w in (re.sub(r'\.\w+$', '.webp', cand), cand + '.webp'):
            if os.path.isfile(f'{SRC}/uploads/{w}'): used.add(w); return '/uploads/' + w
    return None

YT = re.compile(r'(?:youtu\.be/|youtube(?:-nocookie)?\.com/(?:watch\?v=|embed/|shorts/))([\w-]{11})')
def lite(i): return f'<div class="yt" data-yt="{i}" style="background-image:url(https://i.ytimg.com/vi/{i}/hqdefault.jpg)"><button type="button" aria-label="Play video"></button></div>'

def convert(body, slug):
    b = re.sub(r'<!--\s*/?wp:[^>]*-->', '', body)
    ids = []
    def emb(m):
        v = YT.search(m.group(0))
        if v: ids.append(v.group(1)); return '\n@@YT%d@@\n' % (len(ids) - 1)
        return m.group(0)
    b = re.sub(r'<figure class="wp-block-embed[^>]*>.*?</figure>', emb, b, flags=re.S)
    b = re.sub(r'<iframe[^>]*youtube[^>]*embed/(?!videoseries)[\w-]{11}[^>]*>\s*</iframe>', emb, b, flags=re.S)
    b = re.sub(r'(?m)^\s*(https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)[\w\-&=?]+)\s*$', emb, b)
    b = re.sub(r'\[embed\](.*?)\[/embed\]', lambda m: emb(m) if YT.search(m.group(1)) else '', b)
    # captions
    b = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', lambda m: _cap(m.group(1)), b, flags=re.S)
    b = re.sub(r'\[table id=(\d+)\s*/?\]', lambda m: table_html(m.group(1)), b)
    b = re.sub(r'\[(?:Show thumbnails|ngg[^\]]*|nggallery[^\]]*|youtube-feed[^\]]*)\]', '', b, flags=re.I)
    for s in re.findall(r'\[\w[^\]]*\]', b):
        if not re.match(r'\[\d', s): report['shortcodes'].append((slug, s[:60]))
    def img(m):
        u = m.group(1); l = local(u)
        if l: return m.group(0).replace(u, l)
        report['missing_img'].append((slug, u)); return m.group(0)
    b = re.sub(r'<img[^>]*?src="(?:skypec2c:|blob:)[^"]*"[^>]*>', '', b)
    b = re.sub(r'<img[^>]*?src="([^"]+)"', img, b)
    b = re.sub(r'\s(?:srcset|sizes|width|height|decoding|fetchpriority)="[^"]*"', '', b)
    b = re.sub(r'<a href="(https?://[^"]*?/wp-content/uploads/[^"]+)"', lambda m: m.group(0).replace(m.group(1), local(m.group(1)) or m.group(1)), b)
    b = re.sub(r'href="https?://(?:www\.)?paviaracing\.com/?([^"]*)"', lambda m: 'href="/%s"' % m.group(1), b)
    b = re.sub(r'<(img|iframe)\b', r'<\1 loading="lazy"', b)
    b = b.replace('&nbsp;', ' ')
    for n, i in enumerate(ids):
        b = b.replace('@@YT%d@@' % n, '' if n == 0 else lite(i))
    b = re.sub(r'<p>\s*</p>', '', b)
    b = '\n'.join(l.strip() for l in b.split('\n'))
    return (ids[0] if ids else None), re.sub(r'\n{3,}', '\n\n', b).strip()
def _cap(inner):
    m = re.search(r'(<img[^>]*>)\s*(.*)', inner, re.S)
    return f'<figure>{m.group(1)}<figcaption>{m.group(2).strip()}</figcaption></figure>' if m else inner
q = lambda s: json.dumps(s, ensure_ascii=False)

for d in data:
    slug = d['slug']; title = html.unescape(d['title']).strip()
    first, body = convert(d['content'], slug)
    if d['type'] == 'page':
        if slug == 'welcome': continue   # hand-written home.md
        fm = ['---', f'title: {q(title)}', '---']
        open(f'{OUT}/src/content/pages/{slug}.md', 'w', encoding='utf-8').write('\n'.join(fm) + '\n\n' + body + '\n'); continue
    if not first: report['noyt'] += 1
    fm = ['---', f'title: {q(title)}', f'date: {d["date"][:10]}', f'categories: {json.dumps(d["cats"])}']
    if first: fm.append(f'youtube: {first}')
    image = None
    if d['thumb'] and d['thumb'] != DEFAULT:
        image = local(f'https://paviaracing.com/wp-content/uploads/{d["thumb"]}')
    elif not d['thumb']:
        m = re.search(r'<img[^>]*src="(/uploads/[^"]+)"', body); image = m.group(1) if m else None
    if image: fm.append(f'image: {q(image)}')
    if d['desc']: fm.append(f'description: {q(d["desc"])}')
    fm.append('---')
    open(f'{OUT}/src/content/posts/{slug}.md', 'w', encoding='utf-8').write('\n'.join(fm) + '\n\n' + body + '\n')

# copy used images (+ site assets)
for extra in ['2023/12/Pavia-New-Logo-350x100-1.gif', '2023/12/Pavia-FB-Cover.webp', '2023/12/Pavia-FavIcon-2023-300x300.webp', DEFAULT]: used.add(extra)
for f in sorted(used):
    src = f'{SRC}/uploads/{f}'
    if os.path.isfile(src):
        os.makedirs(os.path.dirname(f'{OUT}/public/uploads/{f}'), exist_ok=True); shutil.copy2(src, f'{OUT}/public/uploads/{f}')
    else: report['missing_img'].append(('copy', f))
json.dump(report, open(f'{OUT}/migration/report.json', 'w'), indent=1)
print(len(used), 'images;', {k: (len(v) if isinstance(v, list) else v) for k, v in report.items()})
