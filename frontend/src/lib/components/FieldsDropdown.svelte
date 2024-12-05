<script lang="ts">
    import { facilityStatus } from '../../stores/facilityStatus';
    import { dropdownState, toggleDropdown, selectField, setDefaultField, toggleCreateField } from '../../stores/dropdownState';
    import type { Field, SubField } from '$lib/types/facilityStatus';
    import CreateField from './createField.svelte';
    
    export let fields: Field[];

    const sizeOrder: Record<string, number> = {
        '11v11': 1,
        '8v8': 2,
        '5v5': 3,
        '3v3': 4
    };

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

    $: if (fields.length > 0) {
        setDefaultField(fields);
    }

    function handleClickOutside(event: MouseEvent) {
        const target = event.target as HTMLElement;
        const isClickInsideDropdown = target.closest('.fields-dropdown');
        const isClickInsideCreateCard = target.closest('.create-field-card');
        const isClickInsideInput = target.closest('input, select, button');
        
        if (!isClickInsideDropdown && !isClickInsideCreateCard && !isClickInsideInput) {
            $dropdownState.fieldsOpen = false;
            $dropdownState.showCreateField = false;
        }
    }
</script>

<svelte:window on:mousedown={handleClickOutside} />

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
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a 1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a 1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
            <button 
                class="btn-primary text-sm py-1.5 m-2"
                on:click={toggleCreateField}
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
                                        class="dropdown-item {$dropdownState.selectedField?.field_id === field.field_id ? 'dropdown-item-selected' : ''}"
                                        on:click={() => selectField(field)}
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

{#if $dropdownState.selectedField}
    <div class="fixed left-[calc(20rem+max(1rem,calc((100%-80rem)/2+1rem)))] top-32 right-[max(1rem,calc((100%-80rem)/2+1rem))] z-30">
        <div class="bg-white rounded-2xl shadow-xl border border-mint-100 p-6">
            <h3 class="text-xl font-semibold mb-4">{$dropdownState.selectedField.name}</h3>
            <div class="grid gap-4">
                <div class="space-y-2">
                    <p class="text-sm text-gray-600">Size: {$dropdownState.selectedField.size}</p>
                    <p class="text-sm text-gray-600">Type: {$dropdownState.selectedField.field_type}</p>
                    
                    <!-- Availability -->
                    {#if $dropdownState.selectedField.availability && Object.entries($dropdownState.selectedField.availability).length > 0}
                        <div class="mt-3">
                            <h4 class="text-sm font-medium mb-1">Availability:</h4>
                            <div class="space-y-1">
                                {#each Object.entries($dropdownState.selectedField.availability) as [day, time]}
                                    <p class="text-sm text-gray-600">
                                        {day}: {time.start_time} - {time.end_time}
                                    </p>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Half Subfields -->
                    {#if $dropdownState.selectedField.half_subfields.length > 0}
                        <div class="mt-3">
                            <h4 class="text-sm font-medium mb-1">Half Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each $dropdownState.selectedField.half_subfields as subfield}
                                    <span class="inline-block bg-mint-50 text-mint-700 rounded-lg px-2 py-1 text-sm">
                                        {subfield.name}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Quarter Subfields -->
                    {#if $dropdownState.selectedField.quarter_subfields.length > 0}
                        <div class="mt-3">
                            <h4 class="text-sm font-medium mb-1">Quarter Fields:</h4>
                            <div class="flex flex-wrap gap-2">
                                {#each $dropdownState.selectedField.quarter_subfields as subfield}
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

{#if $dropdownState.showCreateField}
    <div class="fixed left-[calc(20rem+max(1rem,calc((100%-80rem)/2+1rem)))] top-32 right-[max(1rem,calc((100%-80rem)/2+1rem))] z-30 create-field-card">
        <div class="bg-white rounded-2xl shadow-xl border border-mint-100 p-6">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-semibold">Create New Field</h3>
                <button 
                    class="text-sage-500 hover:text-sage-700"
                    on:click={toggleCreateField}
                    aria-label="Close create field form"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <CreateField facilityId={$facilityStatus.selectedFacility?.facility_id ?? 0} />
        </div>
    </div>
{/if}