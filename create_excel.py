import pandas as pd

# Create a DataFrame for tokoh.xlsx
data = {
    'Nama': [
        'Abdul Rahman', 
        'Siti Nurhaliza', 
        'Budi Santoso', 
        'Ani Wijaya', 
        'Dodi Permana',
        'Tito Karnavian',
        'Prabowo Subianto',
        'Bobby Nasution',
        'Muzakir Manaf',
        'Hendri Satrio',
        'Jamiluddin Ritonga',
        'Bima Arya Sugiarto',
        'Syakir'
    ],
    'Wilayah': [
        'Aceh', 
        'Sumatera Utara', 
        'Jakarta', 
        'Jawa Barat', 
        'Sulawesi Selatan',
        'Jakarta',
        'Jakarta',
        'Sumatera Utara',
        'Aceh',
        'Jakarta',
        'Jakarta',
        'Jakarta',
        'Aceh'
    ],
    'Jabatan': [
        'Gubernur', 
        'Bupati', 
        'Walikota', 
        'Camat', 
        'Lurah',
        'Menteri Dalam Negeri',
        'Presiden',
        'Gubernur',
        'Gubernur',
        'Analis Komunikasi Politik',
        'Pengamat Komunikasi Politik',
        'Wakil Menteri Dalam Negeri',
        'Kepala Biro Pemerintahan dan Otonomi Daerah Setda Aceh'
    ],
    'Jenis Kelamin': [
        'Laki-laki', 
        'Perempuan', 
        'Laki-laki', 
        'Perempuan', 
        'Laki-laki',
        'Laki-laki',
        'Laki-laki',
        'Laki-laki',
        'Laki-laki',
        'Laki-laki',
        'Laki-laki',
        'Laki-laki',
        'Laki-laki'
    ],
    'Tingkatan': [
        'Provinsi', 
        'Kabupaten', 
        'Kota', 
        'Kecamatan', 
        'Kelurahan',
        'Nasional',
        'Nasional',
        'Provinsi',
        'Provinsi',
        'Nasional',
        'Nasional',
        'Nasional',
        'Provinsi'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('tokoh.xlsx', index=False)

print("Excel file created successfully.") 