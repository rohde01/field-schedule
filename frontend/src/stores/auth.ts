import { writable } from 'svelte/store';
import type { User, AuthState, AuthStore } from './auth.d';

function createAuthStore(): AuthStore {
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        isAuthenticated: false
    });

    return {
        subscribe,
        set,
        update,
        setUser: (user: User) => {
            set({
                user,
                isAuthenticated: true
            });
        },
        logout: () => {
            set({
                user: null,
                isAuthenticated: false
            });
        }
    };
}

export const auth = createAuthStore();
