import { z } from 'zod';

// Base schemas for common fields
const fieldSizeEnum = z.enum(['11v11', '8v8', '5v5', '3v3']);
const fieldTypeEnum = z.enum(['full', 'half', 'quarter']);
const dayOfWeekEnum = z.enum(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);

// Unified Field availability schema with an optional club_id.
// When creating new records, club_id is omitted; when retrieving records, it is set.
const fieldAvailabilitySchema = z.object({
  day_of_week: dayOfWeekEnum,
  start_time: z.string().regex(
    /^([0-1][0-9]|2[0-3]):(00|15|30|45)$/,
    "Time must be in 15-minute increments (00, 15, 30, 45)"
  ),
  end_time: z.string().regex(
    /^([0-1][0-9]|2[0-3]):(00|15|30|45)$/,
    "Time must be in 15-minute increments (00, 15, 30, 45)"
  ),
  club_id: z.number().int().positive().optional()
});

// Sub-field creation schema (for half fields)
const subFieldCreateSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255),
  field_type: z.literal('half'),
  quarter_fields: z.array(
    z.object({
      name: z.string().trim().min(1, "Name is required").max(255),
      field_type: z.literal('quarter')
    })
  ).max(2, "A half field can have at most 2 quarter fields").default([])
});

// Field creation schema for new fields.
// Notice that club_id is not accepted from the client.
export const fieldCreateSchema = z.object({
  facility_id: z.number().int().positive(),
  name: z.string().trim().min(1, "Name is required").max(255),
  size: fieldSizeEnum,
  field_type: z.literal('full'),
  half_fields: z.array(subFieldCreateSchema)
    .max(2, "A full field can have at most 2 half fields")
    .default([])
    .refine(
      (fields) => fields.length === 0 || fields.length === 2,
      {
        message: "Must specify either 0 or exactly 2 half fields",
        path: ["half_fields"]
      }
    )
    .refine(
      (fields) => fields.every(field =>
        field.quarter_fields.length === 0 || field.quarter_fields.length === 2
      ),
      {
        message: "Each half field must have either 0 or exactly 2 quarter fields",
        path: ["half_fields"]
      }
    ),
  availabilities: z.array(fieldAvailabilitySchema).default([])
});

// Schema for retrieved sub-fields.
const subFieldSchema = z.object({
  field_id: z.number().int().positive(),
  facility_id: z.number().int().positive(),
  club_id: z.number().int().positive(),
  name: z.string(),
  is_active: z.boolean(),
  parent_field_id: z.number().int().positive()
});

// Schema for retrieved fields.
export const fieldSchema = z.object({
  field_id: z.number().int().positive(),
  facility_id: z.number().int().positive(),
  club_id: z.number().int().positive(),
  name: z.string().min(1).max(255),
  size: fieldSizeEnum,
  field_type: fieldTypeEnum,
  parent_field_id: z.number().int().positive().nullable(),
  is_active: z.boolean(),
  availability: z.record(dayOfWeekEnum, fieldAvailabilitySchema),
  quarter_subfields: z.array(subFieldSchema),
  half_subfields: z.array(subFieldSchema)
});

// Field availability creation schema
export const fieldAvailabilityCreateSchema = z.object({
  availabilities: z.array(fieldAvailabilitySchema)
});

export const deleteFieldSchema = z.object({
  field_id: z.number().int().positive()
});

export type DeleteFieldResponse = {
  message: string;
  action: string;
};

// Types
export type Field = z.infer<typeof fieldSchema>;
export type FieldCreate = z.infer<typeof fieldCreateSchema>;
export type FieldAvailability = z.infer<typeof fieldAvailabilitySchema>;
export type FieldAvailabilityCreate = z.infer<typeof fieldAvailabilityCreateSchema>;
