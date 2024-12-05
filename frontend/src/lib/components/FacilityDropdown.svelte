<script lang="ts">
    import { facilityStatus } from '../../stores/facilityStatus';
    import { onMount } from 'svelte';
    import { enhance } from '$app/forms';
    
    export let facilities: Array<{
        facility_id: number;
        name: string;
        is_primary: boolean;
    }>;

    let isOpen = false;
    let isCreating = false;
    let dropdownContainer: HTMLDivElement;
    let nameInput: HTMLInputElement;

    function handleSelect(facility: typeof facilities[0]) {
        facilityStatus.update(status => ({
            ...status!,
            selectedFacility: facility
        }));
        isOpen = false;
    }

    function toggleDropdown() {
        isOpen = !isOpen;
        isCreating = false;
    }

    function startCreating() {
        isCreating = true;
        setTimeout(() => nameInput?.focus(), 0);
    }

    function cancelCreating() {
        isCreating = false;
    }

    function handleClickOutside(event: MouseEvent) {
        if (dropdownContainer && !dropdownContainer.contains(event.target as Node)) {
            isOpen = false;
            isCreating = false;
        }
    }

    onMount(() => {
        document.addEventListener('click', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    });
</script>

<div class="fixed bottom-12 left-16 z-50" bind:this={dropdownContainer}>
    <div 
        class="relative"
        class:w-72={isOpen}
        class:w-56={!isOpen}
    >
        <button
            on:click|stopPropagation={toggleDropdown}
            class="dropdown-trigger"
        >
            <span class="text-sm font-medium truncate">
                {$facilityStatus.selectedFacility?.name || 'Select Facility'}
            </span>
            <svg
                class="w-5 h-5 transition-transform duration-200 ml-3"
                class:rotate-180={isOpen}
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
            >
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
        </button>

        {#if isOpen}
            <div class="dropdown-panel">
                <div class="dropdown-content">
                    {#each facilities as facility}
                        <button
                            on:click|stopPropagation={() => handleSelect(facility)}
                            class="dropdown-item {$facilityStatus.selectedFacility?.facility_id === facility.facility_id ? 'dropdown-item-selected' : ''}"
                        >
                            <span class="font-medium">{facility.name}</span>
                            {#if facility.is_primary}
                                <span class="ml-2 text-xs text-mint-600">(Primary)</span>
                            {/if}
                        </button>
                    {/each}
                </div>
                
                <div class="dropdown-divider">
                    <button
                        class="dropdown-action-button"
                        on:click|stopPropagation={startCreating}
                    >
                        <svg
                            class="w-4 h-4 mr-2"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                        </svg>
                        Create New Facility
                    </button>
                    
                    {#if isCreating}
                        <div class="pl-6 mt-2 relative before:absolute before:left-[0.9375rem] before:top-0 before:h-full before:w-px before:bg-mint-200">
                            <div class="relative before:absolute before:left-[-0.9375rem] before:top-[1.125rem] before:w-3 before:h-px before:bg-mint-200">
                                <form
                                    method="POST"
                                    action="?/create"
                                    class="p-3 space-y-3 bg-mint-50/50 rounded-xl border border-mint-100"
                                    use:enhance
                                    on:submit={() => {
                                        isCreating = false;
                                        isOpen = false;
                                    }}
                                >
                                    <div class="space-y-2">
                                        <p class="text-sm text-sage-600">Give your new facility a unique name</p>
                                        <input
                                            bind:this={nameInput}
                                            type="text"
                                            name="name"
                                            class="form-input text-sm"
                                            placeholder="Facility name"
                                            required
                                        >
                                    </div>
                                    <div class="flex items-center space-x-2 text-sm text-sage-700">
                                        <input
                                            type="checkbox"
                                            name="is_primary"
                                            value="true"
                                            class="rounded border-sage-300 text-mint-600 focus:ring-mint-500"
                                        >
                                        <span>Set as primary facility</span>
                                    </div>
                                    <div class="flex justify-end space-x-2">
                                        <button
                                            type="button"
                                            class="btn-secondary text-sm px-3 py-1.5"
                                            on:click={cancelCreating}
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            type="submit"
                                            class="btn-primary text-sm px-3 py-1.5"
                                        >
                                            Create
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    {/if}
                </div>
            </div>
        {/if}
    </div>
</div>