<script lang="ts">
    import { setFacilities } from '$stores/facilities';
    import { setFields, fields } from '$stores/fields';
    import FacilitiesDropdown from '$lib/components/FacilityDropdown.svelte';
    import FieldsDropdown from '$lib/components/FieldsDropdown.svelte';
    import DisplayCard, { type Column } from '$lib/components/DisplayCard.svelte';
    import { dropdownState } from '$stores/fieldDropdownState';
    import { superForm } from 'sveltekit-superforms/client';
	import CreateField from '$lib/components/CreateField.svelte';

    let { data } = $props();
    
    const deleteForm = superForm(data.deleteForm, {
        onResult: ({ result }) => {
            if (result.type === 'success' && result.data?.field_id) {
                handleFieldDelete(result.data.field_id);
            }
        }
    });


    let displayColumns: Column[] = $state([]);

    const handleFieldDelete = (fieldId: number) => {
        fields.update(t => t.filter(item => item.field_id !== fieldId));
        dropdownState.update(state => ({ ...state, selectedField: null }));
    };

    const formatAvailability = (availability: Record<string, any>) => {
        return Object.entries(availability)
            .map(([day, times]) => 
                `${day}: ${times.start_time}-${times.end_time}`
            )
            .join('\n');
    };

    $effect(() => {
        if ($dropdownState.selectedField) {
            const field = $fields.find(f => f.field_id === $dropdownState.selectedField?.field_id) || $dropdownState.selectedField;
            displayColumns = [
                {
                    fields: [
                        { label: 'Size', value: field.size },
                        { label: 'Field Type', value: field.field_type },
                        { 
                            label: 'Half Fields', 
                            value: field.half_subfields,
                            style: 'subfields' as const 
                        },
                        { 
                            label: 'Quarter Fields', 
                            value: field.quarter_subfields,
                            style: 'subfields' as const 
                        }
                    ]
                },
                {
                    fields: [
                        { 
                            label: 'Availability', 
                            value: formatAvailability(field.availability),
                            style: 'multiline' as const 
                        }
                    ]
                }
            ];
        }
    });

</script>

<div class="page-container">
    <div class="sidebar">
        <div class="sidebar-content">
            <FieldsDropdown fields={$fields}/>
        </div>
        <div class="sidebar-footer">
            <FacilitiesDropdown form={data.facilityForm}/>
        </div>
    </div>

    {#if $dropdownState.selectedField || $dropdownState.showCreateField}
        <div class="main-content">
            {#if $dropdownState.showCreateField}
                <CreateField form={data.createFieldForm} />
            {:else if $dropdownState.selectedField}
                <DisplayCard 
                    title={$fields.find(f => f.field_id === $dropdownState.selectedField?.field_id)?.name || $dropdownState.selectedField.name}
                    columns={displayColumns}
                    deleteConfig={{
                        enabled: true,
                        itemId: $dropdownState.selectedField.field_id || 0,
                        itemName: $dropdownState.selectedField.name,
                        onDelete: handleFieldDelete,
                        actionPath: "?/deleteField",
                        formField: "field_id",
                        enhance: deleteForm.enhance
                    }}
                />
            {/if}
        </div>
    {:else}
        <div class="main-content text-center p-8 text-sage-500">
            Select a field to view details or create a new field.
        </div>
    {/if}
</div>
