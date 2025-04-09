import { z } from "zod";

export const clubSchema = z.object({
    club_id: z.string(),
    name: z.string().nullable(),
    owner_id: z.string().uuid()
});

export const createClubSchema = z.object({
    name: z.string().min(2, "Club name must be at least 2 characters")
});

export const updateNameSchema = z.object({
    name: z.string().min(2, "Club name must be at least 2 characters")
});

export type Club = z.infer<typeof clubSchema>;
export type CreateClub = z.infer<typeof createClubSchema>;
export type UpdateName = z.infer<typeof updateNameSchema>;