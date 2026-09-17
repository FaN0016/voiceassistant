# 🎙️ Asisten AI - Hatsune Miku Voice Assistant

Proyek asisten suara AI lokal berbahasa Indonesia dengan kepribadian dan karakter suara **Hatsune Miku**. Sistem ini mengintegrasikan pendengaran otomatis (*Speech-to-Text*), pemrosesan bahasa alami dengan memori percakapan (*LLM*), sintesis suara (*TTS*), dan konversi karakter vokal (*Retrieval-based Voice Conversion / RVC*).

---

## 🏗️ Arsitektur & Pipeline Sistem

```
[ Microphone ]
      │ (Deteksi Suara / VAD)
      ▼
[ faster-whisper ] ──► Teks Ucapan (Bahasa Indonesia)
      │
      ▼
[ Wake Word Filter ] ──► Validasi pemanggilan ("Miku")
      │
      ▼
[ Ollama (Qwen 2.5:1.5b) ] ◄──► [ memori_miku.json ] (Riwayat Percakapan)
      │ (Generate Jawaban Teks)
      ▼
[ Microsoft Edge-TTS ] ──► Suara Dasar Wanita (id-ID-GadisNeural)
      │
      ▼
[ RVC Inference (miku.pth) ] ──► Konversi ke Karakter Vokal Hatsune Miku
      │
      ▼
[ Pygame Audio Playback ] ──► Speaker Output
```

---

## 📦 Komponen & Teknologi yang Digunakan

| Komponen | Teknologi / Model | Fungsi Utama |
| :--- | :--- | :--- |
| **Voice Detection (VAD)** | `speech_recognition` | Mendengarkan mic secara pasif tanpa tombol fisik |
| **STT (Transkripsi)** | `faster-whisper` (`medium`, `int8`, `cpu`) | Mengubah audio ucapan menjadi teks bahasa Indonesia |
| **Otak AI (LLM)** | `ollama` (`qwen2.5:1.5b`) | Memahami pertanyaan, berpikir, dan menghasilkan jawaban |
| **Memori AI** | `memori_miku.json` (JSON format) | Menyimpan konteks percakapan terakhir (10 sesi terakhir) |
| **TTS Dasar** | `edge-tts` (`id-ID-GadisNeural`) | Menghasilkan suara vokal dasar natural |
| **Voice Conversion** | `rvc-python` (`miku.pth`, `rmvpe`) | Mengubah timbre suara dasar menjadi suara Miku |
| **Audio Output** | `pygame.mixer` | Memutar file audio akhir ke speaker pengguna |

---

## 🎯 Panduan: Apa yang Harus Digunakan & Apa yang Jangan Digunakan (Saat Ini)

### ✅ APA YANG DIGUNAKAN & DIPERTAHANKAN (Recommended)
1. **`faster-whisper` (int8 quantization)**:
   - Sangat efisien di CPU dibandingkan model whisper bawaan OpenAI.
   - Pilihan model `medium` atau `small` untuk bahasa Indonesia sudah sangat akurat.
2. **`edge-tts` (`id-ID-GadisNeural`)**:
   - Gratis, cepat, tidak membebani komputasi lokal, dan artikulasi bahasa Indonesia sangat jelas.
3. **`ollama` dengan `qwen2.5:1.5b`**:
   - Cepat, ringan di RAM/CPU, dan sangat mahir memahami bahasa Indonesia santai/sopan.
4. **Sliding Memory Window (Maksimal 10 Percakapan)**:
   - Membatasi konteks agar LLM tidak *out-of-memory* atau mengalami penurunan performa berpikir.
5. **Virtual Environment Terisolasi (`env_asisten_miku`)**:
   - Menjaga dependensi PyTorch, RVC, dan audio library tidak konflik dengan sistem global.

---

### ⚠️ APA YANG JANGAN DIGUNAKAN / HARUS DIPERBAIKI (Not Recommended / Fix Now)

