# Aplikasi Analisis Kerawanan Wilayah

Aplikasi web berbasis Flask untuk menganalisis potensi kerawanan wilayah berdasarkan data tokoh dan berita terkini.

## Fitur

- Membaca data tokoh dari file Excel (`bahan-asops.xlsx`)
- Membaca paragraf berita dari file Word (`berita.docx`)
- Mencocokkan tokoh dengan paragraf berita menggunakan fuzzy matching
- Analisis paragraf berita menggunakan model Meta Llama 4 Maverick via OpenRouter API
- Menampilkan hasil analisis dalam bentuk tabel dengan fitur filtering

## Struktur Folder

```
/analisis_risiko/
├── app.py
├── templates/
│   └── index.html
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

3. Buka browser dan akses `http://127.0.0.1:5000/`

## Penggunaan

1. Aplikasi akan otomatis memproses data dari file Excel dan Word saat halaman dimuat
2. Hasil analisis ditampilkan dalam tabel dengan warna berbeda berdasarkan kategori risiko:
   - Hijau: Risiko rendah
   - Kuning: Risiko sedang
   - Merah: Risiko tinggi
3. Gunakan filter untuk menyaring hasil berdasarkan kategori risiko

## Contoh Response JSON dari Llama 4 Maverick

```json
{
  "ringkasan": "Gubernur Aceh Abdul Rahman menggelar pertemuan untuk menengahi konflik lahan antara masyarakat dan perusahaan perkebunan kelapa sawit dengan membentuk tim mediasi.",
  "skor": 65,
  "kategori": "sedang"
}
```

## Catatan Penting

- API key OpenRouter yang digunakan dalam aplikasi ini perlu diganti dengan API key Anda sendiri jika ingin digunakan dalam produksi
- Aplikasi ini menjalankan semua proses secara real-time dan tidak menyimpan hasil analisis ke database 