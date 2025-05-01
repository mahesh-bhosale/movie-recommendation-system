'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/navigation';
import axios from 'axios';

interface UserProfile {
    id: number;
    username: string;
    email: string;
    favorite_genres: string[];
    favorite_actors: string[];
    favorite_directors: string[];
}

export default function ProfilePage() {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const token = useAuthStore(state => state.token);
    const isInitialized = useAuthStore(state => state.isInitialized);
    const router = useRouter();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                if (!token) {
                    router.push('/login');
                    return;
                }

                setLoading(true);
                setError(null);

                const response = await axios.get(
                    `${process.env.NEXT_PUBLIC_API_URL}/api/users/profile`,
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                setProfile(response.data);
            } catch (error) {
                console.error('Error fetching profile:', error);
                if (axios.isAxiosError(error)) {
                    if (error.response?.status === 401) {
                        useAuthStore.getState().clearAuth();
                        router.push('/login');
                    } else {
                        setError(error.response?.data?.detail || 'Failed to load profile');
                    }
                } else {
                    setError('An unexpected error occurred');
                }
            } finally {
                setLoading(false);
            }
        };

        if (isInitialized) {
            fetchProfile();
        }
    }, [isInitialized, token, router]);

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
            <div className="max-w-2xl mx-auto">
                <h1 className="text-3xl font-bold mb-8">Profile</h1>

                {error && (
                    <div className="mb-8 p-4 bg-red-900/50 border border-red-500 rounded-lg">
                        <p className="text-red-500">{error}</p>
                    </div>
                )}

                {loading && (
                    <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                        <p className="text-gray-400">Loading profile...</p>
                    </div>
                )}

                {!loading && profile && (
                    <div className="bg-gray-900 rounded-lg p-6">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-400">Username</label>
                                <p className="mt-1 text-lg">{profile.username}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400">Email</label>
                                <p className="mt-1 text-lg">{profile.email}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400">Favorite Genres</label>
                                <div className="mt-1 flex flex-wrap gap-2">
                                    {profile.favorite_genres.length > 0 ? (
                                        profile.favorite_genres.map((genre, index) => (
                                            <span key={index} className="px-3 py-1 bg-blue-600 rounded-full text-sm">
                                                {genre}
                                            </span>
                                        ))
                                    ) : (
                                        <p className="text-gray-400">No favorite genres yet</p>
                                    )}
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400">Favorite Actors</label>
                                <div className="mt-1 flex flex-wrap gap-2">
                                    {profile.favorite_actors.length > 0 ? (
                                        profile.favorite_actors.map((actor, index) => (
                                            <span key={index} className="px-3 py-1 bg-green-600 rounded-full text-sm">
                                                {actor}
                                            </span>
                                        ))
                                    ) : (
                                        <p className="text-gray-400">No favorite actors yet</p>
                                    )}
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400">Favorite Directors</label>
                                <div className="mt-1 flex flex-wrap gap-2">
                                    {profile.favorite_directors.length > 0 ? (
                                        profile.favorite_directors.map((director, index) => (
                                            <span key={index} className="px-3 py-1 bg-purple-600 rounded-full text-sm">
                                                {director}
                                            </span>
                                        ))
                                    ) : (
                                        <p className="text-gray-400">No favorite directors yet</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
} 