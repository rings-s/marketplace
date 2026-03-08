from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
import structlog

from app.config import settings
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.locale import LocaleMiddleware
from app.middleware.response_envelope import ResponseEnvelopeMiddleware
from app.api.routers import (
    auth, users, stores, items, chat, payments, favorites, tags, reports,
    uploads, otp, devices, orders, reviews, notifications,
)
from app.websocket.handlers import ws_router

logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", env=settings.APP_ENV)
    yield
    logger.info("shutdown")


app = FastAPI(
    title="KSA Furniture Marketplace API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware (applied in reverse order — last added runs first)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(ResponseEnvelopeMiddleware)
app.add_middleware(LocaleMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# API routers
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(stores.router, prefix=PREFIX)
app.include_router(items.router, prefix=PREFIX)
app.include_router(chat.router, prefix=PREFIX)
app.include_router(payments.router, prefix=PREFIX)
app.include_router(favorites.router, prefix=PREFIX)
app.include_router(tags.router, prefix=PREFIX)
app.include_router(reports.router, prefix=PREFIX)
app.include_router(uploads.router, prefix=PREFIX)
app.include_router(otp.router, prefix=PREFIX)
app.include_router(devices.router, prefix=PREFIX)
app.include_router(orders.router, prefix=PREFIX)
app.include_router(reviews.router, prefix=PREFIX)
app.include_router(notifications.router, prefix=PREFIX)

# WebSocket
app.include_router(ws_router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
