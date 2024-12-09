import type { User } from '$lib/types/user';
import { jwtDecode } from 'jwt-decode';

interface TokenCache {
    [key: string]: {
        user: User;
        expiresAt: number;
    };
}

const userCache: TokenCache = {};
const CACHE_DURATION = 15 * 60 * 1000; // 15 minutes in milliseconds

export async function validateUser(token: string): Promise<User | null> {
    try {
        const decoded = jwtDecode<{ exp: number }>(token);
        if (decoded.exp * 1000 < Date.now()) {
            return null;
        }

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
        
        const user = {
            id: data.user_id,
            firstName: data.first_name,
            lastName: data.last_name,
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