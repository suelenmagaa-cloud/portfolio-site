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

def pills(cs, cur):
    out = ''
    for c in cs:
        cur_attr = ' aria-current="true"' if c['slides'] == cur else ''
        out += f'<a href="#{c["slides"]}"{cur_attr}>' + t([x.split(' — ')[0] for x in c['title']]) + '</a>'
    return f'<nav class="pills">{out}</nav>'

def case(c, L, cs, n):
    facts = ''.join(f'<div><b>{t(L[k])}</b><p>{t(c[k])}</p></div>' for k in ('context', 'scope', 'deliverables', 'status') if k in c)
    slides = ''
    for i, k in enumerate(('discovery', 'process', 'outcomes', 'learnings')):
        if k not in c: continue
        slides += (f'<section class="slide"><div class="tx"><h3><span class="num">0{i+1}</span>{t(L[k])}</h3><ul>'
                   + ''.join(f'<li>{t(x)}</li>' for x in c[k]) + f'</ul></div><div class="im">{pic(c, k)}</div></section>')
    nav = f'<a href="#top">↑ {t(L["top"])}</a>'
    return (f'<article id="{c["slides"]}"><header class="hero"><div class="hi">{pic(c, "hero")}</div><div class="hx"><span class="tag">{t(c["org"])}</span><h2>{h2(c["title"])}</h2></div></header>'
            f'<div class="facts">{facts}</div><p class="res">{t(c["results"])}</p>'
            f'<div class="car"><button class="ar l" aria-label="Previous / Anterior">&#8249;</button><div class="track" tabindex="0">{slides}</div><button class="ar r" aria-label="Next / Próximo">&#8250;</button></div><div class="dots"></div>'
            f'{figma(c, L)}<div class="nx">{nav}</div></article>')

