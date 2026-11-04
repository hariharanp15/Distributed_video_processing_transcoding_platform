from services.common.app_factory import service_app
from .routes import router
app = service_app("Transcoding Orchestrator Service", router)
