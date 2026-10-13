# SiValid OCR API

Backend Python untuk membaca gambar transkrip nilai dan mencocokkan hasilnya dengan data acuan mahasiswa. Backend ini digunakan oleh aplikasi Android pada repository terpisah [sivalid-mobile-integrated](https://github.com/TampanRupawan/sivalid-mobile-integrated).

Repository ini disiapkan sebagai dokumentasi source code untuk lampiran skripsi. Data akademik mahasiswa asli tidak disertakan.

## Alur pemrosesan

Gambar → YOLO mendeteksi bagian dokumen → potongan gambar → PaddleOCR membaca teks → parser menyusun identitas dan mata kuliah → data acuan dicari berdasarkan NPM → matcher memeriksa kecocokan → respons JSON.

## Teknologi

- FastAPI dan Uvicorn untuk layanan API.
- Ultralytics YOLO untuk deteksi bagian dokumen.
- PaddleOCR untuk pengenalan teks.
- OpenCV untuk pemrosesan gambar.
- Pandas dan OpenPyXL untuk data acuan Excel.
- RapidFuzz untuk pencocokan teks.
- JiWER untuk evaluasi kesalahan karakter (CER).
- Streamlit untuk antarmuka inspeksi proses.

## Menjalankan API

Gunakan Python 3.10 64-bit sebagaimana petunjuk integrasi project. Jalankan perintah dari folder repository:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Siapkan data acuan lokal sesuai [data/README.md](data/README.md), lalu jalankan:

```powershell
uvicorn api:app --host 0.0.0.0 --port 8000
```

Model YOLO di `models/best.pt` dan model PaddleOCR di `models/paddleocr/` disertakan dari project asal. Model dimuat saat server mulai.

- `GET /health`: memeriksa status layanan.
- `POST /analyze`: mengirim satu gambar melalui field multipart bernama `file`.
- Dokumentasi interaktif: `http://127.0.0.1:8000/docs` setelah server berjalan.
- Format input: JPG/JPEG atau PNG, maksimal 5 MB.

Contoh pengiriman di Windows:

```powershell
curl.exe -X POST http://127.0.0.1:8000/analyze -F "file=@transkrip.jpg"
```

## Antarmuka inspeksi

Untuk melihat hasil deteksi, potongan gambar, OCR, parsing, pencocokan, dan evaluasi melalui Streamlit:

```powershell
streamlit run app.py
```

## Source code utama

| File | Fungsi |
| --- | --- |
| `api.py` | Menerima gambar dan membentuk respons untuk Android. |
| `pipeline.py` | Mengatur urutan seluruh tahap analisis. |
| `modules/detector.py` | Deteksi dan pemotongan bagian gambar dengan YOLO. |
| `modules/ocr_engine.py` | Pemrosesan gambar dan pembacaan tulisan dengan PaddleOCR. |
| `modules/parser.py` | Menyusun identitas, kode, nama mata kuliah, dan nilai huruf. |
| `modules/database.py` | Membaca Excel dan mencari data berdasarkan NPM. |
| `modules/matcher.py` | Mencocokkan hasil bacaan dengan data acuan. |
| `modules/cer.py` | Menghitung Character Error Rate terhadap teks acuan. |
| `config.py` | Lokasi berkas, parameter deteksi, dan aturan koreksi OCR. |
| `app.py` | Tampilan Streamlit untuk inspeksi proses. |
| `datatestmap.py` | Evaluasi deteksi; membutuhkan dataset `Scanner-Evaluasi/data.yaml` yang tidak disertakan. |

## Makna hasil dan batasan

- `valid` bernilai benar jika terdapat baris hasil dan semua baris tersebut lolos pemeriksaan kode, nilai huruf, dan nama mata kuliah.
- Pemeriksaan belum mensyaratkan semua mata kuliah dalam data acuan terbaca, atau nama mahasiswa, IPK, dan total kredit cocok.
- Persentase kecocokan dihitung dari baris yang berhasil diproses; bukan jaminan akurasi keseluruhan sistem atau keaslian dokumen.
- Parser menggunakan aturan format tertentu, termasuk kode INF/UNI dan bagian tabel kiri/kanan. Format transkrip lain mungkin memerlukan penyesuaian.
- Penanganan hasil OCR tanpa NPM masih perlu perbaikan: evaluasi CER dapat menghasilkan `None` yang belum ditangani di pembentukan respons API.
- API belum menyediakan autentikasi pengguna. Login dan registrasi Android belum dilayani backend ini.

## Data dan status verifikasi

Excel data mahasiswa asli, gambar transkrip pribadi, kredensial, dan lingkungan Python lokal dikecualikan dari Git. Tanpa data acuan lokal, pipeline tidak dapat dimuat.

Persiapan publikasi tidak mengubah logika pemrosesan. Instalasi dependensi, menjalankan model, dan pengujian menyeluruh belum dilakukan dalam proses persiapan repository ini. Lihat juga [README_API.md](README_API.md).
