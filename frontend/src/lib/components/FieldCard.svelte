<script lang="ts">
    import type { Field as CreateField, FieldSize, SubField, FieldAvailability as CreateFieldAvailability } from '$lib/types/field';
    import type { Field as ViewField, FieldAvailability as ViewFieldAvailability } from '$lib/types/facilityStatus';
    import { enhance } from '$app/forms';
    import type { SubmitFunction } from '@sveltejs/kit';
    import { fade } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    import { facilityStatus } from '../../stores/facilityStatus';

    const dispatch = createEventDispatcher<{
        fieldDeleted: { fieldId: number | undefined };
    }>();

    export let field: ViewField | null = null;
    export let facilityId: number | undefined = undefined;
    export let isCreateMode = false;

    const fieldSizes: FieldSize[] = ['11v11', '8v8', '5v5', '3v3'];
    let halfFields: { 
        name: string, 
        quarterFields: { name: string, isCollapsed?: boolean }[], 
        isCollapsed?: boolean 
    }[] = [];
    let showHalfFieldInputs = true;

    let mainFieldName = '';
    let selectedSize: FieldSize | '' = '';
    let showNameInput = true;
    let showSizeInput = true;

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const;
    let availabilities: CreateFieldAvailability[] = [];

    function addHalfField() {
        if (halfFields.length === 0) {
            halfFields = [
                { name: '', quarterFields: [], isCollapsed: false },
                { name: '', quarterFields: [], isCollapsed: false }
            ];
        }
    }

    function addQuarterFields(halfFieldIndex: number) {
        halfFields[halfFieldIndex].quarterFields = [
            { name: '', isCollapsed: false },
            { name: '', isCollapsed: false }
        ];
        halfFields = [...halfFields];
    }

    function handleHalfFieldBlur(halfIndex: number) {
        if (halfFields[halfIndex].name.trim()) {
            halfFields[halfIndex].isCollapsed = true;
            halfFields = [...halfFields];
        }
    }

    function editHalfField(halfIndex: number) {
        halfFields[halfIndex].isCollapsed = false;
        halfFields = [...halfFields];
    }

    function areAllHalfFieldsComplete() {
        return halfFields.length === 2 && halfFields.every(field => field.name.trim() && field.isCollapsed);
    }

    function handleQuarterFieldBlur(halfIndex: number, quarterIndex: number) {
        const quarterField = halfFields[halfIndex].quarterFields[quarterIndex];
        if (quarterField.name.trim()) {
            quarterField.isCollapsed = true;
            halfFields = [...halfFields];
        }
    }

    function handleMainFieldBlur() {
        if (mainFieldName.trim()) {
            showNameInput = false;
        }
    }

    function handleSizeChange() {
        if (selectedSize) {
            showSizeInput = false;
        }
    }

    function editMainField() {
        showNameInput = true;
    }

    function editSize() {
        showSizeInput = true;
    }

    function prepareFormData() {
        const halfFieldsData = halfFields
            .filter(h => h.name.trim())
            .map(half => ({
                name: half.name,
                field_type: 'half' as const,
                quarter_fields: half.quarterFields
                    .filter(q => q.name.trim())
                    .map(q => ({
                        name: q.name,
                        field_type: 'quarter' as const
                    }))
            }));

        return {
            facility_id: facilityId ?? 0,
            name: mainFieldName,
            size: selectedSize,
            field_type: 'full' as const,
            half_fields: halfFieldsData
        };
    }

    function addAvailability() {
        availabilities = [...availabilities, {
            day_of_week: 'Mon',
            start_time: '16:00',
            end_time: '22:00'
        }];
    }

    function removeAvailability(index: number) {
        availabilities = availabilities.filter((_, i) => i !== index);
    }

    const handleSubmit: SubmitFunction = ({ formData }) => {
        const fieldData = prepareFormData();
        const availabilityData = {
            availabilities: availabilities
                .filter(a => a.day_of_week && a.start_time && a.end_time)
        };

        formData.set('fieldData', JSON.stringify(fieldData));
        formData.set('availabilityData', JSON.stringify(availabilityData));
    };

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

