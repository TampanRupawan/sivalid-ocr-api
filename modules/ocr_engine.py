import os
import cv2
import pandas as pd
from paddleocr import PaddleOCR
import time
import paddle

from config import (
    OCR_LANGUAGE,
    USE_ANGLE_CLS,
    SHOW_OCR_LOG,
    SCALE_TABLE,
    SCALE_HM,
    SCALE_NUMBER,
    SCALE_TEXT,
    USE_GRAYSCALE
)


class OCREngine:

    def __init__(self):

        BASE_DIR = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        PADDLEOCR_DIR = os.path.join(
            BASE_DIR,
            "models",
            "paddleocr"
        )

        DET_MODEL_DIR = os.path.join(
            PADDLEOCR_DIR,
            "en_PP-OCRv3_det_infer"
        )

        REC_MODEL_DIR = os.path.join(
            PADDLEOCR_DIR,
            "en_PP-OCRv4_rec_infer"
        )

        CLS_MODEL_DIR = os.path.join(
            PADDLEOCR_DIR,
            "ch_ppocr_mobile_v2.0_cls_infer"
        )

        self.ocr = PaddleOCR(
            use_angle_cls=USE_ANGLE_CLS,
            lang=OCR_LANGUAGE,
            show_log=SHOW_OCR_LOG,

            det_model_dir=DET_MODEL_DIR,
            rec_model_dir=REC_MODEL_DIR,
            cls_model_dir=CLS_MODEL_DIR,

            enable_mkldnn=True,
            cpu_threads=8,

            det_db_thresh=0.1,
            det_db_box_thresh=0.3,
            det_db_unclip_ratio=2.0
        )

        print("PaddleOCR Loaded")

    # ======================================================
    # PREPROCESS
    # ======================================================

    def preprocess(self, image, class_name):

        if image is None or image.size == 0:
            return None

        # -----------------------------
        # Grayscale
        # -----------------------------

        if USE_GRAYSCALE and len(image.shape) == 3:

            image = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

        # -----------------------------
        # Resize
        # -----------------------------

        if class_name in ["Table Kiri", "Table Kanan"]:
            scale = SCALE_TABLE
        elif class_name in ["HM_Kiri", "HM_Kanan"]:
            scale = SCALE_HM
        elif class_name in ["NPM", "IPK", "kredit"]:
            scale = SCALE_NUMBER

        else:

            scale = SCALE_TEXT

        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

        return image

    # ======================================================
    # CLEAN TEXT
    # ======================================================

    def clean_text(self, text):

        if not text:
            return ""

        text = str(text)
        text = text.replace("\r", "")
        text = text.replace("\t", " ")

        while "  " in text:
            text = text.replace("  ", " ")

        return text.strip()

    # ======================================================
    # OCR
    # ======================================================

    def run(self, crop_result):

        hasil_ocr = []

        for item in crop_result:
            kelas = item["CLASS"]

            print("=" * 60)
            print("OCR :", kelas)

            crop = self.preprocess(
                item["CROP"],kelas)

            if crop is None:

                hasil_ocr.append({

                    "CLASS": kelas,
                    "TEXT": "",
                    "CONF": 0,
                    "X1": item["X1"],
                    "Y1": item["Y1"],
                    "X2": item["X2"],
                    "Y2": item["Y2"]
                })
                continue
            try:
                
                start = time.perf_counter()
                result = self.ocr.ocr(
                    crop,cls=False)
                
                print(f"[OCR TIME] {kelas} : "
                f"{time.perf_counter() - start:.2f} s")

            except Exception as e:

                print("OCR Error :", e)
                result = None

            text = ""
            score = 0

            if result and result[0]:

                texts = []
                scores = []

                for line in result[0]:
                    texts.append(line[1][0])
                    scores.append(line[1][1])

                text = "\n".join(texts)

                if len(scores) > 0:
                    score = sum(scores) / len(scores)

            hasil_ocr.append({

                "CLASS": kelas,
                "TEXT": self.clean_text(text),
                "CONF": round(score, 3),
                "X1": item["X1"],
                "Y1": item["Y1"],
                "X2": item["X2"],
                "Y2": item["Y2"]
            })

        return pd.DataFrame(hasil_ocr)