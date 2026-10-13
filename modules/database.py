import pandas as pd


class Database:

    def __init__(self, file_database):
        self.database = pd.read_excel(file_database)
        self.database.columns = self.database.columns.str.upper()
        print("Database Loaded")


    # ==========================================
    # Ambil Semua Database
    # ==========================================

    def get_all(self):

        return self.database


    # ==========================================
    # Cari Mahasiswa Berdasarkan NPM
    # ==========================================

    def get_mahasiswa(self, npm):

        npm = str(npm).strip()
        df = self.database.copy()
        df["NPM"] = df["NPM"].astype(str)

        hasil = df[
            df["NPM"] == npm
        ].reset_index(drop=True)

        return hasil


    # ==========================================
    # Ambil Identitas
    # ==========================================

    def get_identitas(self, npm):

        data = self.get_mahasiswa(npm)
        if len(data) == 0:

            return None

        return {

            "NPM": data.iloc[0]["NPM"],
            "NAMA": data.iloc[0]["NAMA"],
            "IPK": data.iloc[0]["IPK"],
            "TOTAL KREDIT": data.iloc[0]["TOTAL KREDIT"]
        }