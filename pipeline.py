from modules.detector import YOLODetector
from modules.ocr_engine import OCREngine
from modules.parser import TranscriptParser
from modules.database import Database
from modules.matcher import TranscriptMatcher
from config import MODEL_PATH, DATABASE_PATH
from modules.cer import CEREvaluator

import time

class TranscriptPipeline:

    def __init__(self):

        # ===============================
        # LOAD SEMUA MODULE
        # ===============================

        self.detector = YOLODetector(MODEL_PATH)
        self.ocr = OCREngine()
        self.parser = TranscriptParser()
        self.database = Database(DATABASE_PATH)
        self.matcher = TranscriptMatcher()
        self.cer = CEREvaluator(self.database.get_all())

        print()
        print("="*60)
        print("Pipeline Ready")
        print("="*60)

    def run(self, img):

        total_start = time.perf_counter()

        # -------------------------
        # YOLO
        # -------------------------
        start = time.perf_counter()

        df_deteksi, img_result = self.detector.detect(img)
        crop_result = self.detector.crop(img, df_deteksi)

        print(f"[TIME] YOLO     : {time.perf_counter() - start:.2f} s")

        # -------------------------
        # OCR
        # -------------------------
        start = time.perf_counter()

        df_ocr = self.ocr.run(crop_result)

        print(f"[TIME] OCR      : {time.perf_counter() - start:.2f} s")

        hasil_cer = self.cer.evaluate(df_ocr)

        # -------------------------
        # IDENTITAS
        # -------------------------
        start = time.perf_counter()

        identitas = self.parser.identitas(df_ocr)

        print(f"[TIME] Identitas: {time.perf_counter() - start:.2f} s")

        # -------------------------
        # DATABASE
        # -------------------------
        start = time.perf_counter()

        db_mahasiswa = self.database.get_mahasiswa(
            identitas["npm"]
        )

        print(f"[TIME] Database : {time.perf_counter() - start:.2f} s")

        # -------------------------
        # PARSER
        # -------------------------
        start = time.perf_counter()

        df_transkrip = self.parser.transkrip(df_ocr,db_mahasiswa)

        print(f"[TIME] Parser   : {time.perf_counter() - start:.2f} s")

        # -------------------------
        # MATCHER
        # -------------------------
        start = time.perf_counter()

        hasil_match = self.matcher.match(df_transkrip,db_mahasiswa)

        print(f"[TIME] Matcher  : {time.perf_counter() - start:.2f} s")

        print("=" * 50)
        print(f"[TIME] TOTAL    : {time.perf_counter() - total_start:.2f} s")
        print("=" * 50)

        # -------------------------
        # AKURASI
        # -------------------------

        jumlah_hasil = len(hasil_match)
        if jumlah_hasil == 0:
            akurasi_kode = 0.0
            akurasi_hm = 0.0
            akurasi_nama = 0.0
        else:
            akurasi_kode = (hasil_match["VALID KODE"].sum() / jumlah_hasil) * 100
            akurasi_hm = (hasil_match["VALID HM"].sum() / jumlah_hasil) * 100
            akurasi_nama = (hasil_match["VALID NAMA"].sum() / jumlah_hasil) * 100

        # -------------------------
        # RETURN
        # -------------------------

        return {
            "gambar": img_result,
            "deteksi": df_deteksi,
            "ocr": df_ocr,
            "crop": crop_result,
            "identitas": identitas,
            "transkrip": df_transkrip,
            "database": db_mahasiswa,
            "validasi": hasil_match,
            "akurasi_kode": akurasi_kode,
            "akurasi_hm": akurasi_hm,
            "akurasi_nama": akurasi_nama,
            "CER": hasil_cer,
        }
