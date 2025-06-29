// a store for fetched constraints
import { derived, get, writable } from 'svelte/store';
import type { Constraint } from '$lib/schemas/constraint';
import { selectedSchedule, IsCreating } from '$lib/stores/schedules';
import { getTimeFromDate, getWeekdayNumber } from '$lib/utils/dateUtils';
import { v4 as uuidv4 } from 'uuid';
import { teams } from '$lib/stores/teams';

// Maintain stable uids per schedule entry
const uidMap = new Map<string, string>();

export const constraints = derived(
  [selectedSchedule, IsCreating, teams],
  ([$selected, $isCreating, $teams]) => {
    if (!$selected || !$isCreating) return [] as Constraint[];
    // map schedule entries to constraints
    const scheduleConstraints = $selected.schedule_entries
      .filter(entry => entry.team_id != null)
      .map(entry => ({
        // derive a stable key for this entry
        uid: (() => {
          const key = entry.schedule_entry_id?.toString() ?? `${entry.team_id}-${new Date(entry.dtstart).getTime()}`;
          if (!uidMap.has(key)) uidMap.set(key, uuidv4());
          return uidMap.get(key) as string;
        })(),
        team_id: entry.team_id as number,
        year: $teams.find(t => t.team_id === entry.team_id)?.year!,
        start_time: getTimeFromDate(entry.dtstart),
        length: Math.ceil((new Date(entry.dtend).getTime() - new Date(entry.dtstart).getTime()) / (15 * 60 * 1000)),
        day_of_week: getWeekdayNumber(entry.dtstart) as 0|1|2|3|4|5|6,
        required_cost: null,
        field_id: entry.field_id as number,
      } as Constraint));
    
    // Count existing schedule constraints per team
    const scheduleConstraintsByTeam = new Map<number, number>();
    scheduleConstraints.forEach(constraint => {
      const teamId = constraint.team_id;
      scheduleConstraintsByTeam.set(teamId, (scheduleConstraintsByTeam.get(teamId) || 0) + 1);
    });
    
    // generate team-based constraints to balance with schedule constraints
    const teamConstraints: Constraint[] = [];
    $teams.forEach(team => {
      const requiredCount = team.weekly_trainings;
      const existingCount = scheduleConstraintsByTeam.get(team.team_id as number) || 0;
      const remainingCount = Math.max(0, requiredCount - existingCount);
      
      for (let i = 0; i < remainingCount; i++) {
        const key = `team-constraint-${team.team_id}-${i}`; // Generate a stable key
        if (!uidMap.has(key)) {
          uidMap.set(key, uuidv4()); // Add to map if not present
        }
        teamConstraints.push({
          uid: uidMap.get(key) as string, // Use the stable UID
          team_id: team.team_id as number,
          year: team.year,
          start_time: null,
          length: 6,
          day_of_week: null,
          required_cost: team.minimum_field_size,
          field_id: null,
        });
      }
    });
    return [...scheduleConstraints, ...teamConstraints];
  }
);

// Add global selectedConstraints store
export const selectedConstraints = writable<Constraint[]>([]);

