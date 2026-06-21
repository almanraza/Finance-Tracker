from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
import sentry_sdk

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.expenses import router as expenses_router

# ─── Logging ──────────────────────────────────────────────────────────────────
setup_logging()

# ─── Sentry ───────────────────────────────────────────────────────────────────
if settings.SENTRY_DSN and settings.APP_ENV == "production":
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.2)
    logger.info("Sentry initialized")

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",   # always on — remove in prod if needed
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS — allow everything (Android emulator + Railway + future web) ─────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request Logging ───────────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {response.status_code} {request.url.path}")
    return response

# ─── Global Error Handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# ─── Create DB Tables ──────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(expenses_router, prefix="/api/v1")

# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
@limiter.limit("60/minute")
async def health(request: Request):
    return {"status": "ok", "version": "1.0.0", "env": settings.APP_ENV}