<div class="field-card" role="presentation" on:mousedown|stopPropagation>
    {#if isCreateMode}
        <form
            method="POST"
            action="?/createField"
            use:enhance={handleSubmit}
        >
            <input type="hidden" name="facility_id" value={facilityId} />
            
            <div class="field-card-grid">
                <!-- Left Column: Field Configuration -->
                <div class="field-section">
                    <!-- Main Field Section -->
                    <div class="field-subsection">
                        <!-- Name Section -->
                        {#if showNameInput}
                            <div class="space-y-1">
                                <label for="fieldName" class="field-subtitle">Field Name</label>
                                <div class="flex gap-2">
                                    <input
                                        type="text"
                                        id="fieldName"
                                        name="name"
                                        class="form-input-sm"
                                        bind:value={mainFieldName}
                                        on:blur={handleMainFieldBlur}
                                    />
                                </div>
                            </div>
                        {:else}
                            <div class="mb-6">
                                <div class="flex items-center gap-2">
                                    <h3 class="field-card-title !mb-0">{mainFieldName}</h3>
                                    <button 
                                        type="button"
                                        class="text-mint-600 hover:text-mint-700"
                                        on:click={editMainField}
                                        aria-label="Edit field name"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                                            <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        {/if}

                        <!-- Size and Type Section -->
                        {#if showSizeInput}
                            <div class="space-y-1">
                                <label for="fieldSize" class="field-subtitle">Field Size</label>
                                <select 
                                    id="fieldSize"
                                    name="size"
                                    class="form-input-sm"
                                    bind:value={selectedSize}
                                    on:change={handleSizeChange}
                                >
                                    <option value="">Select a size</option>
                                    {#each fieldSizes as size}
                                        <option value={size}>{size}</option>
                                    {/each}
                                </select>
                            </div>
                        {:else if selectedSize}
                            <div class="space-y-2">
                                <div class="flex items-center gap-2">
                                    <p class="field-info-text">Size: {selectedSize}</p>
                                    <button 
                                        type="button"
                                        class="text-mint-600 hover:text-mint-700"
                                        on:click={editSize}
                                        aria-label="Edit field size"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                                            <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
                                        </svg>
                                    </button>
                                </div>
                                <p class="field-info-text">Type: full</p>
                            </div>
                        {/if}
                    </div>

                    <!-- Half Fields Section -->
                    <div class="field-subsection">
                        <div class="field-header">
                            <h3 class="field-subtitle">Half Fields</h3>
                            {#if halfFields.length === 0}
                                <button 
                                    type="button" 
                                    on:click={addHalfField}
                                    class="btn-secondary text-sm py-1"
                                >
                                    Add Half Fields
                                </button>
                            {/if}
                        </div>

                        <!-- Half Fields Input and Display -->
                        <div class="space-y-3">
                            <!-- Completed Half Fields Display -->
                            <div class="flex flex-wrap gap-2">
                                {#each halfFields as halfField, halfIndex}
                                    {#if halfField.isCollapsed}
                                        <button 
                                            type="button"
                                            class="inline-block bg-mint-50 text-mint-700 rounded-lg px-2 py-1 text-sm hover:bg-mint-100 transition-colors"
                                            on:click={() => editHalfField(halfIndex)}
                                        >
                                            {halfField.name}
                                        </button>
                                    {/if}
                                {/each}
                            </div>

                            <!-- Half Field Inputs -->
                            {#each halfFields as halfField, halfIndex}
                                {#if !halfField.isCollapsed}
                                    <input
                                        type="text"
                                        name="half_fields[{halfIndex}].name"
                                        bind:value={halfField.name}
                                        placeholder="Half field name"
                                        class="form-input-sm"
                                        on:blur={() => handleHalfFieldBlur(halfIndex)}
                                    />
                                {/if}
                            {/each}
                        </div>

                        <!-- Quarter Fields Section -->
                        {#if areAllHalfFieldsComplete()}
                            <div class="field-section">
                                <div class="field-subsection">
                                    <div class="field-header">
                                        <h3 class="field-subtitle">Quarter Fields</h3>
                                        {#if !halfFields.some(field => field.quarterFields.length > 0)}
                                            <button 
                                                type="button" 
                                                on:click={() => {
                                                    halfFields.forEach((_, index) => addQuarterFields(index));
                                                    halfFields = [...halfFields];
                                                }}
                                                class="text-xs px-2 py-1 bg-white text-mint-600 rounded-lg hover:bg-mint-50 transition-colors border border-mint-200"
                                            >
                                                Add Quarter Fields
                                            </button>
                                        {/if}
                                    </div>

                                    <!-- All Completed Quarter Fields Display -->
                                    {#if halfFields.some(field => field.quarterFields.some(q => q.isCollapsed))}
                                        <div class="flex flex-wrap gap-2">
                                            {#each halfFields as halfField}
                                                {#each halfField.quarterFields as quarterField}
                                                    {#if quarterField.isCollapsed}
                                                        <button 
                                                            type="button"
                                                            class="field-tag hover:bg-mint-100 transition-colors"
                                                            on:click={() => {
                                                                quarterField.isCollapsed = false;
                                                                halfFields = [...halfFields];
                                                            }}
                                                        >
                                                            {quarterField.name}
                                                        </button>
                                                    {/if}
                                                {/each}
                                            {/each}
                                        </div>
                                    {/if}
                                </div>

                                {#if halfFields.some(field => field.quarterFields.length > 0)}
                                    <div class="space-y-8">
                                        {#each halfFields as halfField, halfIndex}
                                            {#if halfField.quarterFields.some(q => !q.isCollapsed)}
                                                <div class="field-subsection">
                                                    <h4 class="text-sm font-medium text-sage-600">
                                                        Quarter fields for {halfField.name}
                                                    </h4>
                                                    
                                                    <!-- Quarter Field Inputs -->
                                                    <div class="space-y-2 ml-4">
                                                        {#each halfField.quarterFields as quarterField, quarterIndex}
                                                            {#if !quarterField.isCollapsed}
                                                                <input
                                                                    type="text"
                                                                    name="half_fields[{halfIndex}].quarter_fields[{quarterIndex}].name"
                                                                    bind:value={quarterField.name}
                                                                    placeholder="Quarter field name"
                                                                    class="form-input-sm"
                                                                    on:blur={() => handleQuarterFieldBlur(halfIndex, quarterIndex)}
                                                                />
                                                            {/if}
                                                        {/each}
                                                    </div>
                                                </div>
                                            {/if}
                                        {/each}
                                    </div>
                                {/if}
                            </div>
                        {/if}
                    </div>
                </div>

                <!-- Right Column: Field Availability -->
                <div class="field-section">
                    <h3 class="field-subtitle">Field Availability</h3>
                    <div class="space-y-4">
                        {#each availabilities as availability, i}
                            <div class="flex gap-2 items-center">
                                <select
                                    bind:value={availability.day_of_week}
                                    class="form-input-sm bg-white [&>option:hover]:bg-mint-100 [&>option:checked]:bg-mint-500 [&>option:checked]:text-white"
                                >
                                    {#each days as day}
                                        <option value={day}>{day}</option>
                                    {/each}
                                </select>

                                <input
                                    type="time"
                                    bind:value={availability.start_time}
                                    class="form-input-sm [&::-webkit-calendar-picker-indicator]:filter-mint"
                                />

                                <input
                                    type="time"
                                    bind:value={availability.end_time}
                                    class="form-input-sm [&::-webkit-calendar-picker-indicator]:filter-mint"
                                />

                                <button
                                    type="button"
                                    class="text-sage-500 hover:text-sage-700 transition-colors duration-200"
                                    on:click={() => removeAvailability(i)}
                                    aria-label="Remove availability"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                                        <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                                    </svg>
                                </button>
                            </div>
                        {/each}
                        
                        <button
                            type="button"
                            class="text-xs px-2 py-1 bg-white text-mint-600 rounded-lg hover:bg-mint-50 transition-colors border border-mint-200"
                            on:click={addAvailability}
                        >
                            Add Availability
                        </button>
                    </div>
                </div>
            </div>

            <div class="field-actions">
                <button type="submit" class="btn-primary">Create Field</button>
            </div>
        </form>
    {:else if field}
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
                    <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center" transition:fade="{{ duration: 200 }}">
                        <div class="bg-white rounded-lg p-6 max-w-sm mx-4" 
                             role="dialog"
                             aria-labelledby="delete-modal-title"
                             aria-describedby="delete-modal-description">
                            <h3 id="delete-modal-title" class="text-lg font-semibold mb-2">Delete Field</h3>
                            <p id="delete-modal-description" class="text-sage-600 mb-4">
                                Are you sure you want to delete {field.name}? This action cannot be undone.
                            </p>
                            <div class="flex justify-end space-x-3">
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
                                        class="btn bg-red-500 text-white hover:bg-red-600 focus:ring-red-500"
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
    {/if}
</div>
