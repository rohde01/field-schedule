<script lang="ts">
    import type { Field as CreateField, FieldSize, SubField } from '$lib/types/field';
    import type { Field as ViewField, FieldAvailability } from '$lib/types/facilityStatus';
    import { enhance } from '$app/forms';
    import type { SubmitFunction } from '@sveltejs/kit';
    import { slide } from 'svelte/transition';
    import { dropdownState } from '../../stores/dropdownState';

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

    function addHalfField() {
        if (halfFields.length === 0) {
            halfFields = [
                { name: '', quarterFields: [], isCollapsed: false },
                { name: '', quarterFields: [], isCollapsed: false }
            ];
        }
    }

    function addQuarterFields(halfFieldIndex: number) {
        // Add 2 quarter fields for the half field
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

    const handleSubmit: SubmitFunction = ({ formData }) => {
        const fieldData = prepareFormData();
        formData.set('fieldData', JSON.stringify(fieldData));
    };
</script>

<div class="bg-white rounded-2xl shadow-xl border border-mint-100 p-6" role="presentation" on:mousedown|stopPropagation>
    {#if isCreateMode}
        <form
            method="POST"
            action="?/createField"
            use:enhance={handleSubmit}
        >
            <input type="hidden" name="facility_id" value={facilityId} />
            
            <div class="grid grid-cols-2 gap-6">
                <!-- Left Column: Field Configuration -->
                <div class="space-y-6">
                    <!-- Main Field Section -->
                    <div class="space-y-4">
                        <!-- Name Section -->
                        {#if showNameInput}
                            <div class="space-y-1">
                                <label for="name" class="form-label text-sm">Field Name</label>
                                <input 
                                    type="text" 
                                    id="name" 
                                    name="name" 
                                    bind:value={mainFieldName}
                                    required
                                    class="form-input text-sm py-1 px-2" 
                                    placeholder="Enter field name..."
                                    on:blur={handleMainFieldBlur}
                                />
                            </div>
                        {:else}
                            <div class="flex items-center gap-2">
                                <h3 class="text-base font-medium">
                                    {mainFieldName}
                                </h3>
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
                        {/if}

                        <!-- Size Section -->
                        {#if showSizeInput}
                            <div class="space-y-1">
                                <label for="size" class="form-label text-sm">Field Size</label>
                                <select 
                                    id="size" 
                                    name="size" 
                                    bind:value={selectedSize}
                                    required
                                    class="form-input text-sm py-1 px-2"
                                    on:change={handleSizeChange}
                                >
                                    <option value="" disabled>Choose a size</option>
                                    {#each fieldSizes as size}
                                        <option value={size}>{size}</option>
                                    {/each}
                                </select>
                            </div>
                        {:else}
                            <div class="flex items-center gap-2">
                                <div>
                                    <p class="text-sm text-gray-600">Size: {selectedSize}</p>
                                    <p class="text-sm text-gray-600">Type: full</p>
                                </div>
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
                        {/if}
                    </div>

                    <!-- Half Fields Section -->
                    <div class="space-y-4">
                        <div class="flex items-center justify-between">
                            <h3 class="text-sm font-medium text-sage-700">Half Fields</h3>
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
                                        class="form-input text-sm"
                                        on:blur={() => handleHalfFieldBlur(halfIndex)}
                                    />
                                {/if}
                            {/each}
                        </div>

                        <!-- Quarter Fields Section -->
                        {#if areAllHalfFieldsComplete()}
                            <div class="space-y-6">
                                <div class="space-y-4">
                                    <div class="flex items-center justify-between">
                                        <h3 class="text-sm font-medium text-sage-700">Quarter Fields</h3>
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
                                        <div class="flex flex-wrap gap-2 ml-4">
                                            {#each halfFields as halfField, halfIndex}
                                                {#each halfField.quarterFields as quarterField, quarterIndex}
                                                    {#if quarterField.isCollapsed}
                                                        <button 
                                                            type="button"
                                                            class="inline-block bg-mint-50 text-mint-700 rounded-lg px-2 py-1 text-sm hover:bg-mint-100 transition-colors"
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
                                                <div class="space-y-4">
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
                                                                    class="form-input text-sm"
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

                <!-- Right Column: Field Availability (Coming Soon) -->
                <div class="space-y-4">
                    <h3 class="text-sm font-medium text-sage-700">Field Availability</h3>
                    <p class="text-sage-600 italic">We will implement field availability for field creation later</p>
                </div>
            </div>

            <div class="flex justify-end mt-6">
                <button type="submit" class="btn-primary">Create Field</button>
            </div>
        </form>
    {:else if field}
        <div class="space-y-6">
            <h3 class="text-xl font-semibold">{field.name}</h3>
            <div class="grid grid-cols-2 gap-6">
                <!-- Left Column: Basic Info and Subfields -->
                <div class="space-y-4">
                    <div class="space-y-2">
                        <p class="text-sm text-gray-600">Size: {field.size}</p>
                        <p class="text-sm text-gray-600">Type: {field.field_type}</p>
                    </div>

                    <!-- Half Subfields -->
                    {#if field.half_subfields?.length > 0}
                        <div>
                            <h4 class="text-sm font-medium mb-1">Half Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each field.half_subfields as subfield}
                                    <span class="inline-block bg-mint-50 text-mint-700 rounded-lg px-2 py-1 text-sm">
                                        {subfield.name}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Quarter Subfields -->
                    {#if field.quarter_subfields?.length > 0}
                        <div>
                            <h4 class="text-sm font-medium mb-1">Quarter Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each field.quarter_subfields as subfield}
                                    <span class="inline-block bg-mint-50 text-mint-700 rounded-lg px-2 py-1 text-sm">
                                        {subfield.name}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>

                <!-- Right Column: Availability -->
                <div>
                    {#if field.availability && Object.entries(field.availability).length > 0}
                        <div>
                            <h4 class="text-sm font-medium mb-1">Availability:</h4>
                            <div class="space-y-1">
                                {#each Object.entries(field.availability) as [day, time]}
                                    <p class="text-sm text-gray-600">
                                        {day}: {(time as FieldAvailability).start_time} - {(time as FieldAvailability).end_time}
                                    </p>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    {/if}
</div>
