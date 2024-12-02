import { writable } from 'svelte/store';
import type { User, AuthState, AuthStore } from './auth.d';

function createAuthStore(): AuthStore {
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        isAuthenticated: false
    });

    subscribe((state) => {
        console.log('isAuthenticated:', state.isAuthenticated);
    });

    return {
        subscribe,
        set,
        update,
        setUser: (user: User | null) => {
            set({
                user,
                isAuthenticated: !!user
            });
        },
        logout: async () => {
            const response = await fetch('/logout', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include' 
            });

            if (!response.ok) {
                throw new Error('Logout failed');
            }

            set({
                user: null,
                isAuthenticated: false
            });
        }
    };
}

export const auth = createAuthStore();
