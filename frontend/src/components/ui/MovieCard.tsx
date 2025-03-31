import { useState } from 'react';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

interface Movie {
    id: number;
    title: string;
    overview: string;
    poster_path: string;
    vote_average: number;
}

interface MovieCardProps {
    movie: Movie;
    onClick?: () => void;
}

export default function MovieCard({ movie, onClick }: MovieCardProps) {
    const [isHovered, setIsHovered] = useState(false);
    const token = useAuthStore(state => state.token);

    const handleClick = async () => {
        try {
            // Add to history
            await axios.post('http://127.0.0.1:8000/auth/history', 
                { tmdb_movie_id: movie.id },
                { 
                    headers: { 
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    } 
                }
            );
        } catch (error) {
            console.error('Error adding to history:', error);
        }
    };

    return (
        <div
            className="bg-gray-900 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-pointer"
            onClick={onClick || handleClick}
        >
            <div className="relative pb-[150%]">
                <img
                    src={movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/no-poster.png'}
                    alt={movie.title}
                    className="absolute top-0 left-0 w-full h-full object-cover"
                />
            </div>
            <div className="p-4">
                <h3 className="text-lg font-semibold mb-2 line-clamp-1">{movie.title}</h3>
                <p className="text-gray-400 text-sm mb-2 line-clamp-2">{movie.overview}</p>
                <div className="flex items-center">
                    <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span className="ml-1 text-gray-400">{movie.vote_average.toFixed(1)}</span>
                </div>
            </div>
        </div>
    );
} 