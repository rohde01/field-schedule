import type { z } from 'zod';
import type { fieldSchema } from '$lib/schemas/field';


interface Event {
  id: number;
  title: string;
  field_id: number;
  start_time: string;
  end_time: string;
  week_day: number;
}


export const sampleEvents: Event[] = [
  {
    id: 1,
    title: "Soccer Practice",
    field_id: 275,
    start_time: "16:00",
    end_time: "17:30",
    week_day: 1
  }
];
