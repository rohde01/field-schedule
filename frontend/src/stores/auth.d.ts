import type { Writable } from 'svelte/store';

export interface User {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    role: string;
}

export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
}

export interface AuthStore extends Writable<AuthState> {
    setUser: (user: User) => void;
    logout: () => void;
}

export declare const auth: AuthStore;
