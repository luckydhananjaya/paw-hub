# Paw Note

Offline animal-themed notes and checklists for Android, without an account.
App UI and storage logic live in `index.html`; the Android folder-backup bridge
is in `native/PawBackupPlugin.java`.

## Downloads and signing

Automatic builds on `main` publish **debug APKs** in
[Releases](https://github.com/luckydhananjaya/paw-hub/releases).
These are for device checks, not Play Store upload. Different debug signing
keys may prevent updating an existing install; verify your external backup
before uninstalling.

The **Signed Android Release** workflow builds a signed release APK and AAB
using one persistent upload key. It never creates replacement keys and fails
when signing secrets are missing. Download the `PawNote-signed-release` Actions
artifact after a successful run.

- [Signing and closed-testing guide](docs/PLAY-RELEASE.md)
- [Store listing copy and tester checklist](docs/STORE-LISTING.md)
- [Privacy policy](privacy.html) (bundled offline in the app; public web hosting still required)
- [Support / issues](https://github.com/luckydhananjaya/paw-hub/issues)

## One-time signing helper

On your trusted computer, install Java and GitHub CLI, authenticate `gh` with
permission to manage this repository's Actions Secrets, then run:

```sh
python3 scripts/setup-signing.py
```

The helper retains `~/PawNote-signing/paw-upload.jks`, asks for a password without
echoing it, refuses to replace an existing key, asks you to retain a recovery
copy, configures four repository Actions Secrets and requests the signed build.
It does not upload the app to Google Play. Do not paste key material in a chat
or commit it to this public repository.

## Checks

```sh
node --test tests/*.test.cjs
python3 -m py_compile prepare.py scripts/configure-release.py scripts/setup-signing.py
```

PR CI also compiles Android debug APK and unsigned release AAB. Its unsigned AAB
artifact is a compilation check only. Signing validation, Play acceptance and
real-device checks remain separate release gates.
