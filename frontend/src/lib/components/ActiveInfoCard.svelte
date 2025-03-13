<script lang="ts">
    import EditableField from './EditableField.svelte';
    import type { ActiveSchedule } from '$lib/schemas/schedule';
    import { activeSchedules } from '../../stores/activeSchedules';
    import { writable } from 'svelte/store';

    export let position: { x: number; y: number };
    export let selectedDate: Date;
    export let onClose: () => void;

    // Create a writable store for the form
    const infoCardForm = writable<Record<string, any>>({
        schedule_id: '',
        start_date: selectedDate.toISOString().slice(0, 16),
        end_date: new Date(selectedDate.getTime() + 7 * 24 * 60 * 60 * 1000)
            .toISOString().slice(0, 16),
        is_active: true
    });

    function handleSubmit() {
        const formData = $infoCardForm;
        const newSchedule: ActiveSchedule = {
            active_schedule_id: Date.now(),
            schedule_id: parseInt(formData.schedule_id),
            start_date: new Date(formData.start_date).toISOString(),
            end_date: new Date(formData.end_date).toISOString(),
            is_active: formData.is_active
        };

        activeSchedules.add(newSchedule);
        onClose();
    }
</script>

<div 
    role="button"
    tabindex="0"
    on:keydown={(e) => { if(e.key === "Enter" || e.key === " ") e.stopPropagation(); }}
    on:click|stopPropagation
    class="event-info-card"
    style="position: absolute; top: {position.y}px; left: {position.x}px;"
>
    <div class="event-info-card-header">
        <EditableField
            form={infoCardForm}
            errors={{}}
            name="schedule_id"
            label=""
            type="number"
            view_mode_style="title"
            required={true}
        />
    </div>

    <div class="event-info-card-content">
        <div class="event-info-card-grid">
            <EditableField
                form={infoCardForm}
                errors={{}}
                name="start_date"
                label="Start Date"
                type="text"
                view_mode_style="normal"
                required={true}
            />
            <EditableField
                form={infoCardForm}
                errors={{}}
                name="end_date"
                label="End Date"
                type="text"
                view_mode_style="normal"
                required={true}
            />
        </div>

        <div class="event-info-card-grid">
            <EditableField
                form={infoCardForm}
                errors={{}}
                name="is_active"
                label="Status"
                type="checkbox"
                view_mode_style="normal"
                required={true}
            />
        </div>
    </div>

    <div class="flex justify-end space-x-2 mt-4">
        <button type="button" class="btn-secondary" on:click={onClose}>
            Cancel
        </button>
        <button type="button" class="btn-primary" on:click={handleSubmit}>
            Create
        </button>
    </div>
</div>
