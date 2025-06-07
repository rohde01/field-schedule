import { writable, get } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { scheduleSchema } from '$lib/schemas/schedule';

// Local draft schedule before server save
export type LocalSchedule = Partial<Schedule> & { schedule_entries: ScheduleEntry[]; schedule_id: number | null };

export const schedules = writable<Array<Schedule | LocalSchedule>>([]);
export const deletedEntryIds = writable<number[]>([]);
export const unsavedChanges = writable<boolean>(false);
export const IsCreating = writable<boolean>(false);
export const selectedSchedule = writable<Schedule | LocalSchedule | null>(null);

export function setSchedules(newSchedules: Schedule[]) {
    const coercedSchedules = newSchedules.map(s => scheduleSchema.parse(s));
    const sortedSchedules = [...coercedSchedules].sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return dateB - dateA;
    });
    schedules.set(sortedSchedules);

    if (sortedSchedules.length > 0 && get(selectedSchedule) === null) {
        selectedSchedule.set(sortedSchedules[0]);
    }
    unsavedChanges.set(false);
}

export function addSchedule(schedule: LocalSchedule) {
    schedules.update(list => {
        const updated = [...list, schedule];
        return updated;
    });
}

export function addScheduleEntry(entry: ScheduleEntry) {
    schedules.update(schedulesList => {
        const updatedSchedules = schedulesList.map(schedule => {
            if (schedule.schedule_id === entry.schedule_id) {
                const updatedSchedule = { ...schedule, schedule_entries: [...schedule.schedule_entries, entry] };
                return updatedSchedule;
            }
            return schedule;
        });
        return updatedSchedules;
    });
    if (!get(IsCreating)) unsavedChanges.set(true);

    const updatedSchedule = get(schedules).find(s => s.schedule_id === entry.schedule_id) ?? null;
    selectedSchedule.set(updatedSchedule);
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
                } else {
                    // --- Case 2: No existing exception found - Create a new exception
                    const masterEntry = entries.find(e => e.uid === targetUid && !e.recurrence_id && e.recurrence_rule);
                    if (masterEntry) {
                        const newExceptionData = {
                            ...masterEntry,
                            ...updatedEntry,
                            recurrence_id: targetRecurrenceId,
                            recurrence_rule: null,
                            exdate: null,
                            schedule_entry_id: null
                        };
                        updatedEntries.push(newExceptionData as ScheduleEntry);
                    } else {
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
                } else {
                    return schedule;
                }
            }
            return { ...schedule, schedule_entries: updatedEntries };
        });
    });
    // Update selectedSchedule to reflect the changed entry date
    const updatedSchedule = get(schedules).find(s => s.schedule_id === updatedEntry.schedule_id) ?? null;
    selectedSchedule.set(updatedSchedule);
    if (!get(IsCreating)) unsavedChanges.set(true);
}

export function deleteScheduleEntry(uid: string, schedule_id: number, recurrence_id: Date | null) {
    schedules.update(schedulesList => {
        return schedulesList.map(schedule => {
            if (schedule.schedule_id !== schedule_id) return schedule;

            let updatedEntries = [...schedule.schedule_entries];
            const masterIndex = updatedEntries.findIndex(e => e.uid === uid && !e.recurrence_id);
            const masterEntry = masterIndex !== -1 ? updatedEntries[masterIndex] : undefined;

            if (recurrence_id === null && masterEntry && !masterEntry.recurrence_rule) {
                const id = masterEntry.schedule_entry_id;
                if (id != null) deletedEntryIds.update(ids => [...ids, id]);
                // Remove standalone master entry
                updatedEntries = updatedEntries.filter(e => !(e.uid === uid && !e.recurrence_id));
            } else if (recurrence_id) {
                // Remove existing exception if found
                const exceptionIndex = updatedEntries.findIndex(e => e.uid === uid && e.recurrence_id instanceof Date && e.recurrence_id.getTime() === recurrence_id.getTime());
                if (exceptionIndex !== -1) {
                    const removed = updatedEntries[exceptionIndex];
                    const id2 = removed.schedule_entry_id;
                    if (id2 != null) deletedEntryIds.update(ids => [...ids, id2]);
                    updatedEntries.splice(exceptionIndex, 1);
                }
                // Add recurrence_id to master's exdate
                if (masterEntry) {
                    const existingExdates = masterEntry.exdate ? [...masterEntry.exdate] : [];
                    existingExdates.push(recurrence_id);
                    const updatedMaster = { ...masterEntry, exdate: existingExdates };
                    updatedEntries[masterIndex] = updatedMaster;
                }
            }

            return { ...schedule, schedule_entries: updatedEntries };
        });
    });
    if (!get(IsCreating)) unsavedChanges.set(true);

    const refreshedSchedule = get(schedules).find(s => s.schedule_id === schedule_id) ?? null;
    selectedSchedule.set(refreshedSchedule);
}

export function removeSchedule(schedule: Schedule | LocalSchedule) {
    schedules.update(list => list.filter(s => s !== schedule));
    const remaining = get(schedules);
    selectedSchedule.set(remaining.length > 0 ? remaining[0] : null);
}

export function setScheduleEntries(schedule_id: number, entries: ScheduleEntry[]) {
    schedules.update(list =>
        list.map(schedule =>
            schedule.schedule_id === schedule_id
                ? { ...schedule, schedule_entries: entries }
                : schedule
        )
    );
    const updated = get(schedules).find(s => s.schedule_id === schedule_id) ?? null;
    selectedSchedule.set(updated);
}