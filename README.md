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
