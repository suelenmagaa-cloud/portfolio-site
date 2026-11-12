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
                  f'<span class="lb"><span><i>{t(tl["tag"])}</i><b>{t(tl["title"])}</b></span><span class="more">{t(P["more"])} &#8599;</span></span></button>')
        big = ''.join(f'<img alt="" data-s="assets/{k}.webp">' for k in tl['images'])
        dcs += (f'<div class="dc" hidden><div class="in"><div class="pi" style="--pb:{col}">{big}</div><div class="px"><i>{t(tl["tag"])}</i><h3>{t(tl["title"])}</h3>'
                f'<h4>{t(P["constraint"])}</h4><p>{t(tl["constraint"])}</p><h4>{t(P["did"])}</h4><ul>' + ''.join(f'<li>{t(x)}</li>' for x in tl['did'])
                + f'</ul><div class="ct"><button data-a="p">&#8249; {t(P["prev"])}</button><button data-a="n">{t(P["next"])} &#8250;</button><button data-a="x">{t(P["close"])}</button></div></div></div></div>')
    board = f'<div class="bh"><h2>{t(P["board"])}</h2><span>{t(P["hint"])}</span></div><div class="bd">{tiles}</div>'
    dlg = f'<dialog class="pd" aria-label="Detail">{dcs}</dialog>'
    page = shell('Suelen Magalhães — Pharma design', head + menu + top + board + foot)
    page = page.replace('</style>', PCSS + '</style>', 1).replace('<body>', '<body class="ph">', 1)
    return page.replace('</body>', dlg + f'<script>{PJS}</script></body>', 1)

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
    shutil.copytree(R / 'assets', D / 'assets')

if __name__ == '__main__':
    main()
