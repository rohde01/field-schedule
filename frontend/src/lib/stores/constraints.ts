// a store for fetched constraints
import { derived, get } from 'svelte/store';
import type { Constraint } from '$lib/schemas/constraint';
import { selectedSchedule } from '$lib/stores/schedules';
import { getTimeFromDate, getWeekdayNumber } from '$lib/utils/dateUtils';

export const constraints = derived(
  selectedSchedule,
  ($selected) => {
    if (!$selected) return [] as Constraint[];
    return $selected.schedule_entries
      .filter(entry => entry.team_id != null)
      .map(entry => ({
        team_id: entry.team_id as number,
        sessions: 1,
        start_time: getTimeFromDate(entry.dtstart),
        length: Math.ceil((new Date(entry.dtend).getTime() - new Date(entry.dtstart).getTime()) / (15 * 60 * 1000)),
        day_of_week: getWeekdayNumber(entry.dtstart),
        required_cost: null,
        field_id: entry.field_id as number,
      }));
  }
);

constraints.subscribe(values => {
  console.log('constraints updated:', values);
});

