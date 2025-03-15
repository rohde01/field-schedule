import { writable } from 'svelte/store';
import type { ActiveSchedule } from '$lib/schemas/schedule';

// Store to track if there are unsaved changes
export const hasUnsavedChanges = writable(false);

// Store to track deleted schedules that need to be processed on save
export const deletedSchedules = writable<number[]>([]);

function createActiveSchedulesStore() {
    const { subscribe, set, update } = writable<ActiveSchedule[]>([]);

    return {
        subscribe,
        set: (schedules: ActiveSchedule[]) => {
            set(schedules);
            hasUnsavedChanges.set(false);
            deletedSchedules.set([]);
        },
        add: (schedule: ActiveSchedule) => {
            // Ensure all new schedules have negative IDs
            let newSchedule = { ...schedule };
            
            if (!newSchedule.active_schedule_id || newSchedule.active_schedule_id > 1000000000) {
                newSchedule.active_schedule_id = -Math.floor(Math.random() * 10000 + 1);
                console.log('Assigned temporary ID:', newSchedule.active_schedule_id);
            }
                
            update(schedules => [...schedules, newSchedule]);
            hasUnsavedChanges.set(true);
        },
        remove: (id: number) => {
            update(schedules => 
                schedules.filter(schedule => schedule.active_schedule_id !== id)
            );
            
            // Only track deletion of real schedules (positive IDs)
            if (id > 0) {
                deletedSchedules.update(ids => [...ids, id]);
            }
            
            hasUnsavedChanges.set(true);
        },
        update: (updatedSchedule: ActiveSchedule) => {
            update(schedules => 
                schedules.map(schedule => 
                    schedule.active_schedule_id === updatedSchedule.active_schedule_id 
                        ? updatedSchedule 
                        : schedule
                )
            );
            hasUnsavedChanges.set(true);
        }
    };
}

export const activeSchedules = createActiveSchedulesStore();