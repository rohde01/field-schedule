import { z } from "zod";

export const clubSchema = z.object({
    club_id: z.number().int().positive(),
    name: z.string(),
    owner_id: z.string(),
    created_at: z.string().nullable(),
    updated_at: z.string().nullable()
});

export const createClubSchema = z.object({
    name: z.string().min(3, "Club name must be at least 3 characters"),
});

export const updateClubSchema = z.object({
    name: z.string().min(3, "Club name must be at least 3 characters"),
});

export type Club = z.infer<typeof clubSchema>;
export type CreateClub = z.infer<typeof createClubSchema>;
export type UpdateClub = z.infer<typeof updateClubSchema>;