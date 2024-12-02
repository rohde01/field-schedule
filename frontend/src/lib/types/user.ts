export interface User {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    role: string;
}

declare global {
    namespace App {
        interface Locals {
            user: User | null;
        }
    }
}