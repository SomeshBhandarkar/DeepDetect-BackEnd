from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class DetectionRun(Base):
    __tablename__ = "detection_runs"
    id = Column(String, primary_key=True, index=True)     
    filename = Column(String, nullable=True)
    timestamp_utc = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON, nullable=True)

    objects = relationship("DetectedObject", back_populates="run", cascade="all, delete-orphan")

class DetectedObject(Base):
    __tablename__ = "detected_objects"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(String, ForeignKey("detection_runs.id"), nullable=False)
    class_id = Column(Integer, nullable=False)
    class_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=False)  
    pinned = Column(JSON, nullable=True)
    condition = Column(String, nullable=True)

    run = relationship("DetectionRun", back_populates="objects")

