"""assets-src/<case>_<secao>.(png|jpg|pdf) -> assets/<case>_<secao>.webp (corta margens, redimensiona, otimiza).
Secoes: discovery, process, outcomes, learnings. Uso: python scripts/prepare_images.py"""
import pathlib, subprocess, tempfile
from PIL import Image, ImageChops
R = pathlib.Path(__file__).parent.parent

def load(p):
    if p.suffix.lower() == '.pdf':
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['pdftocairo', '-png', '-transp', '-r', '200', '-singlefile', str(p), d + '/p'], check=True)
            return Image.open(d + '/p.png').convert('RGBA')
    return Image.open(p).convert('RGBA')

def trim(im, pad=12):
    bg = Image.new('RGBA', im.size, im.getpixel((0, 0)))
    box = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box: return im
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))

for p in sorted((R / 'assets-src').iterdir()):
    if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.pdf'):
        im = load(p) if p.stem.endswith('_hero') else trim(load(p)); im.thumbnail((2400, 1400))
        im.save(R / 'assets' / (p.stem + '.webp'), quality=82, method=6)
        print(p.name, '->', im.size)
