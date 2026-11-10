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
    for k in ('discovery', 'process', 'outcomes', 'learnings'):
        if k not in c: continue
        rows += (f'<section class="card"><div class="im">{pic(c, k)}</div><h3>{t(L[k])}</h3><ul>'
                 + ''.join(f'<li>{t(x)}</li>' for x in c[k]) + '</ul></section>')
    return (f'<article id="{c["slides"]}"><header class="hero"><div class="hx"><span class="tag">{t(c["org"])}</span><h2>{h2(c["title"])}</h2>{facts}</div>'
            f'<div class="hi">{pic(c, "hero")}</div></header><p class="res">{t(c["results"])}</p><div class="cards">{rows}</div>{figma(c, L)}'
            f'<details><summary>{t(L["slides"])}</summary>{gallery(c)}</details></article>')

CSS = """:root{--ink:#14122b;--navy:#27506f;--violet:#7c6cf6;--pink:#f58bb8;--soft:#f3efff;
--hex:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100'%3E%3Cpath d='M28 0l28 16v32L28 64 0 48V16zM28 64l28 16v20M28 64L0 80v20' fill='none' stroke='%23fff' stroke-opacity='.08'/%3E%3C/svg%3E");
--glow:radial-gradient(90% 120% at 0% 0%,#0f0d24 0%,rgba(15,13,36,0) 60%);--g:linear-gradient(135deg,#27506f 0%,#5a4fd1 60%,#7c6cf6 100%)}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 Inter,system-ui,sans-serif;color:var(--navy);background:#fff}main{max-width:1080px;margin:auto;padding:16px;counter-reset:c}
h2,h3{font-family:Outfit,Inter,system-ui,sans-serif}
.bar{display:flex;justify-content:flex-end;gap:6px;margin-bottom:8px}.bar button{border:1px solid var(--pink);background:#fff;color:var(--navy);border-radius:999px;padding:5px 16px;cursor:pointer;font:600 .85em Inter,sans-serif}
html[data-lang=en] .bar [data-l=en],html[data-lang=pt] .bar [data-l=pt]{background:linear-gradient(135deg,var(--pink),var(--violet));border-color:transparent;color:#fff}
html[data-lang=pt] [lang=en],html[data-lang=en] [lang=pt]{display:none}
.idx{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 0}.idx a{display:flex;gap:8px;align-items:center;text-decoration:none;color:var(--navy);border:1px solid #e0d9ff;border-radius:999px;padding:6px 16px;font-weight:600;font-size:.9em}.idx i{font-style:normal;color:var(--pink)}
article{margin-top:120px;counter-reset:n;counter-increment:c}article:first-of-type{margin-top:48px}
.hero{display:grid;grid-template-columns:1.1fr 1fr;gap:40px;color:#fff;border-radius:36px;padding:64px 56px;min-height:460px;align-items:center;overflow:hidden;background:var(--hex),var(--glow),var(--g)}
article:nth-of-type(2){--g:linear-gradient(135deg,#1b1840 0%,#9b3d93 65%,#f58bb8 100%)}article:nth-of-type(3){--g:linear-gradient(135deg,#1f4f6e 0%,#1f86ad 60%,#2aa3c8 100%)}
.tag{display:inline-block;border:1px solid rgba(255,255,255,.4);border-radius:999px;padding:2px 14px;font-size:.78em;font-weight:600;letter-spacing:.06em}.tag::before{content:"CASE 0" counter(c) "  ·  "}
h2{font-size:clamp(2.6rem,6vw,4.8rem);line-height:1.02;font-weight:700;letter-spacing:-.03em;margin:.35em 0 .6em}h2 em{display:block;font-style:normal;color:var(--pink)}
.hx b{font-size:.7em;text-transform:uppercase;letter-spacing:.1em;color:var(--pink)}.hx p{margin:.1em 0 .8em;font-size:.92em}
.hi{position:relative}.hi::before{content:"";position:absolute;width:75%;aspect-ratio:1;border-radius:50%;background:linear-gradient(135deg,var(--pink),#ffc2dc);right:-10%;top:-18%}
article:nth-of-type(2) .hi::before{background:linear-gradient(135deg,#ffd0e4,#fff)}
.hi img{position:relative;width:100%;border-radius:24px;display:block;box-shadow:0 20px 50px rgba(15,13,36,.45)}
.res{font:600 1.25rem/1.4 Outfit,sans-serif;color:var(--ink);margin:28px 4px 8px;padding-left:16px;border-left:5px solid var(--pink)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:20px}
.card{background:#fff;border:1px solid #e6e0ff;border-radius:20px;padding:14px 16px 6px;counter-increment:n}
.im{background:var(--soft);border-radius:14px;height:170px;display:flex;align-items:center;justify-content:center;overflow:hidden}.im:empty{display:none}.im img{max-height:100%;max-width:100%;object-fit:contain}
.card h3{font-size:1.05rem;margin:.8em 0 .3em;color:var(--ink)}.card h3::before{content:"0" counter(n);color:var(--pink);margin-right:8px}
.card ul{font-size:.9rem;padding-left:1.1em;margin:0 0 8px}li{margin:.3em 0}li::marker{color:var(--pink)}
.fg{width:100%;height:520px;border:0;border-radius:24px;background:var(--soft);margin-top:20px}summary{cursor:pointer;font-weight:600;margin-top:20px;color:var(--violet)}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin-top:14px}.g img{width:100%;border-radius:10px;cursor:zoom-in}
@media(max-width:700px){.hero{grid-template-columns:1fr;padding:32px 24px;min-height:0;border-radius:26px}article{margin-top:80px}.g.d{display:none}.g.m{display:grid}.g{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}
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
    nav = '<nav class="idx">' + ''.join(f'<a href="#{c["slides"]}"><i>0{n+1}</i>{t([x.split(" — ")[0] for x in c["title"]])}</a>' for n, c in enumerate(data['cases'])) + '</nav>'
    body = nav + '<div class="bar"><button data-l="en">EN</button><button data-l="pt">PT</button></div>' + ''.join(case(c, data['labels']) for c in data['cases'])
    page = (f'<!doctype html><html data-lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Suelen Magalhães — Product Design</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@500;700&display=swap"><style>{CSS}</style></head><body><main>{body}</main><dialog><img alt=""></dialog><script>{JS}</script></body></html>')
    shutil.rmtree(D, ignore_errors=True); D.mkdir()
    (D / 'index.html').write_text(page, 'utf-8')
    shutil.copytree(R / 'slides', D / 'slides')
    shutil.copytree(R / 'assets', D / 'assets')

if __name__ == '__main__':
    main()
