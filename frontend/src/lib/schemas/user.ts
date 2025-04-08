import { z } from "zod";

export const userSchema = z.object({
    user_id: z.number(),
    email: z.string().email(),
    first_name: z.string().nullable(),
    last_name: z.string().nullable(),
    role: z.string().default("member"),
    club_id: z.number().nullable()
});

export const createUserSchema = z.object({
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(8, "Password must be at least 8 characters")
});

export const loginSchema = z.object({
    email: z.string().email(),
    password: z.string()
});


export type User = z.infer<typeof userSchema>;
export type CreateUser = z.infer<typeof createUserSchema>;
export type LoginCredentials = z.infer<typeof loginSchema>;