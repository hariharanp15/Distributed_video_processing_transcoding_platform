from fastapi import FastAPI
from services.common.database import Base, engine
def service_app(name: str, router):
    Base.metadata.create_all(engine)
    app = FastAPI(title=name)
    app.include_router(router)
    @app.get("/health")
    def health(): return {"service": name, "status": "ok"}
    return app
