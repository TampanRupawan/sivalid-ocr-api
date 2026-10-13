from pathlib import Path

# ==============================================================================
# 📁 DIRECTORY & FILE PATHS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "best.pt"
DATABASE_PATH = DATA_DIR / "Database Mahasiswa.xlsx"


# ==============================================================================
# 🎯 DETECTION MODEL (YOLOv8)
# ==============================================================================
YOLO_CONFIDENCE = 0.5     # Batas keyakinan minimal untuk deteksi bounding box YOLO


# ==============================================================================
# 🔍 OPTICAL CHARACTER RECOGNITION (PADDLEOCR)
# ==============================================================================
OCR_LANGUAGE = "en"       # Menggunakan bahasa Inggris (lebih presisi untuk angka & kode)
USE_ANGLE_CLS = False     # Dimatikan agar tidak membuang waktu mengecek teks miring
SHOW_OCR_LOG = False      # [DEBUG] Ubah ke False jika sudah tidak butuh melihat log di terminal

# ==============================================================================
# 🖼️ IMAGE PREPROCESSING & ENHANCEMENT
# ==============================================================================
USE_GRAYSCALE = True      # Mengubah gambar menjadi hitam-putih untuk efisiensi RAM
USE_CLAHE = True          # Mempertajam kontras teks transkrip secara otomatis
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Jarak tambahan tepi (padding) saat memotong bounding box dari YOLO (dalam piksel)
DEFAULT_PADDING = (8, 8)
PADDING = {
    "IPK": (25, 15),
    "kredit": (25, 15),
    "nama": (20, 10),
    "NPM": (20, 10)
}


# ==============================================================================
# 🔎 RESOLUTION SCALING (OPTIMASI KECEPATAN & AKURASI)
# ==============================================================================
# Angka 1.0 berarti menggunakan resolusi asli (paling cepat).
SCALE_TABLE = 1.0         # Teks sangat padat. Gunakan 1.0 agar waktu OCR tidak tembus 60 detik.
SCALE_HM = 1.0            # Teks nilai (A/B/C) sangat kecil, butuh perbesaran agar tidak salah tebak.
SCALE_NUMBER = 1.0        # Angka krusial (IPK, SKS) diperbesar sedikit agar titik/koma tetap terbaca.
SCALE_TEXT = 1.0          # Teks identitas (Nama) sudah cukup jelas di resolusi aslinya.


# ==============================================================================
# 🧠 PARSER LOGIC & ERROR HANDLING (MAPPING OCR)
# ==============================================================================

# Batas kemiripan minimum (Fuzzy String Matching) untuk mencocokkan teks ke database
FUZZ_THRESHOLD = 80

# Daftar prefix (3 huruf awal) kode mata kuliah yang valid
KODE_PREFIX = ("INF", "UNI", "1NF", "UN1", "INE","UNT")

# Daftar Nilai Huruf (HM) yang dianggap sah/valid
VALID_HM = {"A", "B+", "B", "C+", "C", "D", "E"}

# Mapping perbaikan salah baca (typo) dari mesin OCR pada Nilai Huruf
HM_MAPPING = {
    "BF": "B+", "8": "B", "5": "S",
    "V": "A", "Y": "A", "T": "A",
    "<": "C", "￥": "A", "发": "A",
    "EF": "B+"
}

# Mapping perbaikan salah baca (typo) OCR pada Kode Mata Kuliah
KODE_OCR_MAPPING = {
    # Typo pada Prefix INF
    "1NF": "INF", "1F": "INF", "IXF": "INF", "[F": "INF", "1XF": "INF",
    "INFG": "INF", "INE": "INF", "INP": "INF", "1NE": "INF", "INR": "INF",
    "[NF": "INF", "[NP": "INF", "NE": "INF",

    # Typo pada Prefix UNI
    "UN1": "UNI", "0NI": "UNI", "0N1": "UNI",

    # Typo pada Angka (Konversi huruf abjad mirip angka menjadi angka)
    "S": "8", "s": "8",
    "l": "1", "L": "1", "I": "1", "i": "1",
    "Z": "2", "z": "2",
    "O": "0", "o": "0"
}
