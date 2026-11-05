# Paw Note — 14-Day Closed Testing & Release Roadmap

Dokumen ini memuat jadwal rilis, rencana fitur minor/polish, dan teks *Release Notes* resmi (`en-US`) untuk periode Closed Testing 14 hari di Google Play Console (via Testers Community).

---

## 📅 Ringkasan Jadwal Rilis

| Rilis | Hari ke- | Versi | versionCode | Fokus Utama | Target Tanggal |
|---|---|---|---|---|---|
| **Base Build** | Day 0 | `1.0.0` | `1` | Rilis awal closed testing (MVP core + AdMob test) | *Started* |
| **Update #1** | Day 3–4 | `1.0.1` | `2` | UX polish, haptic feedback, search reset, timestamps | *Scheduled* |
| **Update #2** | Day 7–8 | `1.0.2` | `3` | Checklist productivity, word/item counter, duplicate note | *Scheduled* |
| **Update #3** | Day 11–12 | `1.0.3` | `4` | Share note, backup reminder, display & battery polish | *Scheduled* |
| **Production Access** | Day 14+ | `1.0.4` | `5` | Pengajuan akses produksi resmi ke Google Play | *Final Review* |

> ⚠️ **Catatan Penting Google Play Policy & AdMob:**
> - Selama closed testing 14 hari, AdMob **tetap menggunakan Test Ad IDs** (`ca-app-pub-3940256099942544...`).
> - Jangan ganti ke ID iklan produksi sebelum aplikasi disetujui untuk rilis publik (Production Access approved).

---

## 🛠️ Rencana Fitur & Release Notes Siap Pakai

### Update #1 (Hari 3–4) — UX & Responsiveness Polish
- **Versi:** `1.0.1` | **versionCode:** `2`
- **Tujuan:** Menunjukkan responsivitas awal terhadap pengujian pengguna di berbagai tipe perangkat Android.
- **Daftar Perubahan:**
  1. Tombol *clear* (`×`) instan pada kolom pencarian (*search bar*).
  2. Respon getar halus (*gentle haptic feedback*) saat mencentang checklist dan menekan FAB.
  3. Indikator tanggal & waktu pembuatan/pembaruan catatan di editor.
  4. Optimasi transisi *scroll to top* saat berganti kategori hewan.

#### 📋 Google Play Console Release Notes (`en-US`):
```text
<en-US>
What's new in v1.0.1:
• Added quick-clear button (×) in the search bar
• Added gentle haptic feedback on checklist toggle and buttons
• Added note creation timestamp indicator in editor
• Smoother scrolling and category filter transitions
• Minor UI polish and stability improvements
</en-US>
```
*(Karakter: ~285 / 500 — aman dan ringkas)*

---

### Update #2 (Hari 7–8) — Checklist & Productivity Enhancement
- **Versi:** `1.0.2` | **versionCode:** `3`
- **Tujuan:** Menambah fungsi kenyamanan sehari-hari bagi tester aktif tanpa merombak arsitektur single-file.
- **Daftar Perubahan:**
  1. Tombol aksi *Duplicate Note* (duplikasi catatan dengan 1 tap).
  2. Penghitung karakter & jumlah item checklist secara *real-time* di bagian bawah editor.
  3. Opsi cepat untuk membersihkan/menyortir item checklist yang sudah selesai (*completed*).
  4. Ilustrasi *empty state* yang lebih ekspresif saat suatu filter kategori kosong.

#### 📋 Google Play Console Release Notes (`en-US`):
```text
<en-US>
What's new in v1.0.2:
• Added Duplicate Note option for easy note cloning
• Real-time character and checklist item counter in editor
• Quick action to clear or hide completed checklist items
• Enhanced empty state graphics per animal category
• Improved performance and memory efficiency
</en-US>
```
*(Karakter: ~295 / 500 — aman dan ringkas)*

---

### Update #3 (Hari 11–12) — Sharing, Data Safety & Production Readiness
- **Versi:** `1.0.3` | **versionCode:** `4`
- **Tujuan:** Memastikan kesiapan penuh untuk rilis publik, keandalan data lokal, dan kemudahan berbagi catatan.
- **Daftar Perubahan:**
  1. Fitur *Share Note* (membagikan isi catatan sebagai teks biasa via Android native share sheet / clipboard).
  2. Pengingat cadangan (*backup reminder notification/badge*) agar tester menyadari fitur ekspor JSON offline.
  3. Optimasi tampilan layar AMOLED (Samsung One UI / refresh rate 90Hz/120Hz).
  4. Final verifikasi kestabilan database IndexedDB dan kesiapan pengajuan akses produksi.

#### 📋 Google Play Console Release Notes (`en-US`):
```text
<en-US>
What's new in v1.0.3:
• Share notes easily as plain text to other apps
• Added offline backup reminder to keep your notes safe
• Display and animation optimizations for 90Hz/120Hz screens
• Comprehensive bug fixes and final polish for production readiness
• Thank you to all our closed testing community members!
</en-US>
```
*(Karakter: ~330 / 500 — ramah, apresiatif terhadap tester, dan meyakinkan reviewer Google)*

---

## 🚀 Prosedur Eksekusi Tiap Rilis (Quick Guide)

Saat tiba jadwal hari rilis:
1. **Bump Versi di `package.json` & `android/app/build.gradle`:**
   - Ubah `versionCode` (misal `2`, `3`, `4`)
   - Ubah `versionName` (misal `"1.0.1"`, `"1.0.2"`, `"1.0.3"`)
2. **Implementasikan fitur minor di `index.html`.**
3. **Build Android App Bundle (.aab) atau APK:**
   ```bash
   cd android && ./gradlew bundleRelease  # atau assembleRelease
   ```
4. **Upload ke Google Play Console:**
   - Masuk ke menu **Testing > Closed testing**.
   - Klik **Create new release**.
   - Unggah artifact baru.
   - Tempel (*paste*) teks Release Notes yang sudah disediakan di atas.
   - Klik **Save** lalu **Review release** dan **Start rollout to closed testing**.
