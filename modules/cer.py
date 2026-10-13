import pandas as pd
import re
from jiwer import process_characters


class CEREvaluator:

    def __init__(self, database_df):

        self.database = database_df.copy()

    # --------------------------------------------
    # Membuat Ground Truth dari Database
    # --------------------------------------------

    def build_ground_truth(self, npm):

        db = self.database.copy()

        db = db[
            db["NPM"].astype(str) == str(npm)
        ]

        if len(db) == 0:
            return ""

        nama = str(
            db.iloc[0]["NAMA"]
        ).upper().strip()

        ipk = str(
            db.iloc[0]["IPK"]
        ).replace(".", ",")

        kredit = str(
            db.iloc[0]["TOTAL KREDIT"]
        )

        lines = []

        lines.append(nama)
        lines.append(str(npm))
        lines.append(ipk)
        lines.append(kredit)

        for _, row in db.iterrows():

            kode = str(
                row["KODE MATKUL"]
            ).upper().strip()

            matkul = str(
                row["MATA KULIAH"]
            ).upper().strip()

            hm = str(
                row["HM"]
            ).upper().strip()

            lines.append(
                f"{kode} {matkul} {hm}"
            )

        return "\n".join(lines)

    def split_records(self, table_text):

        if table_text is None:
            return []

        text = str(table_text).upper()

        # Samakan newline
        text = text.replace("\r", "\n")

        # Cari semua kode matkul
        pattern = r"(INF\d{6}|UNI\d{6})"

        matches = list(re.finditer(pattern, text))

        if len(matches) == 0:
            return []

        records = []

        for i, m in enumerate(matches):

            start = m.start()

            if i == len(matches) - 1:
                end = len(text)
            else:
                end = matches[i + 1].start()

            record = text[start:end].strip()

            record = re.sub(r"\s+", " ", record)

            records.append(record)

        return records

    def split_hm(self, hm_text):

        if hm_text is None:
            return []

        lines = str(hm_text).upper().splitlines()

        hm = []

        for x in lines:

            x = x.strip()

            if x != "":
                hm.append(x)

        return hm

    # --------------------------------------------
    # Membuat OCR Text
    # --------------------------------------------

    def build_ocr_text(self, df_ocr):

        def ambil(cls):

            row = df_ocr[
                df_ocr["CLASS"].str.upper() == cls.upper()
            ]

            if len(row) == 0:
                return ""

            return str(row.iloc[0]["TEXT"])


        nama = ambil("nama").upper().replace("\n", " ")

        npm = ambil("NPM").strip()

        ipk = ambil("IPK").replace(".", ",")

        kredit = ambil("kredit").strip()


        table_kiri = self.split_records(
            ambil("Table Kiri")
        )

        table_kanan = self.split_records(
            ambil("Table Kanan")
        )

        hm_kiri = self.split_hm(
            ambil("HM_Kiri")
        )

        hm_kanan = self.split_hm(
            ambil("HM_Kanan")
        )

        lines = [

            nama,

            npm,

            ipk,

            kredit

        ]

        for i, rec in enumerate(table_kiri):

            hm = hm_kiri[i] if i < len(hm_kiri) else ""

            lines.append(
                f"{rec} {hm}".strip()
            )

        for i, rec in enumerate(table_kanan):

            hm = hm_kanan[i] if i < len(hm_kanan) else ""

            lines.append(
                f"{rec} {hm}".strip()
            )

        return "\n".join(lines)

    # --------------------------------------------
    # Evaluasi CER
    # --------------------------------------------

    def evaluate(self, df_ocr):

        npm_row = df_ocr[
            df_ocr["CLASS"] == "NPM"
        ]

        if len(npm_row) == 0:

            return None

        npm = str(
        npm_row.iloc[0]["TEXT"]
        ).strip()
        import re

        npm_text = str(
            npm_row.iloc[0]["TEXT"]
        )

        # Ambil 10 digit angka pertama
        match = re.search(r"\d{10}", npm_text)

        if match:
            npm = match.group(0)
        else:
            return None

        print("=" * 60)
        print("NPM OCR :", repr(npm))
        print("=" * 60)

        gt = self.build_ground_truth(npm)

        ocr = self.build_ocr_text(df_ocr)

        hasil = process_characters(gt,ocr)

        ground_truth_chars = len(gt)

        print("=" * 60)
        print("GROUND TRUTH CHARACTER :", ground_truth_chars)
        print("Hits                  :", hasil.hits)
        print("Substitution          :", hasil.substitutions)
        print("Deletion              :", hasil.deletions)
        print("Insertion             :", hasil.insertions)

        print(
            f"CER = ({hasil.substitutions} + "
            f"{hasil.deletions} + "
            f"{hasil.insertions}) / "
            f"{ground_truth_chars}"
        )

        print(
            "=" * 60
        )

        return {
            "CER": hasil.cer,
            "Substitution": hasil.substitutions,
            "Deletion": hasil.deletions,
            "Insertion": hasil.insertions,
            "Hits": hasil.hits,
            "Ground Truth": gt,
            "OCR": ocr,
            "Ground Truth Characters": ground_truth_chars
        }