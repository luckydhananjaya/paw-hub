"""One-time local setup. Requires Java keytool and authenticated GitHub CLI.

Run on your trusted computer. Never run in a disposable CI runner.
Private key and recovery information stay outside the repository.
"""
import base64
import getpass
import os
from pathlib import Path
import shutil
import subprocess

REPO = 'luckydhananjaya/paw-hub'


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def main():
    if not all(shutil.which(cmd) for cmd in ('keytool', 'gh')):
        raise SystemExit('Install Java (keytool) and GitHub CLI (gh), then retry.')
    run(['gh', 'auth', 'status'])
    root = Path.home() / 'PawNote-signing'
    root.mkdir(mode=0o700, exist_ok=True)
    root.chmod(0o700)
    keystore = root / 'paw-upload.jks'
    alias = 'paw-upload'
    password = getpass.getpass('Keystore password (existing password if key exists): ')
    if len(password) < 6:
        raise SystemExit('Use at least 6 characters. Nothing was uploaded.')
    env = dict(os.environ, PAW_LOCAL_STORE_PASSWORD=password)
    if not keystore.exists():
        if password != getpass.getpass('Confirm new keystore password: '):
            raise SystemExit('Passwords do not match. Nothing was uploaded.')
        run(['keytool', '-genkeypair', '-keystore', str(keystore), '-alias', alias,
             '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000',
             '-dname', 'CN=Lucky Dhananjaya, OU=Paw Note, C=ID',
             '-storepass:env', 'PAW_LOCAL_STORE_PASSWORD',
             '-keypass:env', 'PAW_LOCAL_STORE_PASSWORD'], env=env)
        keystore.chmod(0o600)
    # Validate before uploading anything; never replace an existing key.
    run(['keytool', '-list', '-keystore', str(keystore), '-alias', alias,
         '-storepass:env', 'PAW_LOCAL_STORE_PASSWORD'], env=env,
        stdout=subprocess.DEVNULL)
    print(f'Key retained at {keystore}. Save an encrypted backup and password separately.')
    if input('Type BACKED UP after saving your recovery copy: ').strip() != 'BACKED UP':
        raise SystemExit('Stopped before uploading secrets. Existing key was preserved.')
    secrets = {
        'PAW_KEYSTORE_BASE64': base64.b64encode(keystore.read_bytes()).decode(),
        'PAW_STORE_PASSWORD': password,
        'PAW_KEY_ALIAS': alias,
        'PAW_KEY_PASSWORD': password,
    }
    for name, value in secrets.items():
        run(['gh', 'secret', 'set', name, '--repo', REPO], input=value,
            text=True, stdout=subprocess.DEVNULL)
        print(f'Configured {name} (value hidden).')
    run(['gh', 'workflow', 'run', 'signed-release.yml', '--repo', REPO,
         '--ref', 'main', '-f', 'version_name=1.0.0'])
    print('Signed release requested. Check Actions for completion and download its artifacts.')


if __name__ == '__main__':
    main()