CSS = """:root{--ink:#14122b;--navy:#235070;--violet:#7c6cf6;--pink:#f28db1;--soft:#f3efff;--c:#27506f;
--hex:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100'%3E%3Cpath d='M28 0l28 16v32L28 64 0 48V16zM28 64l28 16v20M28 64L0 80v20' fill='none' stroke='%23fff' stroke-opacity='.1'/%3E%3C/svg%3E")}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;overflow-x:hidden;font:16px/1.6 Inter,system-ui,sans-serif;color:var(--navy);background:#fff}main{max-width:1080px;margin:auto;padding:16px;counter-reset:c}
h2,h3{font-family:Outfit,Inter,system-ui,sans-serif}
.top{display:flex;justify-content:space-between;align-items:center}.logo{height:56px;width:auto}.menu{display:flex;flex-wrap:wrap;gap:6px 22px;justify-content:flex-start;margin:10px 0 14px}.menu a{text-decoration:none;color:var(--ink);font:400 .72rem Outfit,sans-serif;letter-spacing:.03em;padding:4px 0}.menu a[aria-current]{color:var(--pink)}.menu a:hover{color:var(--pink)}.brand{display:flex;align-items:center;gap:14px;text-decoration:none;color:var(--navy)}.brand span{font:400 .95rem Outfit,sans-serif;letter-spacing:.16em}.brand b{font-weight:700}.brand i{font-style:normal;color:var(--pink);margin:0 .7em}
.bar{display:flex;gap:6px}.bar button{border:1px solid var(--pink);background:#fff;color:var(--navy);border-radius:999px;padding:5px 16px;cursor:pointer;font:600 .85em Inter,sans-serif}
html[data-lang=en] .bar [data-l=en],html[data-lang=pt] .bar [data-l=pt]{background:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%);background-origin:border-box;border-color:transparent;color:#fff}
html[data-lang=pt] [lang=en],html[data-lang=en] [lang=pt]{display:none}
.idx{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0}.idx a{display:flex;gap:8px;align-items:center;text-decoration:none;color:var(--navy);border:1px solid #e0d9ff;border-radius:999px;padding:7px 18px;font-weight:600;font-size:.92em}.idx a:hover{border-color:var(--pink)}.idx i{font-style:normal;color:var(--pink)}
article{margin-top:104px;counter-reset:n;counter-increment:c}article:first-of-type{margin-top:36px}article:nth-of-type(2){--c:#1b1840}article:nth-of-type(3){--c:#1f4f6e}
.hero{position:relative;border-radius:28px;overflow:hidden;min-height:340px;display:flex;align-items:center;background:var(--c)}
.hi{position:absolute;inset:0}.hi img{width:100%;height:100%;object-fit:cover;display:block}
.hi::after{content:"";position:absolute;inset:0;background:var(--hex),linear-gradient(90deg,var(--c) 0%,var(--c) 28%,transparent 68%)}
.hx{position:relative;z-index:1;color:#fff;padding:40px 48px;max-width:52%}
.tag{display:inline-block;border:1px solid rgba(255,255,255,.45);border-radius:999px;padding:2px 14px;font-size:.75em;font-weight:600;letter-spacing:.06em}.tag::before{content:"CASE  ·  "}
h2{font-size:clamp(2.3rem,5.2vw,3.8rem);line-height:1.02;font-weight:700;letter-spacing:-.03em;margin:.4em 0 0}h2 em{display:block;font-style:normal;font-weight:500;font-size:.36em;line-height:1.3;letter-spacing:0;color:var(--pink);margin-top:.7em}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px 28px;margin:20px 4px 0}.facts b{font-size:.68em;text-transform:uppercase;letter-spacing:.1em;color:var(--pink)}.facts p{margin:.1em 0;font-size:.85rem}
.res{font:600 1.2rem/1.4 Outfit,sans-serif;color:var(--ink);margin:22px 4px 8px;padding-left:16px;border-left:5px solid var(--pink)}
.car{position:relative;margin-top:26px}.track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}.track::-webkit-scrollbar{display:none}
.slide{flex:0 0 100%;min-width:0;scroll-snap-align:start;display:grid;grid-template-columns:1fr 1.15fr;gap:32px;align-items:center;padding:8px 60px;min-height:380px}
h3{font-size:1.2rem;margin:0 0 .4em;color:var(--ink)}.num{display:block;font:700 3rem/1 Outfit,sans-serif;color:transparent;-webkit-text-stroke:1.3px var(--violet);margin-bottom:2px}
.tx ul{padding-left:1.1em;margin:0;font-size:.95rem}li{margin:.35em 0}li::marker{color:var(--pink)}
.im{padding:0;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;min-height:280px}.im:empty{display:none}

.im img{position:relative;max-width:100%;max-height:340px;width:auto;height:auto;object-fit:contain;display:block;cursor:zoom-in}
.ar{position:absolute;top:50%;transform:translateY(-50%);z-index:2;width:44px;height:44px;border-radius:50%;border:1px solid var(--pink);background:#fff;color:var(--navy);font-size:1.7rem;line-height:1;cursor:pointer}.ar.l{left:0}.ar.r{right:0}
.dots{display:flex;justify-content:center;gap:8px;margin-top:10px}.dots i{width:8px;height:8px;border-radius:99px;background:#e0d9ff;transition:.2s}.dots i.on{background:var(--pink);width:22px}
.pills{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;position:sticky;top:0;z-index:30;background:rgba(255,255,255,.92);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);padding:10px 16px;margin:0 -16px;border-bottom:1px solid #f0ecff}article{scroll-margin-top:56px}.pills a{border:1px solid var(--pink);border-radius:999px;padding:6px 20px;text-decoration:none;color:var(--navy);font-weight:600;font-size:.85rem}
.pills a[aria-current]{background:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%);background-origin:border-box;color:#fff;border-color:transparent}
.shero{display:flex;justify-content:space-between;align-items:center;gap:40px;color:#fff;border-radius:0;padding:56px calc(50vw - 50%);margin:12px calc(50% - 50vw) 0;background:var(--hex),linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%)}
.shero small{font-size:.85rem}.shero h1{font:400 clamp(2.6rem,6vw,4.6rem)/1.05 Outfit,sans-serif;margin:.2em 0 0}
.stats{min-width:200px}.stats div{border-top:1px solid rgba(255,255,255,.4);padding:22px 0}.stats div:last-child{padding-bottom:0}.stats div:first-child{border:0}.stats b{font:500 1.5rem/1.1 Outfit,sans-serif;display:block}.stats span{font-size:.75rem;display:block;margin-top:2px}
.intro{font-size:1.15rem;margin:26px 0 16px;text-align:left}
footer.site{margin-top:20px}.bandbar{height:14px;margin:0 calc(50% - 50vw);background:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%)}.ft{display:flex;justify-content:space-between;align-items:center;padding:34px 8px}
.ft h4{font:500 1.6rem Outfit,sans-serif;margin:0;color:var(--ink)}.ft p{margin:.2em 0 0;font-size:.9rem}.btn{border:1px solid #d9d2ff;border-radius:999px;padding:10px 34px;text-decoration:none;color:var(--navy)}
.fl{display:flex;gap:26px;justify-content:center;font-size:.85rem;padding-bottom:24px}.fl a{color:var(--navy)}
html[data-embed] .site{display:none}html[data-embed] .top{justify-content:flex-end}
.fg{width:100%;height:520px;border:0;border-radius:24px;background:var(--soft);margin-top:20px}summary{cursor:pointer;font-weight:600;margin-top:18px;color:var(--violet)}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin-top:14px}.g img{width:100%;border-radius:10px;cursor:zoom-in}
.nx{display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:12px;margin-top:16px}
.nx a{border:1px solid var(--pink);border-radius:999px;padding:8px 22px;text-decoration:none;color:var(--navy);font-weight:600;font-size:.9rem}.nx a.pri{background:linear-gradient(135deg,var(--pink),var(--violet));color:#fff;border-color:transparent;margin-left:auto}
@media(max-width:700px){.logo{height:44px}.brand{gap:8px}.brand span{font-size:.68rem;letter-spacing:.08em}.brand i{margin:0 .4em}.menu{justify-content:flex-start;gap:4px 18px}.slide{grid-template-columns:minmax(0,1fr);padding:0 4px;min-height:0}.im{min-width:0;width:100%}.tx{min-width:0}.ar{display:none}.shero{flex-direction:column;align-items:flex-start;padding:28px}.ft{flex-direction:column;align-items:flex-start;gap:16px}.hero{min-height:320px;align-items:flex-start;border-radius:22px}.hx{max-width:100%;padding:26px 22px}.hi::after{background:var(--hex),linear-gradient(180deg,var(--c) 0%,var(--c) 30%,transparent 90%)}
.row{grid-template-columns:1fr;gap:16px}.row.rev .tx{order:0}article{margin-top:72px}.g.d{display:none}.g.m{display:grid}.g{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}
.im.col{flex-direction:column;gap:10px}.im.col img{max-height:190px}.im.row{gap:12px}.im.row img{flex:1 1 0;min-width:0;max-height:340px;object-fit:contain}
.im.tall{gap:10px;align-items:flex-start}.im.tall img{flex:1 1 0;min-width:0;height:340px;object-fit:cover;object-position:top;border:1px solid #e8e4f7}
.feat{display:grid;grid-template-columns:1fr 1.5fr;gap:32px;align-items:center;margin:48px 4px 0;padding-top:36px;border-top:1px solid #ece8fb}.feat h3{font-size:1.6rem}.feat p{margin:.2em 0 .8em}.fim img{width:100%;height:auto;display:block;cursor:zoom-in;border-radius:10px}
@media(max-width:700px){.feat{grid-template-columns:1fr}.im.row{flex-direction:column}.im.row img{max-height:300px;width:100%}.im.tall img{height:260px}}
.g.m{display:none}dialog{border:0;background:none;padding:0}dialog img{max-width:92vw;max-height:90vh}"""
JS = """const D=document.documentElement,ping=()=>parent.postMessage({h:D.scrollHeight},'*'),
set=l=>{D.dataset.lang=l;ping()};
set(new URLSearchParams(location.search).get('lang')||(navigator.language.startsWith('pt')?'pt':'en'));
document.querySelectorAll('.bar button').forEach(b=>b.onclick=()=>set(b.dataset.l));
addEventListener('message',e=>{if(e.data&&e.data.lang)set(String(e.data.lang).slice(0,2))});
addEventListener('load',ping);addEventListener('resize',ping);
document.querySelectorAll('details').forEach(d=>d.ontoggle=ping);
if(new URLSearchParams(location.search).has('embed'))D.dataset.embed=1;
document.querySelectorAll('.car').forEach(c=>{const tr=c.querySelector('.track'),ds=c.nextElementSibling;ds.innerHTML='<i></i>'.repeat(tr.children.length);
const A=c.querySelector('.l'),B=c.querySelector('.r');const dot=()=>{const k=Math.round(tr.scrollLeft/tr.clientWidth),n=tr.children.length;[...ds.children].forEach((d,j)=>d.className=j==k?'on':'');A.style.visibility=k<=0?'hidden':'visible';B.style.visibility=k>=n-1?'hidden':'visible'};tr.onscroll=dot;dot();
c.querySelector('.l').onclick=()=>tr.scrollBy({left:-tr.clientWidth,behavior:'smooth'});c.querySelector('.r').onclick=()=>tr.scrollBy({left:tr.clientWidth,behavior:'smooth'})});
const pl=[...document.querySelectorAll('.pills a')],arts=[...document.querySelectorAll('article')];
const mark=()=>{let cur=null;arts.forEach(a=>{const r=a.getBoundingClientRect();if(r.top<innerHeight*.4&&r.bottom>innerHeight*.4)cur=a.id});pl.forEach(l=>{if(l.getAttribute('href')=='#'+cur)l.setAttribute('aria-current','true');else l.removeAttribute('aria-current')})};
addEventListener('scroll',mark,{passive:true});mark();
const dl=document.querySelector('dialog');
document.addEventListener('click',e=>{if(e.target.matches('.g img,.im img')){dl.querySelector('img').src=e.target.src;dl.showModal()}else if(e.target===dl||e.target.closest('dialog'))dl.close()});"""

def chrome(S, cur):
    bar = '<div class="bar"><button data-l="en">EN</button><button data-l="pt">PT</button></div>'
    head = '<div class="top"><a class="brand site" href="#top"><img class="logo" src="assets/logo.png" alt=""><span><b>SUELEN MAGALHÃES</b><i>|</i>DESIGN</span></a>' + bar + '</div>'
    menu = '<nav class="menu site">' + ''.join(f'<a href="{html.escape(u)}"' + (' aria-current="page"' if i == cur else '') + f'>{t([en, pt])}</a>' for i, (en, pt, u) in enumerate(S['menu'])) + '</nav>'
    foot = (f'<footer class="site"><div class="bandbar"></div><div class="ft"><div><h4>{t(S["cta"])}</h4><p>{t(S["cta2"])}</p></div>'
            f'<a class="btn" href="mailto:{S["email"]}">{t(S["btn"])}</a></div><div class="fl"><a href="mailto:{S["email"]}">{S["email"]}</a>'
            f'<a href="{S["linkedin"]}">LinkedIn</a><span>© 2026 Suelen Magalhães</span></div></footer>')
    return head, menu, foot

def shell(title, body):
    return (f'<!doctype html><html data-lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@500;700&display=swap"><style>{CSS}</style></head><body><main id="top">{body}</main><dialog><img alt=""></dialog><script>{JS}</script></body></html>')

