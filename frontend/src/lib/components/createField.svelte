<script lang="ts">
    import type { Field, FieldSize } from '$lib/types/field';
    import { enhance } from '$app/forms';
    import type { SubmitFunction } from '@sveltejs/kit';

    export let facilityId: number | undefined = undefined;

    const fieldSizes: FieldSize[] = ['11v11', '8v8', '5v5', '3v3'];
    
    let halfFields: { name: string, hasQuarters: boolean, quarterFields: { name: string }[] }[] = [];

    function addHalfField() {
        halfFields = [...halfFields, { name: '', hasQuarters: false, quarterFields: [] }];
    }

    function addQuarterField(halfFieldIndex: number) {
        halfFields[halfFieldIndex].quarterFields = [
            ...halfFields[halfFieldIndex].quarterFields,
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

<form
    method="POST"
    action="?/createField"
    use:enhance={handleSubmit}
    class="space-y-4"
>
    <input type="hidden" name="facility_id" value={facilityId} />
    
    <div>
        <label for="name">Field Name</label>
        <input type="text" id="name" name="name" required />
    </div>

    <div>
        <label for="size">Field Size</label>
        <select id="size" name="size" required>
            {#each fieldSizes as size}
                <option value={size}>{size}</option>
            {/each}
        </select>
    </div>

    <div>
        <h3>Half Fields</h3>
        <button type="button" on:click={addHalfField}>Add Half Field</button>
        
        {#each halfFields as halfField, halfIndex}
            <div class="ml-4">
                <input
                    type="text"
                    name="half_fields[{halfIndex}].name"
                    bind:value={halfField.name}
                    placeholder="Half field name"
                />
                
                <label>
                    <input
                        type="checkbox"
                        bind:checked={halfField.hasQuarters}
                    />
                    Add quarter fields
                </label>

                {#if halfField.hasQuarters}
                    <button type="button" on:click={() => addQuarterField(halfIndex)}>
                        Add Quarter Field
                    </button>
                    
                    {#each halfField.quarterFields as quarterField, quarterIndex}
                        <div class="ml-4">
                            <input
                                type="text"
                                name="half_fields[{halfIndex}].quarter_fields[{quarterIndex}].name"
                                bind:value={quarterField.name}
                                placeholder="Quarter field name"
                            />
                        </div>
                    {/each}
                {/if}
            </div>
        {/each}
    </div>

    <button type="submit">Create Field</button>
</form>