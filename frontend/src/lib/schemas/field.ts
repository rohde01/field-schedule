import { z } from 'zod';

// Base enums
export const fieldSizeEnum = z.enum(['11v11', '8v8', '5v5', '3v3']);
export const fieldTypeEnum = z.enum(['full', 'half', 'quarter']);
export const dayOfWeekEnum = z.enum(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);

// Base time format validation regex
const timeFormatRegex = /^([0-1][0-9]|2[0-3]):(00|15|30|45)$/;
const timeFormatErrorMsg = "Time must be in 15-minute increments (00, 15, 30, 45)";

// Base field properties
const baseFieldProps = {
  name: z.string().trim().min(1, "Name is required").max(255),
  size: fieldSizeEnum,
  field_type: fieldTypeEnum
};

// Base entity properties with IDs
const baseEntityProps = {
  field_id: z.number().int().positive(),
  facility_id: z.number().int().positive(),
  club_id: z.number().int().positive(),
  is_active: z.boolean(),
};

// Field availability schema
export const fieldAvailabilitySchema = z.object({
  day_of_week: dayOfWeekEnum,
  start_time: z.string().regex(timeFormatRegex, timeFormatErrorMsg),
  end_time: z.string().regex(timeFormatRegex, timeFormatErrorMsg),
  club_id: z.number().int().positive().optional()
});

// Quarter field creation schema
const quarterFieldCreateSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255),
  field_type: z.literal('quarter')
});

// Sub-field creation schema (for half fields)
const subFieldCreateSchema = z.object({
  name: baseFieldProps.name,
  field_type: z.literal('half'),
  quarter_fields: z.array(quarterFieldCreateSchema)
    .max(2, "A half field can have at most 2 quarter fields")
    .default([])
});

// Field creation schema
export const fieldCreateSchema = z.object({
  facility_id: z.number().int().positive(),
  ...baseFieldProps,
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

// Schema for SubField
export interface SubField {
  field_id: number;
  facility_id: number;
  club_id: number;
  field_type: z.infer<typeof fieldTypeEnum>;
  name: string;
  is_active: boolean;
  parent_field_id: number;
  quarter_subfields?: SubField[];
  half_subfields?: SubField[];
}

// SubField Schema
const subFieldSchema: z.ZodType<SubField> = z.lazy(() => z.object({
  ...baseEntityProps,
  name: z.string(),
  field_type: fieldTypeEnum,
  parent_field_id: z.number().int().positive(),
  quarter_subfields: z.array(subFieldSchema).optional(),
  half_subfields: z.array(subFieldSchema).optional()
}));

// Main field schema
export const fieldSchema = z.object({
  ...baseEntityProps,
  ...baseFieldProps,
  parent_field_id: z.number().int().positive().nullable(),
  availability: z.record(dayOfWeekEnum, fieldAvailabilitySchema),
  quarter_subfields: z.array(subFieldSchema).optional().default([]),
  half_subfields: z.array(subFieldSchema).optional().default([])
});

// Flattened field schema
export const flattenedFieldSchema = z.object({
  ...baseEntityProps,
  name: z.string().min(1).max(255),
  size: fieldSizeEnum,
  field_type: fieldTypeEnum,
  parent_field_id: z.number().int().positive().nullable(),
  availability: z.record(dayOfWeekEnum, fieldAvailabilitySchema).optional().default({})
});

// Field availability creation schema
export const fieldAvailabilityCreateSchema = z.object({
  availabilities: z.array(fieldAvailabilitySchema)
});

// Delete and update field schemas
export const deleteFieldSchema = z.object({
  field_id: z.number().int().positive()
});

export const updateFieldSchema = z.object({
  field_id: z.number().int().positive(),
  facility_id: z.number().int().positive(),
  ...baseFieldProps,
  is_active: z.boolean()
});

// Types
export type Field = z.infer<typeof fieldSchema>;
export type FlattenedField = z.infer<typeof flattenedFieldSchema>;
export type FieldCreate = z.infer<typeof fieldCreateSchema>;
export type FieldAvailability = z.infer<typeof fieldAvailabilitySchema>;
export type FieldAvailabilityCreate = z.infer<typeof fieldAvailabilityCreateSchema>;
