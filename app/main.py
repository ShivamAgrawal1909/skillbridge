from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import engine
from app.routers import auth, message, provider, request, review
from app.utils.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("SkillBridge API starting up...")
    yield
    await engine.dispose()
    print("Shutdown complete")


app = FastAPI(
    title="SkillBridge API",
    version="1.0.0",
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(auth.router)
app.include_router(provider.router)
app.include_router(request.router)
app.include_router(message.router)
app.include_router(review.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV}