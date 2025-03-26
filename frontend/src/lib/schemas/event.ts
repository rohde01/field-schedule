import { z } from 'zod';

const timeStringRegex = /^([0-1]\d|2[0-3]):([0-5]\d)(:[0-5]\d)?$/;

export const EventSchema = z.object({
  schedule_entry_id: z.number().int().positive(),
  override_id: z.number().int().positive(),
  override_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  team_id: z.number().int().positive().nullable(),
  field_id: z.number().int().positive().nullable(),
  start_time: z.string().regex(timeStringRegex, { 
    message: "Time must be in HH:MM or HH:MM:SS format" 
  }),
  end_time: z.string().regex(timeStringRegex, { 
    message: "Time must be in HH:MM or HH:MM:SS format" 
  }),
  week_day: z.number().int().min(0).max(6),
  is_deleted: z.boolean()
});

export type Event = z.infer<typeof EventSchema>;

export const EventScheduleSchema = z.object({
  schedule_id: z.number().int().positive(),
  club_id: z.number().int().positive(),
  name: z.string(),
  facility_id: z.number().int().positive().nullable(),
  entries: z.array(EventSchema)
});

export type EventSchedule = z.infer<typeof EventScheduleSchema>;

export const EventOverrideCreateSchema = z.object({
  active_schedule_id: z.number().int().positive(),
  override_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  new_start_time: z.string().regex(timeStringRegex, { 
    message: "Time must be in HH:MM or HH:MM:SS format" 
  }),
  new_end_time: z.string().regex(timeStringRegex, { 
    message: "Time must be in HH:MM or HH:MM:SS format" 
  }),
  new_team_id: z.number().int().positive().nullable().optional(),
  new_field_id: z.number().int().positive().nullable().optional(),
  schedule_entry_id: z.number().int().positive().nullable().optional(),
  is_deleted: z.boolean().optional().default(false)
});

export const EventOverrideUpdateSchema = z.object({
  override_id: z.number().int().positive(),
  new_start_time: z.string().regex(timeStringRegex).optional(),
  new_end_time: z.string().regex(timeStringRegex).optional(),
  new_team_id: z.number().int().positive().nullable().optional(),
  new_field_id: z.number().int().positive().nullable().optional(),
  override_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  is_deleted: z.boolean().optional()
});

export type EventOverrideCreate = z.infer<typeof EventOverrideCreateSchema>;
export type EventOverrideUpdate = z.infer<typeof EventOverrideUpdateSchema>;
