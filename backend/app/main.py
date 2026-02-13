from fastapi import FastAPI

from app.api import admin, ai, alerts, audit, auth, clusters, k8s, kafka, metrics, platform, rbac, spark
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="K8s Data Platform Orchestrator API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    # Dev-friendly bootstrap. Production should use Alembic migrations.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    return {"status": "ready"}


app.include_router(auth.router)
app.include_router(rbac.router)
app.include_router(admin.router)
app.include_router(clusters.router)
app.include_router(k8s.router)
app.include_router(spark.router)
app.include_router(kafka.router)
app.include_router(metrics.router)
app.include_router(platform.router)
app.include_router(alerts.router)
app.include_router(ai.router)
app.include_router(audit.router)
