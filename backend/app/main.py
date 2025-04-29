from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS
from app.routes import user, recommend, hybrid
# from app.hybrid import router as hybrid_router  # Import hybrid router
import app.download_models  #  Ensures models are downloaded before anything else
import uvicorn

app = FastAPI(title="Movie Recommendation System")

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change "*" to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # ✅ Allow all headers
)

# Include routes
app.include_router(user.router, prefix="/auth", tags=["Auth"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendation"])
app.include_router(hybrid.router, prefix="/hybrid", tags=["Hybrid"])  # Add hybrid router

@app.get("/")
def root():
    return {"message": "Welcome to the Movie Recommendation API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
