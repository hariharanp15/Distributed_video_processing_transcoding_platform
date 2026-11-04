import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
def uid(): return str(uuid.uuid4())
class Video(Base):
    __tablename__ = "videos"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    filename: Mapped[str] = mapped_column(String(255)); storage_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="uploaded"); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
class VideoMetadata(Base):
    __tablename__ = "video_metadata"
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"), primary_key=True)
    title: Mapped[str] = mapped_column(String(255)); format: Mapped[str] = mapped_column(String(20)); duration: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, default=0); height: Mapped[int] = mapped_column(Integer, default=0); file_size: Mapped[int] = mapped_column(Integer)
class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="queued"); progress: Mapped[int] = mapped_column(Integer, default=0); retries: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow); updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class ProcessingAttempt(Base):
    __tablename__ = "processing_attempts"; __table_args__ = (UniqueConstraint("job_id", "attempt_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); job_id: Mapped[str] = mapped_column(ForeignKey("processing_jobs.id")); attempt_number: Mapped[int] = mapped_column(Integer); status: Mapped[str] = mapped_column(String(20)); error_message: Mapped[str | None] = mapped_column(Text, nullable=True); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
class TranscodingOutput(Base):
    __tablename__ = "transcoding_outputs"; __table_args__ = (UniqueConstraint("video_id", "resolution"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); video_id: Mapped[str] = mapped_column(ForeignKey("videos.id")); resolution: Mapped[str] = mapped_column(String(10)); url: Mapped[str] = mapped_column(String(500)); status: Mapped[str] = mapped_column(String(20), default="ready")
class VideoThumbnail(Base):
    __tablename__ = "video_thumbnails"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"), unique=True); url: Mapped[str] = mapped_column(String(500)); status: Mapped[str] = mapped_column(String(20), default="ready")
