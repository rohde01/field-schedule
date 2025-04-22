import { writable, get } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { selectSchedule, dropdownState } from './ScheduleDropdownState';

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

export function addScheduleEntry(entry: ScheduleEntry) {
    schedules.update(schedulesList => {
        const updatedSchedules = schedulesList.map(schedule => {
            if (schedule.schedule_id === entry.schedule_id) {
                const updatedSchedule = { ...schedule, schedule_entries: [...schedule.schedule_entries, entry] };
                console.log(`Added entry to schedule ${schedule.schedule_id}:`, entry);
                return updatedSchedule;
            }
            return schedule;
        });
        return updatedSchedules;
    });
}

export function updateScheduleEntry(updatedEntry: Partial<ScheduleEntry> & Pick<ScheduleEntry, 'uid' | 'schedule_id'>) {
    schedules.update(schedulesList => {
        return schedulesList.map(schedule => {
            if (schedule.schedule_id !== updatedEntry.schedule_id) return schedule;

            const entries = schedule.schedule_entries;
            const targetUid = updatedEntry.uid;
            const targetRecurrenceId = updatedEntry.recurrence_id ? updatedEntry.recurrence_id : null;
            let updatedEntries = [...entries];

            if (targetRecurrenceId) {
                // --- Case 1: Updating an existing exception
                const existingExceptionIndex = entries.findIndex(e =>
                    e.uid === targetUid &&
                    e.recurrence_id instanceof Date &&
                    targetRecurrenceId instanceof Date &&
                    e.recurrence_id.getTime() === targetRecurrenceId.getTime()
                );

                if (existingExceptionIndex !== -1) {
                    const originalException = entries[existingExceptionIndex];
                    const mergedException = { ...originalException, ...updatedEntry };
                    updatedEntries[existingExceptionIndex] = mergedException;
                    console.log(`Updated existing exception entry ${targetUid} for instance ${targetRecurrenceId}:`, mergedException);
                } else {
                    // --- Case 2: No existing exception found - Create a new exception
                    const masterEntry = entries.find(e => e.uid === targetUid && !e.recurrence_id && e.recurrence_rule);
                    if (masterEntry) {
                        const newExceptionData = {
                            ...masterEntry,
                            ...updatedEntry,
                            schedule_entry_id: null,
                            recurrence_id: targetRecurrenceId,
                            recurrence_rule: null,
                            exdate: null,
                        };
                        updatedEntries.push(newExceptionData as ScheduleEntry);
                        console.log(`Created new exception entry for ${targetUid} instance ${targetRecurrenceId}:`, newExceptionData);
                    } else {
                        console.warn(`Cannot update instance ${targetRecurrenceId} for entry ${targetUid}: Master recurring entry not found or update data incomplete.`);
                        return schedule;
                    }
                }
            } else {
                // --- Case 3: Updating standalone entry
                const masterIndex = entries.findIndex(e => e.uid === targetUid && !e.recurrence_id);
                if (masterIndex !== -1) {
  
                    const originalMaster = entries[masterIndex];
                    const mergedMaster = { ...originalMaster, ...updatedEntry };

                    updatedEntries[masterIndex] = mergedMaster;
                    console.log(`Updated standalone entry ${targetUid}:`, mergedMaster);
                } else {
                    console.warn(`Cannot update standalone entry ${targetUid}: Entry not found.`);
                    return schedule;
                }
            }
            return { ...schedule, schedule_entries: updatedEntries };
        });
    });
}

export function deleteScheduleEntry(uid: string, schedule_id: number, recurrence_id: Date | null) {
    schedules.update(schedulesList => {
        return schedulesList.map(schedule => {
            if (schedule.schedule_id !== schedule_id) return schedule;

            let updatedEntries = [...schedule.schedule_entries];
            const masterIndex = updatedEntries.findIndex(e => e.uid === uid && !e.recurrence_id);
            const masterEntry = masterIndex !== -1 ? updatedEntries[masterIndex] : undefined;

            if (recurrence_id === null && masterEntry && !masterEntry.recurrence_rule) {
                // Remove standalone master entry
                updatedEntries = updatedEntries.filter(e => !(e.uid === uid && !e.recurrence_id));
                console.log(`Deleted standalone entry ${uid}`);
            } else if (recurrence_id) {
                // Remove existing exception if found
                const exceptionIndex = updatedEntries.findIndex(e => e.uid === uid && e.recurrence_id instanceof Date && e.recurrence_id.getTime() === recurrence_id.getTime());
                if (exceptionIndex !== -1) {
                    updatedEntries.splice(exceptionIndex, 1);
                    console.log(`Removed exception for ${uid} at ${recurrence_id}`);
                }
                // Add recurrence_id to master's exdate
                if (masterEntry) {
                    const existingExdates = masterEntry.exdate ? [...masterEntry.exdate] : [];
                    existingExdates.push(recurrence_id);
                    const updatedMaster = { ...masterEntry, exdate: existingExdates };
                    updatedEntries[masterIndex] = updatedMaster;
                    console.log(`Added exdate ${recurrence_id} to master ${uid}`);
                }
            }

            return { ...schedule, schedule_entries: updatedEntries };
        });
    });
}