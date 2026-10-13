# SiValid OCR API

API ini menjadi penghubung antara aplikasi Android SiValid dan pipeline YOLO serta PaddleOCR.

## Menjalankan server

Gunakan Python 3.10 64-bit agar sesuai dengan paket `paddlepaddle==2.6.2`, lalu jalankan:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000
```

Model dimuat sekali ketika server mulai. Proses awal dapat memerlukan waktu lebih lama daripada request berikutnya.

## Endpoint

- `GET /health` untuk memeriksa server.
- `POST /analyze` untuk mengunggah satu gambar JPG atau PNG menggunakan field multipart bernama `file`.
- Batas ukuran gambar adalah 5 MB.

Contoh:

```bash
curl -X POST http://127.0.0.1:8000/analyze -F "file=@transkrip.jpg"
```

Dokumentasi interaktif tersedia di `http://127.0.0.1:8000/docs`.

## Android

Emulator Android memakai `http://10.0.2.2:8000/`. HP fisik harus memakai alamat IP laptop pada jaringan Wi-Fi yang sama, misalnya `http://192.168.1.10:8000/`.

Untuk build Android dengan alamat lain:

```bash
gradlew.bat assembleDebug -PSIVALID_API_BASE_URL=http://192.168.1.10:8000/
```

Gunakan HTTPS dan batasi detail pesan kesalahan sebelum server dipublikasikan ke internet.
