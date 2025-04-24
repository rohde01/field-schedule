import { z } from 'zod';

export const facilitySchema = z.object({
    facility_id: z.number().int().positive(),
    club_id: z.number().int().positive(),
    name: z.string().min(1).max(255),
    description: z.string().max(1000).optional(),
    is_primary: z.boolean().default(false)
});

export const facilityCreateSchema = facilitySchema.omit({ 
    facility_id: true 
});

export type Facility = z.infer<typeof facilitySchema>;
export type FacilityCreate = z.infer<typeof facilityCreateSchema>;
