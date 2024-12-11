<script lang="ts">
    import type { Field as ViewField, FieldAvailability as ViewFieldAvailability } from '$lib/types/facilityStatus';
    import { fade } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    import { facilityStatus } from '../../stores/facilityStatus';
    import { enhance } from '$app/forms';
    import type { SubmitFunction } from '@sveltejs/kit';

    export let field: ViewField;
    const dispatch = createEventDispatcher<{
        fieldDeleted: { fieldId: number | undefined };
    }>();

    let showDeleteConfirm = false;
    let isDeleting = false;

    const handleDelete: SubmitFunction = () => {
        isDeleting = true;
        return async ({ result }) => {
            if (result.type === 'success') {
                showDeleteConfirm = false;
                if (field?.field_id) {
                    facilityStatus.removeField(field.field_id);
                    dispatch('fieldDeleted', { fieldId: field.field_id });
                }
            }
            isDeleting = false;
        };
    };
</script>

<div class="field-card-content">
    <div class="relative">
        <h3 class="field-card-title">{field.name}</h3>
        
        <!-- Delete Button -->
        <button
            type="button"
            class="btn-trash"
            on:click={() => showDeleteConfirm = true}
            aria-label="Delete field"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
        </button>

        <!-- Delete Confirmation Modal -->
        {#if showDeleteConfirm}
            <div class="modal-overlay" transition:fade={{ duration: 200 }}>
                <div class="modal-container"
                     role="dialog"
                     aria-labelledby="delete-modal-title"
                     aria-describedby="delete-modal-description">
                    <h3 id="delete-modal-title" class="modal-title">Delete Field</h3>
                    <p id="delete-modal-description" class="modal-description">
                        Are you sure you want to delete {field.name}? This action cannot be undone.
                    </p>
                    <div class="modal-actions">
                        <button
                            type="button"
                            class="btn-secondary"
                            on:click={() => showDeleteConfirm = false}
                            disabled={isDeleting}
                        >
                            Cancel
                        </button>
                        <form
                            method="POST"
                            action="?/deleteField"
                            use:enhance={handleDelete}
                            class="inline"
                        >
                            <input type="hidden" name="fieldId" value={field.field_id} />
                            <button
                                type="submit"
                                class="btn-danger"
                                disabled={isDeleting}
                            >
                                {isDeleting ? 'Deleting...' : 'Delete'}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        {/if}

        <div class="field-card-grid">
            <!-- Left Column: Basic Info and Subfields -->
            <div class="field-section">
                <div class="field-subsection">
                    <div class="space-y-2">
                        <p class="field-info-text">Size: {field.size}</p>
                        <p class="field-info-text">Type: {field.field_type}</p>
                    </div>

                    <!-- Half Subfields -->
                    {#if field.half_subfields?.length > 0}
                        <div>
                            <h4 class="field-subtitle">Half Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each field.half_subfields as subfield}
                                    <span class="field-tag">
                                        {subfield.name}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Quarter Subfields -->
                    {#if field.quarter_subfields?.length > 0}
                        <div>
                            <h4 class="field-subtitle">Quarter Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each field.quarter_subfields as subfield}
                                    <span class="field-tag">
                                        {subfield.name}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            </div>

            <!-- Right Column: Availability -->
            <div class="field-section">
                <h3 class="field-subtitle">Availability</h3>
                {#if field.availability && Object.entries(field.availability).length > 0}
                    <div class="space-y-1">
                        {#each Object.entries(field.availability) as [day, time]}
                            <p class="field-info-text">
                                {day}: {(time as ViewFieldAvailability).start_time} - {(time as ViewFieldAvailability).end_time}
                            </p>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>
