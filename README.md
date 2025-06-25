# Aplikasi Analisis Kerawanan Wilayah

Aplikasi web berbasis Flask untuk menganalisis potensi kerawanan wilayah berdasarkan data tokoh dan berita terkini.

## Fitur

- Membaca data tokoh dari file Excel (`bahan-asops.xlsx`)
- Membaca paragraf berita dari file Word (`berita.docx`)
- Mencocokkan tokoh dengan paragraf berita menggunakan fuzzy matching
- Analisis paragraf berita menggunakan model lokal spaCy tanpa memerlukan API eksternal
- Menghasilkan ringkasan dan rekomendasi menggunakan LLM lokal (Llama-cpp atau TinyLlama)
- Menampilkan hasil analisis dalam bentuk tabel dengan fitur filtering

## Struktur Folder

```
/analisis_risiko/
├── app.py
├── templates/
│   └── index.html
├── models/                   # Folder untuk model LLM
│   └── llama-2-7b-chat.Q4_K_M.gguf  # Optional - letakkan model GGUF di sini
├── bahan-asops.xlsx
├── berita.docx
├── requirements.txt
└── README.md
```

## Instalasi

1. Clone repositori ini atau unduh file-file ke komputer lokal Anda.
2. Pastikan Python 3.8+ sudah terinstal di komputer Anda.
3. Instal dependensi yang diperlukan:

```bash
pip install -r requirements.txt
```

4. Instal model spaCy yang diperlukan:

```bash
# Untuk model bahasa Indonesia (jika tersedia)
python -m spacy download id_core_news_lg

# Atau untuk model bahasa Inggris
python -m spacy download en_core_web_lg

# Atau model yang lebih kecil jika memori terbatas
python -m spacy download en_core_web_sm
```

5. (Opsional) Untuk menggunakan LLM lokal dengan performa yang lebih baik, unduh model GGUF:

```bash
# Buat folder models jika belum ada
mkdir -p models

# Unduh model Llama GGUF (contoh: Llama-2-7B-Chat yang dioptimasi)
# Bisa diunduh dari https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
# Letakkan file .gguf di folder models/
# Contoh nama file: llama-2-7b-chat.Q4_K_M.gguf
```

## Persiapan Data

1. **File Excel (`bahan-asops.xlsx`)**
   - Buat file Excel dengan kolom: Nama, Jabatan, Jenis Kelamin, dan Tingkatan
   - Isi dengan data tokoh-tokoh yang ingin dianalisis

2. **File Word (`berita.docx`)**
   - Buat file Word berisi paragraf-paragraf berita terkait tokoh-tokoh tersebut
   - Setiap paragraf akan dianalisis secara terpisah

## Menjalankan Aplikasi

1. Buka terminal dan navigasikan ke folder aplikasi
2. Jalankan aplikasi dengan perintah:

```bash
python app.py
```

3. Buka browser dan akses `http://127.0.0.1:5001/`

## Penggunaan

1. Aplikasi akan otomatis memproses data dari file Excel dan Word saat halaman dimuat
2. Hasil analisis ditampilkan dalam tabel dengan warna berbeda berdasarkan kategori risiko:
   - Hijau: Risiko rendah
   - Kuning: Risiko sedang
   - Merah: Risiko tinggi
3. Gunakan filter untuk menyaring hasil berdasarkan kategori risiko

## Cara Kerja LLM Lokal

Aplikasi ini menggunakan pendekatan bertingkat untuk generasi teks:

1. **Deteksi Risiko**: Menggunakan spaCy atau analisis teks dasar untuk mendeteksi faktor risiko dan menghitung skor
2. **Generasi Ringkasan**: Menggunakan LLM lokal untuk meringkas teks dengan fokus pada faktor risiko
3. **Generasi Rekomendasi**: Menggunakan LLM lokal untuk membuat rekomendasi berdasarkan kategori risiko dan urgensi

Aplikasi akan mencoba beberapa metode LLM secara berurutan:
1. Model GGUF lokal melalui llama-cpp-python (jika tersedia di folder models/)
2. Model TinyLlama dari Hugging Face (diunduh saat pertama kali dijalankan)
3. Fallback ke metode dasar jika kedua opsi di atas tidak tersedia

## Contoh Format Hasil Analisis

```json
{
  "ringkasan": "Gubernur Aceh Abdul Rahman menggelar pertemuan untuk menengahi konflik lahan antara masyarakat dan perusahaan perkebunan kelapa sawit.",
  "skor_risiko": 65,
  "persentase_kerawanan": "65%",
  "kategori": "TINGGI",
  "faktor_risiko": ["konflik", "pertikaian"],
  "rekomendasi": "Segera lakukan koordinasi dengan pihak terkait dan siapkan tim mediasi untuk mencegah eskalasi konflik.",
  "urgensi": "SEGERA"
}
```

## Catatan Penting

- Aplikasi ini menggunakan model NLP dan LLM lokal untuk analisis teks, sehingga tidak memerlukan koneksi internet atau API key
- Kualitas analisis bergantung pada model yang digunakan
- Performa generasi teks akan lebih baik jika menggunakan model GGUF yang diunduh secara terpisah
- Aplikasi ini menjalankan semua proses secara lokal dan menyimpan hasil analisis ke file JSON di folder `cache`
- Jika mengalami kendala memori saat menjalankan model LLM besar, gunakan model yang lebih kecil atau atur parameter n_threads dan n_ctx sesuai kebutuhan 