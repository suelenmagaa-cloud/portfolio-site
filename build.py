import json, html, shutil, subprocess, pathlib
from PIL import Image
R = pathlib.Path(__file__).parent
D = R / 'dist'

def rasterize():
    """pdf/NAME_EN.pdf -> slides/NAME_EN/01.webp ... (runs only if PDFs are present)"""
    for pdf in sorted((R / 'pdf').glob('*.pdf')):
        out = R / 'slides' / pdf.stem
        shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
        subprocess.run(['pdftoppm', '-r', '80', '-png', str(pdf), str(out / 'p')], check=True)
        for p in sorted(out.glob('p-*.png')):
            Image.open(p).convert('RGB').save(out / (p.stem[2:] + '.webp'), quality=78)
            p.unlink()

def crops(data):
    (R / 'assets').mkdir(exist_ok=True)
    for c in data['cases']:
        pdf = R / 'pdf' / f"{c['slides']}_EN.pdf"
        if not pdf.exists(): continue
        for k, (pg, x0, y0, x1, y1) in c.get('crops', {}).items():
            tmp = R / 'assets' / '_t'
            subprocess.run(['pdftoppm', '-r', '160', '-f', str(pg), '-l', str(pg), '-png', '-singlefile', str(pdf), str(tmp)], check=True)
            im = Image.open(str(tmp) + '.png').convert('RGB'); W, H = im.size
            im.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H))).save(R / 'assets' / f"{c['slides']}_{k}.webp", quality=82)
            pathlib.Path(str(tmp) + '.png').unlink()

def t(x):
    return ''.join(f'<span lang="{l}">{html.escape(x[i])}</span>' for i, l in enumerate(('en', 'pt')))

def imgs(d):
    return ''.join(f'<img loading="lazy" alt="" src="slides/{d.name}/{p.name}">' for p in sorted(d.glob('*.webp')))

def pick(name, fallback):
    for n in (name, fallback):
        d = R / 'slides' / n
        if d.exists(): return d

def gallery(c):
    out = ''
    for l in ('en', 'pt'):
        k, L = c['slides'], l.upper()
        desk = pick(f'{k}_{L}', f'{k}_EN')
        mob = pick(f'{k}_{L}_mobile', f'{k}_EN_mobile')
        out += f'<div lang="{l}" class="g{" d" if mob else ""}">{imgs(desk)}</div>'
        if mob: out += f'<div lang="{l}" class="g m">{imgs(mob)}</div>'
    return out

def figma(c, L):
    u = c.get('figma')
    if not u: return ''
    u = u.replace('www.figma.com', 'embed.figma.com') + ('&' if '?' in u else '?') + 'embed-host=share'
    return f'<h3>{t(L["flow"])}</h3><iframe class="fg" loading="lazy" allowfullscreen src="{html.escape(u)}"></iframe>'

def pic(c, k):
    f = R / 'assets' / f"{c['slides']}_{k}.webp"
    return f'<img loading="lazy" alt="" src="assets/{f.name}">' if f.exists() else ''

def h2(x):
    return ''.join(f'<span lang="{l}">{html.escape(x[i].split(" — ")[0])} <em>{html.escape(x[i].split(" — ")[-1])}</em></span>' for i, l in enumerate(('en', 'pt')))

def case(c, L):
    facts = ''.join(f'<div><b>{t(L[k])}</b><p>{t(c[k])}</p></div>' for k in ('context', 'scope', 'deliverables', 'status') if k in c)
    rows = ''
    for i, k in enumerate(('discovery', 'process', 'outcomes', 'learnings')):
        if k not in c: continue
        im = pic(c, k)
        rows += (f'<section class="row{" rev" if i % 2 else ""}{"" if im else " solo"}"><div class="tx"><h3>{t(L[k])}</h3><ul>'
                 + ''.join(f'<li>{t(x)}</li>' for x in c[k]) + f'</ul></div><div class="im">{im}</div></section>')
    return (f'<article id="{c["slides"]}"><header class="hero"><div class="hx"><span class="tag">{t(c["org"])}</span><h2>{h2(c["title"])}</h2>{facts}</div>'
            f'<div class="hi">{pic(c, "hero")}</div></header><p class="res">{t(c["results"])}</p>{rows}{figma(c, L)}'
            f'<details><summary>{t(L["slides"])}</summary>{gallery(c)}</details></article>')

