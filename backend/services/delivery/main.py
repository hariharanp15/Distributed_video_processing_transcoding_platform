from services.common.app_factory import service_app
from .routes import router
app = service_app("Media Delivery Service", router)
