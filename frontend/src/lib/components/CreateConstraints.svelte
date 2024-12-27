<script lang="ts">
    import type { SuperForm } from 'sveltekit-superforms';
    import type { SuperValidated } from 'sveltekit-superforms';
    import type { z } from 'zod';
    import { page } from '$app/stores';
    import EditableField from './EditableField.svelte';
    import type { GenerateScheduleRequest, Constraint } from '$lib/schemas/schedule';
    import { SidebarDropdownState } from '../../stores/ScheduleSidebarState';
    import type { ValidationErrors } from 'sveltekit-superforms';

    let { form } = $props<{ 
        form: SuperForm<GenerateScheduleRequest>['form']
    }>();

    const selectedTeam = $derived($SidebarDropdownState.selectedTeam);
    const errors = $derived($page.form?.errors ?? {});

    function addConstraint(type: 'specific' | 'flexible') {
        form.update(($form: GenerateScheduleRequest) => {
            const constraints = ($form.constraints || []);
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
            return {
                ...$form,
                constraints: [...constraints, newConstraint]
            };
        });
    }

    function removeConstraint(index: number) {
        form.update(($form: GenerateScheduleRequest) => {
            const constraints = [...($form.constraints || [])];
            constraints.splice(index, 1);
            return {
                ...$form,
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
                {#each $form.constraints.filter((c: Constraint) => c.team_id === selectedTeam.team_id) as constraint, index}
                    <div class="bg-gray-50 p-4 rounded-lg mb-4">
                        <div class="flex justify-between items-center mb-4">
                            <h4 class="font-medium">Constraint {index + 1}</h4>
                            <button 
                                class="text-red-500 hover:text-red-700"
                                onclick={() => removeConstraint(index)}
                            >
                                Remove
                            </button>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            {#if constraint.constraint_type === 'specific'}
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].sessions"
                                    label="Sessions (1-7)"
                                    type="number"
                                    min={1}
                                    max={7}
                                    required
                                />
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].start_time"
                                    label="Start Time (optional)"
                                    type="text"
                                    placeholder="HH:MM:SS"
                                />
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].length"
                                    label="Length (# x 15 min)"
                                    type="number"
                                    min={1}
                                    max={10}
                                    required
                                />
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].required_size"
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
                                    {errors}
                                    name="constraints[{index}].subfield_type"
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
                                    {errors}
                                    name="constraints[{index}].partial_ses_space_size"
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
                                    {errors}
                                    name="constraints[{index}].partial_ses_time"
                                    label="Partial Time (1-10)"
                                    type="number"
                                    min={1}
                                    max={10}
                                />
                            {:else if constraint.constraint_type === 'flexible'}
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].sessions"
                                    label="Sessions (1-7)"
                                    type="number"
                                    min={1}
                                    max={7}
                                    required
                                />
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].start_time"
                                    label="Start Time (optional)"
                                    type="text"
                                    placeholder="HH:MM:SS"
                                />
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].length"
                                    label="Length (# x 15 min)"
                                    type="number"
                                    min={1}
                                    max={10}
                                    required
                                />
                                <EditableField
                                    {form}
                                    {errors}
                                    name="constraints[{index}].required_cost"
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
                                    {errors}
                                    name="constraints[{index}].partial_ses_space_cost"
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
                                    {errors}
                                    name="constraints[{index}].partial_ses_time"
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
               <div class="relative inline-block group">
                 <button
                   class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center"
                 >
                   Add Constraint
                   <span class="ml-1">▼</span>
                 </button>
                 <div 
                   class="absolute bg-white border top-full right-0 w-32 hidden group-hover:block z-10"
                 >
                   <button 
                     class="block w-full text-right px-2 py-1 hover:bg-gray-100"
                     onclick={() => addConstraint('specific')}
                   >
                     Specific
                   </button>
                   <button 
                     class="block w-full text-right px-2 py-1 hover:bg-gray-100"
                     onclick={() => addConstraint('flexible')}
                   >
                     Flexible
                   </button>
                 </div>
               </div>
             {/if}
             
        </div>
    {:else}
        <p class="text-gray-500">Select a team to add constraints</p>
    {/if}
</div>