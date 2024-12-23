export interface User {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    role: string;
    primary_club_id?: number | null; 

}

declare global {
    namespace App {
        interface Locals {
            user: User | null;
        }
    }
}