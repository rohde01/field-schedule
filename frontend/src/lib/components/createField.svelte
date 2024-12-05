<script lang="ts">
    import type { Field, FieldSize } from '$lib/types/field';
    import { enhance } from '$app/forms';
    import type { SubmitFunction } from '@sveltejs/kit';
    import { slide } from 'svelte/transition';

    export let facilityId: number | undefined = undefined;

    const fieldSizes: FieldSize[] = ['11v11', '8v8', '5v5', '3v3'];
    
    let halfFields: { name: string, hasQuarters: boolean, quarterFields: { name: string }[] }[] = [];

    function addHalfField() {
        // Add exactly two half fields
        halfFields = [
            ...halfFields,
            { name: '', hasQuarters: false, quarterFields: [] },
            { name: '', hasQuarters: false, quarterFields: [] }
        ];
    }

    function addQuarterField(halfFieldIndex: number) {
        // Add exactly two quarter fields
        halfFields[halfFieldIndex].quarterFields = [
            { name: '' },
            { name: '' }
        ];
        halfFields = [...halfFields];
    }

    function prepareFormData() {
        const halfFieldsData = halfFields
            .filter(h => h.name.trim())
            .map(half => ({
                name: half.name,
                field_type: 'half' as const,
                quarter_fields: half.hasQuarters 
                    ? half.quarterFields
                        .filter(q => q.name.trim())
                        .map(q => ({
                            name: q.name,
                            field_type: 'quarter' as const
                        }))
                    : []
            }));

        return {
            facility_id: facilityId ?? 0,
            name: document.querySelector<HTMLInputElement>('#name')?.value,
            size: document.querySelector<HTMLSelectElement>('#size')?.value,
            field_type: 'full' as const,
            half_fields: halfFieldsData
        };
    }

    const handleSubmit: SubmitFunction = ({ formData }) => {
        const fieldData = prepareFormData();
        formData.set('fieldData', JSON.stringify(fieldData));
    };
</script>

<div role="presentation" on:mousedown|stopPropagation>
    <form
        method="POST"
        action="?/createField"
        use:enhance={handleSubmit}
        class="space-y-6"
    >
        <input type="hidden" name="facility_id" value={facilityId} />
        
        <div class="space-y-2">
            <label for="name" class="form-label">Field Name</label>
            <input 
                type="text" 
                id="name" 
                name="name" 
                required
                class="form-input" 
                placeholder="Enter field name..."
            />
        </div>

        <div class="space-y-2">
            <label for="size" class="form-label">Field Size</label>
            <select 
                id="size" 
                name="size" 
                required
                class="form-input"
            >
                {#each fieldSizes as size}
                    <option value={size}>{size}</option>
                {/each}
            </select>
        </div>

        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <h3 class="text-sm font-medium text-sage-700">Half Fields</h3>
                {#if halfFields.length < 2}
                    <button 
                        type="button" 
                        on:click={addHalfField}
                        class="btn-secondary text-sm py-1"
                    >
                        Add Half Fields
                    </button>
                {/if}
            </div>
            
            <div class="space-y-4">
                {#each halfFields as halfField, halfIndex}
                    <div class="bg-mint-50/50 rounded-xl p-4 space-y-3 transition-all duration-200">
                        <div class="flex items-center gap-3">
                            <input
                                type="text"
                                name="half_fields[{halfIndex}].name"
                                bind:value={halfField.name}
                                placeholder="Half field name"
                                class="form-input text-sm"
                            />
                            
                            <label class="flex items-center gap-2 text-sm text-sage-700 cursor-pointer">
                                <input
                                    type="checkbox"
                                    bind:checked={halfField.hasQuarters}
                                    class="rounded text-mint-500 focus:ring-mint-500"
                                />
                                Split into quarters
                            </label>
                        </div>

                        {#if halfField.hasQuarters}
                            <div class="space-y-3">
                                <div class="flex items-center justify-between">
                                    <span class="text-xs font-medium text-sage-600">Quarter Fields</span>
                                    {#if halfField.quarterFields.length < 2}
                                        <button 
                                            type="button" 
                                            on:click={() => addQuarterField(halfIndex)}
                                            class="text-xs px-2 py-1 bg-white text-mint-600 rounded-lg hover:bg-mint-50 transition-colors"
                                        >
                                            Add Quarter Fields
                                        </button>
                                    {/if}
                                </div>
                                
                                <div class="pl-4 space-y-2">
                                    {#each halfField.quarterFields as quarterField, quarterIndex}
                                        <input
                                            type="text"
                                            name="half_fields[{halfIndex}].quarter_fields[{quarterIndex}].name"
                                            bind:value={quarterField.name}
                                            placeholder="Quarter field name"
                                            class="form-input text-sm"
                                        />
                                    {/each}
                                </div>
                            </div>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>

        <div class="pt-2">
            <button type="submit" class="btn-primary w-full">Create Field</button>
        </div>
    </form>
</div>

<style lang="postcss">
    input[type="checkbox"] {
        width: 1rem;
        height: 1rem;
    }
</style>