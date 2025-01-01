import type { z } from 'zod';
import type { fieldSchema } from '$lib/schemas/field';

type InferredField = z.infer<typeof fieldSchema>;

interface Event {
  id: number;
  title: string;
  field_id: number;
  start_time: string;
  end_time: string;
}

export const sampleFields: InferredField[] = [
  {
    field_id: 1,
    facility_id: 1,
    name: "Kunst 1",
    size: "11v11",
    field_type: "full",
    is_active: true,
    parent_field_id: null,
    availability: {},
    half_subfields: [
      {
        field_id: 2,
        facility_id: 1,
        name: "K1-A",
        is_active: true,
        parent_field_id: 1
      },
      {
        field_id: 5,
        facility_id: 1,
        name: "K1-B",
        is_active: true,
        parent_field_id: 1
      }
    ],
    quarter_subfields: [
      {
        field_id: 3,
        facility_id: 1,
        name: "K1-1",
        is_active: true,
        parent_field_id: 2
      },
      {
        field_id: 4,
        facility_id: 1,
        name: "K1-2",
        is_active: true,
        parent_field_id: 2
      },
      {
        field_id: 6,
        facility_id: 1,
        name: "K1-3",
        is_active: true,
        parent_field_id: 5
      },
      {
        field_id: 7,
        facility_id: 1,
        name: "K1-4",
        is_active: true,
        parent_field_id: 5
      }
    ]
  },
  {
    field_id: 8,
    facility_id: 1,
    name: "Kunst 2",
    size: "11v11",
    field_type: "full",
    is_active: true,
    parent_field_id: null,
    availability: {},
    half_subfields: [
      {
        field_id: 9,
        facility_id: 1,
        name: "K2-A",
        is_active: true,
        parent_field_id: 8
      },
      {
        field_id: 10,
        facility_id: 1,
        name: "K2-B",
        is_active: true,
        parent_field_id: 8
      }
    ],
    quarter_subfields: []
  },
  {
    field_id: 11,
    facility_id: 1,
    name: "Kunst 3",
    size: "11v11",
    field_type: "full",
    is_active: true,
    parent_field_id: null,
    availability: {},
    half_subfields: [],
    quarter_subfields: []
  }
];

export const sampleEvents: Event[] = [
  {
    id: 1,
    title: "Soccer Practice",
    field_id: 1,
    start_time: "16:00",
    end_time: "17:30"
  },
  {
    id: 2,
    title: "Football Match",
    field_id: 11,
    start_time: "17:00",
    end_time: "19:00"
  },
  {
    id: 3,
    title: "Youth Training",
    field_id: 3,
    start_time: "18:00",
    end_time: "20:00"
  }
];