def pimg(k, alt=''):
    return f'<img loading="lazy" alt="{html.escape(alt)}" src="assets/{k}.webp">' if (R / 'assets' / f'{k}.webp').exists() else ''

PCSS = """body.ph{background:#fff}.ph .intro{display:none}
.pt{display:grid;grid-template-columns:1.2fr 1fr;gap:20px 56px;align-items:end;margin:44px 4px 0}
.pt small{display:inline-block;border:1px solid var(--pink);border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em;color:var(--navy)}
.pt h1{font:700 clamp(3rem,8vw,6.2rem)/.95 Outfit,sans-serif;letter-spacing:-.04em;color:var(--ink);margin:.2em 0 0}
.pt p{font-size:1.1rem;margin:0;color:var(--navy)}.pf{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px 28px;margin:34px 4px 0;padding-top:24px;border-top:5px solid;border-image:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%) 1}
.pf b{font-size:.68em;text-transform:uppercase;letter-spacing:.1em;color:var(--pink)}.pf p{margin:.1em 0;font-size:.85rem}
.bh{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px;margin:64px 4px 14px}.bh h2{font-size:1.7rem;margin:0;color:var(--ink);letter-spacing:-.02em}.bh span{font-size:.85rem}
.bd{display:grid;grid-template-columns:repeat(12,1fr);grid-auto-rows:150px;gap:44px 36px}
.tl{width:100%;align-items:stretch;min-width:0;border:0;padding:0;background:none;cursor:pointer;text-align:left;font:inherit;color:var(--ink);display:flex;flex-direction:column;gap:14px;min-height:0}
.tl .ims{position:relative;flex:1;min-height:0;min-width:0;border-radius:6px;overflow:hidden;display:flex;transition:transform .25s}
.tl:hover .ims,.tl:focus-visible .ims{transform:translateY(-4px)}.tl:focus-visible{outline:2px solid var(--violet);outline-offset:6px}
.tl img{flex:1 1 0;min-width:0;height:100%;display:block}
.tl.fit .ims img{object-fit:contain;-webkit-mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent),linear-gradient(180deg,transparent,#000 7%,#000 93%,transparent);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent),linear-gradient(180deg,transparent,#000 7%,#000 93%,transparent);mask-composite:intersect}
.tl.plain .ims{background:#e8e5f2;border-radius:10px}.tl.plain img{object-fit:cover}.tl.plain.top img{object-position:top;border-right:6px solid #e8e5f2}
.tl .lb{display:flex;align-items:flex-end;justify-content:space-between;gap:16px}
.tl .lb i{display:block;font:600 .64rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--pink);font-style:normal;margin-bottom:2px}.tl .lb b{font:500 1.15rem/1.2 Outfit,sans-serif}
.tl .more{flex:none;font:600 .82rem Inter,sans-serif;color:var(--navy);border-bottom:2px solid var(--pink);padding-bottom:1px;white-space:nowrap;transition:color .2s}.tl:hover .more{color:var(--violet)}
dialog.pd{border:0;border-radius:18px;padding:0;width:min(1040px,94vw);max-height:90vh;color:var(--navy);background:#fff}dialog.pd::backdrop{background:rgba(20,18,43,.6)}
.pd .in{display:grid;grid-template-columns:1.35fr 1fr;max-height:90vh}.pd .pi{background:var(--pb,#eeeaf8);padding:16px;overflow:auto;display:flex;flex-direction:column;gap:12px;align-items:center;justify-content:center}.pd .pi img{max-width:100%;height:auto;display:block;border-radius:6px}
.pd .px{padding:30px 30px 22px;overflow:auto}.pd .px i{font:600 .68rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--pink);font-style:normal}
.pd h3{font:700 1.7rem/1.1 Outfit,sans-serif;color:var(--ink);margin:.3em 0 .6em;letter-spacing:-.02em}.pd h4{font:600 .7rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--violet);margin:1.2em 0 .3em}
.pd ul{padding-left:1.1em;margin:0}.pd li{margin:.35em 0}.pd li::marker{color:var(--pink)}.pd p{margin:0}
.pd .ct{position:sticky;bottom:-22px;display:flex;gap:8px;margin-top:22px;padding:12px 0 0;background:#fff}.pd .ct button{border:1px solid var(--pink);background:#fff;color:var(--navy);border-radius:999px;padding:7px 18px;cursor:pointer;font:600 .85rem Inter,sans-serif}.pd .ct button:first-child{margin-right:auto}
@media(max-width:700px){.pt{grid-template-columns:1fr;margin-top:28px}.bd{grid-template-columns:1fr;grid-auto-rows:300px;gap:36px}.tl{grid-area:auto!important}.tl.top img:nth-child(n+3){display:none}.pd .in{grid-template-columns:1fr;overflow:auto}.pd .pi{max-height:44vh}.pd .px{overflow:visible}}"""
PJS = """(()=>{const dl=document.querySelector('dialog.pd');if(!dl)return;const ts=[...document.querySelectorAll('.tl')],ds=[...dl.querySelectorAll('.dc')];let k=0;
const show=n=>{k=(n+ds.length)%ds.length;ds.forEach((d,i)=>d.hidden=i!=k);ds[k].querySelectorAll('img[data-s]').forEach(i=>{i.src=i.dataset.s;i.removeAttribute('data-s')});ds[k].querySelector('.pi').scrollTop=0;ds[k].querySelector('.px').scrollTop=0};
ts.forEach((t,i)=>t.onclick=()=>{show(i);dl.showModal();ping()});
dl.addEventListener('click',e=>{if(e.target===dl)dl.close();const b=e.target.closest('button[data-a]');if(!b)return;if(b.dataset.a=='x')dl.close();else show(k+(b.dataset.a=='n'?1:-1))});
})();"""

