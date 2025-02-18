import type { ScheduleEntry } from '$lib/schemas/schedule';

interface SyncResult {
    success: boolean;
    schedule_entry_id?: number;
    error?: string;
}

export async function syncScheduleEntry(
    entry: ScheduleEntry,
    scheduleId: number,
    isNew: boolean = true
): Promise<SyncResult> {
    const formData = new FormData();
    
    if (isNew) {
        formData.append('scheduleId', scheduleId.toString());
        Object.entries(entry).forEach(([key, value]) => {
            if (key !== 'isTemporary' && key !== 'schedule_entry_id' && value !== null) {
                formData.append(`entry.${key}`, value.toString());
            }
        });
    } else {
        formData.append('entryId', entry.schedule_entry_id.toString());
        Object.entries(entry).forEach(([key, value]) => {
            if (key !== 'isTemporary' && key !== 'schedule_entry_id' && value !== null) {
                formData.append(key, value.toString());
            }
        });
    }

    try {
        const response = await fetch(`/schedules?/${isNew ? 'createEntry' : 'updateEntry'}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            return { 
                success: false, 
                error: errorData.error || 'Failed to sync schedule entry' 
            };
        }

        const result = await response.json();
        return { 
            success: true, 
            schedule_entry_id: result.schedule_entry_id 
        };
    } catch (error) {
        return { 
            success: false, 
            error: error instanceof Error ? error.message : 'Unknown error' 
        };
    }
}
