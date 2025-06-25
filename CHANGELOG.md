# Changelog - Aplikasi Analisis Risiko

## Versi 2.0 - Offline LLM (Juni 2025)

### Perubahan Utama
- **Penghapusan Ketergantungan pada API Eksternal**: Aplikasi sekarang sepenuhnya offline, tidak memerlukan koneksi internet atau API key
- **Implementasi LLM Lokal**: Menggunakan model LLM lokal untuk menghasilkan ringkasan dan rekomendasi
- **Multi-level Fallback**: Sistem akan mencoba beberapa metode secara berurutan jika metode utama gagal

### Fitur Baru
- **Dukungan Model GGUF**: Kemampuan menggunakan model GGUF (Llama-2, Mistral, dll) melalui llama-cpp-python
- **TinyLlama Fallback**: Menggunakan model TinyLlama (1.1B) sebagai alternatif jika model GGUF tidak tersedia
- **Lazy Loading**: Model dimuat hanya saat dibutuhkan untuk menghemat memori
- **Thread Safety**: Perbaikan masalah threading untuk stabilitas aplikasi
- **Error Handling**: Penanganan kesalahan yang lebih baik di seluruh aplikasi

### Perubahan Teknis
- Penambahan thread lock untuk mencegah race conditions saat menggunakan model LLM
- Implementasi lazy loading untuk model NLP dan LLM
- Pemisahan inisialisasi model ke fungsi terpisah untuk load on demand
- Perbaikan bug pada recursive mutex
- Penambahan traceback untuk debugging yang lebih baik

### Alat Bantu
- **Script Download Model**: Utility untuk mendownload model yang diperlukan (`download_models.py`)
- **Script Startup**: Script shell dan batch untuk otomatisasi setup (`run.sh` dan `run.bat`)
- **Folder Models**: Struktur folder untuk menyimpan model GGUF
- **Dokumentasi Lengkap**: Petunjuk terperinci dalam README.md

### Dependensi Baru
- llama-cpp-python: Untuk menjalankan model GGUF
- transformers: Untuk menjalankan model TinyLlama
- torch: Framework backend untuk transformers
- sentencepiece: Untuk tokenisasi teks
- tqdm: Untuk progress bar saat download model
- requests: Untuk download model dari internet

## Instruksi Upgrade

1. Jalankan `pip install -r requirements.txt` untuk menginstal dependensi baru
2. Jalankan `python download_models.py --all` untuk mendownload model yang diperlukan
3. (Opsional) Download model GGUF untuk performa yang lebih baik dan letakkan di folder `models/`
4. Jalankan aplikasi dengan `python app.py` atau gunakan script `run.sh` / `run.bat` 