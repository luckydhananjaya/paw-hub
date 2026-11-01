# Paw Note: signed release and Google Play closed testing

## Signing setup (one time)

Never commit a private keystore, its base64 encoding, or passwords. Keep an encrypted
offline copy of the keystore and passwords. Do not reuse GetLuckyFit signing keys.

1. On a trusted computer with Java installed, generate an upload key:
   `keytool -genkeypair -v -keystore paw-upload.jks -alias paw-upload -keyalg RSA -keysize 2048 -validity 10000`
   Keytool prompts for passwords and identity; no passwords belong in shell history.
2. Base64-encode that file locally. On macOS: `base64 -i paw-upload.jks -o paw-upload.base64`.
   On Linux: `base64 -w 0 paw-upload.jks > paw-upload.base64`.
   Base64 is NOT encryption. Treat this file as the private key.
3. In GitHub Settings > Environments, create `android-release`, restrict deployment to main,
   then add these environment secrets (repository Actions secrets also work):
   - PAW_KEYSTORE_BASE64: the base64 file contents
   - PAW_STORE_PASSWORD: keystore password
   - PAW_KEY_ALIAS: paw-upload
   - PAW_KEY_PASSWORD: key password (often the same as the keystore password)
4. Save the original keystore in a password manager or encrypted offline storage.
   Delete the temporary base64 file after configuring GitHub.
5. Run Actions > Signed Android Release > Run workflow on main.

The workflow does not generate replacement keys. It fails if secrets are absent.
It produces a signed AAB and APK, certificate, checksums and version metadata as a
GitHub Actions artifact. Secrets/private keys are never uploaded as artifacts.
Download within 30 days; retain releases in your own secure archive.

## Versions

Package ID: com.luckydhananjaya.pawnote
Version name: workflow input, default 1.0.0.
Version code: 1000 + the Signed Android Release workflow run number.
Use a new workflow run for a new release (not a rerun of the same run).
If a higher version code is already in Play Console, adjust this scheme before uploading.

## Update behavior

Debug Build 11 used an ephemeral debug key. A newly signed APK cannot update it.
First verify your external folder backup and restore before migrating installations.
Subsequent sideload APKs built with the same key can update each other.
Do NOT rotate the keystore between releases.

Choose Google-generated Play App Signing for Google Play. Our key is then the
upload key, while Google signs installed Play APKs with its app-signing key.
Consequently the sideload release APK and Play install may have different signers;
do not promise direct updates between those channels. Once installed from Play,
keep using Play for updates and validate data retention there.

## Closed testing in Play Console

1. Create Paw Note as an app (default language English), or open its existing entry.
   Confirm its permanent package ID matches the AAB before publishing.
2. Complete the dashboard's required app setup, store listing and app-content forms:
   privacy-policy URL, Data safety, ads declaration, content rating, target audience,
   app access and any account/device verification Google requests.
3. Under Test and release > Testing > Closed testing, create/open a track.
4. Create a release; enroll in Play App Signing and upload PawNote-release.aab.
5. Add testers by email list or Google Group and configure countries.
6. Resolve Play Console validation errors; send for review/roll out as required.
7. Share the opt-in URL with testers AFTER the track is available.
   Testers must opt in; a direct sideload APK is not a Play closed-test enrollment.
8. For new personal developer accounts, Google's current production-access requirement
   is at least 12 continuously opted-in testers for 14 consecutive days. Check the
   account dashboard for the requirement that applies to this account.

## Remaining readiness checks

- Run a real Play-installed update test: create notes, install higher-version Play
  release, confirm notes and folder permission remain.
- Test Backup/Restore and uninstall/reinstall with the same selected folder.
  User has reported local and available cloud provider restoration working in Build 11.
- Test IDs are still used for AdMob; there is no real-ad configuration yet.
  Ads SDK behavior must be reflected accurately in privacy/Data safety declarations.
- No Google sign-in or Paw Note server database. Cloud folder behavior is delegated
  to the selected Android document provider.
- No Play upload/review has been performed by the repository workflow.
- Verify target SDK and any 16 KB page-size/native library requirements against Play's
  actual AAB validation. Passing a Gradle build alone does not establish store approval.

Official references:
- https://developer.android.com/studio/publish/app-signing
- https://support.google.com/googleplay/android-developer/answer/9845334
- https://support.google.com/googleplay/android-developer/answer/14151465
