import pytest
from fastapi import HTTPException
from services.upload.routes import validate_upload
def test_rejects_bad_extension():
    with pytest.raises(HTTPException) as err: validate_upload("movie.exe", 10)
    assert err.value.status_code == 415
def test_rejects_oversize(monkeypatch):
    import services.upload.routes as routes
    monkeypatch.setattr(routes, "MAX_UPLOAD_BYTES", 3)
    with pytest.raises(HTTPException) as err: routes.validate_upload("movie.mp4", 4)
    assert err.value.status_code == 413
def test_allows_permitted_video(): validate_upload("movie.mp4", 10)