1. ❌ **JANGAN Load Model RVC Berulang Kali di Dalam Fungsi**:
   - **Masalah Saat Ini**: Di `asisten_suara.py`, baris `rvc.load_model("miku.pth")` dipanggil di dalam fungsi `berbicara()`. Ini memuat ulang model puluhan MB dari disk setiap kali asisten berbicara, membuat latensi bertambah 2–5 detik.
   - **Solusi**: Pindahkan `rvc.load_model("miku.pth")` ke bagian inisialisasi di awal script (hanya dijalankan 1x saat aplikasi start).

2. ❌ **JANGAN Memeriksa Kata Kunci yang Salah pada Wake Word**:
   - **Masalah Saat Ini**: Di baris 148 terdapat `if "test" in teks_user.lower():`. Ini menyebabkan asisten hanya merespons jika Anda mengucapkan kata `"test"`, bukan `"miku"`.
   - **Solusi**: Ubah kondisi menjadi `if "miku" in teks_user.lower():`.

3. ❌ **JANGAN Menyimpan File Zip Besar di Direktori Aktif Git / Project**:
   - File `MikuAI.zip` (426 MB) memakan ruang disk ganda dan memperlambat pencarian/backup. Simpan arsip di luar folder proyek atau masukkan ke `.gitignore`.

4. ❌ **JANGAN Mengimpor Pustaka yang Tidak Terpakai**:
   - `pyaudio` dan `wave` diimpor di baris atas, tetapi proses perekaman sudah ditangani oleh `speech_recognition`. Menghapus impor yang tidak terpakai mempercepat waktu startup script.

5. ❌ **HINDARI Menjalankan RVC di CPU jika Membutuhkan Realtime Super Cepat**:
   - RVC `rmvpe` pada CPU membutuhkan waktu 3–8 detik untuk mengonversi satu kalimat.
   - *Rekomendasi*: Jika memiliki GPU NVIDIA, ganti `device="cpu"` menjadi `device="cuda"`. Jika tidak ada GPU dan ingin respon instan (< 1 detik), gunakan langsung `edge-tts` dengan *pitch* tinggi tanpa RVC sebagai mode alternatif.

---

## 🚀 Cara Menjalankan Project

### 1. Prasyarat
- **Python 3.10** (Sudah terpasang di `env_asisten_miku`)
- **Ollama**: Pastikan Ollama sudah berjalan dan model telah diunduh:
  ```bash
  ollama run qwen2.5:1.5b
  ```
- **Mikrofon & Speaker** yang aktif di Windows.

### 2. Aktivasi Virtual Environment
Buka PowerShell di folder project:
```powershell
.\env_asisten_miku\Scripts\Activate.ps1
```

### 3. Menjalankan Asisten
```powershell
python asisten_suara.py
```

---

## 🛠️ Rekomendasi Struktur File Ideal

```
AssistenAI/
├── asisten_suara.py         # Skrip utama asisten AI
├── memori_miku.json         # Penyimpanan riwayat percakapan
├── miku.pth                 # Bobot model suara RVC Hatsune Miku
├── miku.index               # Index feature RVC (opsional untuk akurasi)
├── README.md                # Dokumentasi lengkap proyek
├── .gitignore               # Daftar file yang diabaikan (zip, temp audio)
└── env_asisten_miku/        # Virtual environment Python
```

---

## 🔧 Panduan Troubleshooting & FAQ

- **Peringatan PyTorch 2.6 (`weights_only=True`)**:
  - Script sudah menyertakan monkeypatch di baris 1-7 agar model `.pth` RVC yang dibuat dengan PyTorch lama tetap dapat dimuat dengan aman.
- **Asisten Tidak Merespons Suara**:
  - Pastikan mikrofon default Windows aktif.
  - Periksa apakah ambience noise di ruangan terlalu bising (atur `duration=1` di `adjust_for_ambient_noise`).
- **Ollama Connection Refused**:
  - Jalankan aplikasi Ollama di system tray Windows atau ketik `ollama serve` di terminal terpisah.
