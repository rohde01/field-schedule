import type { User } from '$lib/schemas/user';
import { jwtDecode } from 'jwt-decode';
import type { Cookies } from '@sveltejs/kit';

interface TokenCache {
    [key: string]: {
        user: User;
        expiresAt: number;
    };
}

const userCache: TokenCache = {};
const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes in milliseconds
const TOKEN_REFRESH_THRESHOLD = 3 * 60; // 3 minutes in seconds

interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export async function refreshTokens(refreshToken: string): Promise<TokenResponse | null> {
    try {
        const response = await fetch('http://localhost:8000/users/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (!response.ok) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Error refreshing tokens:', error);
        return null;
    }
}

export async function validateAndRefreshTokens(
    accessToken: string,
    refreshToken: string | undefined | null,
    cookies: Cookies
): Promise<{ user: User | null; tokenRefreshed: boolean }> {
    try {
        const decoded = jwtDecode<{ exp: number }>(accessToken);
        const now = Math.floor(Date.now() / 1000);
        
        if (decoded.exp - now < TOKEN_REFRESH_THRESHOLD && refreshToken) {
            const newTokens = await refreshTokens(refreshToken);
            
            if (newTokens) {
                // Update cookies with new tokens
                cookies.set('token', newTokens.access_token, {
                    path: '/',
                    httpOnly: true,
                    sameSite: 'strict',
                    secure: process.env.NODE_ENV === 'production',
                    maxAge: 60 * 30 // 30 minutes
                });

                cookies.set('refresh_token', newTokens.refresh_token, {
                    path: '/',
                    httpOnly: true,
                    sameSite: 'strict',
                    secure: process.env.NODE_ENV === 'production',
                    maxAge: 60 * 60 * 24 * 7 // 7 days
                });

                const user = await validateUser(newTokens.access_token);
                return { user, tokenRefreshed: true };
            }
        }

        if (decoded.exp * 1000 < Date.now()) {
            return { user: null, tokenRefreshed: false };
        }

        const user = await validateUser(accessToken);
        return { user, tokenRefreshed: false };
    } catch (error) {
        console.error('Error in validateAndRefreshTokens:', error);
        return { user: null, tokenRefreshed: false };
    }
}

export async function validateUser(token: string): Promise<User | null> {
    try {
        const cachedData = userCache[token];
        if (cachedData && cachedData.expiresAt > Date.now()) {
            return cachedData.user;
        }

        // If not in cache or expired, fetch from backend
        const response = await fetch('http://localhost:8000/users/me', {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        if (!response.ok) return null;
        const data = await response.json();
        
        const user: User = {
            user_id: data.user_id,
            first_name: data.first_name,
            last_name: data.last_name,
            email: data.email,
            role: data.role,
            primary_club_id: data.primary_club_id
        };

        userCache[token] = {
            user,
            expiresAt: Date.now() + CACHE_DURATION
        };
        
        return user;
    } catch (error) {
        console.error('Error in validateUser:', error);
        return null;
    }
}