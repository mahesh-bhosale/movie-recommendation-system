from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, recommend, hybrid
import app.download_models  # Ensure models are downloaded before anything else
import uvicorn
import os

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
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
