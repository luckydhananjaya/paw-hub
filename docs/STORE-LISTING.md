# Paw Note — Play Console copy and test plan

## Listing copy (English)

App name: Paw Note

Short description:
Cute offline notes and checklists, with animal themes and folder backups.

Full description:

Keep everyday thoughts, plans, and lists together with Paw Note.

Choose an animal theme, write a quick note, or switch to a checklist. Search your
notes, filter by animal, and pin the ones you want to find first.

- Write and edit notes offline, without creating an account.
- Use dog, bunny, dinosaur, elephant, and cat themes.
- Switch between plain text and checklists.
- Search notes and pin favorites.
- Save backups to a folder you choose through Android.
- Restore a saved backup and merge it with your existing notes.

Your notes stay on your device unless you choose to create a folder backup.
Available cloud folders depend on the storage providers installed on your phone.
After reinstalling, select the same backup folder to restore your notes.
Automatic backups run while the app is open after you enable Backup.

## Closed-test release notes

First Paw Note test release: offline notes, animal themes, checklists, search,
pinning, folder backups, and restore. Please test saving notes, reopening the app,
and restoring a backup from your selected folder. Advertising is configured for
Google test ads in this build.

## Console intake — verified versus undecided

| Field | Prepared value / remaining action |
| --- | --- |
| Package | `com.luckydhananjaya.pawnote` |
| Category | Productivity (proposed) |
| App access | No account or login required; core features work offline |
| Ads | Included AdMob SDK and test-ad configuration; do not claim ad-free |
| Price | Free app (proposed); no purchases implemented |
| Privacy | Bundled `privacy.html`; publish to a public webpage and verify URL before submitting |
| Support | Repository issue tracker is available; Play support email still needs owner-provided address |
| Audience | Owner must select actual intended audience; do not infer children from animal artwork |
| Content rating | Complete IARC using actual app functionality; no rating claimed here |
| Data safety | Account for included AdMob SDK as well as app code; see below |
| Artwork | `store-assets/icon-512.png` and `store-assets/feature-1024x500.png` are ready; genuine device screenshots still required |

## Data safety preparation

The app stores note content locally and sends no note content to a developer
backend. Optional JSON backups use a user-selected Android document provider.
There is no account registration or developer account-deletion service.

Do not select “no data collected” just because notes stay local. Google's SDK
disclosure lists IP/approximate location, interactions, diagnostics, and device
or account identifiers. Check the exact SDK version resolved in the release,
the final merged manifest, consent behavior and actual traffic before completing
the form. Test ad IDs alone do not prove that the SDK collects no data.

Sources checked November 1, 2026:
- https://developers.google.com/admob/android/privacy/play-data-disclosure
- https://support.google.com/googleplay/android-developer/answer/10144311

## Tester instructions

Use the Play Console opt-in link after the closed track is available. Install
from Google Play for closed-test participation; a sideload is a separate test.
Keep using the app naturally and report concrete problems through the support
tracker. Do not send private note text, backups or passwords in public issues.

Please check:
1. Make a note, close the editor, force-stop the app, and reopen it.
2. Search, pin, edit, change animal theme, and create/check checklist items.
3. Back up to a local folder, edit a note, then restore an earlier version.
4. If available, repeat with a writable cloud-provider folder and check sync.
5. Verify backup files outside the app before uninstalling. Reinstall and select
   the same folder; restore and compare note text and checklist state.
6. Install a higher-version release from the same Play track and check that
   notes and folder access remain. A debug APK may use a different signing key.
7. Delete all notes, restart, and confirm sample notes do not reappear.
8. Test airplane mode, low storage and revoked folder permission. Failed backup
   must not be presented as successful.

## Release gates still requiring account/device access

- Persistent upload key configured and recovery copy retained.
- Signed-release workflow successful; APK/AAB signature reports inspected.
- Public privacy URL and verified support email supplied.
- Prepared icon/feature graphic and genuine device screenshots uploaded.
- Final Data safety, audience, ads and content-rating forms submitted accurately.
- AAB accepted by Play validation (including target SDK/native-library checks).
- Closed track approved/available; tester invitations and opt-ins complete.

Repository CI success is a compilation result, not Play approval or completion
of a real-device test. No Play Console upload is performed by this repository.