CSS = """:root{--ink:#14122b;--navy:#27506f;--violet:#7c6cf6;--pink:#f58bb8;--soft:#f3efff}
*{box-sizing:border-box}body{margin:0;font:17px/1.65 Inter,system-ui,sans-serif;color:var(--navy);background:#fff}main{max-width:1080px;margin:auto;padding:16px}
h2,h3,.num{font-family:Outfit,Inter,system-ui,sans-serif}
.bar{display:flex;justify-content:flex-end;gap:6px}.bar button{border:1px solid var(--pink);background:#fff;color:var(--navy);border-radius:999px;padding:5px 16px;cursor:pointer;font:600 .85em Inter,sans-serif}
html[data-lang=en] .bar [data-l=en],html[data-lang=pt] .bar [data-l=pt]{background:linear-gradient(135deg,var(--pink),var(--violet));border-color:transparent;color:#fff}
html[data-lang=pt] [lang=en],html[data-lang=en] [lang=pt]{display:none}
article{padding:48px 0 32px;counter-reset:n}
.hero{display:grid;grid-template-columns:1.15fr 1fr;gap:36px;color:#fff;border-radius:32px;padding:44px;align-items:center;overflow:hidden;
background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100'%3E%3Cpath d='M28 0l28 16v32L28 64 0 48V16zM28 64l28 16v20M28 64L0 80v20' fill='none' stroke='%23fff' stroke-opacity='.08'/%3E%3C/svg%3E"),radial-gradient(90% 120% at 0% 0%,#0f0d24 0%,rgba(15,13,36,0) 60%),linear-gradient(135deg,#27506f 0%,#5a4fd1 60%,#7c6cf6 100%)}
.tag{display:inline-block;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:2px 14px;font-size:.8em;font-weight:600;letter-spacing:.05em}
h2{font-size:clamp(2.2rem,5vw,3.7rem);line-height:1.05;font-weight:700;letter-spacing:-.02em;margin:.4em 0 .7em}h2 em{display:block;font-style:normal;color:var(--pink)}
.hx b{font-size:.72em;text-transform:uppercase;letter-spacing:.1em;color:var(--pink)}.hx p{margin:.1em 0 .9em;font-size:.95em;opacity:.95}
.hi{position:relative}.hi::before{content:"";position:absolute;width:75%;aspect-ratio:1;border-radius:50%;background:linear-gradient(135deg,var(--pink),#ffc2dc);right:-10%;top:-18%}
.hi img{position:relative;width:100%;border-radius:24px;display:block;box-shadow:0 20px 50px rgba(15,13,36,.45)}
.res{font:600 clamp(1.3rem,2.6vw,1.9rem)/1.3 Outfit,sans-serif;color:var(--ink);margin:44px 0 12px;padding-left:22px;border-left:6px solid var(--pink)}
.row{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center;padding:32px 0;counter-increment:n}.row.rev .tx{order:2}.row.solo{grid-template-columns:1fr}
h3{font-size:1.5em;margin:0 0 .5em;color:var(--ink)}h3::before{content:"0" counter(n);display:block;font:700 4rem/1 Outfit,sans-serif;color:transparent;-webkit-text-stroke:1.5px var(--violet);margin-bottom:4px}
li{margin:.45em 0}li::marker{color:var(--pink)}
.im{background:var(--soft);border-radius:28px;padding:20px;position:relative;overflow:hidden}.im::before{content:"";position:absolute;width:55%;aspect-ratio:1;border-radius:50%;background:linear-gradient(135deg,var(--pink),var(--violet));opacity:.28;left:-12%;bottom:-18%}
.im img{position:relative;width:100%;max-height:540px;object-fit:contain;border-radius:16px;display:block}
.fg{width:100%;height:520px;border:0;border-radius:24px;background:var(--soft)}summary{cursor:pointer;font-weight:600;margin-top:20px;color:var(--violet)}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin-top:14px}.g img{width:100%;border-radius:10px;cursor:zoom-in}
@media(max-width:700px){.hero,.row{grid-template-columns:1fr}.row.rev .tx{order:0}.hero{padding:26px;border-radius:24px}.row{gap:20px}.g.d{display:none}.g.m{display:grid}.g{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}
.g.m{display:none}dialog{border:0;background:none;padding:0}dialog img{max-width:92vw;max-height:90vh}"""
JS = """const D=document.documentElement,ping=()=>parent.postMessage({h:D.scrollHeight},'*'),
set=l=>{D.dataset.lang=l;ping()};
set(new URLSearchParams(location.search).get('lang')||(navigator.language.startsWith('pt')?'pt':'en'));
document.querySelectorAll('.bar button').forEach(b=>b.onclick=()=>set(b.dataset.l));
addEventListener('message',e=>{if(e.data&&e.data.lang)set(String(e.data.lang).slice(0,2))});
addEventListener('load',ping);addEventListener('resize',ping);
document.querySelectorAll('details').forEach(d=>d.ontoggle=ping);
const dl=document.querySelector('dialog');
document.addEventListener('click',e=>{if(e.target.matches('.g img')){dl.querySelector('img').src=e.target.src;dl.showModal()}else if(e.target===dl||e.target.closest('dialog'))dl.close()});"""

def main():
    rasterize()
    data = json.loads((R / 'content' / 'cases.json').read_text('utf-8'))
    crops(data)
    body = '<div class="bar"><button data-l="en">EN</button><button data-l="pt">PT</button></div>' + ''.join(case(c, data['labels']) for c in data['cases'])
    page = (f'<!doctype html><html data-lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Suelen Magalhães — Product Design</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@500;700&display=swap"><style>{CSS}</style></head><body><main>{body}</main><dialog><img alt=""></dialog><script>{JS}</script></body></html>')
    shutil.rmtree(D, ignore_errors=True); D.mkdir()
    (D / 'index.html').write_text(page, 'utf-8')
    shutil.copytree(R / 'slides', D / 'slides')
    shutil.copytree(R / 'assets', D / 'assets')

if __name__ == '__main__':
    main()
