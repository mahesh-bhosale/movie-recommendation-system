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
    const [searchQuery, setSearchQuery] = useState(''); // State to store search query

    // Store movie history
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
        if (!searchQuery.trim()) return; // Ensure query is not empty
        try {
            const token = localStorage.getItem('token');
            if (!token) throw new Error('No authentication token found');

            if (!movie?.title) {
                throw new Error('Movie title not available');
            }

            console.log('Requesting recommendations for:', movie.title);
            console.log('API URL:', `${process.env.NEXT_PUBLIC_API_URL}/recommend`);

            const response = await axios.get(
                `${process.env.NEXT_PUBLIC_API_URL}/recommend`,
                {
                    params: { movie: searchQuery }, // Send the searchQuery as a param
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            console.log('Recommendation response:', response.data);

            if (response.data?.recommendations) {
                setRecommendations(response.data.recommendations);
                setError(null);
            } else {
                setError('No recommendations available for this movie');
            }
        } catch (err) {
            console.error('Recommendation error:', err);
            if (axios.isAxiosError(err)) {
                if (err.response?.status === 401) {
                    localStorage.removeItem('token');
                    setIsAuthenticated(false);
                    router.push('/login');
                } else {
                    setError(err.response?.data?.message || `Failed to get recommendations: ${err.message}`);
                }
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

            {/* Search Query Input */}
            <div className="max-w-7xl mx-auto px-8 py-4">
                <input
                    type="text"
                    className="p-2 rounded-md border-2 border-gray-700 bg-gray-800 text-white w-full"
                    placeholder="Enter movie title to search recommendations"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)} // Update search query
                />
                <button
                    onClick={handleGetRecommendations}
                    className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none flex items-center gap-2"
                >
                    <span>🎯</span> Get Recommendations
                </button>
                {error && <p className="text-red-500">{error}</p>}
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
                                <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent" />
                                <div className="absolute bottom-0 left-0 right-0 p-4">
                                    <p className="text-white font-semibold">{rec.title}</p>
                                    <p className="text-xs text-gray-300">Rating: {rec.vote_average.toFixed(1)}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
