import json, html, re, shutil, subprocess, pathlib
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

def rich(x):
    en, pt = (s.split('\n\n') for s in x)
    return ''.join('<p>' + re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t([a, p])) + '</p>' for a, p in zip(en, pt))

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
.shero small{font-size:.85rem}.shero h1{font:700 clamp(2.8rem,7vw,4.8rem)/.98 Outfit,sans-serif;letter-spacing:-.04em;margin:.2em 0 0}
.stats{min-width:200px}.stats div{border-top:1px solid rgba(255,255,255,.4);padding:22px 0}.stats div:last-child{padding-bottom:0}.stats div:first-child{border:0}.stats b{font:500 1.5rem/1.1 Outfit,sans-serif;display:block}.stats span{font-size:.75rem;display:block;margin-top:2px}
.intro{font-size:1.15rem;margin:26px 0 16px;text-align:left}
footer.site{margin-top:42px}.bandbar{height:14px;margin:0 calc(50% - 50vw);background:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%)}.ft{display:flex;justify-content:space-between;align-items:center;padding:34px 8px}
.ft h4{font:500 1.6rem Outfit,sans-serif;margin:0;color:var(--ink)}.ft p{margin:.2em 0 0;font-size:.9rem}.btn{border:1px solid #d9d2ff;border-radius:999px;padding:10px 34px;text-decoration:none;color:var(--navy)}
.fl{display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:center;text-align:center;font-size:.85rem;padding:0 8px 24px}.fl a{color:var(--navy);overflow-wrap:anywhere}
html[data-embed] .nx a[href='#top']{display:none}html[data-embed] .site:not(.shero):not(footer){display:none}html[data-embed] .top{justify-content:flex-end}html[data-embed=body] .shero{display:none}html[data-embed],html[data-embed] body{overflow:hidden!important}html[data-embed] [id]{scroll-margin-top:90px}html[data-embed] dialog[open]{position:absolute;top:var(--dy,20px);bottom:auto;left:0;right:0;margin:0 auto;max-height:none}html[data-embed] dialog.hv{height:min(86vh,780px)}html[data-embed] dialog img{max-height:720px}html[data-embed=hero] main>*:not(.shero),html[data-embed=hero] footer,html[data-embed=hero] body>*:not(main){display:none!important}html[data-embed=hero] .shero{margin:0;min-height:100vh;box-sizing:border-box}html[data-embed=hero] body{margin:0;padding:0}html[data-embed=hero] main{max-width:none;padding:0;margin:0;width:100%}html[data-embed=hero],html[data-embed=hero] body{overflow:hidden;height:100%;background:transparent!important}html[data-embed=hero] .shero{background:none!important}html[data-embed=hero] .shero{margin:0!important;padding:20px max(20px,calc((100vw - 900px)/2))!important;border-radius:0;height:100vh;min-height:0!important;overflow:hidden}html[data-embed=hero] .shero h1{font-size:clamp(2.8rem,7vw,4.8rem);line-height:.98}html[data-embed=hero] .stats{gap:0}
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
.g.m{display:none}dialog{border:0;background:none;padding:0}dialog img{max-width:92vw;max-height:90vh}
/* mobile: ajustes gerais */
@media(max-width:700px){
html[data-embed] main{padding-top:0}html[data-embed] .top{margin:0}
.pills{flex-wrap:wrap;justify-content:center;gap:8px;padding:10px 8px;margin:0 -16px}.pills a{flex:1 1 auto;text-align:center;padding:9px 12px!important;font-size:.82rem!important;white-space:nowrap;display:inline-flex;align-items:center;justify-content:center}
.fl{flex-direction:column;align-items:center;gap:6px}
.ft{padding:28px 8px}.btn{padding:10px 28px}
html[data-embed=hero] .shero{height:auto!important;min-height:0!important;overflow:visible!important;padding:22px 20px!important;gap:22px}
html[data-embed=hero] .shero h1{font-size:2.8rem!important;line-height:1}
html[data-embed=hero],html[data-embed=hero] body{overflow:visible!important;height:auto!important}
.stats{min-width:0;width:100%}.stats div{padding:14px 0}
}
@media(max-width:560px){
body.ab .ac li a{flex-wrap:wrap;justify-content:flex-start;gap:6px 10px;padding:14px 16px}body.ab .ac li b{margin-right:0}body.ab .ac li span{flex:1 0 100%;min-width:0;font-size:.98rem;overflow-wrap:anywhere;word-break:normal}
.ac{padding:26px 22px}
}
/* padrão de cabeçalho: pharma, health, brands, about */
body.ph .pt,body.hl .ht,body.br .bt,body.ab .at{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px 0;align-items:center;margin:48px 4px 0;max-width:none}
body.ph .pt>div,body.hl .ht>div,body.ab .at>div{display:contents}
body.ph .pt small,body.hl .ht small{grid-column:1/-1;justify-self:start;margin:0}
body.br .bt,body.ab .at{padding-top:43px}
body.ph .pt h1,body.hl .ht h1,body.br .bt h1,body.ab .at h1{font:700 clamp(2.8rem,7vw,4.8rem)/.95 Outfit,sans-serif;letter-spacing:-.04em;color:var(--ink);margin:0;min-height:1.9em;display:flex;align-items:center;align-self:start}
body.ph .pt>p,body.hl .ht>p,body.ab .at>p,body.br .bt .br p,body.br .bt .ld{font:400 1.1rem/1.5 Inter,sans-serif;color:var(--navy);margin:0;max-width:none;padding:0 0 0 36px;border:0;border-image:none}
body.br .bt .br{padding-left:0}body.br .bt .br p+p{margin-top:12px}
body.ph .pf,body.hl .hg,body.ab .as{margin:44px 4px 0;padding-top:26px;border-top:3px solid;border-image:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%) 1}
body.br .bt{padding-bottom:44px;border-width:0 0 3px;border-style:solid;border-image:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%) 1}body.br .bt+.pz{margin-top:36px}
@media(max-width:700px){body.ph .pt,body.hl .ht,body.br .bt,body.ab .at{grid-template-columns:minmax(0,1fr);margin-top:16px}body.br .bt,body.ab .at{padding-top:0}body.ph .pt h1,body.hl .ht h1,body.br .bt h1,body.ab .at h1{min-height:0}body.ph .pt>p,body.hl .ht>p,body.ab .at>p,body.br .bt .br p,body.br .bt .ld{padding-left:0!important}}
"""
JS = """const D=document.documentElement,ping=()=>parent.postMessage({h:D.scrollHeight},'*'),
set=l=>{D.dataset.lang=l;ping()};
let sv='';try{sv=localStorage.sl||''}catch(e){}
set(new URLSearchParams(location.search).get('lang')||sv||(navigator.language.startsWith('pt')?'pt':'en'));
addEventListener('storage',e=>{if(e.key=='sl'&&e.newValue)set(e.newValue)});
document.querySelectorAll('.bar button').forEach(b=>b.onclick=()=>{set(b.dataset.l);try{localStorage.sl=b.dataset.l}catch(e){}});
addEventListener('message',e=>{if(e.data&&e.data.lang)set(String(e.data.lang).slice(0,2))});
addEventListener('load',ping);addEventListener('resize',ping);
document.querySelectorAll('details').forEach(d=>d.ontoggle=ping);
{var q=new URLSearchParams(location.search);if(q.has('embed'))D.dataset.embed=q.get('embed')||'body';}
(function(){var c=document.createElement('div');c.className='cc';c.setAttribute('role','dialog');var pt=()=>D.dataset.lang=='pt';
c.innerHTML='<button class="x" aria-label="Fechar / Close">&times;</button><b></b><a target="_top" rel="noopener"></a><button class="cp"></button><small></small>';document.body.appendChild(c);
var em=c.querySelector('b'),op=c.querySelector('a'),cp=c.querySelector('.cp'),sm=c.querySelector('small'),cur='';
var close=()=>{c.classList.remove('on');ping()};
c.querySelector('.x').onclick=close;
function copy(t){try{if(navigator.clipboard&&window.isSecureContext)return navigator.clipboard.writeText(t).then(()=>1,()=>old(t))}catch(e){}return Promise.resolve(old(t))}
function old(t){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;top:0;left:0;opacity:0';document.body.appendChild(a);a.select();a.setSelectionRange(0,t.length);var ok=0;try{ok=document.execCommand('copy')}catch(e){}a.remove();return ok}
cp.onclick=()=>{copy(cur).then(ok=>{sm.textContent=ok?(pt()?'E-mail copiado ✓':'Email copied ✓'):(pt()?'Selecione e copie o e-mail acima':'Select and copy the email above')})};
document.addEventListener('click',e=>{var a=e.target.closest('a[href^="mailto:"]');if(a&&!c.contains(a)){e.preventDefault();cur=a.getAttribute('href').slice(7);em.textContent=cur;op.href='mailto:'+cur;op.textContent=pt()?'Abrir meu app de e-mail':'Open my email app';cp.textContent=pt()?'Copiar e-mail':'Copy email';sm.textContent='';var r=a.getBoundingClientRect(),w=Math.min(320,innerWidth-24);c.classList.add('on');var h=c.offsetHeight,y=r.top+scrollY-h-10;if(y<scrollY+8)y=r.bottom+scrollY+10;var x=Math.max(12,Math.min(r.left+scrollX,innerWidth-w-12));c.style.top=y+'px';c.style.left=x+'px';ping();return}
if(c.classList.contains('on')&&!c.contains(e.target))close()});
document.addEventListener('keydown',e=>{if(e.key=='Escape')close()})})();

if(D.dataset.embed){let cy=0;addEventListener('click',e=>{cy=e.clientY+scrollY},true);const o=HTMLDialogElement.prototype.showModal;HTMLDialogElement.prototype.showModal=function(){this.style.setProperty('--dy',Math.max(20,cy-260)+'px');o.call(this);setTimeout(()=>{this.scrollIntoView({block:'center'});parent.postMessage({goto:this.getBoundingClientRect().top+scrollY},'*')},30)}}
if(D.dataset.embed)document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(!a||a.getAttribute('href').length<2)return;const t=document.getElementById(a.getAttribute('href').slice(1));if(!t)return;e.preventDefault();t.scrollIntoView({block:'start'});parent.postMessage({goto:t.getBoundingClientRect().top+scrollY},'*')});
document.querySelectorAll('.car').forEach(c=>{const tr=c.querySelector('.track'),ds=c.nextElementSibling;ds.innerHTML='<i></i>'.repeat(tr.children.length);
const A=c.querySelector('.l'),B=c.querySelector('.r');const dot=()=>{const k=Math.round(tr.scrollLeft/tr.clientWidth),n=tr.children.length;[...ds.children].forEach((d,j)=>d.className=j==k?'on':'');A.style.visibility=k<=0?'hidden':'visible';B.style.visibility=k>=n-1?'hidden':'visible'};tr.onscroll=dot;dot();
c.querySelector('.l').onclick=()=>tr.scrollBy({left:-tr.clientWidth,behavior:'smooth'});c.querySelector('.r').onclick=()=>tr.scrollBy({left:tr.clientWidth,behavior:'smooth'})});
const pl=[...document.querySelectorAll('.pills a')],arts=[...document.querySelectorAll('article')];
const mark=()=>{let cur=null;arts.forEach(a=>{const r=a.getBoundingClientRect();if(r.top<innerHeight*.4&&r.bottom>innerHeight*.4)cur=a.id});pl.forEach(l=>{if(l.getAttribute('href')=='#'+cur)l.setAttribute('aria-current','true');else l.removeAttribute('aria-current')})};
const setCur=id=>pl.forEach(l=>{if(l.getAttribute('href')=='#'+id)l.setAttribute('aria-current','true');else l.removeAttribute('aria-current')});
if(D.dataset.embed&&arts.length){setCur(arts[0].id);const vis={};const io=new IntersectionObserver(es=>{es.forEach(e=>{vis[e.target.id]=e.intersectionRect.height});let b=arts[0].id,m=-1;arts.forEach(a=>{if((vis[a.id]||0)>m){m=vis[a.id]||0;b=a.id}});setCur(b)},{threshold:Array.from({length:21},(_,i)=>i/20)});arts.forEach(a=>io.observe(a))}
else{addEventListener('scroll',mark,{passive:true});mark()}
const dl=document.querySelector('dialog');
document.addEventListener('click',e=>{if(e.target.matches('.g img,.im img')){dl.querySelector('img').src=e.target.src;dl.showModal()}else if(e.target===dl||e.target.closest('dialog'))dl.close()});"""

def chrome(S, cur):
    bar = '<div class="bar"><button data-l="en">EN</button><button data-l="pt">PT</button></div>'
    head = '<div class="top"><a class="brand site" href="#top"><img class="logo" src="assets/logo.png" alt=""><span><b>SUELEN MAGALHÃES</b><i>|</i>DESIGN</span></a>' + bar + '</div>'
    menu = '<nav class="menu site">' + ''.join(f'<a href="{html.escape(u)}"' + (' aria-current="page"' if i == cur else '') + f'>{t([en, pt])}</a>' for i, (en, pt, u) in enumerate(S['menu'])) + '</nav>'
    foot = (f'<footer class="site"><div class="bandbar"></div><div class="ft"><div><h4>{t(S["cta"])}</h4><p>{t(S["cta2"])}</p></div>'
            f'<a class="btn" href="mailto:{S["email"]}">{t(S["btn"])}</a></div><div class="fl"><a href="mailto:{S["email"]}">{S["email"]}</a>'
            f'<a href="{S["linkedin"]}" target="_blank" rel="noopener">LinkedIn</a><span>© 2026 Suelen Magalhães</span></div></footer>')
    return head, menu, foot

def shell(title, body):
    return (f'<!doctype html><html data-lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@500;700&display=swap"><style>{CSS}{CCSS}</style></head><body><main id="top">{body}</main><dialog><img alt=""></dialog><script>{JS}</script></body></html>')

def pimg(k, alt=''):
    return f'<img loading="lazy" alt="{html.escape(alt)}" src="assets/{k}.webp">' if (R / 'assets' / f'{k}.webp').exists() else ''

CCSS = """.cc{position:absolute;z-index:99;width:min(320px,calc(100vw - 24px));background:#fff;border:1px solid #d9d2ff;border-radius:18px;box-shadow:0 12px 36px rgba(20,18,43,.22);padding:18px;display:none;font-family:Inter,sans-serif}.cc.on{display:block}.cc b{display:block;color:var(--ink);font-size:1.02rem;overflow-wrap:anywhere;margin:0 0 12px}.cc a,.cc button{display:block;width:100%;box-sizing:border-box;text-align:center;border-radius:999px;padding:12px 16px;font:600 .95rem Inter,sans-serif;margin-top:8px;cursor:pointer;text-decoration:none;min-height:44px}.cc a{background:linear-gradient(135deg,var(--pink),var(--violet));color:#fff;border:0}.cc button{background:#fff;color:var(--navy);border:1px solid var(--pink)}.cc .x{position:absolute;top:4px;right:6px;width:44px;height:44px;margin:0;border:0;font-size:1.5rem;background:none;padding:0}.cc small{display:block;text-align:center;color:var(--navy);margin-top:8px;min-height:1.2em}a,button,summary{touch-action:manipulation;-webkit-tap-highlight-color:rgba(242,141,177,.25)}
@media(pointer:coarse),(max-width:700px){.bar button{min-height:38px;padding:6px 14px;line-height:1}.menu a{display:inline-block;padding:12px 8px}summary{min-height:44px;display:flex;align-items:center}.shero a,.nx a{min-height:44px;display:inline-flex;align-items:center}dialog button{min-height:44px}.ar,.ar2{min-width:44px;min-height:44px}.fl a{padding:10px 8px}.hb,.pb,.pills a{min-height:44px;box-sizing:border-box}.btn{display:inline-block;min-height:44px;box-sizing:border-box}}
"""

PCSS = """body.ph{background:#fff}.ph .intro{display:none}
.pt{display:grid;grid-template-columns:1.2fr 1fr;gap:20px 56px;align-items:end;margin:44px 4px 0}
.pt small{display:inline-block;border:1px solid var(--pink);border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em;color:var(--navy)}
.pt h1{font:700 clamp(3rem,8vw,6.2rem)/.95 Outfit,sans-serif;letter-spacing:-.04em;color:var(--ink);margin:.2em 0 0}
.pt p{font-size:1.1rem;margin:0;color:var(--navy)}.pf{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px 28px;margin:34px 4px 0;padding-top:24px;border-top:3px solid;border-image:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%) 1}
.pf b{font-size:.68em;text-transform:uppercase;letter-spacing:.1em;color:var(--pink)}.pf p{margin:.1em 0;font-size:.85rem}
.bh{margin:72px 4px 26px}.bh h2{font:700 clamp(2rem,4.6vw,3.1rem)/1.05 Outfit,sans-serif;margin:0;color:var(--ink);letter-spacing:-.03em;padding-left:18px;border-left:6px solid var(--pink)}.bh>span{display:block;margin:12px 0 0 24px;font-size:1rem}
.bd{display:grid;grid-template-columns:repeat(12,1fr);grid-auto-rows:150px;gap:44px 36px}
.tl{width:100%;align-items:stretch;min-width:0;border:0;padding:0;background:none;cursor:pointer;text-align:left;font:inherit;color:var(--ink);display:flex;flex-direction:column;gap:14px;min-height:0}
.tl .ims{position:relative;flex:1;min-height:0;min-width:0;border-radius:6px;overflow:hidden;display:flex;transition:transform .25s}
.tl:hover .ims,.tl:focus-visible .ims{transform:translateY(-4px)}.tl:focus-visible{outline:2px solid var(--violet);outline-offset:6px}
.tl img{flex:1 1 0;min-width:0;height:100%;display:block}
.tl.fit .ims img{object-fit:contain;-webkit-mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent),linear-gradient(180deg,transparent,#000 7%,#000 93%,transparent);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent),linear-gradient(180deg,transparent,#000 7%,#000 93%,transparent);mask-composite:intersect}
.tl.plain .ims{background:#e8e5f2;border-radius:10px}.tl.plain img{object-fit:cover}.tl.plain.top img{object-position:top;border-right:6px solid #e8e5f2}.tl.plain.top .ims{-webkit-mask-image:linear-gradient(180deg,#000 82%,transparent);mask-image:linear-gradient(180deg,#000 82%,transparent)}
.tl .lb{display:flex;align-items:flex-end;justify-content:space-between;gap:16px}
.tl .lb i{display:block;font:600 .64rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--pink);font-style:normal;margin-bottom:2px}.tl .lb b{font:500 1.15rem/1.2 Outfit,sans-serif}
.tl .more{flex:none;font:600 .82rem Inter,sans-serif;color:var(--navy);border-bottom:2px solid var(--pink);padding-bottom:1px;white-space:nowrap;transition:color .2s}.tl:hover .more{color:var(--violet)}
dialog.pd{border:0;border-radius:18px;padding:0;width:min(1040px,94vw);max-height:90vh;color:var(--navy);background:#fff}dialog.pd::backdrop{background:rgba(20,18,43,.6)}
.pd .in{display:grid;grid-template-columns:1.35fr 1fr;max-height:90vh}.pd .pi{background:var(--pb,#eeeaf8);padding:16px;overflow:auto;display:flex;flex-direction:column;gap:12px;align-items:center;justify-content:center}.pd .pi img{max-width:100%;height:auto;display:block;border-radius:6px}
.pd .px{padding:30px 30px 22px;overflow:auto}.pd .px i{font:600 .68rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--pink);font-style:normal}
.pd h3{font:700 1.7rem/1.1 Outfit,sans-serif;color:var(--ink);margin:.3em 0 .6em;letter-spacing:-.02em}.pd h4{font:600 .7rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--violet);margin:1.2em 0 .3em}
.pd ul{padding-left:1.1em;margin:0}.pd li{margin:.35em 0}.pd li::marker{color:var(--pink)}.pd p{margin:0 0 .7em}
.pd .ct{position:sticky;bottom:-22px;display:flex;gap:8px;margin-top:22px;padding:12px 0 0;background:#fff}.pd .ct button{border:1px solid var(--pink);background:#fff;color:var(--navy);border-radius:999px;padding:7px 18px;cursor:pointer;font:600 .85rem Inter,sans-serif}.pd .ct button:first-child{margin-right:auto}
@media(max-width:700px){.pd .in{grid-template-columns:minmax(0,1fr)!important}.pd .px{min-width:0;padding:24px 22px 18px;overflow-wrap:anywhere}.pd .ct{flex-wrap:nowrap;gap:6px}.pd .ct button{flex:1 1 0;min-width:0;padding:8px 6px;white-space:nowrap;text-align:center;margin:0!important}.pt{grid-template-columns:1fr;margin-top:28px}.bd{grid-template-columns:1fr;grid-auto-rows:300px;gap:36px}.tl{grid-area:auto!important}.tl.top img:nth-child(n+3){display:none}.pd .in{grid-template-columns:1fr;overflow:auto}.pd .pi{max-height:44vh}.pd .px{overflow:visible}}"""
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
                f'<h4>{t(P["constraint"])}</h4>' + ''.join(f'<p>{t(x)}</p>' for x in tl['cons']) + (f'<h4>{t(P["did"])}</h4>' + ''.join(f'<p>{t(x)}</p>' for x in tl['did']) if tl['did'] else '')
                + f'<div class="ct"><button data-a="p">&#8249; {t(P["prev"])}</button><button data-a="n">{t(P["next"])} &#8250;</button><button data-a="x">{t(P["close"])}</button></div></div></div></div>')
    board = f'<div class="bh"><h2>{t(P["board"])}</h2><span>{t(P["hint"])}</span></div><div class="bd">{tiles}</div>'
    dlg = f'<dialog class="pd" aria-label="Detail">{dcs}</dialog>'
    page = shell('Suelen Magalhães — Pharma design', head + menu + top + board + foot)
    page = page.replace('</style>', PCSS + '</style>', 1).replace('<body>', '<body class="ph">', 1)
    return page.replace('</body>', dlg + f'<script>{PJS}</script></body>', 1)

HCSS = """body.hl{background:#fff}.hl .intro{display:none}
.ht{margin:48px 4px 0;max-width:980px}.ht small{display:inline-block;border:1px solid var(--pink);border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em;color:var(--navy)}
.ht{display:grid;grid-template-columns:1fr 1fr;gap:20px 0;align-items:end;max-width:none}.ht h1{font:700 clamp(3rem,8vw,6.2rem)/.95 Outfit,sans-serif;letter-spacing:-.04em;color:var(--ink);margin:.2em 0 0}.ht p{font-size:1.1rem;line-height:1.5;color:var(--navy);margin:0;max-width:none;padding-left:36px}@media(max-width:700px){.ht{grid-template-columns:1fr;margin-top:28px}.ht p{padding-left:0}}
.hg{display:grid;grid-template-columns:1fr 1fr;margin:44px 4px 0;border-top:3px solid;border-image:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%) 1}
.hg>div{padding:26px 36px 8px 0}.hg>div+div{padding-left:36px;position:relative}.hg>div+div::before{content:"";position:absolute;left:0;top:30px;bottom:6px;width:1px;background:#e4e0ee}.hg b{font:600 .7rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--pink)}.hg p{font:500 1.35rem/1.3 Outfit,sans-serif;color:var(--ink);margin:.35em 0 0}
.hp{margin:72px 4px 0}.hp h2,.hc h2{font-size:1.7rem;margin:0 0 22px;color:var(--ink);letter-spacing:-.02em}
.tl{max-width:900px;margin:34px auto 0}
.tls{position:relative;display:flex;justify-content:space-around;margin-bottom:46px}
.tst{all:unset;box-sizing:border-box;position:relative;flex:1 1 0;cursor:pointer;text-align:center;display:block}
.tst:focus-visible .ti.d{outline:2px solid var(--pink);outline-offset:6px;border-radius:8px}
.ti{display:block;width:60px;height:60px;margin:0 auto 30px;fill:none;stroke-width:1.2;stroke-linecap:round;stroke-linejoin:round;transition:opacity .25s}
.ti.d{stroke:#a9a5c2}.ti.a{position:absolute;top:0;left:50%;margin:0 0 0 -30px;stroke:url(#ig2);opacity:0}
.tst.on .ti.d{opacity:0}.tst.on .ti.a{opacity:1}
.tt{display:block;position:relative;padding-top:28px;border-top:3px solid #e4e0ee;font:500 .95rem/1.5 Outfit,Inter,sans-serif;color:var(--navy)}
.tst.on .tt{font-weight:700;color:var(--ink)}
.tt::before,.tt::after{content:"";position:absolute;left:50%;border-radius:50%}
.tt::before{top:-8px;width:11px;height:11px;margin-left:-5.5px;border:2px solid #e4e0ee;background:#fff;z-index:5;box-sizing:content-box;transform:translateY(0)}
.tt::after{top:-14px;width:25px;height:25px;margin-left:-12.5px;background:linear-gradient(122deg,#f28db1,#e0568f 45%,#235070);opacity:.35;transform:scale(0);transition:transform .25s}
.tst.on .tt::before{background:#e0568f;border-color:#e0568f}.tst.on .tt::after{transform:scale(1)}
.tmk{position:absolute;left:0;top:0;height:3px;width:0;background:linear-gradient(90deg,#1c1140 0%,#235070 40%,#f28db1 140%);transition:transform .35s cubic-bezier(0,0,0,1.2),width .35s;pointer-events:none}
.tlc{position:relative;isolation:isolate;max-width:none;margin:0;border-radius:10px;height:var(--th,200px);transition:height .3s}
.tlc::after{content:"";position:absolute;inset:0;z-index:-1;border-radius:10px;background:#fff}.tlc::before{content:"";position:absolute;inset:0;z-index:-2;border-radius:10px;background:linear-gradient(122deg,#f28db1 0%,#e0568f 38%,#235070 100%);opacity:.6;filter:blur(20px);transform:translateY(20px)}
.tsl{position:absolute;left:0;top:0;width:100%;box-sizing:border-box;padding:40px 44px;opacity:0;visibility:hidden}.tsl.on{opacity:1;visibility:visible;transition:opacity .25s}
.tsl h3{margin:0 0 .5em;font:700 1.5rem/1.15 Outfit,sans-serif;color:#e0568f}.tsl p{margin:0;line-height:1.7;color:var(--navy)}
@media(max-width:700px){.tls{display:grid;grid-template-columns:repeat(5,1fr);margin-bottom:28px}.ti{width:40px;height:40px;margin-bottom:0}.ti.a{margin-left:-20px}.tt{display:none}.tmk{display:none}.tst.on::after{content:"";display:block;height:3px;margin-top:12px;background:linear-gradient(90deg,#235070,#f28db1)}.tsl{padding:28px 22px}}
.hs{display:flex;gap:0;height:300px;margin:0;padding:0;list-style:none;counter-reset:s}
.hs li:nth-child(1){--c:#1c1140;--n:#1f3a66;--tc:#fff}.hs li:nth-child(2){--c:#3a7aa8;--n:#4a6cb0;--tc:#fff}.hs li:nth-child(3){--c:#6e72b8;--n:#a070b8;--tc:#fff}.hs li:nth-child(4){--c:#d174a6;--n:#a8467f;--tc:#fff}.hs li:nth-child(5){--c:#f28db1;--n:#d46a98;--tc:#14122b}
.hs li{counter-increment:s;position:relative;flex:1 1 0;min-width:0;border-radius:24px;overflow:hidden;cursor:pointer;background:var(--c);color:var(--tc);transition:flex .8s cubic-bezier(.2,.9,.2,1),margin .8s cubic-bezier(.2,.9,.2,1),padding .8s cubic-bezier(.2,.9,.2,1),background .5s;display:flex;flex-direction:column;justify-content:flex-end;padding:0}
.hs li::before{display:none}
.hs li>.vt{position:absolute;left:calc(18px + var(--t,0px));bottom:20px;writing-mode:vertical-rl;transform:rotate(180deg);font:600 1rem Outfit,sans-serif;color:var(--tc);white-space:nowrap;font-style:normal;transition:opacity .35s}
.hs li>b{display:block;font:700 1.45rem/1.1 Outfit,sans-serif;color:var(--tc);margin:0 0 .35em;opacity:0;transform:translateY(14px);transition:opacity .4s,transform .6s}
.hs li>span{display:block;font-size:.95rem;line-height:1.5;color:var(--tc);opacity:0;transform:translateY(14px);transition:opacity .4s,transform .6s}
.hs li>b,.hs li>span{margin-left:0;padding:0 26px}.hs li>span{padding-bottom:30px}
.hs li.on{flex:3.6 1 0;background:linear-gradient(135deg,var(--c),var(--n))}
.hs li.on>.vt{opacity:0}
.hs li.on>b,.hs li.on>span{opacity:1;transform:none;transition-delay:.25s}.hs li.on>span{opacity:.95}
.hs li.on:not(:last-child){clip-path:polygon(0 0,calc(100% - 28px) 0,100% 50%,calc(100% - 28px) 100%,0 100%);padding-right:28px}.hs li+li{margin-left:-24px;padding-left:24px;--t:24px}.hs li+li.on{margin-left:-24px;padding-left:0;--t:0px}.hs li.on+li{margin-left:-40px;padding-left:40px;--t:40px}.hs li:nth-child(1){z-index:5}.hs li:nth-child(2){z-index:4}.hs li:nth-child(3){z-index:3}.hs li:nth-child(4){z-index:2}.hs li:nth-child(5){z-index:1}.hs li.on{z-index:9!important}
.hs li .ic{position:absolute;top:24px;left:calc(50% + var(--t,0px)/2);margin-left:-17px;width:34px;height:34px;fill:none;stroke:url(#ig);stroke-width:1.4;stroke-linecap:round;stroke-linejoin:round;transition:all .7s cubic-bezier(.2,.9,.2,1)}.hs li:nth-child(4) .ic{stroke:url(#igw)}.hs li:last-child .ic{stroke:url(#igd)}
.hs li.on .ic{left:30px;margin-left:0;top:30px;width:92px;height:92px;stroke-width:1.1}
.hs li::after{content:"";position:absolute;left:0;bottom:0;height:5px;width:0;background:var(--tc);opacity:.75}
.hs li.on::after{animation:hsp 3.4s linear forwards}@keyframes hsp{to{width:100%}}
@media(prefers-reduced-motion:reduce){.hs li,.hs li::before,.hs li>b,.hs li>span{transition:none}.hs li.on::after{animation:none;width:100%}}

.hc{margin:88px 4px 0}.hc>p{margin:-12px 0 36px;font-size:.95rem}.hcc{margin-top:120px}.hp h2.x{}.hcc h2{font:700 clamp(2.2rem,5vw,3.4rem)/1.05 Outfit,sans-serif;letter-spacing:-.03em;margin:0 0 16px;padding-left:18px;border-left:6px solid var(--pink)}.hcc>p{margin:0 0 40px 24px;font-size:1rem}
.bk{--a:#c9806a;--t:#fbf1ed;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:40px;align-items:center;border-radius:24px;padding:34px 40px;margin:0 0 26px!important;background:linear-gradient(var(--a),var(--a)) top/100% 7px no-repeat,var(--t)}
.bk.rev{grid-template-columns:minmax(0,1.05fr) minmax(0,1fr)}.bk.rev .fan{order:2}
.fan{position:relative;aspect-ratio:1/1.12;max-width:290px;width:100%;margin:0 auto;border:0;padding:0;background:none;cursor:pointer}
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
.if{background:linear-gradient(135deg,#1c1140 0%,#235070 70%,#4a2c6e 130%);color:#fff;border-radius:24px;padding:34px 40px;margin:0 0 26px;display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.5fr);gap:36px;align-items:center}
.if .k{font:600 .68rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--pink)}.if h3{font:700 clamp(1.5rem,2.6vw,2.15rem)/1.12 Outfit,sans-serif;letter-spacing:-.02em;margin:.3em 0 .5em;color:#fff}.if p{font-size:1rem;line-height:1.55;margin:0 0 14px;color:#e6e2f5}.if .sr{font-size:.8rem;opacity:.75}
.if .hb{color:#fff;border-bottom-color:var(--pink)}.if .hb:hover{color:var(--pink)}
.ifr{display:flex;gap:20px;justify-content:center}.ifr .ifs{flex:0 1 300px;min-width:0;height:460px;overflow-y:auto;overflow-x:hidden;background:#14122b;border-radius:14px;scrollbar-width:thin;box-shadow:0 18px 40px rgba(0,0,0,.35)}.ifr img{display:block;width:100%;height:auto}
.cw{align-items:stretch;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:22px;margin:0 0 26px}
.cs{margin:0!important;--a:#ec6e57;--t:#fdf0ec;background:var(--t);border-radius:24px;overflow:hidden;display:flex;flex-direction:column;grid-column:span 6;background:linear-gradient(var(--a),var(--a)) top/100% 7px no-repeat,var(--t)}
.cs.c1{grid-column:span 8}.cs.c2{grid-column:span 4}.cs.c3{grid-column:span 12;flex-direction:row}
.cs .ci{margin:7px 0 0;line-height:0;background:#fff}.cs .ci img{display:block;width:100%;height:100%;object-fit:cover}.cs.c2 .ci{position:relative;flex:1;min-height:220px}.cs.c2 .ci img{position:absolute;inset:0}.cs.c3 .ci{flex:1.5;min-width:0}
.cs .ct{padding:22px 28px 24px}.cs.c1 .ci{height:290px}.cs.c1 .ci img{object-position:center 35%}.cs.c3 .ct{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;margin-top:7px}
.cs .k{font:600 .68rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--a);filter:brightness(.8)}
.cs h3{font:700 clamp(1.4rem,2.3vw,1.9rem)/1.12 Outfit,sans-serif;color:var(--ink);letter-spacing:-.02em;margin:.3em 0 .45em}.cs h3 small{font:600 .8rem Inter,sans-serif;color:var(--navy);opacity:.6;margin-left:8px;letter-spacing:0}
.cs p{font-size:.95rem;line-height:1.55;color:var(--navy);margin:0 0 16px}.cs .lg{height:38px;width:auto;max-width:100%;object-fit:contain;align-self:flex-start;display:block;margin:0 0 14px}
.cs .tp{margin:0 0 18px;padding:0;list-style:none;display:grid;gap:6px;font-size:.84rem;color:var(--navy)}.cs .tp li{padding-left:16px;position:relative}.cs .tp li::before{content:"";position:absolute;left:0;top:.55em;width:6px;height:6px;border-radius:50%;background:var(--a)}
.cs .chips{margin:0 0 20px}
@media(max-width:860px){.cs.c1 .ci{height:auto}.cw{grid-template-columns:minmax(0,1fr)}.cs,.cs.c1,.cs.c2,.cs.c3{grid-column:auto;flex-direction:column;border-radius:22px}.cs .ct{padding:26px 22px 30px}.cs.c3 .ct{margin-top:0}.cs.c2 .ci{flex:none;min-height:0}.cs.c2 .ci img{position:static}}
dialog.hv{border:0;border-radius:18px;padding:0;width:min(1000px,96vw);height:min(92vh,980px);background:#14122b;color:#fff;overflow:hidden}dialog.hv::backdrop{background:rgba(20,18,43,.72)}
dialog.hv[open]{display:flex;flex-direction:column}.hv .hh{display:flex;align-items:center;gap:14px;padding:14px 20px;border-bottom:1px solid rgba(255,255,255,.12)}.hv .hh b{flex:1;font:600 .95rem Outfit,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hv .hh span{font:600 .8rem Inter,sans-serif;opacity:.7}
.hv button{font:600 .85rem Inter,sans-serif;color:#fff;background:none;border:1px solid rgba(255,255,255,.4);border-radius:999px;padding:6px 16px;cursor:pointer}.hv button:hover{border-color:var(--pink);color:var(--pink)}
.hv .st{flex:1;min-height:0;overflow:auto;display:flex;justify-content:center;padding:20px;background:#2a2740}.hv .st img{display:block;max-width:100%;height:auto;align-self:flex-start;box-shadow:0 10px 30px rgba(0,0,0,.4)}.hv.pg .st{align-items:center}.hv.pg .st img{max-height:100%;width:auto;align-self:center}
.hv .th{display:flex;gap:8px;padding:12px 20px;overflow-x:auto;border-top:1px solid rgba(255,255,255,.12)}.hv .th img{height:64px;width:auto;border-radius:3px;opacity:.5;cursor:pointer;flex:none;border:2px solid transparent}.hv .th img.on{opacity:1;border-color:var(--pink)}
.hv .nv{display:flex;gap:8px}.hv .ar2{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:48px;height:48px;padding:0;border-radius:50%;background:rgba(20,18,43,.78);border:1px solid rgba(255,255,255,.45);font:400 1.9rem/1 Inter,sans-serif;display:grid;place-items:center;padding-bottom:4px;box-shadow:0 6px 18px rgba(0,0,0,.35)}.hv .ar2.l{left:16px}.hv .ar2.r{right:16px}
@media(max-width:860px){.hs li.on:not(:last-child){clip-path:none;padding-right:0}.hs li+li,.hs li+li.on,.hs li.on+li{margin-left:0;padding-left:0;--t:0px}.hs li{z-index:auto!important}.hs li .ic,.hs li.on .ic{top:18px;left:24px;margin-left:0;width:40px;height:40px}.hg>div+div::before{display:none}.hg{grid-template-columns:1fr}.hg>div,.hg>div+div{padding:20px 0 6px;border-left:0}.hs{flex-direction:column;height:auto;gap:10px}.hs li{flex:none;max-height:76px;justify-content:flex-start;transition:max-height .7s cubic-bezier(.2,.9,.2,1),background .5s}.hs li.on{flex:none;max-height:300px}.hs li::before{top:14px;font-size:2.4rem}.hs li>.vt{display:none}.hs li>b{opacity:1;transform:none;padding:26px 18px 6px 96px;font-size:1.15rem;margin:0;color:var(--tc)}.hs li.on>b{color:var(--tc);padding-top:26px}.hs li>span{padding:0 22px 22px 96px;max-height:0;overflow:hidden;opacity:0}.hs li.on>span{max-height:200px;opacity:.95}.hs li.on::before{transform:none}
.bk,.bk.rev,.if{grid-template-columns:minmax(0,1fr);padding:30px 22px;gap:30px;border-radius:22px}.bk.rev .fan{order:0}.fan{max-width:340px}.ifr{gap:12px}.ifr{align-items:flex-start}.ifr .ifs{height:auto;max-height:560px;flex:1 1 0}.hv .th img{height:48px}}"""
HJS = """(()=>{const tl=document.querySelector('.tl');if(tl){const st=[...tl.querySelectorAll('.tst')],sl=[...tl.querySelectorAll('.tsl')],bx=tl.querySelector('.tlc'),mk=tl.querySelector('.tmk'),sp=tl.querySelector('.tls');let a=0;
const lay=()=>{const c=st[a],tt=c.querySelector('.tt'),r=sp.getBoundingClientRect(),cr=c.getBoundingClientRect(),tr=tt.getBoundingClientRect();mk.style.width=cr.width+'px';mk.style.transform='translate('+(cr.left-r.left)+'px,'+(tr.top-r.top)+'px)';bx.style.setProperty('--th',sl[a].offsetHeight+'px')};
const go=i=>{a=i;st.forEach((x,j)=>x.classList.toggle('on',j==i));sl.forEach((x,j)=>x.classList.toggle('on',j==i));lay();setTimeout(ping,350)};
let tm;const auto=()=>{clearTimeout(tm);if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;tm=setTimeout(()=>{go((a+1)%st.length);auto()},15000)};st.forEach((x,i)=>x.addEventListener('click',()=>{go(i);auto()}));addEventListener('resize',lay);addEventListener('load',lay);if(window.ResizeObserver){const ro=new ResizeObserver(()=>{lay();ping()});sl.forEach(x=>ro.observe(x));ro.observe(sp)}if(document.fonts)document.fonts.ready.then(lay);new MutationObserver(()=>setTimeout(lay,50)).observe(document.documentElement,{attributes:true,attributeFilter:['data-lang']});go(0);auto()}
const hs=document.querySelector('.hs');if(hs){const L=[...hs.children];let a=0,tm;const go=n=>{a=(n+L.length)%L.length;L.forEach((x,i)=>x.classList.toggle('on',i==a));setTimeout(ping,750)};const tick=()=>{clearTimeout(tm);if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;tm=setTimeout(()=>{go(a+1);tick()},3400)};go(0);tick();L.forEach((x,i)=>{x.addEventListener('click',()=>{go(i);tick()});x.addEventListener('mouseenter',()=>{if(matchMedia('(hover:hover)').matches){go(i);clearTimeout(tm)}})});hs.addEventListener('mouseleave',tick)}
const dl=document.querySelector('dialog.hv');if(!dl)return;const G=JSON.parse(document.getElementById('hg').textContent),st=dl.querySelector('.st'),th=dl.querySelector('.th'),ct=dl.querySelector('.hh span'),tt=dl.querySelector('.hh b');let g=null,k=0;
const show=n=>{k=(n+g.i.length)%g.i.length;st.innerHTML='<img alt="" src="'+g.i[k]+'">';st.scrollTop=0;ct.textContent=(k+1)+' / '+g.i.length;[...th.children].forEach((x,j)=>x.className=j==k?'on':'');th.children[k]&&th.children[k].scrollIntoView({inline:'center',block:'nearest'})};
const open=(id,n)=>{g=G[id];tt.textContent=D.dataset.lang=='pt'?g.t[1]:g.t[0];dl.classList.toggle('pg',g.p);th.innerHTML=g.i.length>1?g.i.map((s,j)=>'<img alt="" loading="lazy" data-j="'+j+'" src="'+g.h[j]+'">').join(''):'';th.style.display=g.i.length>1?'flex':'none';dl.querySelector('.nv').style.visibility=g.i.length>1?'visible':'hidden';dl.querySelectorAll('.ar2').forEach(x=>x.style.visibility=g.i.length>1?'visible':'hidden');show(n||0);dl.showModal();ping()};
document.querySelectorAll('[data-g]').forEach(b=>b.onclick=()=>open(b.dataset.g,+b.dataset.n||0));
dl.addEventListener('click',e=>{if(e.target===dl)dl.close();const b=e.target.closest('button[data-a]');if(b){if(b.dataset.a=='x')dl.close();else show(k+(b.dataset.a=='n'?1:-1))}const i=e.target.closest('.th img');if(i)show(+i.dataset.j)});
dl.addEventListener('keydown',e=>{if(e.key=='ArrowRight')show(k+1);if(e.key=='ArrowLeft')show(k-1)});
})();"""

def health(data, S):
    P = data['page']; M = P['meta']
    head, menu, foot = chrome(S, 3)
    top = ('<section class="ht"><div><small>' + html.escape(P['tags']) + '</small><h1>' + t(P['title']) + '</h1></div><p>' + t(P['intro']) + '</p></section>'
           f'<div class="hg"><div><b>{t(P["give"])}</b><p>{t(P["give2"])}</p></div><div><b>{t(P["make"])}</b><p>{t(P["make2"])}</p></div></div>')
    ICO = ['<path d="M4 5h12a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H9l-4 3v-3H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><path d="M20 9h1a1 1 0 0 1 1 1v7l-3-2h-5"/>', '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 9v12"/>', '<circle cx="12" cy="12" r="9"/><path d="M7.5 12.5l3 3 6-6.5"/>', '<path d="M12 6c-2-1.6-5-2-8-1.6v13c3-.4 6 0 8 1.6 2-1.6 5-2 8-1.6v-13C17 4 14 4.4 12 6z"/><path d="M12 6v13"/>', '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/><path d="M8 10.5l2 2 3.5-4"/>']
    steps = ''.join(f'<button type="button" class="tst{" on" if i==0 else ""}"><svg class="ti d" viewBox="0 0 24 24" aria-hidden="true">{ICO[i]}</svg><svg class="ti a" viewBox="0 0 24 24" aria-hidden="true">{ICO[i]}</svg><span class="tt">{t(a)}</span></button>' for i, (a, b) in enumerate(P['steps']))
    slides = ''.join(f'<div class="tsl{" on" if i==0 else ""}"><h3>{t(a)}</h3><p>{t(b)}</p></div>' for i, (a, b) in enumerate(P['steps']))
    GR = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="ig2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f28db1"/><stop offset=".5" stop-color="#e0568f"/><stop offset="1" stop-color="#235070"/></linearGradient></defs></svg>'
    proc = f'<section class="hp"><h2>{t(P["process"])}</h2>{GR}<div class="tl"><div class="tls">{steps}<i class="tmk"></i></div><div class="tlc">{slides}</div></div></section>'
    G = {}; blocks = ''
    def ims(key, n): return [f'assets/health/{key}_{i:02d}.webp' for i in range(1, n + 1)]
    for bi, b in enumerate(data['books']):
        I = ims(b['key'], b['n']); title = b['title'][1]
        G[b['id']] = {'t': list(b['title']), 'i': I, 'h': I, 'p': True}
        fan = ''.join(f'<img loading="lazy" alt="" src="assets/health/{b["key"]}_{i:02d}.webp">' for i in b['fan'])
        rows = [(M['inst'], html.escape(b['inst'])), (M['year'], b['year']), (M['pages'], b['pages'])]
        if b.get('org'): rows.insert(1, (M['org'], html.escape(b['org'])))
        if b.get('fund'): rows.append((M['fund'], html.escape(b['fund'])))
        dl = ''.join(f'<dt>{t(a)}</dt><dd>{c}</dd>' for a, c in rows)
        chips = ''.join(f'<span>{t(r)}</span>' for r in b['role'])
        chips = f'<div class="chips">{chips}</div>' if chips else ''
        tx2 = f'<p class="tx2">{t(b["text"])}</p>' if b.get('text') else ''
        cvv = f'<p class="cvv">{t(P["cvv"])}</p>' if b.get('cvv') else ''
        blocks += (f'<article class="bk{" rev" if bi % 2 else ""}" id="{b["id"]}" style="--a:{b["accent"]};--t:{b["tint"]}">'
                   f'<button class="fan" data-g="{b["id"]}" aria-label="{html.escape(title)}">{fan}</button><div><span class="k">{t(b["kind"])}</span>'
                   f'<h3>{t(b["title"])}</h3>{tx2}<dl>{dl}</dl>{chips}'
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
            G[I] = {'t': [c['title'][0] + ' · ' + P['tutorial'][0], c['title'][1] + ' · ' + P['tutorial'][1]], 'i': seq, 'h': seq, 'p': True}
        tp = ''.join(f'<li>{t(x)}</li>' for x in c.get('topics', []))
        tp = f'<ul class="tp" aria-label="{html.escape(P["topics"][1])}">{tp}</ul>' if tp else ''
        chips = ''.join(f'<span>{t(r)}</span>' for r in c['chips'])
        chips = f'<div class="chips">{chips}</div>' if chips else ''
        yr = f'<small>{c["year"]}</small>' if c.get('year') else ''
        lg = f'<img class="lg" alt="" src="assets/health/{c["logo"]}.webp">' if c.get('logo') else ''
        btn = f'<button class="hb" data-g="{I}" style="--a:{c["accent"]}">{t(P["tutorial"])} &#8599;</button>' if I else ''
        courses += (f'<article class="cs {c["cls"]}" id="{c["id"]}" style="--a:{c["accent"]};--t:{c["tint"]}"><div class="ci"><img loading="lazy" alt="" src="assets/health/{c["img"]}.webp"></div>'
                    f'<div class="ct"><h3>{t(c["title"])}{yr}</h3>{lg}{rich(c["text"])}{tp}{chips}{btn}</div></article>')
    if courses:
        chap += f'<section class="hc hcc"><h2>{t(P["courses"])}</h2><p>{t(P["courses2"])}</p><div class="cw">{courses}</div></section>'
    viewer = (f'<dialog class="hv" aria-label="Viewer"><div class="hh"><b></b><span></span><div class="nv"><button data-a="p">&#8249; {t(P["prev"])}</button> <button data-a="n">{t(P["next"])} &#8250;</button></div>'
              f'<button data-a="x">{t(P["close"])}</button></div><div class="st"></div><button class="ar2 l" data-a="p" aria-label="Previous">&#8249;</button><button class="ar2 r" data-a="n" aria-label="Next">&#8250;</button><div class="th"></div></dialog>')
    page = shell('Suelen Magalhães — Health', head + menu + top + proc + chap + foot)
    page = page.replace('</style>', HCSS + '</style>', 1).replace('<body>', '<body class="hl">', 1)
    js = '<script type="application/json" id="hg">' + json.dumps(G, ensure_ascii=False).replace('</', '<\\/') + '</script>'
    return page.replace('</body>', viewer + js + f'<script>{HJS}</script></body>', 1)

BCSS = """body.br{background:#fff}.br .intro{display:none}
.bt{margin:48px 4px 0;max-width:none;display:grid;grid-template-columns:1fr 1fr;gap:20px 0;align-items:end}.bt small{justify-self:start;grid-column:1/-1}.bt .br{padding-left:36px}@media(max-width:700px){.bt{grid-template-columns:1fr}.bt .br{padding-left:0}}.bt small{display:inline-block;border:1px solid var(--pink);border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em;color:var(--navy)}
.bt h1{font:700 clamp(3.2rem,8.5vw,6.6rem)/.95 Outfit,sans-serif;letter-spacing:-.045em;color:var(--ink);margin:.18em 0 0}
.bt .ld{font:500 clamp(1.4rem,2.6vw,2rem)/1.25 Outfit,sans-serif;color:var(--ink);margin:0 0 18px;max-width:28ch;padding-left:22px;border-left:6px solid;border-image:linear-gradient(180deg,#1c1140,#235070 62%,#f28db1) 1}
.bt p{font-size:1.1rem;line-height:1.5;color:var(--navy);max-width:52ch;margin:0}
.bi{margin:64px 4px 0}.bi h2{font-size:1.7rem;margin:0 0 22px;color:var(--ink);letter-spacing:-.02em}
.bl{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px;margin:0;padding:0;list-style:none}
.bl a{display:block;text-decoration:none;color:inherit}.bl .th{aspect-ratio:2/1;border-radius:20px;overflow:hidden;background:#fff;border:1px solid #e6e2f2;transition:transform .25s,box-shadow .25s}.bl .th img{width:100%;height:100%;object-fit:cover;display:block}
.bl a:hover .th{transform:translateY(-4px);box-shadow:0 14px 30px rgba(20,18,43,.16)}
.bl .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}.bl b{display:block;font:600 1rem Outfit,sans-serif;color:var(--ink);margin-top:10px}.bl span{display:block;font-size:.8rem;color:var(--navy)}.bl i{font:600 .68rem Inter,sans-serif;font-style:normal;color:var(--pink);letter-spacing:.1em}
.sc{--fg:#14122b;--ac:#054557;--bar:var(--ac);background:#fff;color:var(--fg);border:1px solid #e6e2f2;border-radius:32px;padding:48px 52px;margin:56px 0 0!important;position:relative;overflow:hidden}
.sc::before{content:"";position:absolute;left:0;top:0;bottom:0;width:10px;background:var(--bar)}
.sh{display:flex;align-items:flex-end;gap:24px;flex-wrap:wrap;margin:0 0 36px}.sh .n{font:700 clamp(3.4rem,8vw,6rem)/.8 Outfit,sans-serif;color:var(--ac);letter-spacing:-.04em}
.sh h2{font:700 clamp(2rem,4.4vw,3.4rem)/1 Outfit,sans-serif;letter-spacing:-.03em;margin:0;color:inherit}.sh .m{display:block;font:600 .75rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;opacity:.75;margin-top:8px}
.sg{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:48px;align-items:center;margin:0 0 28px;min-height:430px}
.sg figure{margin:0}.sg figure img{display:block;width:100%;max-height:440px;object-fit:contain;border-radius:0;box-shadow:none}
.sg blockquote{margin:0 0 18px;font:500 clamp(1.15rem,2vw,1.45rem)/1.3 Outfit,sans-serif;color:inherit;padding-left:20px;border-left:4px solid var(--ac)}
.sg p{font-size:.92rem;line-height:1.5;margin:0 0 12px;opacity:.92;color:inherit}
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
@media(max-width:860px){.bl{grid-template-columns:repeat(2,minmax(0,1fr))}.bl{gap:16px}.sc{padding:34px 22px;border-radius:24px}.sg{grid-template-columns:minmax(0,1fr);gap:28px;min-height:0}.sb{grid-template-columns:repeat(auto-fill,minmax(138px,1fr));gap:16px}}"""

def brands(data, S):
    P = data['page']
    head, menu, foot = chrome(S, 4)
    def im(k, n): return f'assets/brands/{k}_{n:02d}.webp'
    top = (f'<section class="bt"><h1>{t(P["title"])}</h1><div class="br"><p class="ld">{t(P["lead"])}</p><p>{t(P["intro"])}</p></div></section>')
    idx = ''.join(f'<li><a href="#{b["id"]}"><div class="th"><img loading="lazy" alt="" src="{im(b["key"], b["hero"])}"></div><span class="sr">{html.escape(b["name"])}</span></a></li>' for b in data['brands'])
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
        scenes += (f'<section class="sc lt" id="{b["id"]}" style="--fg:{b["fg"] if light else "#14122b"};--ac:{b["ac"] if light else b["bg"]};--bar:{b["ac"]}">'
                   f'<header class="sh"><span class="n">{b["n"]}</span><div><h2>{html.escape(b["name"])}</h2><span class="m">{t(b["kind"])} · {b["year"]}</span></div></header>'
                   f'<div class="sg"><figure><img loading="lazy" alt="{html.escape(b["name"])}" src="{im(b["key"], b["hero"])}"></figure><div><blockquote>{t(b["quote"])}</blockquote>{paras}</div></div>'
                   f'<details class="mr"><summary><span class="o">{t(P["seemore"])}</span><span class="c">{t(P["seeless"])}</span><i></i></summary>'
                   f'<div class="mb"><h3>{t(P["frames"])}</h3><ol class="sb">{fr}</ol><h3>{t(P["palette"])}</h3><div class="pl">{sw}</div>{tyb}{apb}</div></details></section>')
    more = f'<section class="bm"><h2>{t(P["more"])}</h2><p>{t(P["more2"])}</p></section>'
    page = shell('Suelen Magalhães — Brands', head + menu + top + index + scenes + more + foot)
    page = page.replace('</style>', BCSS + '</style>', 1).replace('<body>', '<body class="br">', 1)
    return page.replace('</body>', '<script>document.querySelectorAll("details.mr").forEach(d=>d.addEventListener("toggle",()=>{try{ping()}catch(e){}}))</script></body>', 1)

NCSS = """
.pd{display:flex;gap:10px;flex-wrap:wrap;margin:44px 4px 0;padding:0}
.pd a{display:grid;place-items:center;height:44px;padding:0 20px;border-radius:22px;background:var(--bg);color:var(--fg);font:700 .9rem Outfit,sans-serif;text-decoration:none;box-shadow:0 0 0 1px rgba(20,18,43,.12);transition:transform .2s}.pd a:hover{transform:translateY(-3px)}.pd a:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
.pz{--bg:#054557;--fg:#fff;--ac:#eacf19;margin:28px 4px 0;border-radius:36px;background:var(--bg);color:var(--fg);padding:clamp(28px,5vw,60px);display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:0 clamp(28px,5vw,64px);align-items:center;position:relative;overflow:hidden}
.pz.r .px{order:2}.pz.r .py{order:1}
.px{display:flex;flex-direction:column;align-items:flex-start}
.pt{display:flex;align-items:baseline;gap:18px;margin:0 0 6px}
.pn{font:800 clamp(4.4rem,10vw,8rem)/.8 Outfit,sans-serif;letter-spacing:-.06em;color:transparent;-webkit-text-stroke:2px var(--fg);opacity:.9}
.pk{font:600 .72rem Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;opacity:.85}
.pm{margin:10px 0 22px;font:700 clamp(2.7rem,6.2vw,5.2rem)/.92 Outfit,sans-serif;letter-spacing:-.045em}.pm span{display:block}
.pz blockquote{margin:0 0 16px;font:500 clamp(1.1rem,1.9vw,1.4rem)/1.3 Outfit,sans-serif;padding-left:18px;border-left:4px solid var(--ac);max-width:34ch}
.pp{margin:0 0 24px;font-size:.95rem;line-height:1.55;opacity:.92;max-width:46ch}
.pb{all:unset;box-sizing:border-box;cursor:pointer;display:inline-flex;align-items:center;gap:10px;padding:12px 22px;border-radius:999px;background:var(--fg);color:var(--on,#fff);font:600 .9rem Inter,sans-serif;transition:transform .2s}.pb:hover{transform:translateX(4px)}.pb:focus-visible{outline:3px solid var(--ac);outline-offset:3px}
.pb i{font-style:normal}
.py{padding:clamp(18px,3vw,34px) clamp(8px,2vw,22px) 0}
.gm{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:22px 0 8px}.gm img{width:100%;border-radius:12px;display:block}
.pf{cursor:pointer;margin:0;position:relative;width:90%;margin-bottom:clamp(48px,10vw,104px)}.pz.r .pf{margin-left:auto}
.pf img{display:block;border-radius:18px;box-shadow:0 22px 48px rgba(0,0,0,.3);background:#fff;transition:transform .5s cubic-bezier(.2,.9,.2,1)}
.pf .m0{width:100%;position:relative;z-index:1}
.pf .m1{position:absolute;z-index:3;width:44%;right:-19%;bottom:-24%;transform:rotate(4deg)}
.pf .m2{position:absolute;z-index:2;width:32%;left:-11%;top:-17%;transform:rotate(-5deg)}
.pz:hover .m1{transform:rotate(6deg) translate(10px,10px)}.pz:hover .m2{transform:rotate(-7deg) translate(-8px,-8px)}.pz:hover .m0{transform:scale(1.02)}
@media(prefers-reduced-motion:reduce){.pf img{transition:none}.pz:hover .m0,.pz:hover .m1,.pz:hover .m2{transform:none}}
.pz#margeci .pf{width:100%}.pz.r .pf .m1{right:auto;left:-19%}.pz.r .pf .m2{left:auto;right:-9%;transform:rotate(5deg)}.pz.r:hover .m2{transform:rotate(7deg) translate(8px,-8px)}.pz.r .m1{transform:rotate(-4deg)}.pz.r:hover .m1{transform:rotate(-6deg) translate(-10px,10px)}
.pw{width:90%}.pz.r .pw{margin-left:auto}
.pw{display:flex;height:18px;margin-top:0;border-radius:999px;overflow:hidden;box-shadow:0 0 0 2px rgba(255,255,255,.55)}.pw i{flex:1}
dialog.bd{border:0;border-radius:28px;padding:0;width:min(940px,94vw);background:#fff;color:var(--ink)}dialog.bd::backdrop{background:rgba(20,18,43,.62)}
html:not([data-embed]) dialog.bd{max-height:92vh;overflow:auto}
.bd .dh{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:24px 32px;border-bottom:1px solid #e6e2f2;position:sticky;top:0;background:#fff;z-index:2}
.bd .dh h2{margin:0;font:700 1.7rem/1 Outfit,sans-serif;letter-spacing:-.03em;color:var(--ink)}.bd .dh h2 span.n{color:var(--ac);margin-right:12px}
.bd .x{all:unset;cursor:pointer;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;border:1px solid #d9d5ea;font-size:1.1rem;color:var(--ink)}.bd .x:hover{background:#f3efff}.bd .x:focus-visible{outline:2px solid var(--ac)}
.bd .dc{padding:10px 32px 40px}.bd h3{font:600 .72rem Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--ac);margin:30px 0 16px}
.bd .cp p{font-size:.98rem;line-height:1.6;margin:0 0 12px;color:var(--ink)}.bd .sb{margin:0}.bd .sb b{color:var(--ink)}.bd .sb span.d{color:var(--navy)}.bd .pl{margin:0}.bd .pl .sw{color:var(--ink)}.bd .pl .ch{border:1px solid rgba(0,0,0,.12)}.bd .ty{margin:0}.bd .ty p{color:var(--ink)}
@media(max-width:860px){.pf{width:88%}.pw{width:88%}.pf .m1{right:-10%}.pz.r .pf .m1{left:-10%}.pf .m2{left:-6%}.pz.r .pf .m2{right:-6%}.pz{grid-template-columns:minmax(0,1fr);border-radius:26px}.pz.r .px{order:0}.px{display:contents}.pt{order:0}.pm{order:1}.py{order:2;margin:0 0 22px}.pz blockquote{order:3}.pp{order:4}.pb{order:5}.bd .dh,.bd .dc{padding-left:20px;padding-right:20px}}
"""

MOCK = {'mar': 2, 'gis': 1, 'eff': 2, 'fkl': 3, 'tel': 1, 'hel': 3}

def brands_novo(data, S):
    data = dict(data); data['brands'] = sorted(data['brands'], key=lambda x: -int(x['year']))
    P = data['page']
    head, menu, foot = chrome(S, 4)
    def im(k, n): return f'assets/brands/{k}_{n:02d}.webp'
    top = (f'<section class="bt"><h1>{t(P["title"])}</h1><div class="br"><p class="ld">{t(P["lead"])}</p><p>{t(P["intro"])}</p></div></section>')
    nav = ''.join(f'<a href="#{b["id"]}" aria-label="{html.escape(b["name"])}" style="--bg:{b["bg"]};--fg:{b["fg"]}">{html.escape(b["name"])}</a>' for b in data['brands'])
    nav = f'<nav class="pd" aria-label="{html.escape(P["index"][1])}">{nav}</nav>'
    posters = ''; dialogs = ''
    def lum(c):
        c = c.lstrip('#')
        if len(c) != 6: return 1
        r, g, b_ = (int(c[i:i+2], 16) for i in (0, 2, 4)); return (0.299*r + 0.587*g + 0.114*b_) / 255
    for i, b in enumerate(data['brands']):
        dac = b['ac'] if lum(b['fg']) < .5 else (b['bg'] if b['bg'].startswith('#') and len(b['bg']) == 7 else '#235070')
        on = '#fff' if lum(b['fg']) < .5 else (b['bg'] if b['bg'].startswith('#') and len(b['bg']) == 7 else '#14122b')
        nm = MOCK.get(b['key'], 1)
        mk = lambda j: f'assets/brands/{b["key"]}_m{j}.webp'
        cl = ''.join(f'<img class="m{j-1}" loading="lazy" alt="" src="{mk(j)}">' for j in range(2, nm + 1))
        words = ''.join(f'<span>{html.escape(w)}</span>' for w in b['name'].split())
        ps = ''.join(f'<i style="background:{s["c"]}" title="{s["c"].upper()}"></i>' for s in b['swatches'])
        ps = f'<div class="pw" aria-hidden="true">{ps}</div>' if ps else ''
        posters += (f'<section class="pz{" r" if i % 2 else ""}" id="{b["id"]}" style="--bg:{b["bg"]};--fg:{b["fg"]};--ac:{b["ac"]};--on:{on}">'
                    f'<div class="px"><div class="pt"><span class="pk">{t(b["kind"])} · {b["year"]}</span></div>'
                    f'<h2 class="pm">{words}</h2><blockquote>{t(b["quote"])}</blockquote>{''.join(f'<p class="pp">{t(x)}</p>' for x in b['text'][:b.get('pshow', 1)])}'
                    f'<button type="button" class="pb" data-d="d-{b["id"]}">{t(["See the full story", "Ver a história completa"])} <i>&#8594;</i></button></div>'
                    f'<div class="py"><figure class="pf" data-d="d-{b["id"]}"><img class="m0" loading="lazy" alt="{html.escape(b["name"])}" src="{mk(1)}">{cl}</figure>{ps}</div></section>')
        paras = ''.join(f'<p>{t(x)}</p>' for x in b['text'])
        fr = ''.join(f'<li><img loading="lazy" alt="" src="{im(b["key"], f["img"])}"><b>{t(f["t"])}</b><span class="d">{t(f["d"])}</span></li>' for f in b['frames'])
        sw = ''.join(f'<div class="sw"><div class="ch" style="background:{x["c"]}"></div><b>{t(x["n"])}</b><code>{x["c"].upper()}</code><span>{t(x["d"])}</span></div>' for x in b['swatches'])
        ty = ''.join(f'<p><b>{html.escape(x[0])}</b> · {t([x[1], x[2]])}</p>' for x in b['type'])
        ap = ''.join(f'<li><img loading="lazy" alt="" src="{im(b["key"], f["img"])}"><b>{t(f["t"])}</b><span class="d">{t(f["d"])}</span></li>' for f in b['apps'])
        gal = ''.join(f'<img loading="lazy" alt="" src="{mk(j)}">' for j in range(1, nm + 1))
        body = f'<div class="cp">{paras}</div><div class="gm">{gal}</div>'
        if fr: body += f'<h3>{t(P["frames"])}</h3><ol class="sb">{fr}</ol>'
        if sw: body += f'<h3>{t(P["palette"])}</h3><div class="pl">{sw}</div>'
        if ty: body += f'<h3>{t(P["type"])}</h3><div class="ty">{ty}</div>'
        if ap: body += f'<h3>{t(P["apps"])}</h3><ol class="sb ap">{ap}</ol>'
        dialogs += (f'<dialog class="bd" id="d-{b["id"]}" style="--ac:{dac}" aria-labelledby="t-{b["id"]}"><div class="dh"><h2 id="t-{b["id"]}">{html.escape(b["name"])}</h2>'
                    f'<button type="button" class="x" aria-label="{html.escape("Fechar")}">&#10005;</button></div><div class="dc">{body}</div></dialog>')
    more = f'<section class="bm"><h2>{t(P["more"])}</h2><p>{t(P["more2"])}</p></section>'
    js = ('<script>document.addEventListener("click",e=>{const o=e.target.closest(".pb,.pf");if(o){const d=document.getElementById(o.dataset.d);if(d){d.showModal();try{ping()}catch(x){}}return}'
          'const d=e.target.closest("dialog.bd");if(d&&(e.target===d||e.target.closest(".x")))d.close()})</script>')
    page = shell('Suelen Magalhães — Brands', head + menu + top + posters + more + dialogs + foot)
    page = page.replace('</style>', BCSS + NCSS + '</style>', 1).replace('<body>', '<body class="br">', 1)
    return page.replace('</body>', js + '</body>', 1)


ACSS = """body.ab{background:#fff}.ab .intro{display:none}.ab footer .ft{display:none}.ab footer .bandbar{display:none}.ab footer .fl a{display:none}.ab footer .fl{justify-content:center}
.at{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:22px clamp(28px,6vw,72px);align-items:end;margin:44px 4px 0}
.at small{display:inline-block;border:1px solid var(--pink);border-radius:999px;padding:3px 16px;font:600 .75rem Inter,sans-serif;letter-spacing:.06em;color:var(--navy)}
.at h1{font:700 clamp(3.6rem,11vw,8.4rem)/.9 Outfit,sans-serif;letter-spacing:-.05em;color:var(--ink);margin:.12em 0 0}
.at p{margin:0;font:500 1.35rem/1.3 Outfit,sans-serif;color:var(--ink);padding-left:22px;border-left:6px solid;border-image:linear-gradient(180deg,#1c1140,#235070 62%,#f28db1) 1}
.as{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:34px 26px;margin:46px 4px 0;padding-top:26px;border-top:3px solid;border-image:linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%) 1}
.as>div{grid-column:span 2}.as>div:nth-child(4){grid-column:2/span 2}.as>div:nth-child(5){grid-column:4/span 2}.as .v{display:flex;align-items:center;gap:.22em;font:600 clamp(2.6rem,6.2vw,4.6rem)/1 Outfit,sans-serif;letter-spacing:-.04em;color:#f28db1}.as .v svg{width:.62em;height:.62em;flex:none;fill:none;stroke:#f28db1;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;opacity:.9}.as .v b{padding:.12em .14em .08em 0;margin:-.12em -.14em -.08em 0;font:inherit;background:linear-gradient(90deg,#f28db1 55%,#c9669a 130%);-webkit-background-clip:text;background-clip:text;color:transparent;font-variant-numeric:tabular-nums}.as div>span{display:block;margin-top:10px;font:600 1rem/1.4 Inter,sans-serif;max-width:26ch;color:var(--ink)}.as>div{opacity:0;transform:translateY(14px);transition:opacity .6s,transform .6s}.as.in>div{opacity:1;transform:none}.as.in>div:nth-child(2){transition-delay:.12s}.as.in>div:nth-child(3){transition-delay:.24s}.as.in>div:nth-child(4){transition-delay:.36s}.as.in>div:nth-child(5){transition-delay:.48s}.as.nj>div{opacity:1;transform:none;transition:none}
.ab2{display:grid;grid-template-columns:minmax(0,1fr);gap:18px;margin:56px 4px 0}.ab2 p{margin:0;font-size:1.1rem;line-height:1.5;color:var(--navy)}.ab2 strong{color:var(--ink);font-weight:700}
.ac{margin:72px 4px 40px;border-radius:32px;padding:clamp(28px,5vw,60px);color:#fff;background:radial-gradient(800px 420px at 90% 10%,rgba(124,108,246,.4),transparent 60%),var(--hex),linear-gradient(90deg,#1c1140 0%,#235070 62%,#f28db1 190%);display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px clamp(24px,5vw,60px);align-items:end}
.ac small{font:600 .72rem Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#f28db1}.ac h2{font:700 clamp(2.4rem,6.4vw,5rem)/.95 Outfit,sans-serif;letter-spacing:-.04em;margin:.15em 0 .25em}.ac .ct{margin:0;font-size:1.1rem;opacity:.92}.ac .pl{margin:14px 0 0;font:600 .8rem Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase;opacity:.7}
.ac ul{list-style:none;margin:0;padding:0;display:grid;gap:10px}.ac li a{display:flex;justify-content:space-between;align-items:baseline;gap:14px;flex-wrap:wrap;text-decoration:none;color:#fff;padding:14px 18px;border:1px solid rgba(255,255,255,.28);border-radius:16px;transition:background .2s,color .2s,transform .2s}
.ac li a:hover,.ac li a:focus-visible{background:#fff;color:#14122b;transform:translateX(4px);outline:0}.ac li svg{width:22px;height:22px;flex:none;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}.ac li svg.f{fill:currentColor;stroke:none}.ac li a{align-items:center;flex-wrap:nowrap}.ac li b{margin-right:auto}.ac li b{font:600 .72rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;opacity:.75}.ac li span{font:500 1rem Inter,sans-serif;overflow-wrap:anywhere}
.ac li:first-child a{background:#f28db1;border-color:#f28db1;color:#14122b}.ac li:first-child a:hover{background:#fff}
@media(max-width:860px){.as{grid-template-columns:repeat(2,minmax(0,1fr))}.as>div,.as>div:nth-child(4),.as>div:nth-child(5){grid-column:auto}.as>div:nth-child(5){grid-column:1/-1}.at,.ab2,.ac{grid-template-columns:minmax(0,1fr)}.ac{border-radius:24px}}"""

def about(data, S):
    P = data['page']
    S2 = dict(S); S2['menu'] = [m for m in S['menu'] if m[0] != 'CONTACT']
    S2['menu'] = [[P['menu_about'][0], P['menu_about'][1], m[2]] if m[0] == 'ABOUT' else m for m in S2['menu']]
    head, menu, foot = chrome(S2, 7)
    top = f'<section class="at"><div><h1>{t(P["title"])}</h1></div><p>{t(P["lead"])}</p></section>'
    SI = ['<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h10M7 21h10M8 3c0 5 8 5 8 9s-8 4-8 9M16 3c0 5-8 5-8 9s8 4 8 9"/></svg>',
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/><path d="M8.5 10.5l2.5 2.5 4.5-5"/></svg>',
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 3L3 10.5l7 3 3 7z"/><path d="M10 13.5L21 3"/></svg>',
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>',
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4h8v5a4 4 0 01-8 0zM8 6H4v1a4 4 0 004 4M16 6h4v1a4 4 0 01-4 4M12 13v4M8 21h8M10 17h4"/></svg>']
    def sv(a, i):
        if isinstance(a, list): v = t(a)
        else:
            m = re.match(r'^(\D*)(\d+)(.*)$', a)
            v = f'<span data-n="{m.group(2)}" data-pre="{html.escape(m.group(1))}" data-suf="{html.escape(m.group(3))}">{html.escape(a)}</span>' if m else html.escape(a)
        return f'<div class="v">{SI[i]}<b>{v}</b></div>'
    st = ''.join(f'<div>{sv(a, i)}<span>{t(b)}</span></div>' for i, (a, b) in enumerate(P['stats']))
    body = ''.join('<div><p>' + re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t(x)) + '</p></div>' for x in P['body'])
    IC = {'Email': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 7 8.5-7"/></svg>',
          'LinkedIn': '<svg viewBox="0 0 24 24" aria-hidden="true" class="f"><path d="M4.98 3.5a2.5 2.5 0 11-.02 5 2.5 2.5 0 01.02-5zM3 9.75h4V21H3zM9.5 9.75h3.8v1.6h.06c.53-1 1.82-2 3.75-2 4 0 4.74 2.6 4.74 6V21h-4v-4.9c0-1.2 0-2.7-1.7-2.7s-1.9 1.3-1.9 2.6V21h-4z"/></svg>'}
    lk = ''.join(f'<li><a href="{html.escape(u)}"' + (' target="_blank" rel="noopener"' if u.startswith('http') else '') + f'>{IC.get(a, "")}<b>{html.escape(a)}</b><span>{html.escape(b)}</span></a></li>' for a, b, u in P['links'])
    ct = (f'<section class="ac" id="contact"><div><small>{t(P["contact_k"])}</small><h2>{t(P["contact_h"])}</h2><p class="ct">{t(P["contact_t"])}</p><p class="pl">{t(P["place"])}</p></div><ul>{lk}</ul></section>')
    page = shell('Suelen Magalhães — About & Contact', head + menu + top + f'<section class="as">{st}</section><section class="ab2">{body}</section>' + ct + foot)
    page = page.replace('</style>', ACSS + '</style>', 1).replace('<body>', '<body class="ab">', 1)
    js = ('<script>(function(){var s=document.querySelector(".as");if(!s)return;var rm=matchMedia("(prefers-reduced-motion:reduce)").matches;'
          'if(rm||!("IntersectionObserver" in window)){s.classList.add("nj");return}'
          'var ns=[].slice.call(s.querySelectorAll("[data-n]"));ns.forEach(function(e){e.textContent=e.dataset.pre+"0"+e.dataset.suf});'
          'function run(){s.classList.add("in");ns.forEach(function(e,i){var n=+e.dataset.n,t0=null,d=1400;function f(t){if(t0===null)t0=t;var p=Math.min(1,(t-t0)/d),k=1-Math.pow(1-p,3);e.textContent=e.dataset.pre+Math.round(n*k)+e.dataset.suf;if(p<1)requestAnimationFrame(f)}setTimeout(function(){requestAnimationFrame(f)},i*120)})}'
          'var io=new IntersectionObserver(function(es){if(es[0].isIntersecting){io.disconnect();run()}},{threshold:.25});io.observe(s);'
          'setTimeout(function(){if(!s.classList.contains("in")){try{io.disconnect()}catch(x){}run()}},6000)})()</script>')
    return page.replace('</body>', js + '</body>', 1)

ICSS = """body.ia{background:#fff}.ia .intro{display:none}
.fb{margin-left:calc(50% - 50vw);margin-right:calc(50% - 50vw);position:relative;overflow:hidden}.in{max-width:1080px;margin:0 auto;padding:0 16px}
.ia .k{display:inline-block;font:600 .72rem Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#f28db1;margin-bottom:14px}
.a1{margin-top:28px;color:#fff;background:radial-gradient(900px 500px at 85% 20%,rgba(124,108,246,.45),transparent 60%),linear-gradient(110deg,#14122b 0%,#235070 70%,#f28db1 190%);padding:clamp(40px,7vw,84px) 0 0}
.a1 .g{display:grid;grid-template-columns:1.25fr .75fr;gap:30px;align-items:center}
.a1 h1{font:700 clamp(8rem,28vw,20rem)/.78 Outfit,sans-serif;letter-spacing:-.07em;margin:0 0 .06em -.04em;background:linear-gradient(180deg,#fff 20%,#f28db1);-webkit-background-clip:text;background-clip:text;color:transparent}
.a1 .h2{font:700 clamp(2rem,5.6vw,4.2rem)/1 Outfit,sans-serif;letter-spacing:-.035em;margin:0}.a1 .h2 s{display:block;text-decoration:none;color:transparent;-webkit-text-stroke:1.5px #fff}.a1 .h2 b{display:block;color:#f28db1}
.a1 p.in2{max-width:50ch;font-size:1.05rem;line-height:1.55;margin:22px 0 0;opacity:.92}
.mk{justify-self:end;width:100%;max-width:300px;background:rgba(20,18,43,.72);border:1px solid rgba(255,255,255,.2);border-radius:20px;padding:14px;transform:rotate(3deg);box-shadow:0 30px 60px rgba(0,0,0,.35)}
.mk i{display:flex;gap:5px;margin-bottom:12px}.mk i:before,.mk i:after,.mk i span{content:"";width:9px;height:9px;border-radius:50%;background:#f28db1;opacity:.9}.mk i:after{background:#7c6cf6}.mk i span{background:#fff;opacity:.5}
.mk p{margin:0 0 8px;font:500 .9rem/1.35 Inter,sans-serif;padding:10px 12px;border-radius:14px}.mk .m{background:#f28db1;color:#14122b;margin-left:22px}.mk .c{background:#235070;margin-right:22px}.mk b{display:block;font:600 .62rem Inter,sans-serif;letter-spacing:.1em;text-transform:uppercase;opacity:.7;margin-bottom:2px}
.tk{margin-top:clamp(40px,6vw,70px);border-top:1px solid rgba(255,255,255,.25);padding:14px 0;overflow:hidden;white-space:nowrap}.tk div{display:inline-block;animation:tk 38s linear infinite;font:600 .8rem Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase}.tk span{margin:0 22px}.tk span:before{content:"✦";color:#f28db1;margin-right:44px}
@keyframes tk{to{transform:translateX(-50%)}}@media(prefers-reduced-motion:reduce){.tk div{animation:none}}
.a1x{margin-top:28px}.bn{min-height:clamp(220px,32vw,360px);border:2px dashed #cfcce0;border-radius:24px;background:#f7f6fb}
.a0{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px 30px;padding:clamp(34px,5vw,56px) 0 0}.a0 div{border-top:3px solid #14122b;padding-top:12px}.a0 div:nth-child(2){border-color:#235070}.a0 div:nth-child(3){border-color:#f28db1}
.a0 h3{margin:0;font:700 clamp(1.8rem,4.4vw,3.2rem)/1 Outfit,sans-serif;letter-spacing:-.04em;color:#14122b}.a0 div:nth-child(2) h3{color:#235070}.a0 div:nth-child(3) h3{color:#f28db1}.a0 p{margin:8px 0 0;font-size:1rem;line-height:1.4}
.a2{padding:clamp(48px,7vw,84px) 0}.a2 .big{display:flex;align-items:baseline;flex-wrap:wrap;gap:0 .3em;font:700 clamp(3.6rem,14vw,11rem)/.95 Outfit,sans-serif;letter-spacing:-.06em;color:var(--ink)}
.a2 s{text-decoration:none;position:relative;color:#b9b6cc}.a2 s:after{content:"";position:absolute;left:-2%;right:-2%;top:52%;height:.09em;background:#f28db1;transform:rotate(-4deg)}.a2 em{font-style:normal;background:linear-gradient(90deg,#235070,#f28db1);-webkit-background-clip:text;background-clip:text;color:transparent}
.a2 p{max-width:60ch;font-size:1.1rem;line-height:1.55;margin:26px 0 0}.a2 small{display:block;margin-top:14px;color:#6b6985;font-size:.85rem}
.a3{background:#f3efff;padding:clamp(40px,6vw,70px) 0}.a3 h2{font:700 clamp(1.6rem,3.6vw,2.6rem)/1.05 Outfit,sans-serif;letter-spacing:-.03em;margin:0 0 22px;color:var(--ink)}
.ch2{background:#fff;border:1px solid #e3e1ef;border-radius:18px;padding:18px 20px 12px}.ch2 .ct{font:600 .85rem Inter,sans-serif;color:var(--ink);margin-bottom:14px}
.br2{display:grid;grid-template-columns:90px 1fr;gap:0 14px;align-items:center;margin:0 0 8px}.br2 b{font:600 .9rem Outfit,sans-serif;color:var(--ink)}
.tr{height:30px;border-right:1px solid #e3e1ef;border-left:1px solid #e3e1ef;background:linear-gradient(90deg,#ececf5 1px,transparent 1px) 0 0/25% 100%;display:flex;align-items:center}.tr i{display:block;height:20px;border-radius:0 8px 8px 0;background:#8da1b8}.tr em{font-style:normal;font-size:.78rem;margin-left:8px;color:#6b6985;white-space:nowrap}
.br2.big .tr{height:38px}.br2.big .tr i{height:28px;background:linear-gradient(90deg,#1c1140,#235070 62%,#f28db1);width:100%;display:flex;align-items:center;justify-content:flex-end;padding-right:12px;color:#fff;font:600 .8rem Inter,sans-serif}.br2.big b{font-size:1rem}
.ax{display:grid;grid-template-columns:90px 1fr;gap:0 14px;margin-top:4px}.ax div{display:flex;justify-content:space-between;font:600 .68rem Inter,sans-serif;color:#6b6985;letter-spacing:.04em;text-transform:uppercase}
.a3 small{display:block;margin-top:12px;color:#6b6985;font-size:.8rem}
.a4{padding:clamp(40px,6vw,70px) 0}.tl{display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);gap:10px 40px;align-items:center;padding:16px 0;border-top:1px solid #e3e1ef}
.tl h3{margin:0;font:700 clamp(2rem,5vw,3.4rem)/1 Outfit,sans-serif;letter-spacing:-.04em;color:#235070}.tl:nth-child(2n) h3{color:#f28db1}.tl p{margin:0;font-size:1.05rem;line-height:1.5}
.a5{background:#14122b;color:#fff;padding:clamp(40px,6vw,76px) 0}.rh{font:800 clamp(2.4rem,6vw,4.4rem)/1 Outfit,sans-serif;letter-spacing:-.045em;margin:12px 0 clamp(26px,4vw,44px);max-width:16ch;color:#fff}.rh em{font-style:normal;background:linear-gradient(90deg,#fff,#f28db1);-webkit-background-clip:text;background-clip:text;color:transparent}
.rg{display:grid;grid-template-columns:1fr 1.15fr;gap:34px;align-items:start}.rl{display:flex;flex-direction:column;gap:6px}.ri .pm{display:none}
.rb{all:unset;box-sizing:border-box;cursor:pointer;display:grid;grid-template-columns:34px 1fr auto;align-items:center;gap:10px;padding:16px 20px;border-radius:26px;width:100%}.rb:focus-visible{outline:2px solid #f28db1;outline-offset:2px}
.rb b{font:700 .8rem Inter,sans-serif;opacity:.5;color:#8d89a8}.rb h3{margin:0;font:700 clamp(1.25rem,2.6vw,2rem)/1.1 Outfit,sans-serif;letter-spacing:-.03em;color:#8d89a8}.rb>span{font-size:.78rem;color:#8d89a8;text-align:right;white-space:nowrap}.rb:hover h3{color:#c9c3ff}
.ri.on .rb{background:#f28db1}.ri.on .rb b,.ri.on .rb h3,.ri.on .rb>span{color:#14122b;opacity:1}.ri.on .rb b{opacity:.7}
.rcard{position:relative;border-radius:34px;padding:22px;background:#f5a6c4;color:#235070}.nt{position:absolute;left:-30px;top:14px;width:0;height:0;border-top:34px solid transparent;border-bottom:34px solid transparent;border-right:30px solid #f5a6c4;transition:top .2s}
.pd{display:none}.pd.on{display:block}.inn{background:#fff;border-radius:24px;padding:26px 26px 12px}.a5 .ic{width:44px;height:44px;stroke:#235070;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.inn h2{font:700 clamp(1.25rem,2.2vw,1.7rem)/1.2 Outfit,sans-serif;letter-spacing:-.02em;margin:14px 0 16px;color:#235070}.inn .no{margin:6px 0 16px;color:#6b7b90;font-size:.95rem}
.rc{border-top:1px solid #dfe6ee;padding:14px 0 18px}.rc p{margin:0 0 8px;font-size:.78rem;color:#6b7b90}.rc p i{font-style:normal;font-weight:700;color:#235070;font-size:.72rem;letter-spacing:.04em;text-transform:uppercase}
.rw{display:grid;grid-template-columns:1fr 22px 1fr;gap:8px;align-items:center}.cr{background:#235070;color:#fff;font-weight:700;font-size:.9rem;border-radius:12px;padding:10px 14px;line-height:1.3}.ok{background:#e8f0f6;color:#235070;font-weight:700;font-size:.9rem;border-radius:12px;padding:10px 14px;line-height:1.3}.rw .ra{text-align:center;color:#235070;opacity:.6}
.a5 .lb{margin:20px 0 10px;font:600 .66rem Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#235070}.a5 .ch>span{display:inline-block;color:#235070;border:1px solid #235070;background:#fff;border-radius:999px;padding:7px 14px;font-size:.82rem;margin:0 8px 8px 0}
@media(max-width:820px){.rg{display:block}.rcard{display:none}.ri .pm{display:none;background:#f5a6c4;border-radius:0 0 26px 26px;padding:14px;margin-top:-10px;color:#235070}.ri.on .pm{display:block}.ri.on .rb{border-radius:26px 26px 0 0}.rw{grid-template-columns:1fr}.rw .ra{transform:rotate(90deg)}}
.a6{padding:clamp(40px,6vw,70px) 0}.fw{display:grid;grid-template-columns:1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr;align-items:stretch;margin:6px 0 0}
.fw .nd{border:1px solid #e3e1ef;border-radius:16px;padding:14px 12px;text-align:center}.fw .ic{height:44px;display:grid;place-items:center;margin-bottom:8px}.fw .ic img{height:44px;width:44px;border-radius:50%}.fw .ic svg{width:34px;height:34px;stroke:#235070;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.fw b{display:block;font:700 .98rem Outfit,sans-serif;color:var(--ink)}.fw p{margin:4px 0 0;font-size:.82rem;line-height:1.35}.fw .fa{align-self:center;text-align:center;color:#f28db1;font-weight:700}
.a6 p.t{max-width:62ch;margin:20px 0 0}.lp2{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 0;padding:0;list-style:none}.lp2 li{border-radius:999px;padding:5px 14px;background:#f3efff;font:600 .82rem Outfit,sans-serif;color:var(--ink)}.lp2 li:last-child{background:#f28db1}
.pc{max-width:70ch;font-size:1.1rem;line-height:1.55;margin:0 0 22px;color:var(--navy)}.pl{display:flex;margin:0;padding:6px;list-style:none;border-radius:999px;background:linear-gradient(90deg,#f28db1,#7c6cf6 55%,#235070)}
.pl li{flex:1;position:relative;text-align:center;padding:12px 8px;border-radius:999px;color:#fff;font:600 .95rem Outfit,sans-serif;animation:pls 10s infinite;animation-delay:calc(var(--i)*2s)}.pl li:not(:last-child):after{content:"→";position:absolute;right:-8px;top:50%;transform:translateY(-50%);z-index:1;font-weight:400}
@keyframes pls{0%,19%{background:#fff;color:#14122b}20%,100%{background:transparent;color:#fff}}@media(prefers-reduced-motion:reduce){.pl li{animation:none}}
@media(max-width:820px){.pl{flex-direction:column;border-radius:28px}.pl li:not(:last-child):after{content:"↓";right:auto;left:50%;top:auto;bottom:-10px;transform:translateX(-50%)}}
.a8{margin-top:clamp(40px,6vw,64px);border-top:1px dashed #cfcce0;padding:18px 0 8px}.a8 .k{color:#6b6985}.a8 .og{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 30px}.a8 b{display:block;font:700 1rem Outfit,sans-serif;color:var(--ink)}.a8 p{margin:3px 0 0;font-size:.9rem;line-height:1.4;color:#4f5d78}
@media(max-width:820px){.a1 .g{grid-template-columns:1fr}.mk{justify-self:start;max-width:300px;transform:rotate(2deg)}.a0{grid-template-columns:1fr}.rc{grid-template-columns:1fr}.rc.hd{display:none}.rc div small{display:block;font:600 .62rem Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;opacity:.65;margin-bottom:3px}.tl{grid-template-columns:1fr}.fw{grid-template-columns:1fr}.fw .fa{transform:rotate(90deg);padding:6px 0}.a8 .og{grid-template-columns:1fr}.br2,.ax{grid-template-columns:62px 1fr}}
"""

ICO = {
 'ai': '<svg viewBox="0 0 24 24"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 16l.7 1.8L21.5 18.5l-1.8.7L19 21l-.7-1.8-1.8-.7 1.8-.7z"/></svg>',
 'git': '<svg viewBox="0 0 24 24"><circle cx="6" cy="5" r="2.4"/><circle cx="6" cy="19" r="2.4"/><circle cx="18" cy="9" r="2.4"/><path d="M6 7.4v9.2M18 11.4c0 4-6 3-12 5.6"/></svg>',
 'web': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>',
 'ok': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M7.5 12.5l3 3 6-7"/></svg>'}

def ia(data, S):
    P = data['page']
    head, menu, foot = chrome(S, 6)
    tk = ''.join(f'<span>{t(x)}</span>' for x in P['ticker'])
    hero = '<section class="a1x"><div class="bn"></div></section>'
    top3 = '<section class="a0">' + ''.join(f'<div><h3>{t(a)}</h3><p>{t(b)}</p></div>' for a, b in zip(P['close'], P['close_t'])) + '</section>'
    time_ = (f'<section class="a2"><span class="k">{t(P["time_k"])}</span><div class="big"><s>{t(P["time_old"])}</s><em>{t(P["time_new"])}</em></div>'
             f'<p>{t(P["time_t"])}</p><small>{t(P["time_n"])}</small></section>')
    bars = ''.join(f'<div class="br2"><b>{b[0]}</b><div class="tr"><i style="width:{b[2]}%"></i><em>{t(b[1])}</em></div></div>' for b in P['bars'])
    ax = ''.join(f'<span>{t(x)}</span>' for x in P['axis'])
    bars_ = (f'<section class="fb a3"><div class="in"><span class="k">{t(P["bars_k"])}</span><h2>{t(P["bars_h"])}</h2>'
             f'<div class="ch2" role="img" aria-label="chart"><div class="ct">{t(P["chart_t"])}</div>{bars}'
             f'<div class="br2 big"><b>{t(P["bar_big"])}</b><div class="tr"><i>{t(P["bar_big2"])}</i></div></div>'
             f'<div class="ax"><span></span><div>{ax}</div></div></div><small>{t(P["bar_note"])}</small></div></section>')
    tools = ''.join(f'<div class="tl"><h3>{t(x[0])}</h3><p>{t(x[1])}</p></div>' for x in P['tools'])
    tools_ = f'<section class="a4"><span class="k">{t(P["tool_k"])}</span>{tools}</section>'
    also = ''.join(f'<span>{t(x)}</span>' for x in P['also_l'])
    def panel(r):
        if r['r']:
            rc = ''.join(f'<div class="rc"><p><i>{t(P["rr_ask"])}</i> {t(x[0])} · <i>{t(P["rr_ret"])}</i> {t(x[1])}</p><div class="rw"><div class="cr">{t(x[2])}</div><div class="ra">→</div><div class="ok">{t(x[3])}</div></div></div>' for x in r['r'])
        else:
            rc = f'<p class="no">{t(P["rr_none"])}</p>'
        return f'<div class="inn"><svg class="ic" viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg><h2>{t(r["s"])}</h2>{rc}</div>'
    items = ''.join(f'<div class="ri{" on" if i==2 else ""}"><button type="button" class="rb" data-i="{i}" aria-expanded="{"true" if i==2 else "false"}"><b>{i+1:02d}</b><h3>{t(r["t"])}</h3><span>{t(r["m"])}</span></button><div class="pm">{panel(r)}<div class="lb">{t(P["also"])}</div><div class="ch">{also}</div></div></div>' for i, r in enumerate(P['rr_rules']))
    pans = ''.join(f'<div class="pd{" on" if i==2 else ""}" data-i="{i}">{panel(r)}</div>' for i, r in enumerate(P['rr_rules']))
    rec_ = (f'<section class="fb a5"><div class="in"><span class="k">{t(P["rr_k"])}</span><h1 class="rh">{t(P["rr_h1"])} <em>{t(P["rr_h2"])}</em></h1>'
            f'<div class="rg"><div class="rl">{items}</div><div class="rcard"><i class="nt"></i>{pans}<div class="lb">{t(P["also"])}</div><div class="ch">{also}</div></div></div></div>'
            '<script>(function(){var s=document.currentScript.parentNode,bs=s.querySelectorAll(".rb"),it=s.querySelectorAll(".ri"),pd=s.querySelectorAll(".pd"),c=s.querySelector(".rcard"),n=s.querySelector(".nt");'
            'function pos(){var a=s.querySelector(".ri.on .rb");if(!a||!c||getComputedStyle(c).display=="none")return;var y=a.getBoundingClientRect().top+a.offsetHeight/2-c.getBoundingClientRect().top-34;n.style.top=Math.max(14,Math.min(y,c.offsetHeight-82))+"px"}'
            'function go(i){it.forEach(function(e,k){e.classList.toggle("on",k==i);bs[k].setAttribute("aria-expanded",k==i)});pd.forEach(function(e,k){e.classList.toggle("on",k==i)});pos();try{ping()}catch(e){}}'
            'bs.forEach(function(b){b.addEventListener("click",function(){go(+b.dataset.i)})});window.addEventListener("resize",pos);window.addEventListener("load",pos);setTimeout(pos,50)})()</script></section>')
    pl = ''.join(f'<li style="--i:{i}">{t(x)}</li>' for i, x in enumerate(P['pl']))
    pipe_ = f'<section class="a6"><span class="k">{t(P["pipe_k"])}</span><p class="pc">{t(P["proc"])}</p><ol class="pl">{pl}</ol></section>'
    rules_ = f'<section class="fb a7"><div class="in"><span class="k">{t(P["rules_k"])}</span><ol>' + ''.join(f'<li>{t(x)}</li>' for x in P['rules']) + '</ol></div></section>'
    out_ = f'<section class="a8"><span class="k">{t(P["out_k"])}</span><div class="og">' + ''.join(f'<div><b>{t(o[0])}</b><p>{t(o[1])}</p></div>' for o in P['out']) + '</div></section>'
    body = head + menu + hero + top3 + time_ + bars_ + tools_ + rec_ + pipe_ + out_ + foot
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
        (D / 'brands-novo.html').write_text(brands_novo(json.loads(bj.read_text('utf-8')), S), 'utf-8')
    aj = R / 'content' / 'about.json'
    if aj.exists():
        (D / 'about.html').write_text(about(json.loads(aj.read_text('utf-8')), S), 'utf-8')
    ij = R / 'content' / 'ia.json'
    if ij.exists():
        (D / 'ia.html').write_text(ia(json.loads(ij.read_text('utf-8')), S), 'utf-8')
    shutil.copytree(R / 'assets', D / 'assets')

if __name__ == '__main__':
    main()
