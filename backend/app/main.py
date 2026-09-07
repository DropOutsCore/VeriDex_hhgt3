from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api.scan import router as scan_router

app = FastAPI(
    title="VERIDEX API",
    description="Visual Evidence Verification Engine Core Service API",
    version="0.1.0",
)

# Register API routes
app.include_router(scan_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok", "service": "VERIDEX Backend", "version": "0.1.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler ensuring no internal stack traces are leaked to users."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred while processing your request.",
            "error_type": type(exc).__name__,
            "details": str(exc),
        },
    )
