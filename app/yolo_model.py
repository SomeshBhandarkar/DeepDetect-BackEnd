import os
from pathlib import Path
from ultralytics import YOLO

MODEL_PATH = os.environ.get("YOLO_MODEL_PATH", "/app/models/best.pt")
MODEL_PATH = str(MODEL_PATH)

_model = None

def get_model():
    """Lazy load the YOLO model on first use"""
    global _model
    if _model is None:
        if not Path(MODEL_PATH).exists():
            raise FileNotFoundError(
                f"YOLO model not found at {MODEL_PATH}. "
                f"Place best.pt in the models directory or set YOLO_MODEL_PATH env var."
            )
        print(f"Loading YOLO model from {MODEL_PATH}...")
        _model = YOLO(MODEL_PATH)
        print("YOLO model loaded successfully!")
    return _model

def predict_from_path(image_path, conf=0.25, imgsz=640):
    """
    Returns list of detections:
    [{'class_id': int, 'class_name': str, 'confidence': float, 'bbox_xyxy': [x1,y1,x2,y2]}, ...]
    """
    model = get_model() 
    results = model.predict(source=str(image_path), imgsz=imgsz, conf=conf, save=False)
    res = results[0]
    detections = []
    if hasattr(res, "boxes") and res.boxes is not None:
        for b in res.boxes:
            try:
                xyxy = b.xyxy.cpu().numpy().tolist()[0]
            except Exception:
                xyxy = getattr(b, "xyxy", b.xyxy).tolist()[0]
            try:
                conf_score = float(b.conf.cpu().numpy()[0])
            except Exception:
                conf_score = float(getattr(b, "conf", b.conf).tolist()[0])
            try:
                cls_id = int(b.cls.cpu().numpy()[0])
            except Exception:
                cls_id = int(getattr(b, "cls", b.cls).tolist()[0])
            name = model.names.get(cls_id, str(cls_id)) if hasattr(model, "names") else str(cls_id)
            detections.append({
                "class_id": cls_id,
                "class_name": name,
                "confidence": conf_score,
                "bbox_xyxy": [float(v) for v in xyxy]
            })

    return detections
