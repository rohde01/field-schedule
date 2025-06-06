import { z } from 'zod';

export const constraintSchema = z.object({
  uid: z.string().uuid({ message: "uid must be a valid UUID" }),
  team_id: z.number(),
  year: z.string().regex(/^U([4-9]|1[0-9]|2[0-4])$/),
  start_time: z.string()
    .regex(/^([01]\d|2[0-3]):([0-5]\d)$/, "Must be in HH:MM format")
    .nullable()
    .optional(),
  length: z.number(),
  day_of_week: z.union([
    z.literal(0), z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5), z.literal(6)
  ]).nullable().optional(),
  required_cost: z.union([
    z.literal(125), z.literal(250), z.literal(500), z.literal(1000)
  ]).nullable().optional(),
  field_id: z.number().nullable().optional(),
});

export type Constraint = z.infer<typeof constraintSchema>;
