import { writable, get } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { selectSchedule, dropdownState } from './ScheduleDropdownState';
import { invalidateAll } from '$app/navigation';
import { syncScheduleEntry } from '$lib/utils/scheduleSync';

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

export async function updateScheduleEntry(entryId: number, changes: Partial<ScheduleEntry>, isLocal: boolean = false) {
    const previousState = get(schedules);
    const currentSchedules = get(schedules);
    const entry = currentSchedules.flatMap(s => s.entries).find(e => e.schedule_entry_id === entryId);
    
    if (!entry) return;

    const updatedEntry = { ...entry, ...changes };
    schedules.update(schedulesList => 
        schedulesList.map(schedule => ({
            ...schedule,
            entries: schedule.entries.map(e => 
                e.schedule_entry_id === entryId ? updatedEntry : e
            )
        }))
    );

    // Skip server sync for local updates during drag
    if (isLocal) return;

    // Sync with server if needed
    if (entry.isTemporary && changes.team_id) {
        const currentDropdown = get(dropdownState);
        if (currentDropdown.selectedSchedule) {
            const result = await syncScheduleEntry(updatedEntry, currentDropdown.selectedSchedule.schedule_id);
            if (!result.success) {
                schedules.set(previousState);
                await invalidateAll();
            }
        }
    } else if (!entry.isTemporary) {
        const result = await syncScheduleEntry(updatedEntry, 0, false);
        if (!result.success) {
            schedules.set(previousState);
            await invalidateAll();
        }
    }
}

export async function addScheduleEntry(newEntry: ScheduleEntry) {
    const currentDropdown = get(dropdownState);
    const selectedSchedule = currentDropdown.selectedSchedule;
    if (!selectedSchedule) return;

    const entryWithFlag = { ...newEntry, isTemporary: !newEntry.team_id };
    // Update local state
    schedules.update(schedulesList => 
        schedulesList.map(schedule => 
            schedule.schedule_id === selectedSchedule.schedule_id
                ? { ...schedule, entries: [...schedule.entries, entryWithFlag] }
                : schedule
        )
    );
    // Only sync with server if entry has a team
    if (!entryWithFlag.isTemporary) {
        const result = await syncScheduleEntry(entryWithFlag, selectedSchedule.schedule_id);
        if (!result.success) {
            // Remove entry if sync failed
            schedules.update(schedulesList => 
                schedulesList.map(schedule => ({
                    ...schedule,
                    entries: schedule.entries.filter(e => 
                        e.schedule_entry_id !== newEntry.schedule_entry_id
                    )
                }))
            );
            await invalidateAll();
        }
    }
}
