<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    import { superForm } from 'sveltekit-superforms/client';
    import { facilities, addFacility } from '$lib/stores/facilities';
    import { dropdownState, toggleDropdown, selectFacility } from '$lib/stores/FacilityDropdownState';
    import type { Facility } from '$lib/schemas/facility';

    let { form: facilityFormData } = $props();

    let errorMessage = $state('');

    const { form, errors, enhance, message } = superForm(facilityFormData, {
        taintedMessage: null,
        onUpdate: ({ form }) => {
            console.log('Form data being submitted:', form.data);
        },
        onResult: async ({ result }) => {
            if (result.type === 'success') {
                errorMessage = '';
                const newFacility = result.data?.facility;
                if (newFacility) {
                    addFacility(newFacility);
                    selectFacility(newFacility);
                    dropdownState.update(state => ({
                        ...state,
                        isOpen: false,
                        selectedFacility: newFacility 
                    }));
                    isCreating = false;
                }
                await invalidateAll();
            } else if (result.type === 'failure') {
                errorMessage = result.data?.error || 'Failed to create facility';
            }
        },
        onError: (err) => {
            console.error('Form submission error:', err);
        }
    });

    let dropdownContainer: HTMLDivElement;
    let nameInput = $state<HTMLInputElement | null>(null);
    let isCreating = $state(false);

    function handleSelect(facility: Facility) {
        selectFacility(facility);
        dropdownState.update(state => ({ ...state, isOpen: false }));
    }

    function startCreating() {
        isCreating = true;
        setTimeout(() => nameInput?.focus(), 0);
    }

    function cancelCreating() {
        isCreating = false;
        $form.name = '';
    }

    $effect(() => {
        if ($message?.type === 'success') {
            isCreating = false;
        }
    });
</script>

<div class="facilities-dropdown">
    <div 
        class="relative"
        class:w-72={$dropdownState.isOpen}
        class:w-56={!$dropdownState.isOpen}
    >
        <button
            onclick={(e) => {
                e.stopPropagation();
                toggleDropdown('isOpen');
            }}
            class="dropdown-trigger"
        >
            <span class="text-sm font-medium truncate">
                {$dropdownState.selectedFacility?.name || 'Select Facility'}
            </span>
            <svg
                class="w-5 h-5 transition-transform duration-200"
                class:rotate-180={$dropdownState.isOpen}
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
            >
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
        </button>

        {#if $dropdownState.isOpen}
            <div class="dropdown-panel">
                <div class="dropdown-content">
                    {#each $facilities as facility}
                        <button
                            onclick={(e) => {
                                e.stopPropagation();
                                handleSelect(facility);
                            }}
                            class="dropdown-item {$dropdownState.selectedFacility?.facility_id === facility.facility_id ? 'dropdown-item-selected' : ''}"
                        >
                            <span class="font-medium">{facility.name}</span>
                            {#if facility.is_primary}
                                <span class="ml-2 text-xs text-mint-600">(Primary)</span>
                            {/if}
                        </button>
                    {/each}
                </div>
                
                <div class="dropdown-divider">
                    {#if !isCreating}
                        <button
                            type="button"
                            class="dropdown-action-button"
                            onclick={(e) => {
                                e.stopPropagation();
                                startCreating();
                            }}
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
                    {:else}
                        <div class="pl-6 mt-2 relative before:absolute before:left-[0.9375rem] before:top-0 before:h-full before:w-px before:bg-mint-200">
                            <div class="relative before:absolute before:left-[-0.9375rem] before:top-[1.125rem] before:w-3 before:h-px before:bg-mint-200">
                                <form
                                    method="POST"
                                    action="?/create"
                                    class="p-3 space-y-3 bg-mint-50/50 rounded-xl border border-mint-100"
                                    use:enhance
                                >
                                    <input 
                                        type="hidden" 
                                        name="club_id" 
                                        bind:value={$form.club_id}
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
                                            class:border-red-300={!!errorMessage}
                                        >
                                        {#if errorMessage}
                                            <p class="text-sm text-red-600 mt-1">{errorMessage}</p>
                                        {/if}
                                    </div>
                                    <div class="flex items-center space-x-2 text-sm text-sage-700">
                                        <input
                                            type="checkbox"
                                            name="is_primary"
                                            value="true"
                                            class="rounded-sm border-sage-300 text-mint-600 focus:ring-mint-500"
                                        >
                                        <span>Set as primary facility</span>
                                    </div>
                                    <div class="flex justify-end space-x-2">
                                        <button
                                            type="button"
                                            class="btn-secondary text-sm px-3 py-1.5"
                                            onclick={cancelCreating}
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