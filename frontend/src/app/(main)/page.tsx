'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';
import MovieCard from '@/components/ui/MovieCard';

interface Movie {
    id: number;
    title: string;
    overview: string;
    poster_path: string;
    vote_average: number;
}

interface Genre {
    id: number;
    name: string;
}

interface Person {
    id: number;
    name: string;
    profile_path: string;
}

export default function HomePage() {
    const router = useRouter();
    const token = useAuthStore(state => state.token);
    const isInitialized = useAuthStore(state => state.isInitialized);
    
    const [recommendedMovies, setRecommendedMovies] = useState<Movie[]>([]);
    const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
    const [favoriteGenres, setFavoriteGenres] = useState<Genre[]>([]);
    const [favoriteActors, setFavoriteActors] = useState<Person[]>([]);
    const [favoriteDirectors, setFavoriteDirectors] = useState<Person[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isInitialized && !token) {
            router.push('/login');
            return;
        }

        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                // Fetch popular movies from TMDB first
                const popularResponse = await axios.get(
                    'https://api.themoviedb.org/3/movie/popular?api_key=64172a9a636863a3103a08adbfb987b8&language=en-US&page=1'
                );

                // Fetch user's history to get recommendations
                const historyResponse = await axios.get(
                    'http://127.0.0.1:8000/auth/history',
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                // If user has history, fetch recommendations
                if (historyResponse.data && historyResponse.data.length > 0) {
                    try {
                        const recommendedResponse = await axios.get(
                            'http://127.0.0.1:8000/auth/recommendations',
                            {
                                headers: {
                                    'Authorization': `Bearer ${token}`,
                                    'Content-Type': 'application/json'
                                }
                            }
                        );
                        setRecommendedMovies(recommendedResponse.data.recommendations || []);
                    } catch (recommendError) {
                        console.warn('Failed to fetch recommendations:', recommendError);
                        // Don't set error state for recommendation failure
                    }
                }

                // Fetch favorite genres
                try {
                    const genresResponse = await axios.get(
                        'http://127.0.0.1:8000/auth/favorites/genres',
                        {
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        }
                    );
                    // Convert string array to genre objects
                    const genres = (genresResponse.data || []).map((name: string, index: number) => ({
                        id: index + 1,
                        name: name
                    }));
                    setFavoriteGenres(genres);
                } catch (genresError) {
                    console.warn('Failed to fetch favorite genres:', genresError);
                }

                // Fetch favorite actors
                try {
                    const actorsResponse = await axios.get(
                        'http://127.0.0.1:8000/auth/favorites/actors',
                        {
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        }
                    );
                    // Convert string array to person objects
                    const actors = (actorsResponse.data || []).map((name: string, index: number) => ({
                        id: index + 1,
                        name: name,
                        profile_path: '/default-profile.jpg' // Use a default profile image
                    }));
                    setFavoriteActors(actors);
                } catch (actorsError) {
                    console.warn('Failed to fetch favorite actors:', actorsError);
                }

                // Fetch favorite directors
                try {
                    const directorsResponse = await axios.get(
                        'http://127.0.0.1:8000/auth/favorites/directors',
                        {
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        }
                    );
                    // Convert string array to person objects
                    const directors = (directorsResponse.data || []).map((name: string, index: number) => ({
                        id: index + 1,
                        name: name,
                        profile_path: '/default-profile.jpg' // Use a default profile image
                    }));
                    setFavoriteDirectors(directors);
                } catch (directorsError) {
                    console.warn('Failed to fetch favorite directors:', directorsError);
                }

                setPopularMovies(popularResponse.data.results || []);
            } catch (error) {
                console.error('Error fetching data:', error);
                if (axios.isAxiosError(error)) {
                    if (error.response?.status === 401) {
                        useAuthStore.getState().clearAuth();
                        router.push('/login');
                    } else {
                        setError(error.response?.data?.detail || 'Failed to load data');
                    }
                } else {
                    setError('An unexpected error occurred');
                }
            } finally {
                setLoading(false);
            }
        };

        if (isInitialized && token) {
            fetchData();
        }
    }, [isInitialized, token, router]);

    const renderSection = <T,>(
        title: string,
        items: T[],
        renderItem: (item: T) => React.ReactNode,
        emptyMessage?: string
    ) => (
        <section className="mb-12">
            <h2 className="text-2xl font-semibold mb-6">{title}</h2>
            {items.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {items.map((item) => renderItem(item))}
                </div>
            ) : (
                <p className="text-gray-400">{emptyMessage || 'No items found.'}</p>
            )}
        </section>
    );

    if (!isInitialized || !token) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-white">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="text-white p-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-bold mb-8">Welcome to MovieRec</h1>

                {error && (
                    <div className="mb-8 p-4 bg-red-900/50 border border-red-500 rounded-lg">
                        <p className="text-red-500">{error}</p>
                    </div>
                )}

                {loading ? (
                    <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                        <p className="text-gray-400">Loading your personalized content...</p>
                    </div>
                ) : (
                    <>
                        {/* Popular Movies Section */}
                        {renderSection(
                            'Popular Movies',
                            popularMovies,
                            (movie) => (
                                <MovieCard
                                    key={movie.id}
                                    movie={movie}
                                    onClick={() => router.push(`/movie/${movie.id}`)}
                                />
                            )
                        )}

                        {/* Recommended Movies Section */}
                        {renderSection(
                            'Recommended for You',
                            recommendedMovies,
                            (movie) => (
                                <MovieCard
                                    key={movie.id}
                                    movie={movie}
                                    onClick={() => router.push(`/movie/${movie.id}`)}
                                />
                            ),
                            'Start watching movies to get personalized recommendations!'
                        )}

                        {/* Favorite Genres Section */}
                        {renderSection(
                            'Your Favorite Genres',
                            favoriteGenres,
                            (genre) => (
                                <div
                                    key={genre.id}
                                    className="bg-gray-900 rounded-lg p-4 cursor-pointer hover:bg-gray-800 transition-colors"
                                    onClick={() => router.push(`/search?genre=${genre.id}`)}
                                >
                                    <h3 className="text-lg font-medium">{genre.name}</h3>
                                </div>
                            ),
                            'No favorite genres yet. Start exploring movies!'
                        )}

                        {/* Favorite Actors Section */}
                        {renderSection(
                            'Your Favorite Actors',
                            favoriteActors,
                            (actor) => (
                                <div
                                    key={actor.id}
                                    className="bg-gray-900 rounded-lg p-4 cursor-pointer hover:bg-gray-800 transition-colors"
                                    onClick={() => router.push(`/search?actor=${actor.id}`)}
                                >
                                    <div className="aspect-square mb-3 rounded-lg overflow-hidden">
                                        <img
                                            src={actor.profile_path ? 
                                                `https://image.tmdb.org/t/p/w500${actor.profile_path}` : 
                                                'https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg'}
                                            alt={actor.name}
                                            className="w-full h-full object-cover"
                                            onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.src = 'https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg';
                                            }}
                                        />
                                    </div>
                                    <h3 className="text-lg font-medium">{actor.name}</h3>
                                </div>
                            ),
                            'No favorite actors yet. Start watching movies!'
                        )}

                        {/* Favorite Directors Section */}
                        {renderSection(
                            'Your Favorite Directors',
                            favoriteDirectors,
                            (director) => (
                                <div
                                    key={director.id}
                                    className="bg-gray-900 rounded-lg p-4 cursor-pointer hover:bg-gray-800 transition-colors"
                                    onClick={() => router.push(`/search?director=${director.id}`)}
                                >
                                    <div className="aspect-square mb-3 rounded-lg overflow-hidden">
                                        <img
                                            src={director.profile_path ? 
                                                `https://image.tmdb.org/t/p/w500${director.profile_path}` : 
                                                'https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg'}
                                            alt={director.name}
                                            className="w-full h-full object-cover"
                                            onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.src = 'https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg';
                                            }}
                                        />
                                    </div>
                                    <h3 className="text-lg font-medium">{director.name}</h3>
                                </div>
                            ),
                            'No favorite directors yet. Start watching movies!'
                        )}
                    </>
                )}
            </div>
        </div>
    );
} 