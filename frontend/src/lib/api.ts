import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";
const TMDB_API_KEY = "64172a9a636863a3103a08adbfb987b8";

// Register User
export const registerUser = async (userData: {
    username: string;
    email: string;
    password: string;
    favorite_genres: string[];
    favorite_actors: string[];
    favorite_directors: string[];
}) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/auth/register`, userData);
        return response.data;
    } catch (error) {
        console.error("Registration error:", error);
        throw error;
    }
};

// Login User
export const loginUser = async (userData: { username: string; password: string }) => {
    try {
        console.log("Attempting login with:", userData);
        const response = await axios.post(`${API_BASE_URL}/auth/login`, userData);
        console.log("Login response:", response.data);
        
        if (!response.data.access_token) {
            console.error("No access token received in response");
            throw new Error("No access token received");
        }

        // Set the token in a cookie for middleware access
        document.cookie = `token=${response.data.access_token}; path=/`;

        return response.data;
    } catch (error) {
        console.error("Login error:", error);
        throw error;
    }
};

// Fetch Recommendations with Full Movie Details
export const getRecommendations = async (movie: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/recommend/`, {
            params: { movie },
        });

        const movieTitles = response.data.recommendations || [];

        // Fetch movie details
        const movieDetails = await Promise.all(
            movieTitles.map(async (title: string) => {
                try {
                    const searchRes = await axios.get(
                        `https://api.themoviedb.org/3/search/movie`,
                        {
                            params: { api_key: TMDB_API_KEY, query: title },
                        }
                    );

                    if (!searchRes.data.results.length) return null;

                    const movieData = searchRes.data.results[0];

                    return {
                        id: movieData.id,
                        title: movieData.title,
                        poster_path: movieData.poster_path,
                        overview: movieData.overview,
                        vote_average: movieData.vote_average,
                        genre_ids: movieData.genre_ids,
                    };
                } catch (err) {
                    console.error("Error fetching movie details from TMDb:", err);
                    return null;
                }
            })
        );

        return movieDetails.filter(Boolean);
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        throw error;
    }
};

// Fetch Popular Movies
export const getPopularMovies = async () => {
    try {
        const response = await axios.get(`https://api.themoviedb.org/3/movie/popular`, {
            params: { api_key: TMDB_API_KEY, language: "en-US", page: 1 },
        });

        interface TMDBMovie {
            id: number;
            title: string;
            poster_path: string;
            overview: string;
            vote_average: number;
        }

        return response.data.results.map((movie: TMDBMovie) => ({
            id: movie.id,
            title: movie.title,
            poster_path: movie.poster_path,
            overview: movie.overview,
            vote_average: movie.vote_average,
        }));
    } catch (error) {
        console.error("Error fetching popular movies:", error);
        return [];
    }
};

// Fetch Recommendation History
export const fetchHistory = async (token: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/auth/history`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        return response.data;
    } catch (error) {
        console.error("Error fetching history:", error);
        return [];
    }
};

// Add to History
export const addToHistory = async (token: string, tmdb_movie_id: number) => {
    try {
        console.log(`Adding movie ${tmdb_movie_id} to history...`);  // Debugging
        const response = await axios.post(
            `${API_BASE_URL}/auth/history`,
            { tmdb_movie_id },
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
            }
        );
        console.log('History response:', response.data);  // Debugging
        return response.data;
    } catch (error) {
        console.error("Error adding to history:", error);
        if (axios.isAxiosError(error)) {
            if (error.response?.status === 404) {
                throw new Error("Movie not found");
            } else if (error.response?.status === 422) {
                throw new Error("Invalid movie ID");
            } else if (error.response?.status === 500) {
                throw new Error("Server error while adding to history");
            }
        }
        throw error;
    }
};

// Clear History
export const clearHistory = async (token: string) => {
    try {
        const response = await axios.delete(`${API_BASE_URL}/auth/history`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        console.error("Error clearing history:", error);
        throw error;
    }
};

// Get user's favorite genres
export const getFavoriteGenres = async (token: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/auth/favorites/genres`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching favorite genres:", error);
        return [];
    }
};

// Get user's favorite actors
export const getFavoriteActors = async (token: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/auth/favorites/actors`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching favorite actors:", error);
        return [];
    }
};

// Get user's favorite directors
export const getFavoriteDirectors = async (token: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/auth/favorites/directors`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching favorite directors:", error);
        return [];
    }
};

// Update user's favorite genres
export const updateFavoriteGenres = async (token: string, genres: string[]) => {
    try {
        const response = await axios.put(
            `${API_BASE_URL}/auth/favorites/genres`,
            genres,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        );
        return response.data;
    } catch (error) {
        console.error("Error updating favorite genres:", error);
        throw error;
    }
};

// Update user's favorite actors
export const updateFavoriteActors = async (token: string, actors: string[]) => {
    try {
        const response = await axios.put(
            `${API_BASE_URL}/auth/favorites/actors`,
            actors,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        );
        return response.data;
    } catch (error) {
        console.error("Error updating favorite actors:", error);
        throw error;
    }
};

// Update user's favorite directors
export const updateFavoriteDirectors = async (token: string, directors: string[]) => {
    try {
        const response = await axios.put(
            `${API_BASE_URL}/auth/favorites/directors`,
            directors,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        );
        return response.data;
    } catch (error) {
        console.error("Error updating favorite directors:", error);
        throw error;
    }
};

// Get personalized recommendations
export const getPersonalizedRecommendations = async (token: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/auth/recommendations`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data.recommendations || [];
    } catch (error) {
        console.error("Error fetching personalized recommendations:", error);
        return [];
    }
};
