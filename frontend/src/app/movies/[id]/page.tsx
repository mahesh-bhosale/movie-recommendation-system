'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import Image from 'next/image';

interface MovieDetails {
    id: number;
    title: string;
    overview: string;
    poster_path: string;
    backdrop_path: string;
    release_date: string;
    vote_average: number;
    vote_count: number;
    genres: Array<{ id: number; name: string }>;
    runtime: number;
    tagline: string;
    budget: number;
    revenue: number;
    status: string;
    original_language: string;
    popularity: number;
    production_companies: Array<{ id: number; name: string; logo_path: string }>;
    videos: {
        results: Array<{
            key: string;
            site: string;
            type: string;
            official: boolean;
            published_at: string;
        }>;
    };
}

interface Recommendation {
    id: number;
    title: string;
    poster_path: string;
    vote_average: number;
}

export default function MovieDetailsPage() {
    const { id } = useParams();
    const router = useRouter();
    const [movie, setMovie] = useState<MovieDetails | null>(null);
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showTrailer, setShowTrailer] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    const storeMovieHistory = async (tmdbId: number) => {
    if (!isAuthenticated) return;

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            setIsAuthenticated(false);
            return;
        }

        await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL}/auth/history`,
            { tmdb_movie_id: tmdbId },
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );
    } catch (err) {
        console.error('Error storing movie history:', err);
        if (axios.isAxiosError(err) && err.response?.status === 401) {
            // Handle unauthorized error
            localStorage.removeItem('token');
            setIsAuthenticated(false);
            router.push('/login');
        }
    }
};

    useEffect(() => {
        const token = localStorage.getItem('token');
        setIsAuthenticated(!!token);
    }, []);

    useEffect(() => {
        const fetchMovieDetails = async () => {
            try {
                const response = await axios.get(
                    `https://api.themoviedb.org/3/movie/${id}?api_key=${process.env.NEXT_PUBLIC_TMDB_API_KEY}&append_to_response=credits,videos,production_companies`
                );
                setMovie(response.data);
                if (isAuthenticated) {
                    storeMovieHistory(Number(id));
                }
            } catch (err) {
                console.error('Error fetching movie details:', err);
                setError('Failed to load movie details');
            } finally {
                setIsLoading(false);
            }
        };

        fetchMovieDetails();
    }, [id, isAuthenticated]);

    const handleGetRecommendations = async () => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }
    
        try {
            const token = localStorage.getItem('token');
            if (!token) throw new Error('No authentication token found');
            
            if (!movie?.title) {
                throw new Error('Movie title not available');
            }
    
            // First store in history
            await storeMovieHistory(movie.id);
    
            // Then get recommendations
            const response = await axios.get(
                `${process.env.NEXT_PUBLIC_API_URL}/recommend`, // Remove trailing slash
                {
                    params: { 
                        movie: (movie.title).trim() 
                    },
                    headers: { 
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
    
            if (response.data?.recommendations) {
                setRecommendations(response.data.recommendations);
                setError(null);
            } else {
                setError('No recommendations available for this movie');
            }
        } catch (err) {
            console.error('Recommendation error:', err);
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.message || 'Failed to get recommendations');
            } else {
                setError('Failed to get recommendations. Please try again later.');
            }
        }
    };
    
    const getOfficialTrailer = () => {
        if (!movie?.videos?.results) return null;
        return movie.videos.results.find(
            video => video.type === 'Trailer' && video.official && video.site === 'YouTube'
        );
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
                <div className="text-xl">Loading...</div>
            </div>
        );
    }

    if (error || !movie) {
        return (
            <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
                <div className="text-xl text-red-500">{error || 'Movie not found'}</div>
            </div>
        );
    }

    const trailer = getOfficialTrailer();

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Hero Section */}
            <div className="relative h-[60vh] w-full">
                <Image
                    src={`https://image.tmdb.org/t/p/original${movie.backdrop_path}`}
                    alt={movie.title}
                    fill
                    className="object-cover"
                    priority
                />
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-8">
                    <div className="max-w-7xl mx-auto">
                        <h1 className="text-4xl font-bold mb-4">{movie.title}</h1>
                        <p className="text-xl text-gray-300 mb-4">{movie.tagline}</p>
                        <div className="flex gap-4 text-sm text-gray-300">
                            <span>{new Date(movie.release_date).getFullYear()}</span>
                            <span>•</span>
                            <span>{movie.runtime} minutes</span>
                            <span>•</span>
                            <span>{movie.vote_average.toFixed(1)} / 10 ({movie.vote_count} votes)</span>
                        </div>
                        {trailer && (
                            <button
                                onClick={() => setShowTrailer(true)}
                                className="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none flex items-center gap-2"
                            >
                                <span>▶</span> Watch Trailer
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Trailer Modal */}
            {showTrailer && trailer && (
                <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
                    <div className="relative w-full max-w-4xl">
                        <button
                            onClick={() => setShowTrailer(false)}
                            className="absolute -top-12 right-0 text-white text-2xl hover:text-gray-300"
                        >
                            ✕
                        </button>
                        <div className="relative pt-[56.25%]">
                            <iframe
                                src={`https://www.youtube.com/embed/${trailer.key}`}
                                className="absolute inset-0 w-full h-full"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* Content Section */}
            <div className="max-w-7xl mx-auto px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Movie Poster */}
                    <div className="md:col-span-1">
                        <div className="relative aspect-[2/3] rounded-lg overflow-hidden">
                            <Image
                                src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                alt={movie.title}
                                fill
                                className="object-cover"
                            />
                        </div>
                    </div>

                    {/* Movie Details */}
                    <div className="md:col-span-2">
                        <h2 className="text-2xl font-bold mb-4">Overview</h2>
                        <p className="text-gray-300 mb-6">{movie.overview}</p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
                            <div>
                                <h3 className="text-lg font-semibold mb-2">Movie Info</h3>
                                <div className="space-y-2 text-gray-300">
                                    <p><span className="font-medium">Status:</span> {movie.status}</p>
                                    <p><span className="font-medium">Release Date:</span> {new Date(movie.release_date).toLocaleDateString()}</p>
                                    <p><span className="font-medium">Runtime:</span> {movie.runtime} minutes</p>
                                    <p><span className="font-medium">Budget:</span> ${movie.budget?.toLocaleString() || 'N/A'}</p>
                                    <p><span className="font-medium">Revenue:</span> ${movie.revenue?.toLocaleString() || 'N/A'}</p>
                                    <p><span className="font-medium">Language:</span> {movie.original_language.toUpperCase()}</p>
                                    <p><span className="font-medium">Popularity:</span> {movie.popularity.toFixed(1)}</p>
                                </div>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold mb-2">Genres</h3>
                                <div className="flex flex-wrap gap-2">
                                    {movie.genres.map((genre) => (
                                        <span
                                            key={genre.id}
                                            className="px-3 py-1 bg-blue-600 rounded-full text-sm"
                                        >
                                            {genre.name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {movie.production_companies.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold mb-2">Production Companies</h3>
                                <div className="flex flex-wrap gap-4">
                                    {movie.production_companies.map((company) => (
                                        <div key={company.id} className="flex items-center gap-2">
                                            {company.logo_path && (
                                                <Image
                                                    src={`https://image.tmdb.org/t/p/w92${company.logo_path}`}
                                                    alt={company.name}
                                                    width={40}
                                                    height={40}
                                                    className="rounded"
                                                />
                                            )}
                                            <span className="text-gray-300">{company.name}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <h2 className="text-2xl font-bold mb-4">Get Recommendations</h2>
                        {!isAuthenticated ? (
                            <div className="mb-6">
                                <p className="text-gray-300 mb-4">Please log in to get personalized recommendations.</p>
                                <button
                                    onClick={() => router.push('/login')}
                                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none"
                                >
                                    Log In
                                </button>
                            </div>
                        ) : (
                            <div className="flex flex-col gap-4">
                                <button
                                    onClick={handleGetRecommendations}
                                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none flex items-center gap-2"
                                >
                                    <span>🎯</span> Get Recommendations Based on This Movie
                                </button>
                                {error && <p className="text-red-500">{error}</p>}
                            </div>
                        )}
                    </div>
                </div>

                {/* Recommendations */}
                {recommendations.length > 0 && (
                    <div className="mt-12">
                        <h2 className="text-2xl font-bold mb-6">Recommended Movies</h2>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                            {recommendations.map((rec) => (
                                <div
                                    key={rec.id}
                                    className="relative aspect-[2/3] rounded-lg overflow-hidden group cursor-pointer"
                                    onClick={async () => {
                                        if (isAuthenticated) await storeMovieHistory(rec.id);
                                        router.push(`/movies/${rec.id}`);
                                    }}
                                >
                                    <Image
                                        src={`https://image.tmdb.org/t/p/w500${rec.poster_path}`}
                                        alt={rec.title}
                                        fill
                                        className="object-cover transition-transform duration-300 group-hover:scale-105"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                        <div className="absolute bottom-0 left-0 right-0 p-4">
                                            <h3 className="text-lg font-semibold mb-2">{rec.title}</h3>
                                            <p className="text-sm text-yellow-400">
    Rating: {rec.vote_average ? rec.vote_average.toFixed(1) : 'N/A'} / 10
</p>

                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}