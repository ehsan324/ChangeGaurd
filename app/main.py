from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.changes import router as changes_router
from app.api.routes.audit import router as audit_router
from app.api.routes import metrics



def create_app() -> FastAPI:
    app = FastAPI(
        title="ChangeGaurd",
        version="0.1.0",
    )
    app.include_router(health_router)
    app.include_router(changes_router)
    app.include_router(audit_router)
    app.include_router(metrics.router)

    return app


app = create_app()
