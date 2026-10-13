import re
import pandas as pd
from rapidfuzz import process, fuzz

from config import (
    FUZZ_THRESHOLD,
    HM_MAPPING,
    VALID_HM,
    KODE_PREFIX,
    KODE_OCR_MAPPING
)


class TranscriptParser:

    def __init__(self):

        print("Transcript Parser Loaded")

        # Prefix kode mata kuliah yang valid
        self.prefix = [x.upper() for x in KODE_PREFIX]

        # Regex prefix
        self.prefix_pattern = "|".join(self.prefix)

        # Mapping OCR
        self.ocr_mapping = KODE_OCR_MAPPING

        # Threshold RapidFuzz
        self.fuzz_threshold = FUZZ_THRESHOLD

    # ==================================================
    # IDENTITAS
    # ==================================================

    def identitas(self, df_ocr):

        hasil = {
            "nama": "",
            "npm": "",
            "ipk": "",
            "kredit": ""
        }

        if df_ocr is None or len(df_ocr) == 0:
            return hasil

        for _, row in df_ocr.iterrows():

            cls = str(
                row.get("CLASS", "")
            ).strip().lower()

            text = str(
                row.get("TEXT", "")
            ).strip()

            if text == "":
                continue

            # -------------------------------
            # Nama
            # -------------------------------

            if cls == "nama":

                nama_bersih = re.sub(r"^[^a-zA-Z]+", "",text)
                hasil["nama"] = nama_bersih.strip().upper()

            # -------------------------------
            # NPM
            # -------------------------------

            elif cls == "npm":

                npm = re.search(
                    r"\d{8,15}",
                    text
                )

                if npm:
                    hasil["npm"] = npm.group()

            # -------------------------------
            # IPK
            # -------------------------------

            elif cls == "ipk":

                ipk = re.search(
                    r"\d+[.,]\d{2}",
                    text
                )

                if ipk:

                    hasil["ipk"] = (
                        ipk.group()
                        .replace(".", ",")
                    )

            # -------------------------------
            # Total Kredit
            # -------------------------------

            elif cls == "kredit":

                kredit = re.findall(
                    r"\d+",
                    text
                )

                if kredit:
                    hasil["kredit"] = kredit[-1]

        return hasil

    # ==================================================
    # TABLE
    # ==================================================

    def get_table(self, df_ocr):

        if df_ocr is None or len(df_ocr) == 0:
            return []

        # ==========================================
        # Gabungkan seluruh OCR Table
        # ==========================================

        table_text = ""

        for _, row in df_ocr.iterrows():

            cls = str(
                row.get("CLASS", "")
            ).strip()

            if cls not in [
                "Table Kiri",
                "Table Kanan"
            ]:
                continue

            text = str(
                row.get("TEXT", "")
            )

            table_text += "\n"
            table_text += text

        # ------------------------------------------

        table_text = table_text.replace("\r", "\n")

        table_text = table_text.upper()

        table_text = re.sub(
            r"\s+",
            " ",
            table_text
        )

        # ------------------------------------------
        # Pisahkan berdasarkan kemunculan kode
        # ------------------------------------------

        pattern = re.compile(
            rf"((?:{self.prefix_pattern})\s*\d{{6}})",
            flags=re.IGNORECASE
        )

        hasil = []

        matches = list(
            pattern.finditer(table_text)
        )

        for i, match in enumerate(matches):

            start = match.start()

            if i == len(matches)-1:
                end = len(table_text)
            else:
                end = matches[i+1].start()

            record = table_text[start:end]

            record = re.sub(
                r"\s+",
                " ",
                record
            ).strip()

            hasil.append(record)

        return hasil

    # ==================================================
    # HM
    # ==================================================

    def get_hm(self, df_ocr):

        hm = []

        if df_ocr is None or len(df_ocr) == 0:
            return hm

        for _, row in df_ocr.iterrows():

            cls = str(
                row.get("CLASS", "")
            ).strip()

            if cls not in [
                "HM_Kiri",
                "HM_Kanan"
            ]:
                continue

            text = str(
                row.get("TEXT", "")
            )

            text = text.replace(
                "\r",
                "\n"
            )

            lines = text.split("\n")

            for item in lines:

                item = item.strip().upper()

                if item == "":
                    continue

                hm.append(item)

        return hm

    # ==================================================
    # CLEAN HM
    # ==================================================

    def clean_hm(self, hm):

        hasil = []

        if hm is None:
            return hasil

        for nilai in hm:

            nilai = str(nilai).upper().strip()

            # -------------------------------
            # Mapping OCR
            # -------------------------------

            if nilai in HM_MAPPING:
                nilai = HM_MAPPING[nilai]

            # -------------------------------
            # HM Valid
            # -------------------------------

            if nilai in VALID_HM:
                hasil.append(nilai)

        return hasil

        # ==================================================
    # CLEAN RECORD
    # ==================================================

    def clean_record(self, record):

        if record is None:
            return ""

        record = str(record).upper().strip()

        # Rapikan whitespace
        record = re.sub(r"\s+", " ", record)

        # Hilangkan nomor urut
        record = re.sub(
            r"^\d{1,2}[\.\,\:\-]?\s*",
            "",
            record
        )

        # Hilangkan simbol di depan
        record = re.sub(
            r"^[\-\:\.\,\(\)]+",
            "",
            record
        )

        # Hilangkan simbol di belakang
        record = re.sub(
            r"[\-\:\.\,\(\)]+$",
            "",
            record
        )

        # Rapikan kembali
        record = re.sub(
            r"\s+",
            " ",
            record
        ).strip()

        return record


    # ==================================================
    # NORMALIZE RECORD
    # ==================================================

    def normalize_record(self, record):

        if record is None:
            return ""

        record = str(record).upper().strip()

        # --------------------------------------
        # Rapikan spasi
        # --------------------------------------

        record = re.sub(
            r"\s+",
            " ",
            record
        )

        # --------------------------------------
        # INF 620101
        # ->
        # INF620101
        # --------------------------------------

        for prefix in self.prefix:

            record = re.sub(
                rf"\b{prefix}\s+([A-Z0-9]{{6}})",
                rf"{prefix}\1",
                record,
                flags=re.IGNORECASE
            )

        # --------------------------------------
        # Koreksi OCR
        # --------------------------------------

        def fix_match(match):
            
            kode = match.group(0)
        
            if kode.upper() == "INFORMASI":
                return kode

            prefix = kode[:3]
            
            # --- TAMBAHAN BARU: Perbaiki prefix jika ada typo ---
            prefix = self.ocr_mapping.get(prefix, prefix)

            angka = kode[3:]
            hasil = ""
            
            for ch in angka:
                hasil += self.ocr_mapping.get(ch, ch)

            return prefix + hasil

        record = re.sub(
            rf"(?:{self.prefix_pattern})\d{{6}}",
            fix_match,
            record,
            flags=re.IGNORECASE
        )

        # --------------------------------------
        # INF620101ALGORITMA
        # ->
        # INF620101 ALGORITMA
        # --------------------------------------

        record = re.sub(
            rf"((?:{self.prefix_pattern})\d{{6}})([A-Z])",
            r"\1 \2",
            record,
            flags=re.IGNORECASE
        )

        # --------------------------------------
        # INF620101INF620102
        # ->
        # INF620101 INF620102
        # --------------------------------------

        record = re.sub(
            rf"(\d{{6}})((?:{self.prefix_pattern})[A-Z0-9]{{6}})",
            r"\1 \2",
            record,
            flags=re.IGNORECASE
        )

        record = re.sub(
            r"\s+",
            " ",
            record
        ).strip()

        return record


    # ==================================================
    # EXTRACT CODE
    # ==================================================

    def extract_code(self, record):

        if record is None:
            return None

        pattern = re.compile(
            rf"\b(?:{self.prefix_pattern})\d{{6}}\b",
            flags=re.IGNORECASE
        )

        match = pattern.search(record)

        if match:
            return match.group(0).upper()

        return None


    # ==================================================
    # EXTRACT NAME
    # ==================================================

    def extract_name(self, record, kode):

        if record is None:
            return ""

        if kode is None:
            return ""

        posisi = record.find(kode)

        if posisi == -1:
            return ""

        nama = record[
            posisi + len(kode):
        ]

        nama = nama.strip()

        nama = re.sub(
            r"^[\-\:\.\,\(\)]+",
            "",
            nama
        )

        nama = re.sub(
            r"[\-\:\.\,\(\)]+$",
            "",
            nama
        )

        nama = re.sub(
            r"\s+",
            " ",
            nama
        )

        return nama.strip()


    # ==================================================
    # FIX KODE
    # ==================================================

    def fix_kode(self, raw_code, daftar_kode):

        if raw_code is None:
            return None

        if not daftar_kode:
            return raw_code

        hasil = process.extractOne(
            query=raw_code,
            choices=daftar_kode,
            scorer=fuzz.ratio,
            score_cutoff=self.fuzz_threshold
        )

        if hasil is None:
            return raw_code

        kode, score, _ = hasil

        return kode

        # ==================================================
    # PARSE RECORD
    # ==================================================

    def parse_record(self, record, daftar_kode):

        # --------------------------------------
        # Bersihkan record
        # --------------------------------------

        record = self.clean_record(record)

        if record == "":
            return None

        # --------------------------------------
        # Normalisasi OCR
        # --------------------------------------

        record = self.normalize_record(record)

        # --------------------------------------
        # Ambil kode OCR
        # --------------------------------------

        raw_code = self.extract_code(record)

        if raw_code is None:
            return None

        # --------------------------------------
        # Perbaiki kode
        # --------------------------------------

        kode = self.fix_kode(
            raw_code,
            daftar_kode
        )

        # jika RapidFuzz gagal
        if kode is None:
            kode = raw_code

        # --------------------------------------
        # Ambil nama matkul
        # --------------------------------------

        nama = self.extract_name(
            record,
            raw_code
        )

        if nama == "":
            return None

        return {

            "KODE OCR": kode,

            "NAMA OCR": nama

        }


    # ==================================================
    # PARSE MATA KULIAH
    # ==================================================

    def parse_matkul(self, records, daftar_kode):

        hasil = []

        if records is None:

            return pd.DataFrame(
                columns=[
                    "KODE OCR",
                    "NAMA OCR"
                ]
            )

        for record in records:

            item = self.parse_record(
                record,
                daftar_kode
            )

            if item is None:
                continue

            hasil.append(item)

        df = pd.DataFrame(hasil)

        if len(df) == 0:

            return pd.DataFrame(
                columns=[
                    "KODE OCR",
                    "NAMA OCR"
                ]
            )

        # hilangkan duplikasi
        df = df.drop_duplicates(
            subset=["KODE OCR"],
            keep="first"
        )

        # reset index
        df = df.reset_index(drop=True)

        return df


    # ==================================================
    # TRANSKRIP
    # ==================================================

    def transkrip(self, df_ocr, db):
        """
        Pipeline utama parser transkrip.

        YOLO
            ↓
        Identitas
            ↓
        Record OCR
            ↓
        HM OCR
            ↓
        Parsing Mata Kuliah
            ↓
        Sinkronisasi HM
            ↓
        DataFrame Final
        """

        # --------------------------------------
        # Identitas
        # --------------------------------------

        identitas = self.identitas(
            df_ocr
        )

        # --------------------------------------
        # Record OCR
        # --------------------------------------

        records = self.get_table(
            df_ocr
        )

        # --------------------------------------
        # HM
        # --------------------------------------

        hm = self.clean_hm(
            self.get_hm(df_ocr)
        )

        # --------------------------------------
        # Database kode
        # --------------------------------------

        daftar_kode = (
            db["KODE MATKUL"]
            .astype(str)
            .str.upper()
            .tolist()
        )

        # --------------------------------------
        # Parsing mata kuliah
        # --------------------------------------

        hasil = self.parse_matkul(
            records,
            daftar_kode
        )

        # --------------------------------------
        # Sinkronisasi HM
        # --------------------------------------

        if len(hasil) > 0:
            
            # Jika jumlah HM kurang dari jumlah mata kuliah, tambahkan list HM dengan tanda "-"
            while len(hm) < len(hasil):
                hm.append("-")
                
            # Jika kelebihan, cukup potong seukuran jumlah mata kuliah
            hm = hm[:len(hasil)]
            hasil["HM OCR"] = hm

        else:
            hasil["HM OCR"] = []

        # --------------------------------------
        # Tambahkan identitas
        # --------------------------------------

        hasil["NAMA"] = identitas["nama"]
        hasil["NPM"] = identitas["npm"]
        hasil["IPK"] = identitas["ipk"]
        hasil["KREDIT"] = identitas["kredit"]

        # --------------------------------------
        # Susun urutan kolom
        # --------------------------------------

        hasil = hasil[

            [
                "NAMA",
                "NPM",
                "IPK",
                "KREDIT",
                "KODE OCR",
                "NAMA OCR",
                "HM OCR"
            ]
        ]

        return hasil