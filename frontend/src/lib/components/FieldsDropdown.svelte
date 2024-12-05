<script lang="ts">
    import { facilityStatus } from '../../stores/facilityStatus';
    import { dropdownState, toggleDropdown } from '../../stores/dropdownState';
    import type { Field, SubField } from '$lib/types/facilityStatus';
    
    export let fields: Field[];
    let selectedField: Field | null = null;

    // Size order mapping (larger fields first)
    const sizeOrder: Record<string, number> = {
        '11v11': 1,
        '8v8': 2,
        '5v5': 3,
        '3v3': 4
    };

    // Group and sort fields by size
    $: groupedFields = Object.entries(
        fields.reduce((groups: Record<string, Field[]>, field) => {
            const size = field.size;
            if (!groups[size]) {
                groups[size] = [];
            }
            groups[size].push(field);
            return groups;
        }, {})
    ).sort(([sizeA], [sizeB]) => (sizeOrder[sizeA] || 99) - (sizeOrder[sizeB] || 99));

    // Set default selected field if none is selected
    $: if (!selectedField && fields.length > 0) {
        const firstGroup = groupedFields[0];
        if (firstGroup && firstGroup[1].length > 0) {
            selectedField = firstGroup[1][0];
        }
    }

    function handleSelectField(field: Field) {
        selectedField = selectedField?.field_id === field.field_id ? null : field;
        $dropdownState.fieldsOpen = false;
    }

    function handleClickOutside(event: MouseEvent) {
        const target = event.target as HTMLElement;
        if (!target.closest('.fields-dropdown')) {
            $dropdownState.fieldsOpen = false;
        }
    }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="fixed left-[max(1rem,calc((100%-80rem)/2+1rem))] top-32 z-40 w-72 fields-dropdown">
    <div class="bg-white rounded-2xl shadow-xl border border-mint-100 overflow-hidden">
        <div class="flex items-center">
            <div class="flex-1 flex items-center">
                <h2 class="text-sm font-medium text-sage-700 pl-4">Fields</h2>
                <button
                    class="p-2 ml-2"
                    on:click={() => toggleDropdown('fieldsOpen')}
                    aria-label="Toggle fields dropdown"
                >
                    <svg
                        class="w-5 h-5 transition-transform duration-200 text-sage-600"
                        class:rotate-180={$dropdownState.fieldsOpen}
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
            <button 
                class="btn-primary text-sm py-1.5 m-2"
                on:click={() => window.location.href = '/fields/new'}
            >
                Create Field
            </button>
        </div>
        {#if $dropdownState.fieldsOpen}
            <div class="dropdown-content border-t border-mint-100">
                {#if fields && fields.length > 0}
                    <div class="p-1 space-y-3">
                        {#each groupedFields as [size, sizeFields]}
                            <div class="space-y-1">
                                <h3 class="text-xs font-medium text-sage-600 px-2">{size}</h3>
                                {#each sizeFields as field}
                                    <button
                                        class="dropdown-item {selectedField?.field_id === field.field_id ? 'dropdown-item-selected' : ''}"
                                        on:click={() => handleSelectField(field)}
                                    >
                                        <span class="font-medium">{field.name}</span>
                                    </button>
                                {/each}
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="p-4 text-sage-500 text-center text-sm">
                        No fields available
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>

{#if selectedField}
    <div class="fixed left-[calc(20rem+max(1rem,calc((100%-80rem)/2+1rem)))] top-32 right-[max(1rem,calc((100%-80rem)/2+1rem))] z-30">
        <div class="bg-white rounded-2xl shadow-xl border border-mint-100 p-6">
            <h3 class="text-xl font-semibold mb-4">{selectedField.name}</h3>
            <div class="grid gap-4">
                <div class="space-y-2">
                    <p class="text-sm text-gray-600">Size: {selectedField.size}</p>
                    <p class="text-sm text-gray-600">Type: {selectedField.field_type}</p>
                    
                    <!-- Availability -->
                    {#if selectedField.availability && Object.entries(selectedField.availability).length > 0}
                        <div class="mt-3">
                            <h4 class="text-sm font-medium mb-1">Availability:</h4>
                            <div class="space-y-1">
                                {#each Object.entries(selectedField.availability) as [day, time]}
                                    <p class="text-sm text-gray-600">
                                        {day}: {time.start_time} - {time.end_time}
                                    </p>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Half Subfields -->
                    {#if selectedField.half_subfields.length > 0}
                        <div class="mt-3">
                            <h4 class="text-sm font-medium mb-1">Half Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each selectedField.half_subfields as subfield}
                                    <span class="inline-block bg-mint-50 text-mint-700 rounded-lg px-2 py-1 text-sm">
                                        {subfield.name}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Quarter Subfields -->
                    {#if selectedField.quarter_subfields.length > 0}
                        <div class="mt-3">
                            <h4 class="text-sm font-medium mb-1">Quarter Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each selectedField.quarter_subfields as subfield}
                                    <span class="inline-block bg-mint-50 text-mint-700 rounded-lg px-2 py-1 text-sm">
                                        {subfield.name}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
{/if}