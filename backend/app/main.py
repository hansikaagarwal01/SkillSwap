import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.dependencies import limiter, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("skillswap")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# SlowAPI Limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Consistent Error Handling
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "details": None
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "message": err.get("msg")})
    
    first_msg = errors[0]["message"] if errors else "Invalid request data."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": first_msg,
                "details": errors
            }
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("Database IntegrityError: %s", str(exc.orig))
    orig_msg = str(exc.orig)
    code = "CONFLICT"
    message = "A database constraint violation occurred."
    
    if "Duplicate entry" in orig_msg:
        code = "DUPLICATE_ENTRY"
        message = "A record with this identifier or email already exists."
    elif "foreign key constraint fails" in orig_msg:
        code = "FOREIGN_KEY_VIOLATION"
        message = "Referenced entity does not exist or cannot be modified."
    elif "chk_" in orig_msg:
        code = "CHECK_CONSTRAINT_VIOLATION"
        message = "Value violates business logic constraint rules."

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": orig_msg
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled Exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
                "details": None if settings.APP_ENV == "production" else str(exc)
            }
        }
    )

from app.routers.auth import router as auth_router, admin_router
from app.routers.students import router as students_router
from app.routers.skills import router as skills_router
from app.routers.learning import router as learning_router
from app.routers.marketplace import router as marketplace_router
from app.routers.analytics import router as analytics_router
from app.routers.inquiries import router as inquiries_router
from app.routers.notifications import router as notifications_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1")
app.include_router(skills_router, prefix="/api/v1")
app.include_router(learning_router, prefix="/api/v1")
app.include_router(marketplace_router, prefix="/api/v1")
app.include_router(inquiries_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

# Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    db_status = "disconnected"
    try:
        from app.db.session import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1;"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error("Health check DB connection failed: %s", str(e))
        db_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "app_env": settings.APP_ENV,
        "project": settings.PROJECT_NAME
    }

# Root redirect to docs
@app.get("/", include_in_schema=False)
def root():
    return {"message": "SkillSwap JKLU API is running. Visit /docs for interactive Swagger documentation."}
