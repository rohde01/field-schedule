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

interface TempEntry {
    tempId: number;
    permanentId?: number;
}

const tempEntries = new Map<number, TempEntry>();

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

    // Only sync with server if the entry is NOT temporary or if it's being converted to permanent
    if (!entry.isTemporary) {
        const result = await syncScheduleEntry(updatedEntry, 0, false);
        if (!result.success) {
            schedules.set(previousState);
            await invalidateAll();
        }
    } else if (entry.isTemporary && changes.team_id) {
        // Convert temporary entry to permanent
        const currentDropdown = get(dropdownState);
        if (currentDropdown.selectedSchedule) {
            const result = await syncScheduleEntry(updatedEntry, currentDropdown.selectedSchedule.schedule_id);
            if (result.success && result.schedule_entry_id) {
                updateEntryId(entryId, result.schedule_entry_id);
            } else {
                schedules.set(previousState);
                await invalidateAll();
            }
        }
    }
}

export async function addScheduleEntry(newEntry: ScheduleEntry) {
    const currentDropdown = get(dropdownState);
    const selectedSchedule = currentDropdown.selectedSchedule;
    if (!selectedSchedule) return;

    const tempId = Date.now();
    const entryWithFlag = { 
        ...newEntry, 
        schedule_entry_id: tempId,
        isTemporary: true
    };

    // Track the temporary entry
    tempEntries.set(tempId, { tempId });

    // Update local state
    schedules.update(schedulesList => 
        schedulesList.map(schedule => 
            schedule.schedule_id === selectedSchedule.schedule_id
                ? { ...schedule, entries: [...schedule.entries, entryWithFlag] }
                : schedule
        )
    );

    // If entry already has a team, update it immediately to convert to permanent
    if (newEntry.team_id) {
        await updateScheduleEntry(tempId, { team_id: newEntry.team_id });
    }
}

function updateEntryId(tempId: number, permanentId: number) {
    tempEntries.set(tempId, { tempId, permanentId });
    
    schedules.update(schedulesList =>
        schedulesList.map(schedule => ({
            ...schedule,
            entries: schedule.entries.map(entry =>
                entry.schedule_entry_id === tempId
                    ? { ...entry, schedule_entry_id: permanentId, isTemporary: false }
                    : entry
            )
        }))
    );
}

export function createEmptySchedule(name: string, facilityId: number, clubId: number): Schedule {
    const emptySchedule: Schedule = {
        schedule_id: -Date.now(),
        name,
        facility_id: facilityId,
        club_id: clubId,
        entries: [],
        is_active: true
    };
    
    schedules.update(currentSchedules => [...currentSchedules, emptySchedule]);
    selectSchedule(emptySchedule);
    return emptySchedule;
}

export function deleteSchedule(scheduleId: number) {
    schedules.update(currentSchedules => 
        currentSchedules.filter(schedule => schedule.schedule_id !== scheduleId)
    );
    const currentDropdown = get(dropdownState);
    if (currentDropdown.selectedSchedule?.schedule_id === scheduleId) {
        selectSchedule(null);
    }
}
