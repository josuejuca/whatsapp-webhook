from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.routers.webhook import router as webhook_router
from src.routers.ping import router as ping_router
from src.db.storage import db

API_VERSION = "0.1.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 50)
    db.initialize()
    print("=" * 50)
    yield
    # Shutdown (se necessário no futuro)
    print("até dps, vlw flw...")

app = FastAPI(
    title="Webhook Whatsapp",
    version=API_VERSION,
    description="API Whatsapp Webhook.",
    docs_url="/juk/docs",
    redoc_url="/juk/redoc",
    openapi_url=f"/juk/openapi.json",
    lifespan=lifespan
)

# Registrar rotas
app.include_router(webhook_router)
app.include_router(ping_router)


@app.get("/", tags=["Sistema"])
def read_root():
    return {"message": "Hello Clancy!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
