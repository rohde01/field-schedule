import { writable, get } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { selectSchedule } from './ScheduleDropdownState';
import { dropdownState } from './ScheduleDropdownState';

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

export function updateScheduleEntry(entryId: number, changes: Partial<ScheduleEntry>) {
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
