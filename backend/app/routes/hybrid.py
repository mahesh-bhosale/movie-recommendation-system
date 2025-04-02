import numpy as np
import pandas as pd
import joblib
import pickle
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict

# Load collaborative filtering model files
MoviesData = joblib.load("app/ml_model/Movies_Datase.pkl")
X = joblib.load("app/ml_model/Movies_Learned_Features.pkl")

# Load content-based filtering model files
movie_dict = pickle.load(open("app/ml_model/movie_dict.pkl", "rb"))
simi = pickle.load(open("app/ml_model/simi.pkl", "rb"))
movies = pd.DataFrame(movie_dict)

# FastAPI Router
router = APIRouter()

# Global storage (consider using a database instead)
user_ratings = np.zeros((9724, 1))
added_movies = []

class MovieRating(BaseModel):
    movie: str
    rating: int

class RecommendationResponse(BaseModel):
    recommended_movies: List[Dict[str, str]]

def gradient_descent(X, y, theta, alpha=0.001, num_iters=4000):
    """Gradient descent for collaborative filtering."""
    m = float(y.shape[0])
    for _ in range(num_iters):
        # Ensure the shapes are correct
        if len(theta.shape) == 1:
            theta = theta.reshape(-1, 1)  # Reshape to (n, 1)
        if len(y.shape) == 1:
            y = y.reshape(-1, 1)  # Reshape to (m, 1)
        
        # Perform gradient descent step
        theta -= (alpha / m) * np.dot(X.T, (np.dot(X, theta) - y))
    return theta

def add_movie(movie: str, rating: int):
    """Check and add movie to user ratings."""
    global user_ratings, added_movies

    if not (0 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")

    movie = movie.lower().strip()
    
    # Ensure case-insensitive search
    index = MoviesData[MoviesData["title"].str.lower().str.strip() == movie].index
    if index.empty:
        raise HTTPException(status_code=404, detail="Movie not found in dataset")

    index = index.values[0]
    user_ratings[index] = rating

    if movie in added_movies:
        raise HTTPException(status_code=400, detail="Movie already added")

    added_movies.append(movie)
    return {"message": f"Successfully added {movie} with rating {rating}"}

@router.post("/add_movie", response_model=dict)
def add_movie_to_ratings(movie_data: MovieRating):
    return add_movie(movie_data.movie, movie_data.rating)

@router.post("/reset")
def reset_ratings():
    """Reset all user ratings."""
    global user_ratings, added_movies
    user_ratings = np.zeros((9724, 1))
    added_movies = []
    return {"message": "Successfully reset all ratings"}

def collaborative_recommend():
    """Generate movie recommendations using collaborative filtering."""
    global user_ratings, added_movies

    if len(added_movies) == 0:
        return pd.DataFrame(columns=["title", "collab_score"])

    y = user_ratings[np.nonzero(user_ratings)].reshape(-1, 1)
    indices = np.where(user_ratings)[0]
    X_selected = np.array([X[idx] for idx in indices])

    # Ensure theta has the correct shape: (num_features, 1)
    theta = gradient_descent(X_selected, y, np.zeros((X_selected.shape[1], 1)))

    # Matrix multiplication (ensure compatibility)
    predictions = X @ theta  # X: (num_movies, num_features), theta: (num_features, 1)
    predictions = np.reshape(predictions, -1)  # Flatten to 1D array

    predicted_data = MoviesData.copy()
    predicted_data["collab_score"] = predictions
    sorted_movies = predicted_data.sort_values(by="collab_score", ascending=False)

    # Remove already rated (added) movies from the recommendations
    sorted_movies = sorted_movies[~sorted_movies["title"].isin(added_movies)]

    return sorted_movies[["title", "collab_score"]]


def content_recommend(movie_name: str):
    """Generate movie recommendations using content-based filtering."""
    global movies, simi

    movie_name = movie_name.lower().strip()
    
    if movie_name not in movies['title'].str.lower().values:
        raise HTTPException(status_code=404, detail="Movie not found in content-based dataset")
    
    movie_idx = movies[movies['title'].str.lower() == movie_name].index[0]
    sim_scores = simi[movie_idx]
    
    # Sort by similarity score, excluding the movie itself
    sim_scores = sorted(list(enumerate(sim_scores)), key=lambda x: x[1], reverse=True)
    
    # Get top 10 recommended movies
    recommended_movies = []
    for idx, score in sim_scores[1:11]:  # Skip the movie itself
        recommended_movies.append({"title": movies.iloc[idx]["title"], "content_score": score})

    return pd.DataFrame(recommended_movies)


@router.get("/recommend", response_model=RecommendationResponse)
def recommend_movies(limit: int = Query(10, ge=1, le=50)):
    """Generate hybrid movie recommendations."""
    global user_ratings, added_movies

    if len(added_movies) == 0:
        raise HTTPException(status_code=400, detail="Add some movies first!")

    # Get collaborative recommendations
    collab_recs = collaborative_recommend()
    if collab_recs is None or collab_recs.empty:
        raise HTTPException(status_code=500, detail="Collaborative filtering failed")

    # Get content-based recommendations for user's first rated movie
    content_recs = content_recommend(added_movies[0])
    
    # Merge the two recommendation lists
    hybrid_recs = collab_recs.merge(content_recs, on="title", how="outer").fillna(0)

    # Weighted blending
    alpha = 0.7  # Adjust weight between CF & CB
    hybrid_recs["final_score"] = alpha * hybrid_recs["collab_score"] + (1 - alpha) * hybrid_recs["content_score"]

    # Sort by final score
    hybrid_recs = hybrid_recs.sort_values(by="final_score", ascending=False)

    recommendations = [{"title": row["title"]} for _, row in hybrid_recs.head(limit).iterrows()]
    return {"recommended_movies": recommendations}

@router.get("/movies/dataset")
def get_dataset_movies():
    """Get list of movies from the trained dataset."""
    try:
        movies_list = MoviesData["title"].tolist()
        return {"movies": movies_list}
    except Exception as e:
        print(f"Error in get_dataset_movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
