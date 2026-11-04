from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from services.common.config import MEDIA_ROOT, MEDIA_ACCESS_TOKEN
from services.common.database import Base, engine
from services.upload.routes import router as upload
from services.metadata.routes import router as metadata
from services.orchestrator.routes import router as orchestrator
from services.delivery.routes import router as delivery
Base.metadata.create_all(engine)
app = FastAPI(title="Distributed Video Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
app.include_router(upload); app.include_router(metadata); app.include_router(orchestrator); app.include_router(delivery)
@app.get("/media/{asset_path:path}")
def media(asset_path: str, token: str = ""):
    if MEDIA_ACCESS_TOKEN and token != MEDIA_ACCESS_TOKEN: raise HTTPException(401, "Valid media token required")
    root, asset = Path(MEDIA_ROOT).resolve(), (Path(MEDIA_ROOT) / asset_path).resolve()
    if root not in asset.parents or not asset.is_file(): raise HTTPException(404, "Media asset not found")
    return FileResponse(asset)
@app.get("/health")
def health(): return {"status": "ok"}
