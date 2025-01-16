<script lang="ts">
    import type { SuperForm, SuperValidated, ValidationErrors } from 'sveltekit-superforms';
    import EditableField from './EditableField.svelte';
    import type { GenerateScheduleRequest, Constraint } from '$lib/schemas/schedule';
    import { SidebarDropdownState } from '../../stores/ScheduleSidebarState';
    import type { Writable } from 'svelte/store';
    import { writable } from 'svelte/store';
    import { fields } from '../../stores/fields';
    
    let { form, errors } = $props<{ 
        form: Writable<GenerateScheduleRequest>,
        errors: Writable<ValidationErrors<GenerateScheduleRequest>>
    }>();

    const selectedTeam = $derived($SidebarDropdownState.selectedTeam);
    const expandedConstraints = writable<Set<number>>(new Set());

    function addConstraint(type: 'specific' | 'flexible') {
        const newConstraint: Constraint = {
            team_id: selectedTeam?.team_id || 0,
            required_field: null,
            required_cost: null,
            sessions: 1,
            length: 1,
            partial_ses_space_size: null,
            partial_ses_space_cost: null,
            partial_ses_time: null,
            start_time: null,
            constraint_type: type
        };

        form.update((f: GenerateScheduleRequest) => ({
            ...f,
            constraints: [...(f.constraints || []), newConstraint]
        }));
    }

    function getActualIndex(visibleIndex: number): number {
        if (!$form.constraints) return -1;
        let count = -1;
        return $form.constraints.findIndex((c: Constraint) => {
            if (c.team_id === selectedTeam?.team_id) {
                count++;
                return count === visibleIndex;
            }
            return false;
        });
    }

    function removeConstraint(visibleIndex: number) {
        const actualIndex = getActualIndex(visibleIndex);
        if (actualIndex === -1) return;

        form.update((f: GenerateScheduleRequest) => {
            const constraints = [...(f.constraints || [])];
            constraints.splice(actualIndex, 1);
            return {
                ...f,
                constraints
            };
        });
    }

    function togglePartialFields(visibleIndex: number) {
        expandedConstraints.update(expanded => {
            const newExpanded = new Set(expanded);
            if (newExpanded.has(visibleIndex)) {
                newExpanded.delete(visibleIndex);
            } else {
                newExpanded.add(visibleIndex);
            }
            return newExpanded;
        });
    }
</script>

