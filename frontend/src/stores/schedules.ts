import { writable, get } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { selectSchedule, dropdownState } from './ScheduleDropdownState';
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

    const parentSchedule = currentSchedules.find(s => 
        s.entries.some(e => e.schedule_entry_id === entryId)
    );
    if (isLocal || entry.isTemporary || (parentSchedule && parentSchedule.schedule_id < 0)) {
        if (entry.isTemporary && changes.team_id && parentSchedule && parentSchedule.schedule_id > 0) {
            const currentDropdown = get(dropdownState);
            if (!currentDropdown.selectedSchedule) return;

            try {
                const formData = new FormData();
                formData.append('scheduleId', currentDropdown.selectedSchedule.schedule_id.toString());
                const finalEntry = { ...entry, ...changes };
                Object.entries(finalEntry).forEach(([key, value]) => {
                    if (value !== null && key !== 'isTemporary' && key !== 'schedule_entry_id') {
                        formData.append(`entry.${key}`, value.toString());
                    }
                });

                const response = await fetch('?/createEntry', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    await invalidateAll();
                } else {
                    await invalidateAll();
                }
            } catch (error) {
                await invalidateAll();
            }
        }
        return;
    }

    try {
        const formData = new FormData();
        formData.append('entryId', entryId.toString());
        Object.entries(changes).forEach(([key, value]) => {
            if (value !== null) {
                formData.append(key, value.toString());
            }
        });

        const response = await fetch('?/updateEntry', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            schedules.set(previousState);
            await invalidateAll();
        }
    } catch (error) {
        schedules.set(previousState);
        await invalidateAll();
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

    schedules.update(schedulesList => 
        schedulesList.map(schedule => 
            schedule.schedule_id === selectedSchedule.schedule_id
                ? { ...schedule, entries: [...schedule.entries, entryWithFlag] }
                : schedule
        )
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

export async function deleteScheduleEntry(entryId: number): Promise<boolean> {
    try {
        const formData = new FormData();
        formData.append('entryId', entryId.toString());

        const response = await fetch(`?/deleteEntry`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            console.error('Failed to delete entry:', await response.json());
            return false;
        }

        schedules.update(schedulesList => 
            schedulesList.map(schedule => ({
                ...schedule,
                entries: schedule.entries.filter(entry => entry.schedule_entry_id !== entryId)
            }))
        );

        return true;
    } catch (error) {
        console.error('Error deleting schedule entry:', error);
        return false;
    }
}
