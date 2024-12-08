<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{ subfieldsChange: any }>();

    let halfFields: { 
        name: string, 
        quarterFields: { name: string, isCollapsed?: boolean }[], 
        isCollapsed?: boolean 
    }[] = [];

    let showHalfFieldInputs = true; // If needed

    function addHalfField() {
        if (halfFields.length === 0) {
            halfFields = [
                { name: '', quarterFields: [], isCollapsed: false },
                { name: '', quarterFields: [], isCollapsed: false }
            ];
            dispatchUpdatedData();
        }
    }

    function addQuarterFields(halfFieldIndex: number) {
        halfFields[halfFieldIndex].quarterFields = [
            { name: '', isCollapsed: false },
            { name: '', isCollapsed: false }
        ];
        halfFields = [...halfFields];
        dispatchUpdatedData();
    }

    function handleHalfFieldBlur(halfIndex: number) {
        if (halfFields[halfIndex].name.trim()) {
            halfFields[halfIndex].isCollapsed = true;
            halfFields = [...halfFields];
            dispatchUpdatedData();
        }
    }

    function editHalfField(halfIndex: number) {
        halfFields[halfIndex].isCollapsed = false;
        halfFields = [...halfFields];
        dispatchUpdatedData();
    }

    function areAllHalfFieldsComplete() {
        return halfFields.length === 2 && halfFields.every(field => field.name.trim() && field.isCollapsed);
    }

    function handleQuarterFieldBlur(halfIndex: number, quarterIndex: number) {
        const quarterField = halfFields[halfIndex].quarterFields[quarterIndex];
        if (quarterField.name.trim()) {
            quarterField.isCollapsed = true;
            halfFields = [...halfFields];
            dispatchUpdatedData();
        }
    }

    function dispatchUpdatedData() {
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
        dispatch('subfieldsChange', halfFieldsData);
    }
</script>

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

    <!-- Display completed half fields -->
    <div class="space-y-3">
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
                    placeholder="Half field name"
                    class="form-input-sm"
                    bind:value={halfField.name}
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
                                dispatchUpdatedData();
                            }}
                            class="text-xs px-2 py-1 bg-white text-mint-600 rounded-lg hover:bg-mint-50 transition-colors border border-mint-200"
                        >
                            Add Quarter Fields
                        </button>
                    {/if}
                </div>

                <!-- Completed Quarter Fields Display -->
                {#if halfFields.some(field => field.quarterFields.some(q => q.isCollapsed))}
                    <div class="flex flex-wrap gap-2">
                        {#each halfFields as halfField, halfIndex}
                            {#each halfField.quarterFields as quarterField, quarterIndex}
                                {#if quarterField.isCollapsed}
                                    <button 
                                        type="button"
                                        class="field-tag hover:bg-mint-100 transition-colors"
                                        on:click={() => {
                                            quarterField.isCollapsed = false;
                                            halfFields = [...halfFields];
                                            dispatchUpdatedData();
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
                                                placeholder="Quarter field name"
                                                class="form-input-sm"
                                                bind:value={quarterField.name}
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
