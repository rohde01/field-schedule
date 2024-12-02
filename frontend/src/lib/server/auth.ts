import type { User } from '$lib/types/user';

export async function validateUser(token: string): Promise<User | null> {
    try {
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
            role: data.role
        };
        
        console.log('validateUser return value:', user);
        return user;
    } catch {
        console.log('validateUser return value: null');
        return null;
    }
}