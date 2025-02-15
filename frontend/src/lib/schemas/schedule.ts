import { z } from 'zod';
const timeStringRegex = /^([0-1]\d|2[0-3]):([0-5]\d)(:[0-5]\d)?$/;

export const scheduleEntrySchema = z.object({
    schedule_entry_id: z.number().int().positive(),
    team_id: z.number().int().positive().nullable(),
    field_id: z.number().int().positive().nullable(),
    start_time: z.string().regex(timeStringRegex, { 
        message: "Time must be in HH:MM or HH:MM:SS format" 
    }),
    end_time: z.string().regex(timeStringRegex, { 
        message: "Time must be in HH:MM or HH:MM:SS format" 
    }),
    week_day: z.number().int().min(0).max(6),
    isTemporary: z.boolean().optional()
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
    constraint_id: z.number().int().positive().optional(),
    schedule_entry_id: z.number().int().positive().nullable().optional(),
    team_id: z.number().int().nonnegative(),
    constraint_type: z.enum(['specific', 'flexible', 'auto']),
    sessions: z.number().int().min(1).max(7),
    start_time: z
      .string()
      .regex(timeStringRegex, {
        message: 'Time must be in HH:MM or HH:MM:SS format'
      })
      .nullable()
      .optional(),
    length: z.number().int().min(1).max(10),
    day_of_week: z.number().int().min(0).max(6).nullable(),
    required_field : z.number().int().positive().nullable().optional(),
    partial_field: z.number().int().positive().nullable().optional(),
    required_cost: z.number()
      .refine((val) => [1000, 500, 250, 125].includes(val), {
        message: 'Cost must be one of: 1000, 500, 250, or 125'
      })
      .nullable()
      .optional(),
    partial_cost: z.number()
      .refine((val) => [1000, 500, 250, 125].includes(val), {
        message: 'Cost must be one of: 1000, 500, 250, or 125'
      })
      .nullable()
      .optional(),
    partial_time: z.number().int().min(1).max(10).nullable().optional()
}).superRefine((data, ctx) => {
    const sizeHierarchy = ['quarter', 'half', 'full'] as const;
    const fieldSizeHierarchy = {
        '3v3': 0,
        '5v5': 1,
        '8v8': 2,
        '11v11': 3
    } as const;

    if (data.constraint_type === 'specific') {
        if (!data.required_field) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['required_field'],
                message: 'Required field is required for specific constraint type.'
            });
        }
        if ((data.partial_field === null) !== (data.partial_time === null)) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: 'For specific constraint type, partial_field and partial_time must both be either null or filled.',
                path: ['partial_field']
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
        if ((data.partial_cost === null) !== (data.partial_time === null)) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: 'For flexible constraint type, partial_cost and partial_time must both be either null or filled.',
                path: ['partial_cost']
            });
        }

        if (data.partial_cost && data.required_cost &&
            data.partial_cost <= data.required_cost) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['partial_cost'],
                message: 'Partial session space cost must be strictly larger than required cost'
            });
        }
    }
    if (data.partial_time !== undefined && 
        data.partial_time !== null && 
        data.partial_time >= data.length) {
        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ['partial_time'],
            message: 'Partial session time must be less than total session length.'
        });
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
    schedule_name: z.string()
});

export const deleteScheduleSchema = z.object({
    schedule_id: z.number().int().positive()
});

export type DeleteScheduleResponse = {
    message: string;
    action: string;
};

export type GenerateScheduleRequest = z.infer<typeof generateScheduleRequestSchema>;
