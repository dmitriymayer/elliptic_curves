import re, json, html, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'src')
OUT = os.path.join(HERE, '..')
REPO_URL = os.environ.get('REPO_URL', 'https://github.com/')
NAMES = {'Main.dc.html': 'index.html'}
for i in range(1, 7): NAMES[f'Problem-1-{i}.dc.html'] = f'problem-1-{i}.html'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr'}
RAW = {'style','script','textarea'}
HOLE = re.compile(r'\{\{\s*(.*?)\s*\}\}')
TAG = re.compile(r'<!--.*?-->|</([A-Za-z][\w:.-]*)\s*>|<([A-Za-z][\w:.-]*)((?:\s+[^\s=/>]+(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+))?)*)\s*(/?)>', re.S)
ATTR = re.compile(r'([^\s=/>]+)(?:\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+))?')

def parts(text, decode=True):
    out = []; pos = 0
    for m in HOLE.finditer(text):
        if m.start() > pos: out.append(html.unescape(text[pos:m.start()]) if decode else text[pos:m.start()])
        out.append({'h': m.group(1)}); pos = m.end()
    if pos < len(text): out.append(html.unescape(text[pos:]) if decode else text[pos:])
    return out

def attrval(v):
    if v is None: return ''
    if v[:1] in '"\'': v = v[1:-1]
    hs = list(HOLE.finditer(v))
    if not hs: return html.unescape(v)
    if len(hs) == 1 and hs[0].span() == (0, len(v)): return {'h': hs[0].group(1)}
    return {'i': parts(v)}

def parse(src):
    root = ['root', [], []]; stack = [root]; pos = 0
    def add(n): stack[-1][-1].append(n) if stack[-1][0] == 'root' else stack[-1][3].append(n)
    while True:
        m = TAG.search(src, pos)
        end = m.start() if m else len(src)
        if end > pos:
            t = src[pos:end]
            add(['t', parts(t)])
        if not m: break
        pos = m.end()
        if m.group(0).startswith('<!--'): continue
        if m.group(1):
            name = m.group(1)
            top = stack.pop()
            if top[0] == 'root' or top[1] != name:
                raise SystemExit(f'mismatch </{name}> vs {top[1]} at {m.start()}: {src[m.start()-200:m.start()+50]!r}')
            continue
        name, attrs_s, selfc = m.group(2), m.group(3), m.group(4)
        attrs = [(a.group(1), attrval(a.group(2))) for a in ATTR.finditer(attrs_s)]
        el = ['e', name, attrs, []]
        add(el)
        if name.lower() in RAW:
            close = src.find(f'</{name}>', pos)
            el[3].append(['t', [src[pos:close]]]); pos = close + len(name) + 3
            continue
        if selfc or name.lower() in VOID: continue
        stack.append(el)
    assert len(stack) == 1, [s[1] for s in stack]
    return root[2]

def convert(n):
    """convert e-nodes with sc-* to f/i nodes; mark static; return (node, static)"""
    if n[0] == 't':
        return n, all(isinstance(p, str) for p in n[1])
    name, attrs, ch = n[1], n[2], n[3]
    conv = [convert(c) for c in ch]
    children = [c for c, _ in conv]; st = all(s for _, s in conv)
    A = dict(attrs)
    if name == 'sc-for':
        return ['f', A['list']['h'], A.get('as', 'item'), children], False
    if name == 'sc-if':
        return ['i', A['value']['h'], children], False
    if name == 'dc-import': raise SystemExit('dc-import unsupported')
    st = st and all(isinstance(v, str) for _, v in attrs)
    return ['e', name, attrs, children, 1 if st else 0], st

def build(fn):
    s = open(os.path.join(SRC, fn)).read()
    for a, b in NAMES.items(): s = s.replace(f'"{a}"', f'"{b}"').replace(f'"{a}#', f'"{b}#')
    s = s.replace('/_blob/7e2a9c3f14bcd4567d4e99be847e3b62', 'assets/katex/katex.min.css')
    s = s.replace('"https://github.com/"', '"' + REPO_URL + '"')
    pm = re.search(r'<span>(problems/[^<]*?\.py)[^<]*</span>', s)
    if pm:
        py = pm.group(1)
        s, nrun = re.subn(r'<button type="button" style="([^"]*)">\s*(<svg[^>]*>.*?</svg>)\s*Запустить в браузере\s*</button>',
            lambda m: f'<a href="{py}" download="solution.py" style="{m.group(1)}; text-decoration: none">{m.group(2)} Скачать solution.py</a>', s, flags=re.S)
        assert nrun == 1, fn
    title = re.search(r'<title>(.*?)</title>', s, re.S).group(1)
    lang = re.search(r'<html lang="([^"]+)"', s).group(1)
    head_extra = re.findall(r'<link rel="stylesheet" href="assets/[^"]+">', s.split('<body>')[0])
    xdc = s.split('<x-dc>', 1)[1].rsplit('</x-dc>', 1)[0]
    helmet = ''
    m = re.search(r'<helmet>(.*?)</helmet>', xdc, re.S)
    if m: helmet = m.group(1); xdc = xdc[:m.start()] + xdc[m.end():]
    assert '{{' not in helmet
    sm = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', s, re.S)
    js = sm.group(1)
    tree = [convert(n)[0] for n in parse(xdc)]
    tj = json.dumps(tree, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    page = f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{chr(10).join(head_extra)}
{helmet.strip()}
<style>#dc-root svg text{{-webkit-user-select:none;user-select:none}}</style>
</head>
<body>
<div id="dc-root"></div>
<noscript><p style="padding: 24px; font-family: sans-serif">Для работы страницы нужен JavaScript.</p></noscript>
<script src="assets/dc-runtime.js"></script>
<script src="assets/site.js"></script>
<script>
DC.mount({tj}, function (DCLogic, React) {{
{js}
return Component;
}});
</script>
</body>
</html>
'''
    open(os.path.join(OUT, NAMES[fn]), 'w').write(page)
    return len(page)

if __name__ == '__main__':
    os.makedirs(OUT + '/assets/katex', exist_ok=True)
    if os.environ.get('RUNTIME'): shutil.copy(os.environ['RUNTIME'], OUT + '/assets/dc-runtime.js')
    k = os.environ.get('KATEX_DIST')
    if k:
        shutil.copy(k + 'katex.min.css', OUT + '/assets/katex/katex.min.css')
        if os.path.exists(OUT + '/assets/katex/fonts'): shutil.rmtree(OUT + '/assets/katex/fonts')
        os.makedirs(OUT + '/assets/katex/fonts')
        for f in os.listdir(k + 'fonts'):
            if f.endswith('.woff2'): shutil.copy(k + 'fonts/' + f, OUT + '/assets/katex/fonts/' + f)
    for fn in NAMES: print(fn, build(fn))
