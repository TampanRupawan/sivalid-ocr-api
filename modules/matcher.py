import pandas as pd
from rapidfuzz import fuzz, process


class TranscriptMatcher:

    def __init__(self):
        print("Matcher Loaded")

    # ==================================================
    # NORMALISASI KODE MATKUL
    # ==================================================

    def normalize_kode(self, text):

        if pd.isna(text):
            return ""

        text = str(text).upper().strip()

        # Perbaikan OCR hanya pada prefix kode
        if text.startswith("1NF"):
            text = "INF" + text[3:]

        elif text.startswith("UN1"):
            text = "UNI" + text[3:]

        text = " ".join(text.split())

        return text

    # ==================================================
    # NORMALISASI NAMA MATKUL
    # ==================================================

    def normalize_nama(self, text):

        if pd.isna(text):
            return ""

        text = str(text).upper().strip()

        # Hilangkan spasi berlebih
        text = " ".join(text.split())

        return text
    
    # ==================================================
    # PERBAIKI KODE OCR
    # ==================================================

    def fix_kode(self, kode_ocr, daftar_kode):

        if pd.isna(kode_ocr):
            return ""

        kode = str(kode_ocr).upper()

        kode = (
            kode
            .replace("O","0")
            .replace("I","1")
            .replace("L","1")
            .replace("Z","2")
            .replace("E","F")
        )

        hasil = process.extractOne(
            kode,
            daftar_kode,
            scorer=fuzz.ratio
        )

        if hasil is None:
            return kode

        kandidat, score, _ = hasil

        if score >= 85:

            return kandidat
        return kode

    # ==================================================
    # MATCH
    # ==================================================

    def match(self, df_ocr, df_db):

        hasil = []

        daftar_kode = df_db["KODE MATKUL"].tolist()

        for _, ocr in df_ocr.iterrows():

            kode_ocr = self.fix_kode(

                ocr["KODE OCR"],

                daftar_kode

            )

            kandidat = df_db[

                df_db["KODE MATKUL"] == kode_ocr

            ]

            if kandidat.empty:

                hasil.append({

                    "KODE OCR": kode_ocr,
                    "KODE DB": "",

                    "NAMA OCR": ocr["NAMA OCR"],
                    "NAMA DB": "",

                    "HM OCR": ocr["HM OCR"],
                    "HM DB": "",

                    "VALID KODE": False,
                    "VALID HM": False,
                    "SIMILARITY": 0,
                    "VALID NAMA": False

                })

                continue

            db = kandidat.iloc[0]

            nama_ocr = self.normalize_nama(

                ocr["NAMA OCR"]

            )

            nama_db = self.normalize_nama(

                db["MATA KULIAH"]

            )

            hm_ocr = str(

                ocr["HM OCR"]

            ).strip().upper()

            hm_db = str(

                db["HM"]

            ).strip().upper()

            score = fuzz.ratio(

                nama_ocr,

                nama_db

            )

            hasil.append({

                "KODE OCR": kode_ocr,
                "KODE DB": db["KODE MATKUL"],

                "NAMA OCR": nama_ocr,
                "NAMA DB": nama_db,

                "HM OCR": hm_ocr,
                "HM DB": hm_db,

                "VALID KODE": True,
                "VALID HM": hm_ocr == hm_db,

                "SIMILARITY": round(score,2),

                "VALID NAMA": score >= 90

            })

        return pd.DataFrame(hasil)