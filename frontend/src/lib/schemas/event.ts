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