<div class="detail-card">
    {#if selectedTeam}
        <div class="mb-4">
            <h3 class="text-lg font-semibold mb-2">Constraints for {selectedTeam.name}</h3>
            {#if $form.constraints}
                {#each $form.constraints.filter((c: Constraint) => c.team_id === selectedTeam.team_id) as constraint, visibleIndex}
                    <div class="bg-gray-50 p-4 rounded-lg mb-4">
                        <div class="flex justify-between items-center mb-4">
                            <h4 class="font-medium">Constraint {visibleIndex + 1}</h4>
                            <button 
                                class="text-red-500 hover:text-red-700"
                                onclick={() => removeConstraint(visibleIndex)}
                            >
                                Remove
                            </button>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            {#if constraint.constraint_type === 'specific'}
                                {@const actualIndex = getActualIndex(visibleIndex)}
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].sessions"
                                    label="Sessions for this constraint"
                                    type="select"
                                    options={[
                                        { value: 1, label: '1' },
                                        { value: 2, label: '2' },
                                        { value: 3, label: '3' },
                                        { value: 4, label: '4' },
                                        { value: 5, label: '5' },
                                        { value: 6, label: '6' },
                                        { value: 7, label: '7' }
                                    ]}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].required_field"
                                    label="Required Field"
                                    type="select"
                                    options={$fields.flatMap(field => [
                                        { value: field.field_id, label: `${field.name} (${field.field_type})` },
                                        ...field.half_subfields.map(half => ({ 
                                            value: half.field_id, 
                                            label: `${half.name} (half of ${field.name})` 
                                        })),
                                        ...field.quarter_subfields.map(quarter => ({ 
                                            value: quarter.field_id, 
                                            label: `${quarter.name} (quarter of ${field.name})` 
                                        }))
                                    ])}
                                />
                            
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].length"
                                    label="Length"
                                    type="select"
                                    options={[
                                        { value: 1, label: '15 minutes' },
                                        { value: 2, label: '30 minutes' },
                                        { value: 3, label: '45 minutes' },
                                        { value: 4, label: '60 minutes (1 hour)' },
                                        { value: 5, label: '75 minutes' },
                                        { value: 6, label: '90 minutes (1,5 hours)' },
                                        { value: 7, label: '105 minutes' },
                                        { value: 8, label: '120 minutes (2 hours' },
                                        { value: 9, label: '135 minutes' },
                                        { value: 10, label: '150 minutes (2,5 hours)' }
                                    ]}
                                    required
                                />

                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].start_time"
                                    label="Start Time"
                                    type="text"
                                    placeholder="HH:MM:SS"
                                    hide_label_in_view={false}
                                />

                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].day_of_week"
                                    label="Day of Week"
                                    type="select"
                                    options={[
                                        { value: 0, label: 'Monday' },
                                        { value: 1, label: 'Tuesday' },
                                        { value: 2, label: 'Wednesday' },
                                        { value: 3, label: 'Thursday' },
                                        { value: 4, label: 'Friday' },
                                        { value: 5, label: 'Saturday' },
                                        { value: 6, label: 'Sunday' }
                                    ]}
                                />

                                <div class="col-span-2 flex justify-end">
                                    <button
                                        class="flex items-center text-mint-600 hover:text-mint-700 mt-2"
                                        onclick={() => togglePartialFields(visibleIndex)}
                                    >
                                        <span class="mr-1">{$expandedConstraints.has(visibleIndex) ? '−' : '+'}</span>
                                        Partial Session Options
                                    </button>
                                </div>
                                
                                {#if $expandedConstraints.has(visibleIndex)}
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].partial_ses_space_size"
                                        label="Partial Size"
                                        type="select"
                                        options={[
                                            { value: 'full', label: 'Full' },
                                            { value: 'half', label: 'Half' },
                                            { value: 'quarter', label: 'Quarter' }
                                        ]}
                                    />
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].partial_ses_time"
                                        label="Partial Time"
                                        type="select"
                                        options={[
                                            { value: 1, label: '15 minutes' },
                                            { value: 2, label: '30 minutes' },
                                            { value: 3, label: '45 minutes' },
                                            { value: 4, label: '60 minutes (1 hour)' },
                                            { value: 5, label: '75 minutes' },
                                            { value: 6, label: '90 minutes (1,5 hours)' }]}
                                    />
                                {/if}
                            {:else if constraint.constraint_type === 'flexible'}
                                {@const actualIndex = getActualIndex(visibleIndex)}
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].sessions"
                                    label="Sessions for this constraint"
                                    type="select"
                                    options={[
                                        { value: 1, label: '1' },
                                        { value: 2, label: '2' },
                                        { value: 3, label: '3' },
                                        { value: 4, label: '4' },
                                        { value: 5, label: '5' },
                                        { value: 6, label: '6' },
                                        { value: 7, label: '7' }
                                    ]}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].start_time"
                                    label="Start Time"
                                    type="text"
                                    placeholder="HH:MM:SS"
                                />

                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].day_of_week"
                                    label="Day of Week"
                                    type="select"
                                    options={[
                                        { value: 0, label: 'Monday' },
                                        { value: 1, label: 'Tuesday' },
                                        { value: 2, label: 'Wednesday' },
                                        { value: 3, label: 'Thursday' },
                                        { value: 4, label: 'Friday' },
                                        { value: 5, label: 'Saturday' },
                                        { value: 6, label: 'Sunday' }
                                    ]}
                                />

                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].length"
                                    label="Length"
                                    type="select"
                                    options={[
                                        { value: 1, label: '15 minutes' },
                                        { value: 2, label: '30 minutes' },
                                        { value: 3, label: '45 minutes' },
                                        { value: 4, label: '60 minutes (1 hour)' },
                                        { value: 5, label: '75 minutes' },
                                        { value: 6, label: '90 minutes (1,5 hours)' },
                                        { value: 7, label: '105 minutes' },
                                        { value: 8, label: '120 minutes (2 hours' },
                                        { value: 9, label: '135 minutes' },
                                        { value: 10, label: '150 minutes (2,5 hours)' }
                                    ]}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].required_cost"
                                    label="Required Size"
                                    type="select"
                                    options={[
                                        { value: 1000, label: '11v11' },
                                        { value: 500, label: '8v8, Half 11v11' },
                                        { value: 250, label: '5v5, Half 8v8, Quarter 11v11' },
                                        { value: 125, label: '3v3, Half 5v5, Quarter 8v8' }
                                    ]}
                                    view_mode_style="pill"
                                    required
                                />
                                <div class="col-span-2 flex justify-end">
                                    <button
                                        class="flex items-center text-mint-600 hover:text-mint-700 mt-2"
                                        onclick={() => togglePartialFields(visibleIndex)}
                                    >
                                        <span class="mr-1">{$expandedConstraints.has(visibleIndex) ? '−' : '+'}</span>
                                        Partial Session Options
                                    </button>
                                </div>
                                
                                {#if $expandedConstraints.has(visibleIndex)}
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].partial_ses_space_cost"
                                        label="Partial Size"
                                        type="select"
                                        options={[
                                            { value: 1000, label: '11v11' },
                                            { value: 500, label: '8v8, Half 11v11' },
                                            { value: 250, label: '5v5, Half 8v8, Quarter 11v11' }
                                        ]}
                                        view_mode_style="pill"
                                    />
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].partial_ses_time"
                                        label="Partial Time"
                                        type="select"
                                        options={[
                                            { value: 1, label: '15 minutes' },
                                            { value: 2, label: '30 minutes' },
                                            { value: 3, label: '45 minutes' },
                                            { value: 4, label: '60 minutes (1 hour)' },
                                            { value: 5, label: '75 minutes' },
                                            { value: 6, label: '90 minutes (1,5 hours)' }
                                    ]}
                                    />
                                {/if}
                            {/if}
                        </div>
                    </div>
                {/each}
            {/if}
            
            {#if !$form.constraints?.filter((c: Constraint) => c.team_id === selectedTeam.team_id).length 
                || $form.constraints?.filter((c: Constraint) => c.team_id === selectedTeam.team_id).length < 7}
                <div class="relative inline-block">
                    <button 
                        class="btn-add"
                        onclick={() => {
                            const dropdown = document.getElementById('constraintTypeDropdown');
                            if (dropdown) {
                                dropdown.classList.toggle('hidden');
                            }
                        }}
                    >
                        Add Constraint
                    </button>
                    <div 
                        id="constraintTypeDropdown"
                        class="hidden absolute left-0 top-full mt-2 w-48 bg-white rounded-xl shadow-xl border border-mint-100 z-10"
                    >
                        <div class="dropdown-content">
                            <button
                                class="dropdown-item"
                                onclick={() => {
                                    addConstraint('specific');
                                    document.getElementById('constraintTypeDropdown')?.classList.add('hidden');
                                }}
                            >
                                Specific
                            </button>
                            <button
                                class="dropdown-item"
                                onclick={() => {
                                    addConstraint('flexible');
                                    document.getElementById('constraintTypeDropdown')?.classList.add('hidden');
                                }}
                            >
                                Flexible
                            </button>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    {:else}
        <p class="text-gray-500">Select a team to add constraints</p>
    {/if}
</div>