# Portfolio — Product Design (embed para o Wix)

- `content/cases.json`: todo o texto, EN e PT (edite aqui).
- `pdf/`: nomes `case_EN.pdf`, `case_PT.pdf`, `case_EN_mobile.pdf`, `case_PT_mobile.pdf` (case = agro_flow, planta_pacheco, tede). Mobile aparece em telas até 700px; o que faltar cai no EN.
- `python build.py` gera `dist/index.html` (precisa de poppler-utils e pillow).
- Push na `main` = deploy no GitHub Pages (Settings → Pages → Source: GitHub Actions).

## No Wix
Add → Embed Code → Embed a Site → URL do GitHub Pages (`?lang=pt` força idioma). Para sincronizar idioma e altura (Velo, não testado):

```js
import wixWindow from 'wix-window';
$w.onReady(() => {
  const h = $w('#html1');
  h.postMessage({ lang: wixWindow.multilingual.currentLanguage });
  h.onMessage(e => { if (e.data.h) h.height = e.data.h; });
});
```

## Figma
Cole o link do arquivo/frame em `"figma"` no `cases.json` (compartilhamento: qualquer pessoa com o link pode ver). O build converte em embed com zoom e arraste.

## Migração (site funcionando sem o Wix)
O plano do Wix renova em 19/dez/2026. Enquanto isso, o Wix continua no ar e as páginas embutidas não mudam (no modo embed o menu e o rodapé ficam escondidos).

Feito:
- Menu igual ao do Wix atual (PRODUCT, PHARMA, HEALTH, BRAND, ABOUT, IA + DESIGN), apontando para as páginas do próprio site; Contato faz parte de Sobre. Home e Other Media saíram, como no Wix.
- `404.html`, `sitemap.xml`, `robots.txt`, favicon e descrição para buscadores/LinkedIn.
- Endereços do Wix, atuais e antigos (`/pharma`, `/health`, `/brands`, `/about`, `/ia-design`, `/farmacêutico`, `/impressos`, `/sobre`…), redirecionam para a página nova — só passam a valer quando o domínio apontar para o GitHub. Lista em `site.wix_redirects` no `cases.json`.

Falta decidir:
- **Other Media**: conteúdo ainda só no Wix (`/videos`), fora do menu.
- Domínio: quando aprovar, trocar `site.base_url` para `https://www.suelenmagaa.com.br/`, criar o arquivo `CNAME` e apontar o DNS no Registro.br para o GitHub Pages. Não fazer antes de tudo aprovado — o CNAME redireciona o github.io para o domínio.
