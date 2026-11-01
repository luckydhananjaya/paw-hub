"""Called by the GitHub workflow. Two modes:
   python3 prepare.py fonts    -> copy fonts into www/fonts
   python3 prepare.py android  -> add icons, colors and AdMob test ID to the Android project
"""
import shutil, sys, os

def fonts():
    os.makedirs('www/fonts', exist_ok=True)
    for pkg, names in {
        'caveat-brush': ['caveat-brush-latin-400-normal.woff2', 'caveat-brush-latin-ext-400-normal.woff2'],
        'itim': ['itim-latin-400-normal.woff2', 'itim-latin-ext-400-normal.woff2'],
    }.items():
        for n in names:
            shutil.copy(f'node_modules/@fontsource/{pkg}/files/{n}', 'www/fonts/' + n)

def android():
    from PIL import Image, ImageDraw
    main = 'android/app/src/main/'
    p = main + 'AndroidManifest.xml'
    s = open(p).read()
    if 'APPLICATION_ID' not in s:
        s = s.replace('        <provider', '''        <!-- Google TEST AdMob App ID. Replace with the real one before release. -->
        <meta-data
            android:name="com.google.android.gms.ads.APPLICATION_ID"
            android:value="ca-app-pub-3940256099942544~3347511713" />

        <provider''', 1)
        s = s.replace('<uses-permission android:name="android.permission.INTERNET" />',
                      '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />')
        open(p, 'w').write(s)
    open(main + 'res/values/ic_launcher_background.xml', 'w').write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#FFD84D</color>\n</resources>\n')
    INK = (28, 27, 26, 255); YEL = (255, 216, 77, 255)
    def paw(size, scale):
        S = size * 4
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        u = S * scale / 64.0; o = (S - 64 * u) / 2
        def el(cx, cy, rx, ry, rot=0):
            e = Image.new('RGBA', (S, S), (0, 0, 0, 0))
            X = o + cx * u; Y = o + cy * u
            ImageDraw.Draw(e).ellipse([X - rx * u, Y - ry * u, X + rx * u, Y + ry * u], fill=INK)
            if rot: e = e.rotate(-rot, center=(X, Y), resample=Image.BICUBIC)
            im.alpha_composite(e)
        el(32, 43, 14, 11); el(13, 29, 6, 8, -20); el(25, 17, 6, 8.5, -8); el(39, 17, 6, 8.5, 8); el(51, 29, 6, 8, 20)
        return im.resize((size, size), Image.LANCZOS)
    fg = {'mdpi': 108, 'hdpi': 162, 'xhdpi': 216, 'xxhdpi': 324, 'xxxhdpi': 432}
    lg = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
    for k in fg:
        d = main + f'res/mipmap-{k}/'
        paw(fg[k], 0.50).save(d + 'ic_launcher_foreground.png')
        n = lg[k]
        sq = Image.new('RGBA', (n * 4, n * 4), (0, 0, 0, 0))
        ImageDraw.Draw(sq).rounded_rectangle([0, 0, n * 4 - 1, n * 4 - 1], radius=n * 0.88, fill=YEL)
        sq = sq.resize((n, n), Image.LANCZOS); sq.alpha_composite(paw(n, 0.72)); sq.save(d + 'ic_launcher.png')
        rd = Image.new('RGBA', (n * 4, n * 4), (0, 0, 0, 0))
        ImageDraw.Draw(rd).ellipse([0, 0, n * 4 - 1, n * 4 - 1], fill=YEL)
        rd = rd.resize((n, n), Image.LANCZOS); rd.alpha_composite(paw(n, 0.66)); rd.save(d + 'ic_launcher_round.png')

{'fonts': fonts, 'android': android}[sys.argv[1]]()
print('done:', sys.argv[1])
