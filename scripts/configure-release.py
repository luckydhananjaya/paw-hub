"""Configure a generated Capacitor Android project for repeatable releases."""
import os
import re
from pathlib import Path

def configure(project=Path("android/app/build.gradle"), signed=False):
    code = int(os.environ.get("PAW_VERSION_CODE", "1"))
    if code < 1 or code > 2100000000:
        raise ValueError("Invalid Android version code")
    name = os.environ.get("PAW_VERSION_NAME", "1.0.0")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.-]+)?", name):
        raise ValueError("Invalid version name")
    text = project.read_text()
    text, n = re.subn(r"versionCode\s+\d+", f"versionCode {code}", text, count=1)
    if n != 1:
        raise ValueError("Missing versionCode")
    text, n = re.subn(r'versionName\s+"[^"]+"', f'versionName "{name}"', text, count=1)
    if n != 1:
        raise ValueError("Missing versionName")
    if signed:
        required = ["PAW_KEYSTORE_PATH", "PAW_STORE_PASSWORD", "PAW_KEY_ALIAS", "PAW_KEY_PASSWORD"]
        if not all(os.environ.get(key) for key in required):
            raise ValueError("Missing signing environment variables")
        if not Path(os.environ["PAW_KEYSTORE_PATH"]).is_file():
            raise ValueError("Keystore file not found")
        block = """
    signingConfigs {
        pawRelease {
            storeFile file(System.getenv("PAW_KEYSTORE_PATH"))
            storePassword System.getenv("PAW_STORE_PASSWORD")
            keyAlias System.getenv("PAW_KEY_ALIAS")
            keyPassword System.getenv("PAW_KEY_PASSWORD")
        }
    }
"""
        if "buildTypes {" not in text or "release {" not in text:
            raise ValueError("Unsupported Android Gradle template")
        text = text.replace("    buildTypes {", block + "    buildTypes {", 1)
        text = text.replace("release {", "release {\n            signingConfig signingConfigs.pawRelease", 1)
    project.write_text(text)

if __name__ == "__main__":
    import sys
    configure(signed="--signed" in sys.argv)
