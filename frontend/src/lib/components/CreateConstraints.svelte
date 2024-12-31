<script lang="ts">
    import type { SuperForm, SuperValidated, ValidationErrors } from 'sveltekit-superforms';
    import EditableField from './EditableField.svelte';
    import type { GenerateScheduleRequest, Constraint } from '$lib/schemas/schedule';
    import { SidebarDropdownState } from '../../stores/ScheduleSidebarState';
    import type { Writable } from 'svelte/store';

    let { form, errors } = $props<{ 
        form: Writable<GenerateScheduleRequest>,
        errors: Writable<ValidationErrors<GenerateScheduleRequest>>
    }>();

    const selectedTeam = $derived($SidebarDropdownState.selectedTeam);

    function addConstraint(type: 'specific' | 'flexible') {
        const newConstraint: Constraint = {
            team_id: selectedTeam?.team_id || 0,
            required_size: null,
            subfield_type: null,
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
</script>

<div class="detail-card">
    {#if selectedTeam}
        <div class="mb-4">
            <h3 class="text-lg font-semibold mb-2">Team Constraints</h3>
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
                                    label="Sessions (1-7)"
                                    type="number"
                                    min={1}
                                    max={7}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].start_time"
                                    label="Start Time (optional)"
                                    type="text"
                                    placeholder="HH:MM:SS"
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].length"
                                    label="Length (# x 15 min)"
                                    type="number"
                                    min={1}
                                    max={10}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].required_size"
                                    label="Required Size"
                                    type="select"
                                    options={[
                                        { value: '11v11', label: '11v11' },
                                        { value: '8v8', label: '8v8' },
                                        { value: '5v5', label: '5v5' },
                                        { value: '3v3', label: '3v3' }
                                    ]}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].subfield_type"
                                    label="Subfield Type"
                                    type="select"
                                    options={[
                                        { value: 'full', label: 'Full' },
                                        { value: 'half', label: 'Half' },
                                        { value: 'quarter', label: 'Quarter' }
                                    ]}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].partial_ses_space_size"
                                    label="Partial Space Size (optional)"
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
                                    label="Partial Time (1-10)"
                                    type="number"
                                    min={1}
                                    max={10}
                                />
                            {:else if constraint.constraint_type === 'flexible'}
                                {@const actualIndex = getActualIndex(visibleIndex)}
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].sessions"
                                    label="Sessions (1-7)"
                                    type="number"
                                    min={1}
                                    max={7}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].start_time"
                                    label="Start Time (optional)"
                                    type="text"
                                    placeholder="HH:MM:SS"
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].length"
                                    label="Length (# x 15 min)"
                                    type="number"
                                    min={1}
                                    max={10}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].required_cost"
                                    label="Required Cost"
                                    type="select"
                                    options={[
                                        { value: '1000', label: '1000' },
                                        { value: '500', label: '500' },
                                        { value: '250', label: '250' },
                                        { value: '125', label: '125' }
                                    ]}
                                    required
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].partial_ses_space_cost"
                                    label="Partial Space Cost (optional)"
                                    type="select"
                                    options={[
                                        { value: '1000', label: '1000' },
                                        { value: '500', label: '500' },
                                        { value: '250', label: '250' }
                                    ]}
                                />
                                <EditableField
                                    {form}
                                    errors={$errors}
                                    name="constraints[{actualIndex}].partial_ses_time"
                                    label="Partial Time (1-10)"
                                    type="number"
                                    min={1}
                                    max={10}
                                />
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