def edgecolor(k):
    f = R / 'assets' / f'{k}.webp'
    if not f.exists(): return '#e8e5f2'
    im = Image.open(f).convert('RGB'); w, h = im.size; px = im.load(); pts = []
    for x in range(0, w, max(1, w // 60)):
        pts += [px[x, 1], px[x, h - 2]]
    for y in range(0, h, max(1, h // 60)):
        pts += [px[1, y], px[w - 2, y]]
    pts.sort(key=sum); m = pts[len(pts) // 2]
    return '#%02x%02x%02x' % m

def pharma(data, S, L):
    P = data['page']
    head, menu, foot = chrome(S, 2)
    top = ('<section class="pt"><div><small>' + html.escape(P['tags']) + '</small><h1>' + t(P['title']) + '</h1></div><p>' + t(P['intro']) + '</p></section>'
           '<div class="pf">' + ''.join(f'<div><b>{t(a)}</b><p>{t(b)}</p></div>' for a, b in P['facts']) + '</div>')
    tiles = ''; dcs = ''
    for i, tl in enumerate(data['tiles']):
        ims = ''.join(pimg(k) for k in tl['images'])
        plain = tl.get('plain'); col = '#e8e5f2' if plain else edgecolor(tl['images'][0])
        cls = 'plain' + (' top' if tl['fit'] == 'top' else '') if plain else 'fit'
        tiles += (f'<button class="tl {cls}" id="{tl["id"]}" style="grid-area:{tl["area"]}" aria-haspopup="dialog"><span class="ims" style="background:{col}">{ims}</span>'
                  f'<span class="lb"><span><i>{t(tl["tag"])}</i><b>{t(tl["title"])}</b></span><span class="more">{t(P.get("more", ["See more", "Ver mais"]))} &#8599;</span></span></button>')
        big = ''.join(f'<img alt="" data-s="assets/{k}.webp">' for k in tl['images'])
        dcs += (f'<div class="dc" hidden><div class="in"><div class="pi" style="--pb:{col}">{big}</div><div class="px"><i>{t(tl["tag"])}</i><h3>{t(tl["title"])}</h3>'
                f'<h4>{t(P["constraint"])}</h4><p>{t(tl["constraint"])}</p><h4>{t(P["did"])}</h4><ul>' + ''.join(f'<li>{t(x)}</li>' for x in tl['did'])
                + f'</ul><div class="ct"><button data-a="p">&#8249; {t(P["prev"])}</button><button data-a="n">{t(P["next"])} &#8250;</button><button data-a="x">{t(P["close"])}</button></div></div></div></div>')
    board = f'<div class="bh"><h2>{t(P["board"])}</h2><span>{t(P["hint"])}</span></div><div class="bd">{tiles}</div>'
    dlg = f'<dialog class="pd" aria-label="Detail">{dcs}</dialog>'
    page = shell('Suelen Magalhães — Pharma design', head + menu + top + board + foot)
    page = page.replace('</style>', PCSS + '</style>', 1).replace('<body>', '<body class="ph">', 1)
    return page.replace('</body>', dlg + f'<script>{PJS}</script></body>', 1)

HCSS = """body.hl{background:#fff}.hl .intro{display:none}
.ht{margin:48px 4px 0;max-width:980px}.ht small{display:inline-block;border:1px solid var(--pink);border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em;color:var(--navy)}
.ht h1{font:700 clamp(3.4rem,9vw,7rem)/.92 Outfit,sans-serif;letter-spacing:-.045em;color:var(--ink);margin:.18em 0 .25em}.ht p{font-size:1.25rem;line-height:1.45;color:var(--navy);margin:0;max-width:44ch}
.hg{display:grid;grid-template-columns:1fr 1fr;margin:44px 4px 0;border-top:5px solid;border-image:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%) 1}
.hg>div{padding:26px 36px 8px 0}.hg>div+div{padding-left:36px;border-left:1px solid #e4e0ee}.hg b{font:600 .7rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--pink)}.hg p{font:500 1.35rem/1.3 Outfit,sans-serif;color:var(--ink);margin:.35em 0 0}
.hp{margin:72px 4px 0}.hp h2,.hc h2{font-size:1.7rem;margin:0 0 22px;color:var(--ink);letter-spacing:-.02em}
.hs{display:grid;grid-template-columns:repeat(5,1fr);gap:0;position:relative;counter-reset:s}.hs::before{content:"";position:absolute;left:0;right:0;top:19px;height:3px;background:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%)}
.hs li{list-style:none;position:relative;padding:50px 22px 0 0;counter-increment:s}.hs li::before{content:counter(s);position:absolute;left:0;top:0;width:40px;height:40px;border-radius:50%;background:#fff;border:3px solid var(--navy);display:grid;place-items:center;font:700 .95rem Outfit,sans-serif;color:var(--navy)}
.hs b{display:block;font:600 1.05rem Outfit,sans-serif;color:var(--ink);margin-bottom:.3em}.hs span{font-size:.85rem;line-height:1.45;color:var(--navy)}.hs ol{display:contents;margin:0;padding:0}
.hc{margin:88px 4px 0}.hc>p{margin:-12px 0 36px;font-size:.95rem}
.bk{--a:#c9806a;--t:#fbf1ed;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:56px;align-items:center;border-radius:28px;padding:56px;margin:0 0 36px!important;background:linear-gradient(var(--a),var(--a)) top/100% 7px no-repeat,var(--t)}
.bk.rev{grid-template-columns:minmax(0,1.05fr) minmax(0,1fr)}.bk.rev .fan{order:2}
.fan{position:relative;aspect-ratio:1/1.12;max-width:420px;width:100%;margin:0 auto;border:0;padding:0;background:none;cursor:pointer}
.fan img{position:absolute;width:72%;height:auto;border-radius:3px;box-shadow:0 14px 34px rgba(20,18,43,.22);transition:transform .35s}
.fan img:nth-child(1){left:0;top:6%;transform:rotate(-7deg);z-index:1}.fan img:nth-child(2){right:0;top:0;transform:rotate(6deg);z-index:2}.fan img:nth-child(3){left:14%;top:12%;z-index:3;width:74%}
.fan:hover img:nth-child(1){transform:rotate(-10deg) translateX(-10px)}.fan:hover img:nth-child(2){transform:rotate(9deg) translateX(10px)}.fan:focus-visible{outline:2px solid var(--violet);outline-offset:8px}
.bk .k{font:600 .68rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--a);filter:brightness(.8)}
.bk h3{font:700 clamp(1.5rem,2.6vw,2.15rem)/1.12 Outfit,sans-serif;color:var(--ink);letter-spacing:-.02em;margin:.3em 0 .4em}.bk .in2{font-size:.9rem;color:var(--navy);margin:0 0 14px}
.bk .tx2{font-size:1rem;line-height:1.55;color:var(--navy);margin:0 0 20px}
.bk dl{display:grid;grid-template-columns:auto 1fr;gap:6px 22px;margin:0 0 20px;font-size:.88rem}.bk dt{font:600 .66rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--ink);opacity:.55;padding-top:3px}.bk dd{margin:0;color:var(--navy)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 24px}.chips>span{background:#fff;border:1px solid var(--a);border-radius:999px;padding:4px 14px;font:600 .74rem Inter,sans-serif;color:var(--navy)}
.hb{border:0;background:none;padding:0 0 2px;cursor:pointer;font:600 .95rem Inter,sans-serif;color:var(--navy);border-bottom:3px solid var(--a);transition:color .2s}.hb:hover{color:var(--violet)}
.cvv{margin:18px 0 0;font-size:.8rem;color:var(--navy);opacity:.8}
.if{background:linear-gradient(135deg,#1c1140 0%,#235070 70%,#4a2c6e 130%);color:#fff;border-radius:28px;padding:56px;margin:0 0 36px;display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.5fr);gap:48px;align-items:center}
.if .k{font:600 .68rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--pink)}.if h3{font:700 clamp(1.5rem,2.6vw,2.15rem)/1.12 Outfit,sans-serif;letter-spacing:-.02em;margin:.3em 0 .5em;color:#fff}.if p{font-size:1rem;line-height:1.55;margin:0 0 14px;color:#e6e2f5}.if .sr{font-size:.8rem;opacity:.75}
.if .hb{color:#fff;border-bottom-color:var(--pink)}.if .hb:hover{color:var(--pink)}
.ifr{display:flex;gap:20px;justify-content:center}.ifr .ifs{flex:0 1 360px;min-width:0;height:720px;overflow-y:auto;overflow-x:hidden;background:#14122b;border-radius:14px;scrollbar-width:thin;box-shadow:0 18px 40px rgba(0,0,0,.35)}.ifr img{display:block;width:100%;height:auto}
.cw{align-items:stretch;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:28px;margin:0 0 36px}
.cs{margin:0!important;--a:#ec6e57;--t:#fdf0ec;background:var(--t);border-radius:28px;overflow:hidden;display:flex;flex-direction:column;grid-column:span 6;background:linear-gradient(var(--a),var(--a)) top/100% 7px no-repeat,var(--t)}
.cs.c1{grid-column:span 8}.cs.c2{grid-column:span 4}.cs.c3{grid-column:span 12;flex-direction:row}
.cs .ci{margin:7px 0 0;line-height:0;background:#fff}.cs .ci img{display:block;width:100%;height:100%;object-fit:cover}.cs.c2 .ci{position:relative;flex:1;min-height:340px}.cs.c2 .ci img{position:absolute;inset:0}.cs.c3 .ci{flex:1.5;min-width:0}
.cs .ct{padding:34px 36px 38px}.cs.c3 .ct{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;margin-top:7px}
.cs .k{font:600 .68rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--a);filter:brightness(.8)}
.cs h3{font:700 clamp(1.4rem,2.3vw,1.9rem)/1.12 Outfit,sans-serif;color:var(--ink);letter-spacing:-.02em;margin:.3em 0 .45em}.cs h3 small{font:600 .8rem Inter,sans-serif;color:var(--navy);opacity:.6;margin-left:8px;letter-spacing:0}
.cs p{font-size:.95rem;line-height:1.55;color:var(--navy);margin:0 0 16px}.cs .lg{height:38px;width:auto;display:block;margin:0 0 14px}
.cs .tp{margin:0 0 18px;padding:0;list-style:none;display:grid;gap:6px;font-size:.84rem;color:var(--navy)}.cs .tp li{padding-left:16px;position:relative}.cs .tp li::before{content:"";position:absolute;left:0;top:.55em;width:6px;height:6px;border-radius:50%;background:var(--a)}
.cs .chips{margin:0 0 20px}
@media(max-width:860px){.cw{grid-template-columns:minmax(0,1fr)}.cs,.cs.c1,.cs.c2,.cs.c3{grid-column:auto;flex-direction:column;border-radius:22px}.cs .ct{padding:26px 22px 30px}.cs.c3 .ct{margin-top:0}.cs.c2 .ci{flex:none;min-height:0}.cs.c2 .ci img{position:static}}
dialog.hv{border:0;border-radius:18px;padding:0;width:min(1000px,96vw);height:min(92vh,980px);background:#14122b;color:#fff;overflow:hidden}dialog.hv::backdrop{background:rgba(20,18,43,.72)}
dialog.hv[open]{display:flex;flex-direction:column}.hv .hh{display:flex;align-items:center;gap:14px;padding:14px 20px;border-bottom:1px solid rgba(255,255,255,.12)}.hv .hh b{flex:1;font:600 .95rem Outfit,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hv .hh span{font:600 .8rem Inter,sans-serif;opacity:.7}
.hv button{font:600 .85rem Inter,sans-serif;color:#fff;background:none;border:1px solid rgba(255,255,255,.4);border-radius:999px;padding:6px 16px;cursor:pointer}.hv button:hover{border-color:var(--pink);color:var(--pink)}
.hv .st{flex:1;min-height:0;overflow:auto;display:flex;justify-content:center;padding:20px;background:#2a2740}.hv .st img{display:block;max-width:100%;height:auto;align-self:flex-start;box-shadow:0 10px 30px rgba(0,0,0,.4)}.hv.pg .st{align-items:center}.hv.pg .st img{max-height:100%;width:auto;align-self:center}
.hv .th{display:flex;gap:8px;padding:12px 20px;overflow-x:auto;border-top:1px solid rgba(255,255,255,.12)}.hv .th img{height:64px;width:auto;border-radius:3px;opacity:.5;cursor:pointer;flex:none;border:2px solid transparent}.hv .th img.on{opacity:1;border-color:var(--pink)}
.hv .nv{display:flex;gap:8px}
@media(max-width:860px){.hg{grid-template-columns:1fr}.hg>div,.hg>div+div{padding:20px 0 6px;border-left:0}.hs{grid-template-columns:1fr}.hs::before{left:19px;right:auto;top:0;bottom:0;width:3px;height:auto}.hs li{padding:0 0 26px 58px;min-height:40px}
.bk,.bk.rev,.if{grid-template-columns:minmax(0,1fr);padding:30px 22px;gap:30px;border-radius:22px}.bk.rev .fan{order:0}.fan{max-width:340px}.ifr{gap:12px}.ifr{align-items:flex-start}.ifr .ifs{height:auto;max-height:560px;flex:1 1 0}.hv .th img{height:48px}}"""
HJS = """(()=>{const dl=document.querySelector('dialog.hv');if(!dl)return;const G=JSON.parse(document.getElementById('hg').textContent),st=dl.querySelector('.st'),th=dl.querySelector('.th'),ct=dl.querySelector('.hh span'),tt=dl.querySelector('.hh b');let g=null,k=0;
const show=n=>{k=(n+g.i.length)%g.i.length;st.innerHTML='<img alt="" src="'+g.i[k]+'">';st.scrollTop=0;ct.textContent=(k+1)+' / '+g.i.length;[...th.children].forEach((x,j)=>x.className=j==k?'on':'');th.children[k]&&th.children[k].scrollIntoView({inline:'center',block:'nearest'})};
const open=(id,n)=>{g=G[id];tt.textContent=g.t;dl.classList.toggle('pg',g.p);th.innerHTML=g.i.length>1?g.i.map((s,j)=>'<img alt="" loading="lazy" data-j="'+j+'" src="'+g.h[j]+'">').join(''):'';th.style.display=g.i.length>1?'flex':'none';dl.querySelector('.nv').style.visibility=g.i.length>1?'visible':'hidden';show(n||0);dl.showModal();ping()};
document.querySelectorAll('[data-g]').forEach(b=>b.onclick=()=>open(b.dataset.g,+b.dataset.n||0));
dl.addEventListener('click',e=>{if(e.target===dl)dl.close();const b=e.target.closest('button[data-a]');if(b){if(b.dataset.a=='x')dl.close();else show(k+(b.dataset.a=='n'?1:-1))}const i=e.target.closest('.th img');if(i)show(+i.dataset.j)});
dl.addEventListener('keydown',e=>{if(e.key=='ArrowRight')show(k+1);if(e.key=='ArrowLeft')show(k-1)});
})();"""

def health(data, S):
    P = data['page']; M = P['meta']
    head, menu, foot = chrome(S, 3)
    top = ('<section class="ht"><small>' + html.escape(P['tags']) + '</small><h1>' + t(P['title']) + '</h1><p>' + t(P['intro']) + '</p></section>'
           f'<div class="hg"><div><b>{t(P["give"])}</b><p>{t(P["give2"])}</p></div><div><b>{t(P["make"])}</b><p>{t(P["make2"])}</p></div></div>')
    steps = ''.join(f'<li><b>{t(a)}</b><span>{t(b)}</span></li>' for a, b in P['steps'])
    proc = f'<section class="hp"><h2>{t(P["process"])}</h2><ol class="hs">{steps}</ol></section>'
    G = {}; blocks = ''
    def ims(key, n): return [f'assets/health/{key}_{i:02d}.webp' for i in range(1, n + 1)]
    for bi, b in enumerate(data['books']):
        I = ims(b['key'], b['n']); title = b['title'][1]
        G[b['id']] = {'t': title, 'i': I, 'h': I, 'p': True}
        fan = ''.join(f'<img loading="lazy" alt="" src="assets/health/{b["key"]}_{i:02d}.webp">' for i in b['fan'])
        rows = [(M['inst'], html.escape(b['inst'])), (M['year'], b['year']), (M['pages'], b['pages'])]
        if b.get('org'): rows.insert(1, (M['org'], html.escape(b['org'])))
        if b.get('fund'): rows.append((M['fund'], html.escape(b['fund'])))
        dl = ''.join(f'<dt>{t(a)}</dt><dd>{c}</dd>' for a, c in rows)
        chips = ''.join(f'<span>{t(r)}</span>' for r in b['role'])
        cvv = f'<p class="cvv">{t(P["cvv"])}</p>' if b.get('cvv') else ''
        blocks += (f'<article class="bk{" rev" if bi % 2 else ""}" id="{b["id"]}" style="--a:{b["accent"]};--t:{b["tint"]}">'
                   f'<button class="fan" data-g="{b["id"]}" aria-label="{html.escape(title)}">{fan}</button><div><span class="k">{t(b["kind"])}</span>'
                   f'<h3>{t(b["title"])}</h3><p class="tx2">{t(b["text"])}</p><dl>{dl}</dl><div class="chips">{chips}</div>'
                   f'<button class="hb" data-g="{b["id"]}">{t(P["browse"])} ({b["n"]}) &#8599;</button>{cvv}</div></article>')
        if b['id'] == 'ijc':
            blocks += (f'<article class="if" id="infografico"><div><span class="k">{t(P["info_tag"])}</span><h3>{t(P["info_title"])}</h3><p>{t(P["info_text"])}</p>'
                       f'<p class="sr">{t(P["info_src"])}</p></div>'
                       '<div class="ifr"><div class="ifs" tabindex="0" aria-label="Infographic 1"><img loading="lazy" alt="" src="assets/health/info_1.webp"></div>'
                       '<div class="ifs" tabindex="0" aria-label="Infographic 2"><img loading="lazy" alt="" src="assets/health/info_3.webp"></div></div></article>')
    chap = f'<section class="hc"><h2>{t(P["chapter"])}</h2><p>{t(P["chapter2"])}</p>{blocks}</section>'

    courses = ''
    for c in data.get('courses', []):
        I = c.get('viewer')
        if I:
            seq = ['assets/health/tut_%02d.webp' % i for i in range(0, 8)]
            G[I] = {'t': c['title'][1] + ' · ' + P['tutorial'][1], 'i': seq, 'h': seq, 'p': True}
        tp = ''.join(f'<li>{t(x)}</li>' for x in c.get('topics', []))
        tp = f'<ul class="tp" aria-label="{html.escape(P["topics"][1])}">{tp}</ul>' if tp else ''
        chips = ''.join(f'<span>{t(r)}</span>' for r in c['chips'])
        yr = f'<small>{c["year"]}</small>' if c.get('year') else ''
        lg = f'<img class="lg" alt="" src="assets/health/{c["logo"]}.webp">' if c.get('logo') else ''
        btn = f'<button class="hb" data-g="{I}" style="--a:{c["accent"]}">{t(P["tutorial"])} &#8599;</button>' if I else ''
        courses += (f'<article class="cs {c["cls"]}" id="{c["id"]}" style="--a:{c["accent"]};--t:{c["tint"]}"><div class="ci"><img loading="lazy" alt="" src="assets/health/{c["img"]}.webp"></div>'
                    f'<div class="ct"><span class="k">{t(c["kind"])}</span><h3>{t(c["title"])}{yr}</h3>{lg}<p>{t(c["text"])}</p>{tp}<div class="chips">{chips}</div>{btn}</div></article>')
    if courses:
        chap += f'<section class="hc"><h2>{t(P["courses"])}</h2><p>{t(P["courses2"])}</p><div class="cw">{courses}</div></section>'
    viewer = (f'<dialog class="hv" aria-label="Viewer"><div class="hh"><b></b><span></span><div class="nv"><button data-a="p">&#8249; {t(P["prev"])}</button> <button data-a="n">{t(P["next"])} &#8250;</button></div>'
              f'<button data-a="x">{t(P["close"])}</button></div><div class="st"></div><div class="th"></div></dialog>')
    page = shell('Suelen Magalhães — Health', head + menu + top + proc + chap + foot)
    page = page.replace('</style>', HCSS + '</style>', 1).replace('<body>', '<body class="hl">', 1)
    js = '<script type="application/json" id="hg">' + json.dumps(G, ensure_ascii=False).replace('</', '<\\/') + '</script>'
    return page.replace('</body>', viewer + js + f'<script>{HJS}</script></body>', 1)

BCSS = """body.br{background:#fff}.br .intro{display:none}
.bt{margin:48px 4px 0;max-width:980px}.bt small{display:inline-block;border:1px solid var(--pink);border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em;color:var(--navy)}
.bt h1{font:700 clamp(3.2rem,8.5vw,6.6rem)/.95 Outfit,sans-serif;letter-spacing:-.045em;color:var(--ink);margin:.18em 0 .3em}
.bt .ld{font:500 clamp(1.4rem,2.6vw,2rem)/1.25 Outfit,sans-serif;color:var(--ink);margin:0 0 18px;max-width:28ch;padding-left:22px;border-left:6px solid;border-image:linear-gradient(180deg,#1c1140,#235070 62%,#f28db1) 1}
.bt p{font-size:1.1rem;line-height:1.5;color:var(--navy);max-width:52ch;margin:0}
.bi{margin:64px 4px 0}.bi h2{font-size:1.7rem;margin:0 0 22px;color:var(--ink);letter-spacing:-.02em}
.bl{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px;margin:0;padding:0;list-style:none}
.bl a{display:block;text-decoration:none;color:inherit}.bl .th{aspect-ratio:4/3;border-radius:20px;overflow:hidden;background:#f2f1f7;transition:transform .25s,box-shadow .25s}.bl .th img{width:100%;height:100%;object-fit:contain;display:block}
.bl a:hover .th{transform:translateY(-4px);box-shadow:0 14px 30px rgba(20,18,43,.16)}
.bl b{display:block;font:600 1rem Outfit,sans-serif;color:var(--ink);margin-top:10px}.bl span{display:block;font-size:.8rem;color:var(--navy)}.bl i{font:600 .68rem Inter,sans-serif;font-style:normal;color:var(--pink);letter-spacing:.1em}
.sc{--bg:#054557;--fg:#fff;--ac:#eacf19;background:var(--bg);color:var(--fg);border-radius:32px;padding:56px;margin:56px 0 0!important;position:relative;overflow:hidden}
.sc::before{content:"";position:absolute;left:0;top:0;bottom:0;width:10px;background:var(--ac)}
.sh{display:flex;align-items:flex-end;gap:24px;flex-wrap:wrap;margin:0 0 36px}.sh .n{font:700 clamp(3.4rem,8vw,6rem)/.8 Outfit,sans-serif;color:var(--ac);letter-spacing:-.04em}
.sh h2{font:700 clamp(2rem,4.4vw,3.4rem)/1 Outfit,sans-serif;letter-spacing:-.03em;margin:0;color:inherit}.sh .m{display:block;font:600 .75rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;opacity:.75;margin-top:8px}
.sg{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:48px;align-items:center;margin:0 0 32px}
.sg figure{margin:0}.sg figure img{display:block;width:100%;border-radius:16px;box-shadow:0 18px 40px rgba(0,0,0,.28)}
.sg blockquote{margin:0 0 22px;font:500 clamp(1.25rem,2.2vw,1.65rem)/1.3 Outfit,sans-serif;color:inherit;padding-left:20px;border-left:4px solid var(--ac)}
.sg p{font-size:.98rem;line-height:1.6;margin:0 0 14px;opacity:.92;color:inherit}
.sc h3{font:600 .72rem Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--ac);margin:0 0 16px;filter:brightness(.92)}
.sb{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:22px;margin:0 0 48px;padding:0;list-style:none;counter-reset:f}
.sb li{counter-increment:f}.sb li img{display:block;width:100%;border-radius:12px;box-shadow:0 10px 26px rgba(0,0,0,.2)}
.sb .no::before{content:counter(f);display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--ac);color:#fff;font:700 .78rem Outfit,sans-serif;margin-right:8px}
.sb b{display:flex;align-items:center;margin:12px 0 4px;font:600 .95rem Outfit,sans-serif;color:inherit}.sb span.d{display:block;font-size:.82rem;line-height:1.45;opacity:.85}
.sb.ap{counter-reset:f 0}.sb.ap .no::before{content:none}
.pl{display:flex;flex-wrap:wrap;gap:18px 24px;margin:0 0 20px}.pl .sw{flex:1 1 150px;max-width:230px}.pl .ch{height:78px;border-radius:14px;border:1px solid rgba(255,255,255,.6);margin-bottom:10px}
.sc.lt .pl .ch{border-color:rgba(0,0,0,.12)}.pl b{display:block;font:600 .9rem Outfit,sans-serif}.pl code{font:500 .72rem Inter,sans-serif;opacity:.7}.pl span{display:block;font-size:.8rem;line-height:1.4;opacity:.85;margin-top:2px}
.ty{margin:0 0 48px;display:grid;gap:8px}.ty p{margin:0;font-size:.88rem;opacity:.92}.ty b{font:600 1rem Outfit,sans-serif}
.mr summary{list-style:none;display:inline-flex;align-items:center;gap:10px;cursor:pointer;font:600 1rem Inter,sans-serif;color:inherit;padding:0 0 3px;border-bottom:3px solid var(--ac)}.mr summary::-webkit-details-marker{display:none}
.mr summary i{width:9px;height:9px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg) translateY(-2px);transition:transform .25s}.mr[open] summary i{transform:rotate(-135deg) translateY(-2px)}
.mr .c{display:none}.mr[open] .c{display:inline}.mr[open] .o{display:none}.mr summary:hover{opacity:.8}.mr summary:focus-visible{outline:2px solid var(--ac);outline-offset:6px}.mb{margin-top:44px}
.bm{margin:56px 4px 0}.bm h2{font-size:1.3rem;margin:0 0 8px;color:var(--ink)}.bm p{margin:0;font-size:.95rem;color:var(--navy);line-height:1.6}
@media(max-width:860px){.bl{grid-template-columns:repeat(2,minmax(0,1fr))}.bl{gap:16px}.sc{padding:34px 22px;border-radius:24px}.sg{grid-template-columns:minmax(0,1fr);gap:28px}.sb{grid-template-columns:repeat(auto-fill,minmax(138px,1fr));gap:16px}}"""

def brands(data, S):
    P = data['page']
    head, menu, foot = chrome(S, 4)
    def im(k, n): return f'assets/brands/{k}_{n:02d}.webp'
    top = (f'<section class="bt"><small>{html.escape(P["tags"])}</small><h1>{t(P["title"])}</h1><p class="ld">{t(P["lead"])}</p><p>{t(P["intro"])}</p></section>')
    idx = ''.join(f'<li><a href="#{b["id"]}"><div class="th"><img loading="lazy" alt="" src="{im(b["key"], b["hero"])}"></div><i>{b["n"]}</i><b>{html.escape(b["name"])}</b><span>{t(b["symbol"])}</span></a></li>' for b in data['brands'])
    index = f'<section class="bi"><h2>{t(P["index"])}</h2><ol class="bl">{idx}</ol></section>'
    scenes = ''
    def lum(c):
        c = c.lstrip('#')
        if len(c) != 6: return 1
        r, g, b_ = (int(c[i:i+2], 16) for i in (0, 2, 4)); return (0.299*r + 0.587*g + 0.114*b_) / 255
    for b in data['brands']:
        light = lum(b['fg']) < .5
        paras = ''.join(f'<p>{t(x)}</p>' for x in b['text'])
        fr = ''.join(f'<li><img loading="lazy" alt="" src="{im(b["key"], f["img"])}"><b><span class="no"></span>{t(f["t"])}</b><span class="d">{t(f["d"])}</span></li>' for f in b['frames'])
        sw = ''.join(f'<div class="sw"><div class="ch" style="background:{s["c"]}"></div><b>{t(s["n"])}</b><code>{s["c"].upper()}</code><span>{t(s["d"])}</span></div>' for s in b['swatches'])
        ty = ''.join(f'<p><b>{html.escape(x[0])}</b> · {t([x[1], x[2]])}</p>' for x in b['type'])
        tyb = f'<h3>{t(P["type"])}</h3><div class="ty">{ty}</div>' if ty else '<div style="height:28px"></div>'
        ap = ''.join(f'<li><img loading="lazy" alt="" src="{im(b["key"], f["img"])}"><b>{t(f["t"])}</b><span class="d">{t(f["d"])}</span></li>' for f in b['apps'])
        apb = f'<h3>{t(P["apps"])}</h3><ol class="sb ap">{ap}</ol>' if ap else ''
        scenes += (f'<section class="sc{" lt" if light else ""}" id="{b["id"]}" style="--bg:{b["bg"]};--fg:{b["fg"]};--ac:{b["ac"]}">'
                   f'<header class="sh"><span class="n">{b["n"]}</span><div><h2>{html.escape(b["name"])}</h2><span class="m">{t(b["kind"])} · {b["year"]}</span></div></header>'
                   f'<div class="sg"><figure><img loading="lazy" alt="{html.escape(b["name"])}" src="{im(b["key"], b["hero"])}"></figure><div><blockquote>{t(b["quote"])}</blockquote>{paras}</div></div>'
                   f'<details class="mr"><summary><span class="o">{t(P["seemore"])}</span><span class="c">{t(P["seeless"])}</span><i></i></summary>'
                   f'<div class="mb"><h3>{t(P["frames"])}</h3><ol class="sb">{fr}</ol><h3>{t(P["palette"])}</h3><div class="pl">{sw}</div>{tyb}{apb}</div></details></section>')
    more = f'<section class="bm"><h2>{t(P["more"])}</h2><p>{t(P["more2"])}</p></section>'
    page = shell('Suelen Magalhães — Brands', head + menu + top + index + scenes + more + foot)
    page = page.replace('</style>', BCSS + '</style>', 1).replace('<body>', '<body class="br">', 1)
    return page.replace('</body>', '<script>document.querySelectorAll("details.mr").forEach(d=>d.addEventListener("toggle",()=>{try{ping()}catch(e){}}))</script></body>', 1)

ICSS = """body.ia{background:#fff}.ia .intro{display:none}
.ih{margin:40px 4px 0;border-radius:28px;padding:clamp(28px,5vw,60px);color:#fff;background:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%)}
.ih small{display:inline-block;border:1px solid #f28db1;border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em}
.ih h1{font:700 clamp(4rem,12vw,9rem)/.9 Outfit,sans-serif;letter-spacing:-.05em;margin:.12em 0 .2em}
.ih .ld{font:500 clamp(1.4rem,2.6vw,2rem)/1.25 Outfit,sans-serif;margin:0 0 14px;max-width:26ch}
.ih p.in{font-size:1.05rem;line-height:1.55;max-width:56ch;margin:0;opacity:.9}
.ist{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:34px}
.ist div{background:rgba(255,255,255,.1);border-radius:18px;padding:16px}.ist b{display:block;font:700 2.6rem/1 Outfit,sans-serif;color:#f28db1}.ist span{display:block;margin-top:6px;font-size:.88rem;line-height:1.35}
.is{margin:64px 4px 0}.is h2{font-size:1.7rem;margin:0 0 6px;color:var(--ink);letter-spacing:-.02em}.is>p.s{margin:0 0 24px;color:var(--navy)}
.pn{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:0;padding:0;list-style:none}
.pn li{position:relative;border:1px solid #e3e1ef;border-radius:20px;padding:18px;background:#fff}
.pn li:not(:last-child):after{content:"→";position:absolute;right:-13px;top:50%;transform:translateY(-50%);z-index:2;background:#fff;color:#f28db1;font-weight:700;width:14px;text-align:center}
.pn b{display:block;font:700 1.15rem Outfit,sans-serif;color:var(--ink)}.pn p{margin:6px 0 12px;font-size:.92rem;line-height:1.4;color:var(--navy)}
.pn em{font-style:normal;font:600 .72rem Inter,sans-serif;letter-spacing:.05em;text-transform:uppercase;border-radius:999px;padding:3px 10px;background:#f2f1f7;color:var(--navy)}
.pn .me em{background:#f28db1;color:#14122b}
.rg{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.rg div{border-radius:20px;padding:20px;background:#f7f6fb}.rg i{font:700 .8rem Inter,sans-serif;color:#f28db1;font-style:normal}.rg b{display:block;margin:6px 0;font:700 1.1rem/1.2 Outfit,sans-serif;color:var(--ink)}.rg p{margin:0;font-size:.93rem;line-height:1.45;color:var(--navy)}
.lp{display:flex;gap:10px;margin:0 0 28px;padding:0;list-style:none;counter-reset:l}
.lp li{flex:1;counter-increment:l;border-radius:999px;padding:12px 16px;background:#235070;color:#fff;font:600 .95rem Outfit,sans-serif;text-align:center}
.lp li:before{content:counter(l) " · ";color:#f28db1}.lp li:last-child{background:#f28db1;color:#14122b}.lp li:last-child:before{color:#14122b}
.ch{max-width:720px;display:flex;flex-direction:column;gap:10px}
.ch h3{margin:0 0 4px;font-size:1rem;color:var(--navy)}
.bu{max-width:80%;border-radius:20px;padding:12px 16px;font-size:.98rem;line-height:1.4}
.bu b{display:block;font:600 .72rem Inter,sans-serif;letter-spacing:.05em;text-transform:uppercase;opacity:.75;margin-bottom:3px}
.bu.me{align-self:flex-end;background:#f28db1;color:#14122b;border-bottom-right-radius:6px}
.bu.ai{align-self:flex-start;background:#235070;color:#fff;border-bottom-left-radius:6px}
.wh{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.wh div{border-radius:20px;padding:22px;background:#f7f6fb}.wh h3{margin:0 0 10px;font:700 1.2rem Outfit,sans-serif;color:var(--ink)}.wh .a{background:#14122b}.wh .a h3,.wh .a li{color:#fff}
.wh ul{margin:0;padding-left:18px}.wh li{margin:6px 0;line-height:1.4;font-size:.95rem;color:var(--navy)}
.ww{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.ww div{border-left:4px solid #f28db1;padding:4px 0 4px 16px}.ww b{display:block;font:700 1.05rem Outfit,sans-serif;color:var(--ink);margin-bottom:6px}.ww p{margin:0;font-size:.93rem;line-height:1.45;color:var(--navy)}
.ib{margin:64px 4px 0;border-radius:24px;padding:clamp(24px,4vw,44px);background:#f7f6fb}.ib h2{margin:0 0 10px;font-size:1.7rem;color:var(--ink)}.ib p{margin:0;max-width:60ch;line-height:1.55;color:var(--navy)}
@media(max-width:900px){.pn{grid-template-columns:1fr}.pn li:not(:last-child):after{content:"↓";right:auto;left:50%;top:auto;bottom:-14px;transform:translateX(-50%)}.rg,.ww{grid-template-columns:1fr}.wh{grid-template-columns:1fr}.lp{flex-direction:column}}
@media(max-width:700px){.ist{grid-template-columns:repeat(2,minmax(0,1fr))}.bu{max-width:92%}}
"""

def ia(data, S):
    P = data['page']
    head, menu, foot = chrome(S, 6)
    stats = ''.join(f'<div><b>{html.escape(a)}</b><span>{t(b)}</span></div>' for a, b in P['stats'])
    top = (f'<section class="ih"><small>{t(P["tag"])}</small><h1>{t(P["title"])}</h1><p class="ld">{t(P["lead"])}</p><p class="in">{t(P["intro"])}</p><div class="ist">{stats}</div></section>')
    def sec(h, s, inner): return f'<section class="is"><h2>{t(h)}</h2>{('<p class="s">'+t(s)+'</p>') if s else '<div style="height:18px"></div>'}{inner}</section>'
    nodes = ''.join(f'<li class="{"me" if n[2][0]=="Me" else ""}"><b>{t(n[0])}</b><p>{t(n[1])}</p><em>{t(n[2])}</em></li>' for n in P['nodes'])
    rules = ''.join(f'<div><i>{i+1:02d}</i><b>{t(r[0])}</b><p>{t(r[1])}</p></div>' for i, r in enumerate(P['rule_items']))
    steps = ''.join(f'<li>{t(s)}</li>' for s in P['steps'])
    bubbles = ''.join(f'<div class="bu {w}"><b>{t(P["me"] if w=="me" else P["claude"])}</b>{t(x)}</div>' for w, x in P['talk'])
    loop = f'<ol class="lp">{steps}</ol><div class="ch"><h3>{t(P["chat"])}</h3>{bubbles}</div>'
    who = (f'<div class="wh"><div><h3>{t(P["me_h"])}</h3><ul>' + ''.join(f'<li>{t(x)}</li>' for x in P['me_l']) + '</ul></div>'
           f'<div class="a"><h3>{t(P["ai_h"])}</h3><ul>' + ''.join(f'<li>{t(x)}</li>' for x in P['ai_l']) + '</ul></div></div>')
    wrong = '<div class="ww">' + ''.join(f'<div><b>{t(w[0])}</b><p>{t(w[1])}</p></div>' for w in P['wrong_items']) + '</div>'
    beyond = f'<section class="ib"><h2>{t(P["beyond"])}</h2><p>{t(P["beyond2"])}</p></section>'
    body = (head + menu + top + sec(P['setup'], P['setup2'], f'<ol class="pn">{nodes}</ol>') + sec(P['rules'], P['rules2'], f'<div class="rg">{rules}</div>')
            + sec(P['loop'], P['loop2'], loop) + sec(P['who'], '', who) + sec(P['wrong'], P['wrong2'], wrong) + beyond + foot)
    page = shell('Suelen Magalhães — AI', body)
    return page.replace('</style>', ICSS + '</style>', 1).replace('<body>', '<body class="ia">', 1)

def main():
    rasterize()
    data = json.loads((R / 'content' / 'cases.json').read_text('utf-8'))
    crops(data)
    S = data['site']; cs = data['cases']
    head, menu, foot = chrome(S, 1)
    hero = ('<section class="shero site"><div><small>' + html.escape(S['tags']) + '</small><h1>' + t(S['title']) + '</h1></div><div class="stats">'
            + ''.join(f'<div><b>{html.escape(a)}</b><span>{t(b)}</span></div>' for a, b in S['stats']) + '</div></section><p class="intro site">' + t(S['intro']) + '</p>')
    body = head + menu + hero + pills(cs, None) + ''.join(case(c, data['labels'], cs, n) for n, c in enumerate(cs)) + foot
    shutil.rmtree(D, ignore_errors=True); D.mkdir()
    (D / 'index.html').write_text(shell('Suelen Magalhães — Product Design', body), 'utf-8')
    pj = R / 'content' / 'pharma.json'
    if pj.exists():
        (D / 'pharma.html').write_text(pharma(json.loads(pj.read_text('utf-8')), S, data['labels']), 'utf-8')
    hj = R / 'content' / 'health.json'
    if hj.exists():
        (D / 'health.html').write_text(health(json.loads(hj.read_text('utf-8')), S), 'utf-8')
    bj = R / 'content' / 'brands.json'
    if bj.exists():
        (D / 'brands.html').write_text(brands(json.loads(bj.read_text('utf-8')), S), 'utf-8')
    ij = R / 'content' / 'ia.json'
    if ij.exists():
        (D / 'ia.html').write_text(ia(json.loads(ij.read_text('utf-8')), S), 'utf-8')
    shutil.copytree(R / 'assets', D / 'assets')

if __name__ == '__main__':
    main()
