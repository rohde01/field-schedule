<script lang="ts">
    import EditableField from './EditableField.svelte';
    import type { ActiveSchedule } from '$lib/schemas/schedule';
    import { activeSchedules } from '../../stores/activeSchedules';
    import { schedules } from '../../stores/schedules';
    import { writable } from 'svelte/store';

    export let position: { x: number; y: number };
    export let selectedDate: Date;
    export let onClose: () => void;
    export let editingEvent: ActiveSchedule | null = null;

    $: scheduleOptions = $schedules.map(schedule => ({
        value: schedule.schedule_id,
        label: schedule.name
    }));

    const infoCardForm = writable<Record<string, any>>(
        editingEvent ? {
            schedule_id: editingEvent.schedule_id.toString(),
            start_date: new Date(editingEvent.start_date).toISOString().slice(0, 16),
            end_date: new Date(editingEvent.end_date).toISOString().slice(0, 16),
            is_active: editingEvent.is_active
        } : {
            schedule_id: '',
            start_date: selectedDate.toISOString().slice(0, 16),
            end_date: new Date(selectedDate.getTime() + 7 * 24 * 60 * 60 * 1000)
                .toISOString().slice(0, 16),
            is_active: true
        }
    );

    let showConfirmModal = false;

    $: {
        // Update store whenever form values change
        const formData = $infoCardForm;
        if (formData.schedule_id && formData.start_date && formData.end_date) {
            if (editingEvent) {
                const updatedSchedule: ActiveSchedule = {
                    ...editingEvent,
                    schedule_id: parseInt(formData.schedule_id),
                    start_date: new Date(formData.start_date).toISOString(),
                    end_date: new Date(formData.end_date).toISOString(),
                    is_active: formData.is_active
                };
                activeSchedules.update(updatedSchedule);
            } else {
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
        }
    }

    function handleDelete() {
        showConfirmModal = true;
    }
    
    function confirmDelete() {
        if (editingEvent) {
            activeSchedules.remove(editingEvent.active_schedule_id);
            onClose();
        }
        showConfirmModal = false;
    }
    
    function cancelDelete() {
        showConfirmModal = false;
    }
</script>

<div 
    role="button"
    tabindex="0"
    on:keydown={(e) => { if(e.key === "Enter" || e.key === " ") e.stopPropagation(); }}
    on:click|stopPropagation
    class="event-info-card relative"
    style="position: absolute; top: {position.y}px; left: {position.x}px;"
>
    <div class="event-info-card-header">
        <EditableField
            form={infoCardForm}
            errors={{}}
            name="schedule_id"
            label="Schedule"
            type="select"
            options={scheduleOptions}
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

    {#if editingEvent}
        <div class="flex items-center mt-2">
            <button 
                type="button" 
                class="btn-trash" 
                aria-label="Delete entry" 
                on:click|stopPropagation={handleDelete}
                tabindex="-1"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
            </button>
        </div>
    {/if}
</div>

{#if showConfirmModal}
    <div 
        class="modal-overlay" 
        on:click|self={cancelDelete}
        on:keydown={(e) => {
            if (e.key === 'Escape') cancelDelete();
        }}
        role="dialog"
        aria-labelledby="modal-title"
        aria-describedby="modal-description"
    >
        <div class="modal-container">
            <h2 id="modal-title" class="modal-title">Confirm Deletion</h2>
            <p id="modal-description" class="modal-description">Are you sure you want to remove this schedule from the club calender?</p>
            
            <div class="modal-actions">
                <button class="btn-secondary" on:click={cancelDelete}>Cancel</button>
                <button class="btn-danger" on:click={confirmDelete}>Delete</button>
            </div>
        </div>
    </div>
{/if}
