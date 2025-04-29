from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import user, recommend, hybrid
import app.download_models  # Ensure models are downloaded before anything else
import uvicorn
import os
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Starting application...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

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
        # Check if model files exist
        model_dir = Path("app/ml_model")
        if not model_dir.exists():
            logger.error(f"Model directory not found: {model_dir}")
            raise HTTPException(status_code=500, detail="Model directory not found")
        
        # Check if required model files exist
        required_files = ["movie_dict.pkl", "simi.pkl"]
        missing_files = [f for f in required_files if not (model_dir / f).exists()]
        if missing_files:
            logger.error(f"Missing model files: {missing_files}")
            raise HTTPException(status_code=500, detail=f"Missing model files: {missing_files}")
        
        # Check if database is accessible
        # Add your database health check here if needed
        
        logger.info("Health check passed")
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
