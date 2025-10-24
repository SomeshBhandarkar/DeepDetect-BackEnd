import uuid
import shutil
import os
from pathlib import Path as PathlibPath
from fastapi import FastAPI, UploadFile, File, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.yolo_model import predict_from_path
from app.database import SessionLocal, init_db
from app.models import DetectionRun, DetectedObject

UPLOAD_DIR = PathlibPath("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR = PathlibPath("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="DeepDetect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

class UpdateObjectSchema(BaseModel):
    pinned: Optional[dict] = None
    condition: Optional[str] = None

@app.post("/api/damage/analyze")
async def analyze_image(file: UploadFile = File(...), conf: float = Query(0.25, ge=0.0, le=1.0)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    run_id = str(uuid.uuid4())
    ext = PathlibPath(file.filename).suffix or ".jpg"
    save_path = UPLOAD_DIR / f"{run_id}{ext}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)


    detections = predict_from_path(save_path, conf=conf)

    db = SessionLocal()
    try:
        run = DetectionRun(id=run_id, filename=file.filename, meta={"saved_path": str(save_path)})
        db.add(run)
        db.commit()

        for d in detections:
            obj = DetectedObject(
                run_id=run_id,
                class_id=d["class_id"],
                class_name=d["class_name"],
                confidence=d["confidence"],
                bbox=d["bbox_xyxy"],
                pinned={"bbox": d["bbox_xyxy"]},
                condition="unknown"
            )
            db.add(obj)
        db.commit()
        db.refresh(run)

        response_detections = []
        for o in run.objects:
            response_detections.append({
                "object_id": o.id,
                "class_id": o.class_id,
                "class_name": o.class_name,
                "confidence": o.confidence,
                "bbox": o.bbox,
                "pinned": o.pinned,
                "condition": o.condition
            })
    finally:
        db.close()

    return {"id": run_id, "filename": file.filename, "detections": response_detections}

@app.get("/api/damage/{run_id}")
async def get_run(run_id: str = Path(...)):
    db = SessionLocal()
    try:
        run = db.query(DetectionRun).filter(DetectionRun.id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        objects = []
        for o in run.objects:
            objects.append({
                "object_id": o.id,
                "class_id": o.class_id,
                "class_name": o.class_name,
                "confidence": o.confidence,
                "bbox": o.bbox,
                "pinned": o.pinned,
                "condition": o.condition
            })
        return {"id": run.id, "filename": run.filename, "timestamp_utc": run.timestamp_utc.isoformat(), "objects": objects}
    finally:
        db.close()

@app.patch("/api/damage/{run_id}/objects/{object_id}")
async def update_object(run_id: str, object_id: int, payload: UpdateObjectSchema):
    db = SessionLocal()
    try:
        obj = db.query(DetectedObject).filter(DetectedObject.run_id == run_id, DetectedObject.id == object_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        if payload.pinned is not None:
            obj.pinned = payload.pinned
        if payload.condition is not None:
            obj.condition = payload.condition
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {
            "object_id": obj.id,
            "class_id": obj.class_id,
            "class_name": obj.class_name,
            "confidence": obj.confidence,
            "bbox": obj.bbox,
            "pinned": obj.pinned,
            "condition": obj.condition
        }
    finally:
        db.close()

