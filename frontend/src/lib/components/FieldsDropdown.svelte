<script lang="ts">
    import { dropdownState as facilityDropdownState } from '../../stores/FacilityDropdownState';
    import { dropdownState, toggleDropdown, selectField, setDefaultField, toggleCreateField } from '../../stores/fieldDropdownState';
    import type { Field } from '$lib/schemas/field';

    let { fields } = $props<{ fields: Field[] }>();

    const filteredFields = $derived(
        $facilityDropdownState.selectedFacility
            ? fields.filter((field: Field) => field.facility_id === $facilityDropdownState.selectedFacility?.facility_id)
            : fields
    );

    const sizeOrder: Record<string, number> = {
        '11v11': 1,
        '8v8': 2,
        '5v5': 3,
        '3v3': 4
    };

    const groupedFields = $derived(
        Object.entries(
            filteredFields.reduce((groups: Record<string, Field[]>, field: Field) => {
                const size = field.size;
                if (!groups[size]) {
                    groups[size] = [];
                }
                groups[size].push(field);
                return groups;
            }, {})
        ).sort(([sizeA], [sizeB]) => sizeOrder[sizeA] - sizeOrder[sizeB]) as [string, Field[]][]
    );

    $effect(() => {
        if (filteredFields.length > 0) {
            setDefaultField(filteredFields);
        }
    });


    function handleClickOutside(event: MouseEvent) {
        const target = event.target as HTMLElement;
        const isClickInsideDropdown = target.closest('.fields-dropdown');
        const isClickInsideCreateCard = target.closest('.field-card');
        const isClickInsideInput = target.closest('input, select, button');
        
        if (!isClickInsideDropdown && !isClickInsideCreateCard && !isClickInsideInput) {
            $dropdownState.fieldsOpen = false;
            $dropdownState.showCreateField = false;
        }
    }
</script>


<div class="fields-dropdown">
    <div class="bg-white rounded-2xl shadow-xl border border-mint-100 overflow-hidden w-full">
        <div class="flex items-center">
            <div class="flex-1 flex items-center">
                <h2 class="text-sm font-medium text-sage-700 pl-4">Fields</h2>
                <button
                    class="p-2 ml-2"
                    onclick={() => toggleDropdown('fieldsOpen')}
                    aria-label="Toggle fields dropdown"
                >
                    <svg
                        class="w-5 h-5 transition-transform duration-200 text-sage-600"
                        class:rotate-180={$dropdownState.fieldsOpen}
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a 1 1 0 111.414 1.414l-4 4a 1 1 0 01-1.414 0l-4-4a 1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
            <button 
                class="btn-primary text-sm py-1.5 m-2"
                onclick={toggleCreateField}
            >
                Create Field
            </button>
        </div>
        {#if $dropdownState.fieldsOpen}
            <div class="dropdown-content border-t border-mint-100">
                {#if fields && filteredFields.length > 0}
                    <div class="p-1 space-y-3">
                        {#each groupedFields as [size, sizeFields]}
                            <div class="space-y-1">
                                <h3 class="text-xs font-medium text-sage-600 px-2">{size}</h3>
                                {#each sizeFields as field}
                                    <button
                                        class="dropdown-item {$dropdownState.selectedField?.field_id === field.field_id ? 'dropdown-item-selected' : ''}"
                                        onclick={() => selectField(field)}
                                    >
                                        <span class="font-medium">{field.name}</span>
                                    </button>
                                {/each}
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="p-4 text-sage-500 text-center text-sm">
                        <p>No fields available{$facilityDropdownState.selectedFacility ? ' for this facility' : ''}</p>
                        <p class="mt-1 text-xs">Click 'Create Field' to add one</p>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>