import { writable, get } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { selectSchedule } from './ScheduleDropdownState';
import { dropdownState } from './ScheduleDropdownState';
import { invalidateAll } from '$app/navigation';

export const schedules = writable<Schedule[]>([]);

schedules.subscribe((schedulesList) => {
  if (schedulesList.length === 0) return;

  const currentDropdown = get(dropdownState);
  if (currentDropdown.selectedSchedule) {
    const currentId = currentDropdown.selectedSchedule.schedule_id;
    const updatedSchedule = schedulesList.find(s => s.schedule_id === currentId);
    if (updatedSchedule) {
      selectSchedule(updatedSchedule);
    } else {
      selectSchedule(schedulesList[schedulesList.length - 1]);
    }
  } else {
    selectSchedule(schedulesList[schedulesList.length - 1]);
  }
});

export function setSchedules(newSchedules: Schedule[]) {
    schedules.update(() => {
        console.log('Setting schedules to:', newSchedules);
        return [...newSchedules];
    });
}

export function addSchedule(schedule: Schedule) {
    schedules.update(schedules => {
        const updatedSchedules = [...schedules, schedule];
        console.log('Updated schedules after adding:', updatedSchedules);
        return updatedSchedules;
    });
}

export async function updateScheduleEntry(entryId: number, changes: Partial<ScheduleEntry>) {
    const previousState = get(schedules);
    
    schedules.update(schedulesList => {
        return schedulesList.map(schedule => {
            const updatedEntries = schedule.entries.map(entry => {
                if (entry.schedule_entry_id === entryId) {
                    return { ...entry, ...changes };
                }
                return entry;
            });
            return { ...schedule, entries: updatedEntries };
        });
    });

    // Try to sync with server
    try {
        const formData = new FormData();
        formData.append('entryId', entryId.toString());
        Object.entries(changes).forEach(([key, value]) => {
            formData.append(key, value?.toString() ?? '');
        });

        const response = await fetch('/schedules?/updateEntry', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to update schedule entry');
        }
    } catch (error) {
        console.error('Error updating schedule entry:', error);
        // Revert to previous state if server update fails
        schedules.set(previousState);
        await invalidateAll();
    }
}

export function addScheduleEntry(newEntry: ScheduleEntry) {
    schedules.update(schedulesList => {
        const currentDropdown = get(dropdownState);
        const selectedSchedule = currentDropdown.selectedSchedule;
        if (!selectedSchedule) return schedulesList;
        return schedulesList.map(schedule => {
            if (schedule.schedule_id === selectedSchedule.schedule_id) {
                return { ...schedule, entries: [...schedule.entries, newEntry] };
            }
            return schedule;
        });
    });
}
