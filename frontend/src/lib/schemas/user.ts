import { z } from "zod";

export const userSchema = z.object({
    user_id: z.string(),
    email: z.string().email(),
    first_name: z.string().nullable(),
    last_name: z.string().nullable(),
    role: z.string().default("member"),
    is_active: z.boolean().default(true),
    club_id: z.number().int().positive().nullable(),
    created_at: z.string().nullable(),
    updated_at: z.string().nullable()
});

export const createUserSchema = z.object({
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(8, "Password must be at least 8 characters")
});

export const loginSchema = z.object({
    email: z.string().email(),
    password: z.string()
});

export const updateNameSchema = z.object({
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required")
});

export type User = z.infer<typeof userSchema>;
export type CreateUser = z.infer<typeof createUserSchema>;
export type LoginCredentials = z.infer<typeof loginSchema>;
export type UpdateName = z.infer<typeof updateNameSchema>;