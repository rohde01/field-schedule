import { z } from "zod";

export const userSchema = z.object({
    user_id: z.number(),
    email: z.string().email(),
    first_name: z.string().nullable(),
    last_name: z.string().nullable(),
    role: z.string().default("member"),
    primary_club_id: z.number().nullable()
});

export const createUserSchema = z.object({
    email: z.string().email(),
    password: z.string().min(8, "Password must be at least 8 characters"),
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required"),
});

export const loginSchema = z.object({
    email: z.string().email(),
    password: z.string()
});

export const refreshTokenSchema = z.object({
    refresh_token: z.string()
});

export const loginResponseSchema = z.object({
    access_token: z.string(),
    refresh_token: z.string(),
    user: userSchema
});

export type User = z.infer<typeof userSchema>;
export type CreateUser = z.infer<typeof createUserSchema>;
export type LoginCredentials = z.infer<typeof loginSchema>;
export type RefreshToken = z.infer<typeof refreshTokenSchema>;
export type LoginResponse = z.infer<typeof loginResponseSchema>;