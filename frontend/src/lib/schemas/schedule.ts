import { z } from 'zod';

const dateCoercer = (message: string = "Must be a valid date/time") => 
  z.coerce.date({
    errorMap: () => ({ message })
  });

export const scheduleEntrySchema = z.object({
    schedule_entry_id: z.number().int().nullable().optional().default(null), // Database primary key for this specific entry. Generated by the database.
    schedule_id: z.number().int().positive().nullable().optional(), // Foreign key linking this entry to a parent 'schedules' container.

    uid: z.string().uuid({ message: "uid must be a valid UUID" }), // A unique identifier for this entry, used to distinguish it from other entries. This is a UUID.

    team_id: z.number().int().positive().nullable().optional(),
    field_id: z.number().int().positive().nullable().optional(),

    // The start date and time of this specific event instance or the first instance in a recurring series. Required.
    dtstart: dateCoercer("dtstart must be a valid date/time string"),
    
    // The end date and time of this specific event instance or the first instance in a recurring series. Must be after dtstart. Required.
    dtend: dateCoercer("dtend must be a valid date/time string"),
    
    recurrence_rule: z.string().nullable().optional(), // An RFC 5545 recurrence rule string (e.g., 'FREQ=WEEKLY;BYWEEKDAY=MO;UNTIL=...') defining how this event repeats. Null for standalone events or exception entries.
    
    // If this entry represents an exception (modification/override) to a recurring series, this field holds the ORIGINAL start timestamp of the instance being overridden. Null otherwise.
    recurrence_id: dateCoercer("recurrence_id must be a valid date/time string").nullable().optional(),
    
    // An array of specific original start dates/times that should be excluded (cancelled) from the recurrence rule defined in the master entry.
    exdate: z.array(dateCoercer("Each exdate must be a valid date/time string")).nullable().optional(),
  
    summary: z.string().max(255).nullable().optional(), // A short, user-visible title or summary for the event (e.g., "U12 Practice").
    description: z.string().nullable().optional(), // A longer, user-visible description or notes field for the event.
  
  }).refine(data => data.dtend > data.dtstart, {
    message: "dtend must be after dtstart",
    path: ["dtend"], // Point error to the dtend field
  });
  

export const scheduleSchema = z.object({
    schedule_id: z.number().int().nullable().optional(),
    club_id: z.number().int().positive(),
    name: z.string().min(1),
    facility_id: z.number().int().positive().nullable().optional(),
    schedule_entries: z.array(scheduleEntrySchema),
    active_from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, {
        message: "active_from must be in the format YYYY-MM-DD"
      }).nullable().optional(),
    active_until: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, {
        message: "active_until must be in the format YYYY-MM-DD"
      }).nullable().optional(),
    description: z.string().nullable().optional(),
    created_at: z.string().optional()
    
});

export const createScheduleSchema = z.object({
  club_id: z.number().int().positive(),
  facility_id: z.number().int().positive(),
  name: z.string().min(1),
  active_from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, { message: "active_from must be in the format YYYY-MM-DD" }).nullable().optional(),
  active_until: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, { message: "active_until must be in the format YYYY-MM-DD" }).nullable().optional(),
  description: z.string().nullable().optional(),
  schedule_entries: z.array(scheduleEntrySchema).optional(),
});
export type CreateScheduleInput = z.infer<typeof createScheduleSchema>;

export const deleteScheduleSchema = z.object({
    schedule_id: z.number().int().positive()
});

export type ScheduleEntry = z.infer<typeof scheduleEntrySchema>;
export type Schedule = z.infer<typeof scheduleSchema>;
export type DeleteScheduleResponse = {
    message: string;
    action: string;
};

export const updateScheduleSchema = z.object({
  schedule_id: z.number().int().positive(),
  name: z.string().min(1),
  description: z.string().nullable().optional(),
  active_from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, { message: "active_from must be in the format YYYY-MM-DD" }).nullable().optional(),
  active_until: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, { message: "active_until must be in the format YYYY-MM-DD" }).nullable().optional()
});
export type UpdateScheduleInput = z.infer<typeof updateScheduleSchema>;

