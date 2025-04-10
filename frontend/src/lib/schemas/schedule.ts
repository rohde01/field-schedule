import { z } from 'zod';
import { constraintSchema } from './constraint';
const timeStringRegex = /^([0-1]\d|2[0-3]):([0-5]\d)(:[0-5]\d)?$/;

export const scheduleEntrySchema = z.object({
    schedule_entry_id: z.number().int().positive(),
    override_id: z.number().int().positive().nullable().optional(),
    schedule_id: z.number().int().positive(),
    team_id: z.number().int().positive().nullable(),
    field_id: z.number().int().positive().nullable(),
    start_time: z.string().regex(timeStringRegex, { 
      message: "Time must be in HH:MM or HH:MM:SS format" 
    }),
    end_time: z.string().regex(timeStringRegex, { 
      message: "Time must be in HH:MM or HH:MM:SS format" 
    }),
    week_day: z.number().int().min(0).max(6).nullable().optional(),
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, { 
      message: "Date must be in the format YYYY-MM-DD" 
    }).nullable().optional(),
    type: z.enum(["recurring", "override", "one_off"]),
    is_deleted: z.boolean().default(false),
    isTemporary: z.boolean().optional()
  });
  

export const scheduleSchema = z.object({
    schedule_id: z.number().int(),
    club_id: z.number().int().positive(),
    name: z.string().min(1),
    facility_id: z.number().int().positive(),
    schedule_entries: z.array(scheduleEntrySchema)
});

export type ScheduleEntry = z.infer<typeof scheduleEntrySchema>;
export type Schedule = z.infer<typeof scheduleSchema>;

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

export const activeScheduleCreateSchema = z.object({
    club_id: z.number(),
    schedule_id: z.number(),
    start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/)  
});

export const activeScheduleUpdateSchema = z.object({
    schedule_id: z.number(),
    start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/) 
});

export type ActiveSchedule = {
    active_schedule_id: number;
    schedule_id: number;
    start_date: string;
    end_date: string;
    is_active?: boolean;
};

export type CalendarDate = {
    date: Date;
    weekDay: number;
    formattedDate: string;
    isWithinActiveSchedule: boolean;
    activeScheduleId?: number;
};

export type ActiveScheduleCreate = z.infer<typeof activeScheduleCreateSchema>;
export type ActiveScheduleUpdate = z.infer<typeof activeScheduleUpdateSchema>;
