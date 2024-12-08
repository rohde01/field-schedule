<script lang="ts">
    import type { FieldSize, FieldAvailability as CreateFieldAvailability } from '$lib/types/field';
    import { enhance } from '$app/forms';
    import type { SubmitFunction } from '@sveltejs/kit';

    import FieldSubfieldsEditor from './SubfieldsEditor.svelte';
    import FieldAvailabilityEditor from './AvailabilityEditor.svelte';

    export let facilityId: number | undefined = undefined;

    const fieldSizes: FieldSize[] = ['11v11', '8v8', '5v5', '3v3'];

    // Main field data
    let mainFieldName = '';
    let selectedSize: FieldSize | '' = '';
    let showNameInput = true;
    let showSizeInput = true;

    // Availability
    let availabilities: CreateFieldAvailability[] = [];

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

    function prepareFormData(subfieldsData: any) {
        return {
            facility_id: facilityId ?? 0,
            name: mainFieldName,
            size: selectedSize,
            field_type: 'full' as const,
            half_fields: subfieldsData
        };
    }

    const handleSubmit: SubmitFunction = ({ formData }) => {
        // We get subfield and availability data when we submit
        // We'll handle that by listening to a custom event dispatched by subfield and availability editors
        // or simply referencing their states directly.

        // We'll assume we have a function or a reactive block that gives us `subfieldsData` from FieldSubfieldsEditor
        // For simplicity, we will store them in this component using a callback.

        formData.set('fieldData', JSON.stringify(prepareFormData(halfFieldsData)));
        formData.set('availabilityData', JSON.stringify({ availabilities }));
    };

    // We'll store halfFieldsData coming from FieldSubfieldsEditor via events
    let halfFieldsData: any = [];

    function handleSubfieldsChange(event: CustomEvent) {
        halfFieldsData = event.detail;
    }

    function handleAvailabilitiesChange(event: CustomEvent) {
        availabilities = event.detail;
    }

    function addAvailability() {
        availabilities = [...availabilities, {
            day_of_week: 'Mon',
            start_time: '16:00',
            end_time: '22:00'
        }];
    }
</script>

<form
    method="POST"
    action="?/createField"
    use:enhance={handleSubmit}
>
    <input type="hidden" name="facility_id" value={facilityId} />

    <div class="field-card-grid">
        <!-- Left Column: Field Configuration -->
        <div class="field-section">

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
                            <!-- Edit icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                                <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
                            </svg>
                        </button>
                    </div>
                </div>
            {/if}

            <!-- Size Section -->
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
                            <!-- Edit icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                                <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
                            </svg>
                        </button>
                    </div>
                    <p class="field-info-text">Type: full</p>
                </div>
            {/if}

            <!-- Subfields Section -->
            <FieldSubfieldsEditor on:subfieldsChange={handleSubfieldsChange} />

        </div>

        <!-- Right Column: Field Availability -->
        <FieldAvailabilityEditor
            {availabilities}
            on:availabilitiesChange={handleAvailabilitiesChange}
        />

    </div>

    <div class="field-actions">
        <button type="submit" class="btn-primary">Create Field</button>
    </div>
</form>
