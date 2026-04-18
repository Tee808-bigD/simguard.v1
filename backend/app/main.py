"""SimGuard FastAPI entry point."""
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
from app.security import check_payload_size, SECURITY_HEADERS
from app.rate_limiter import limiter
from app.api.transactions import router as tx_router
from app.api.fraud import router as fraud_router
from app.api.dashboard import router as dash_router
from app.api.verification import router as ver_router
from app.websocket import manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SimGuard starting...")
    await init_db()
    logger.info("Database ready")
    yield
    logger.info("SimGuard stopping...")


app = FastAPI(title="SimGuard API", description="Real-time SIM Swap Fraud Prevention", version="1.0.0", lifespan=lifespan,
              docs_url="/docs", redoc_url=None)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"], expose_headers=["*"], max_age=600)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH"):
        await check_payload_size(request)
    response = await call_next(request)
    for k, v in SECURITY_HEADERS.items():
        response.headers[k] = v
    if "server" in response.headers:
        del response.headers["server"]
    return response


app.include_router(tx_router)
app.include_router(fraud_router)
app.include_router(dash_router)
app.include_router(ver_router)


@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    return {"name": "SimGuard", "version": "1.0.0", "camara_apis": ["SIM Swap", "Device Swap", "Number Verification"], "ai": "Claude"}


@app.get("/health")
async def health():
    return {"status": "healthy"}