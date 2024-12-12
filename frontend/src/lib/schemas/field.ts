import { z } from 'zod';

const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const;
const fieldSizes = ['11v11', '8v8', '5v5', '3v3'] as const;
const fieldTypes = ['full', 'half', 'quarter'] as const;

export const fieldAvailabilitySchema = z.object({
    day_of_week: z.enum(daysOfWeek),
    start_time: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/),
    end_time: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/)
});

export const subFieldSchema: z.ZodType<any> = z.lazy(() => 
    z.object({
        name: z.string().min(1).max(255),
        field_type: z.enum(['half', 'quarter']),
        quarter_fields: z.array(subFieldSchema).optional()
    })
);

export const fieldSchema = z.object({
    facility_id: z.number().int().positive(),
    name: z.string().min(1).max(255),
    size: z.enum(fieldSizes),
    field_type: z.literal('full'),
    half_fields: z.array(subFieldSchema).optional(),
    availabilities: z.array(fieldAvailabilitySchema).optional()
});

export type FieldAvailability = z.infer<typeof fieldAvailabilitySchema>;
export type SubField = z.infer<typeof subFieldSchema>;
export type Field = z.infer<typeof fieldSchema>;
