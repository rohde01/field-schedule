import { z } from 'zod';
const timeStringRegex = /^([0-1]\d|2[0-3]):([0-5]\d)(:[0-5]\d)?$/;

export const scheduleEntrySchema = z.object({
    schedule_entry_id: z.number().int().positive(),
    team_id: z.number().int().positive().nullable(),
    field_id: z.number().int().positive().nullable(),
    parent_schedule_entry_id: z.number().int().positive().nullable(),
    start_time: z.string().regex(timeStringRegex, { 
        message: "Time must be in HH:MM or HH:MM:SS format" 
    }),
    end_time: z.string().regex(timeStringRegex, { 
        message: "Time must be in HH:MM or HH:MM:SS format" 
    }),
    week_day: z.number().int().min(0).max(6)
});

export const scheduleSchema = z.object({
    schedule_id: z.number().int().positive(),
    club_id: z.number().int().positive(),
    name: z.string().min(1),
    facility_id: z.number().int().positive().nullable(),
    entries: z.array(scheduleEntrySchema)
});

export type ScheduleEntry = z.infer<typeof scheduleEntrySchema>;
export type Schedule = z.infer<typeof scheduleSchema>;

// Constraint schema
export const constraintSchema = z.object({
    team_id: z.number().int().nonnegative(),
    constraint_type: z.enum(['specific', 'flexible']),
    sessions: z.number().int().min(1).max(7),
    start_time: z
      .string()
      .regex(timeStringRegex, {
        message: 'Time must be in HH:MM or HH:MM:SS format'
      })
      .nullable()
      .optional(),
    length: z.number().int().min(1).max(10),
    required_size: z.enum(['11v11', '8v8', '5v5', '3v3']).nullable().optional(),
    subfield_type: z.enum(['full', 'half', 'quarter']).nullable().optional(),
    partial_ses_space_size: z.enum(['full', 'half', 'quarter']).nullable().optional(),
    required_cost: z.number()
      .refine((val) => [1000, 500, 250, 125].includes(val), {
        message: 'Cost must be one of: 1000, 500, 250, or 125'
      })
      .nullable()
      .optional(),
    partial_ses_space_cost: z.number()
      .refine((val) => [1000, 500, 250, 125].includes(val), {
        message: 'Cost must be one of: 1000, 500, 250, or 125'
      })
      .nullable()
      .optional(),
    partial_ses_time: z.number().int().min(1).max(10).nullable().optional()
}).superRefine((data, ctx) => {
    if (data.constraint_type === 'specific') {
        if (!data.required_size) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['required_size'],
                message: 'Required size is required for specific constraint type.'
            });
        }
        if (!data.subfield_type) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['subfield_type'],
                message: 'Subfield type is required for specific constraint type.'
            });
        }
        // Validate partial session fields for specific type
        if ((data.partial_ses_space_size === null) !== (data.partial_ses_time === null)) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: 'For specific constraint type, partial_ses_space_size and partial_ses_time must both be either null or filled.',
                path: ['partial_ses_space_size']
            });
        }
    }
    if (data.constraint_type === 'flexible') {
        if (!data.required_cost) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['required_cost'],
                message: 'Required cost is required for flexible constraint type.'
            });
        }
        // Validate partial session fields for flexible type
        if ((data.partial_ses_space_cost === null) !== (data.partial_ses_time === null)) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: 'For flexible constraint type, partial_ses_space_cost and partial_ses_time must both be either null or filled.',
                path: ['partial_ses_space_cost']
            });
        }
    }
});

export type Constraint = z.infer<typeof constraintSchema>;

export const generateScheduleRequestSchema = z.object({
    facility_id: z.number().int().positive(),
    team_ids: z.array(z.number().int().positive()).min(1, {
        message: "You must tick off at least one team from the sidebar to go in the schedule"
    }),
    constraints: z.array(constraintSchema).optional(),
    club_id: z.number().int().positive(),
    schedule_name: z.string().default("Generated Schedule")
});

export type GenerateScheduleRequest = z.infer<typeof generateScheduleRequestSchema>;
