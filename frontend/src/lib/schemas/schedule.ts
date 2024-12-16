import { z } from 'zod';

const timeStringRegex = /^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/;

export const scheduleEntrySchema = z.object({
    schedule_entry_id: z.number().int().positive(),
    team_id: z.number().int().positive().nullable(),
    field_id: z.number().int().positive().nullable(),
    parent_schedule_entry_id: z.number().int().positive().nullable(),
    start_time: z.string().regex(timeStringRegex, { 
        message: "Time must be in HH:MM:SS format" 
    }),
    end_time: z.string().regex(timeStringRegex, { 
        message: "Time must be in HH:MM:SS format" 
    }),
    week_day: z.number().int().min(0).max(6)
});

export const scheduleSchema = z.object({
    schedule_id: z.number().int().positive(),
    club_id: z.number().int().positive(),
    name: z.string().min(1),
    entries: z.array(scheduleEntrySchema)
});

export type ScheduleEntry = z.infer<typeof scheduleEntrySchema>;
export type Schedule = z.infer<typeof scheduleSchema>;

export const generateScheduleRequestSchema = z.object({
    facility_id: z.number().int().positive(),
    team_ids: z.array(z.number().int().positive()),
    constraints: z.array(z.object({
        team_id: z.number().int().positive(),
        required_size: z.string().nullable().optional(),
        subfield_type: z.string().nullable().optional(),
        required_cost: z.number().nullable().optional(),
        sessions: z.number().int().min(1).default(1),
        length: z.number().int().min(1).default(1),
        partial_ses_space_size: z.string().nullable().optional(),
        partial_ses_space_cost: z.number().nullable().optional(),
        partial_ses_time: z.number().nullable().optional(),
        start_time: z.string().nullable().optional()
    })),
    club_id: z.number().int().positive(),
    schedule_name: z.string().default("Generated Schedule")
});

export type GenerateScheduleRequest = z.infer<typeof generateScheduleRequestSchema>;
