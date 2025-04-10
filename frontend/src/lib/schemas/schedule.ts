import { z } from 'zod';
import { constraintSchema } from './constraint';

export const scheduleEntrySchema = z.object({
    schedule_entry_id: z.number().int().positive(),
    schedule_id: z.number().int().positive(),
    team_id: z.number().int().positive().nullable(),
    field_id: z.number().int().positive().nullable(),
    dtstart: z.string().refine(val => !isNaN(Date.parse(val)), {
        message: "dtstart must be a valid datetime string",
      }),
      dtend: z.string().refine(val => !isNaN(Date.parse(val)), {
        message: "dtend must be a valid datetime string",
      }),
    is_deleted: z.boolean().default(false),
    recurrence_rule: z.string().optional(),  // If present, should be a valid RRULE string
    recurrence_id: z.string().optional(),
    parent_entry_id: z.number().int().optional(),
  });
  

export const scheduleSchema = z.object({
    schedule_id: z.number().int(),
    club_id: z.number().int().positive(),
    name: z.string().min(1),
    facility_id: z.number().int().positive(),
    schedule_entries: z.array(scheduleEntrySchema),
    active_from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, {
        message: "active_from must be in the format YYYY-MM-DD"
      }),
    active_until: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, {
        message: "active_until must be in the format YYYY-MM-DD"
      }),
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
