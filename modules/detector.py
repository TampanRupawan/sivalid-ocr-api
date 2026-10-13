import pandas as pd
from ultralytics import YOLO

from config import (YOLO_CONFIDENCE,PADDING,DEFAULT_PADDING)


class YOLODetector:

    def __init__(self, model_path):
        self.model = YOLO(str(model_path))
        print("YOLO Loaded")

    # ======================================================
    # DETEKSI
    # ======================================================

    def detect(self, image, conf=YOLO_CONFIDENCE):

        results = self.model.predict(
            source=image,
            conf=conf,
            verbose=False
        )

        detections = []

        for result in results:

            boxes = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()

            for box, cls, score in zip(boxes, classes, scores):

                x1, y1, x2, y2 = map(int, box)

                detections.append({

                    "CLASS": self.model.names[int(cls)],
                    "CONFIDENCE": float(score),

                    "X1": x1,
                    "Y1": y1,
                    "X2": x2,
                    "Y2": y2

                })

        if len(detections) == 0:

            return (
                pd.DataFrame(
                    columns=[
                        "CLASS",
                        "CONFIDENCE",
                        "X1",
                        "Y1",
                        "X2",
                        "Y2"
                    ]
                ),
                image
            )
        df = pd.DataFrame(detections)

        df = pd.DataFrame(detections)

        # ======================================================
        # MERGE DETEKSI GANDA
        # ======================================================

        df = self.merge_duplicate_boxes(df)

        # Urutkan hasil
        df = df.sort_values(["Y1", "X1"]).reset_index(drop=True)
        img_result = results[0].plot()

        return df, img_result 


    # ======================================================
    # MERGE DETEKSI GANDA
    # ======================================================

    def merge_duplicate_boxes(self, df, iou_threshold=0.3):

        hasil = []

        classes = df["CLASS"].unique()

        for cls in classes:

            group = df[df["CLASS"] == cls].copy()

            if len(group) == 1:
                hasil.append(group.iloc[0].to_dict())
                continue

            while len(group) > 0:

                base = group.iloc[0]

                x1 = base["X1"]
                y1 = base["Y1"]
                x2 = base["X2"]
                y2 = base["Y2"]

                conf = base["CONFIDENCE"]

                drop_index = [group.index[0]]

                for idx in group.index[1:]:

                    row = group.loc[idx]

                    xx1 = max(x1, row["X1"])
                    yy1 = max(y1, row["Y1"])
                    xx2 = min(x2, row["X2"])
                    yy2 = min(y2, row["Y2"])

                    inter = max(0, xx2 - xx1) * max(0, yy2 - yy1)

                    area1 = (x2 - x1) * (y2 - y1)
                    area2 = (row["X2"] - row["X1"]) * (row["Y2"] - row["Y1"])

                    union = area1 + area2 - inter

                    iou = inter / union if union > 0 else 0

                    if iou > iou_threshold:

                        x1 = min(x1, row["X1"])
                        y1 = min(y1, row["Y1"])
                        x2 = max(x2, row["X2"])
                        y2 = max(y2, row["Y2"])

                        conf = max(conf, row["CONFIDENCE"])

                        drop_index.append(idx)

                hasil.append({

                    "CLASS": cls,
                    "CONFIDENCE": conf,

                    "X1": int(x1),
                    "Y1": int(y1),
                    "X2": int(x2),
                    "Y2": int(y2)

                })

                group = group.drop(drop_index)

        return pd.DataFrame(hasil)

    # ======================================================
    # CROP
    # ======================================================

    def crop(self, image, detections):
        """
        Melakukan crop setiap hasil deteksi.
        """

        hasil_crop = []
        tinggi, lebar = image.shape[:2]

        for _, row in detections.iterrows():

            kelas = row["CLASS"]

            x1 = int(row["X1"])
            y1 = int(row["Y1"])
            x2 = int(row["X2"])
            y2 = int(row["Y2"])

            # Ambil padding dari config
            pad_x, pad_y = PADDING.get(kelas,DEFAULT_PADDING)

            x1 = max(0, x1 - pad_x)
            y1 = max(0, y1 - pad_y)

            x2 = min(lebar, x2 + pad_x)
            y2 = min(tinggi, y2 + pad_y)

            crop = image[y1:y2, x1:x2]

            # Lewati crop kosong
            if crop.size == 0:
                continue

            hasil_crop.append({
                **row.to_dict(),
                "CROP": crop
            })

        return hasil_crop