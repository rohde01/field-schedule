import { writable } from 'svelte/store';
import type { ActiveSchedule } from '$lib/schemas/schedule';

function createActiveSchedulesStore() {
    const { subscribe, set, update } = writable<ActiveSchedule[]>([]);

    return {
        subscribe,
        set: (schedules: ActiveSchedule[]) => set(schedules),
        add: (schedule: ActiveSchedule) => update(schedules => [...schedules, schedule]),
        remove: (id: number) => update(schedules => 
            schedules.filter(schedule => schedule.active_schedule_id !== id)
        ),
        update: (updatedSchedule: ActiveSchedule) => update(schedules => 
            schedules.map(schedule => 
                schedule.active_schedule_id === updatedSchedule.active_schedule_id 
                    ? updatedSchedule 
                    : schedule
            )
        )
    };
}

export const activeSchedules = createActiveSchedulesStore();