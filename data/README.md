# Data acuan lokal

Data mahasiswa asli tidak dipublikasikan. Untuk menjalankan pipeline, siapkan workbook Excel lokal dengan nama **Database Mahasiswa.xlsx** di folder ini, menggunakan data sintetis atau data yang memang berwenang Anda gunakan.

Kode membaca sheet pertama. Setiap baris mewakili satu mata kuliah seorang mahasiswa. Kolom yang diperlukan:

| Kolom | Isi |
| --- | --- |
| `NPM` | Nomor mahasiswa; harus konsisten dengan NPM pada dokumen. |
| `NAMA` | Nama mahasiswa. |
| `IPK` | Indeks prestasi kumulatif. |
| `TOTAL KREDIT` | Total kredit mahasiswa. |
| `KODE MATKUL` | Kode mata kuliah. |
| `MATA KULIAH` | Nama mata kuliah. |
| `HM` | Nilai huruf mata kuliah. |

Identitas mahasiswa diulang pada setiap baris mata kuliahnya. Untuk evaluasi CER pada implementasi sekarang, NPM yang dibaca mengikuti pola 10 digit.

Berkas Excel lokal dikecualikan melalui `.gitignore`. Jangan memasukkan data akademik pribadi ke repository publik.
