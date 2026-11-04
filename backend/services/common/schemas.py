from pydantic import BaseModel
from datetime import datetime
class ProcessRequest(BaseModel): resolutions: list[str] = ["360p", "720p", "1080p"]
class VideoOut(BaseModel): id: str; filename: str; status: str; created_at: datetime
class JobOut(BaseModel): id: str; video_id: str; status: str; progress: int; retries: int; error_message: str | None = None
class MetadataOut(BaseModel): title: str; format: str; duration: int; width: int; height: int; file_size: int
class VideoDetailOut(VideoOut): metadata: MetadataOut | None = None
class StatusOut(BaseModel): video_id: str; status: str; job: JobOut | None = None
class OutputOut(BaseModel): resolution: str; url: str; status: str
class ThumbnailOut(BaseModel): url: str; status: str
class UploadOut(BaseModel): video_id: str; status: str
class ProcessOut(BaseModel): job_id: str; status: str; idempotent: bool | None = None; retry: bool | None = None
