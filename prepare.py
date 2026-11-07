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
    # Install the app-local Storage Access Framework plugin.
    package_dir = main + 'java/com/luckydhananjaya/pawnote/'
    os.makedirs(package_dir, exist_ok=True)
    shutil.copy('native/PawBackupPlugin.java', package_dir + 'PawBackupPlugin.java')
    open(package_dir + 'MainActivity.java', 'w').write("""package com.luckydhananjaya.pawnote;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
public class MainActivity extends BridgeActivity {
    @Override public void onCreate(Bundle savedInstanceState) {
        registerPlugin(PawBackupPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
""")
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

    import json, re
    if os.path.exists('android/app/build.gradle'):
        bg = open('android/app/build.gradle').read()
        cur_code_m = re.search(r'versionCode (\d+)', bg)
        cur_code = int(cur_code_m.group(1)) if cur_code_m else 1002

        v_name = None
        v_code = None

        if os.path.exists('package.json'):
            pkg = json.load(open('package.json'))
            v_name = pkg.get('version')
            v_code = pkg.get('versionCode') or pkg.get('androidVersionCode')

        # Environment variable override takes highest precedence
        env_code = os.environ.get('VERSION_CODE') or os.environ.get('PAW_VERSION_CODE')
        if env_code:
            try:
                v_code = int(env_code)
            except ValueError:
                raise ValueError(f"Invalid versionCode in environment: {env_code}")

        if v_code is None:
            v_code = cur_code

        # Strict validation: Play Console previously accepted versionCode 1001
        # Any new release build MUST be strictly > 1001 and <= 2100000000
        LAST_ACCEPTED_VERSION_CODE = 1001
        if not isinstance(v_code, int) or v_code <= LAST_ACCEPTED_VERSION_CODE or v_code > 2100000000:
            raise ValueError(
                f"Invalid versionCode {v_code}: must be an integer strictly greater than "
                f"the last uploaded Play Console versionCode ({LAST_ACCEPTED_VERSION_CODE}) "
                f"and <= 2100000000."
            )

        if v_name:
            bg = re.sub(r'versionName "[^"]+"', f'versionName "{v_name}"', bg)
        bg = re.sub(r'versionCode \d+', f'versionCode {v_code}', bg)

        open('android/app/build.gradle', 'w').write(bg)
        print(f'Synced Android version: {v_name or "unchanged"} (versionCode: {v_code})')

{'fonts': fonts, 'android': android}[sys.argv[1]]()
print('done:', sys.argv[1])
