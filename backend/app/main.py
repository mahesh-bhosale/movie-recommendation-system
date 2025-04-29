from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import user, recommend, hybrid
import app.download_models  # Ensure models are downloaded before anything else
import uvicorn
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Movie Recommendation System")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(user.router, prefix="/auth", tags=["Auth"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendation"])
app.include_router(hybrid.router, prefix="/hybrid", tags=["Hybrid"])

@app.get("/")
def root():
    return {"message": "Welcome to the Movie Recommendation API"}

@app.get("/health")
def health_check():
    try:
        # Add any health checks here (database, model loading, etc.)
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="debug")
