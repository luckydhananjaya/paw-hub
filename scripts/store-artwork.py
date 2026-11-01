"""Render Play artwork using the existing app paw drawing, without new branding.

Requires Pillow and DejaVu Sans (available on Ubuntu). Output PNGs are opaque.
"""
import ast
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    source = ast.parse(Path('prepare.py').read_text())
    android = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'android')
    paw_function = next(n for n in android.body if isinstance(n, ast.FunctionDef) and n.name == 'paw')
    namespace = {'Image': Image, 'ImageDraw': ImageDraw, 'INK': (28, 27, 26, 255)}
    exec(compile(ast.Module(body=[paw_function], type_ignores=[]), 'prepare.py', 'exec'), namespace)
    paw = namespace['paw']
    output = Path('store-assets')
    output.mkdir(exist_ok=True)
    icon = Image.new('RGBA', (512, 512), '#FFD84D')
    icon.alpha_composite(paw(512, 0.72))
    icon.convert('RGB').save(output / 'icon-512.png')
    feature = Image.new('RGB', (1024, 500), '#FFF6E3')
    draw = ImageDraw.Draw(feature)
    draw.rounded_rectangle((54, 82, 390, 418), radius=72, fill='#FFD84D')
    feature.paste(paw(300, 0.72), (72, 100), paw(300, 0.72))
    draw.text((444, 160), 'Paw Note', font=ImageFont.truetype('DejaVuSans-Bold.ttf', 80), fill='#1C1B1A')
    draw.text((450, 265), 'A little space for your thoughts.',
              font=ImageFont.truetype('DejaVuSans.ttf', 26), fill='#514A42')
    feature.save(output / 'feature-1024x500.png')
    print('Created 512×512 icon and 1024×500 feature graphic.')


if __name__ == '__main__':
    main()
