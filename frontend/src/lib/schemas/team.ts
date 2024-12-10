import { z } from 'zod';

const validFieldSizes = [125, 250, 500, 1000] as const;
type ValidFieldSize = typeof validFieldSizes[number];

export const teamSchema = z.object({
    name: z.string().min(1),
    year: z.string().regex(/^U([4-9]|1[0-9]|2[0-4])$/),
    club_id: z.number().int().positive(),
    gender: z.enum(['boys', 'girls']),
    is_academy: z.boolean(),
    minimum_field_size: z.number()
        .refine((size): size is ValidFieldSize => validFieldSizes.includes(size as ValidFieldSize), 
            { message: 'Field size must be one of: 125, 250, 500, 1000' }),
    preferred_field_size: z.number()
        .refine((size): size is ValidFieldSize => validFieldSizes.includes(size as ValidFieldSize), 
            { message: 'Preferred field size must be one of: 125, 250, 500, 1000' })
        .nullable(),
    level: z.number().int().min(1).max(5),
    is_active: z.boolean().default(true)
});

export type TeamSchema = z.infer<typeof teamSchema>;