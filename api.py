from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

import cv2
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from pipeline import TranscriptPipeline


MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if pd.isna(value):
        return None
    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame is None or frame.empty:
        return []
    return _json_value(frame.to_dict(orient="records"))


def _build_response(result: dict[str, Any]) -> dict[str, Any]:
    validation = result["validasi"]
    total_courses = len(validation)

    required_columns = {"VALID KODE", "VALID HM", "VALID NAMA"}
    has_required_columns = required_columns.issubset(validation.columns)
    is_valid = bool(
        total_courses > 0
        and has_required_columns
        and validation[list(required_columns)].all(axis=1).all()
    )

    identity = _json_value(result["identitas"])
    return {
        "status": "success",
        "valid": is_valid,
        "student": {
            "name": identity.get("nama") or "",
            "npm": identity.get("npm") or "",
            "gpa": identity.get("ipk") or "",
            "credits": identity.get("kredit") or "",
        },
        "summary": {
            "total_courses": total_courses,
            "code_accuracy": float(result["akurasi_kode"]),
            "grade_accuracy": float(result["akurasi_hm"]),
            "name_accuracy": float(result["akurasi_nama"]),
            "cer": _json_value(result["CER"].get("CER")),
        },
        "courses": _records(validation),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipeline = await run_in_threadpool(TranscriptPipeline)
    app.state.pipeline_lock = asyncio.Lock()
    yield


app = FastAPI(
    title="SiValid OCR API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Format belum didukung. Gunakan JPG, JPEG, atau PNG.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Berkas gambar kosong.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Ukuran berkas melebihi 5 MB.")

    image_array = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Berkas tidak dapat dibaca sebagai gambar.")

    try:
        async with app.state.pipeline_lock:
            result = await run_in_threadpool(app.state.pipeline.run, image)
        return _build_response(result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline OCR gagal memproses dokumen: {exc}",
        ) from exc
