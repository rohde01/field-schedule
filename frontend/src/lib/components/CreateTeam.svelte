<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import type { SuperValidated } from 'sveltekit-superforms';
    import type { TeamSchema } from '$lib/schemas/team';
    import { page } from '$app/stores';
    import { dropdownState } from '$stores/teamDropdownState';
    import { addTeam } from '$stores/teams';

    let { form: formData } = $props<{ form: SuperValidated<TeamSchema> }>();
    let formElement: HTMLFormElement;
    
    const { form, errors, enhance, message } = superForm(formData, {
        taintedMessage: null,
        onUpdate: ({ form }) => {
            console.log('Form data being submitted:', form.data);
        },
        onResult: ({ result }) => {
            console.log('Form submission result:', result);
            if (result.type === 'success') {
                console.log('Team created successfully');
                if (result.data?.team) {
                    addTeam(result.data.team);
                }
                dropdownState.update(state => ({
                    ...state,
                    showCreateTeam: false,
                    selectedTeam: result.data?.team || null
                }));
            }
        },
        onError: (err) => {
            console.error('Form submission error:', err);
        }
    });

    $form.is_active = true;
</script>

<div class="detail-card">
    <h2 class="detail-card-title">Create New Team</h2>

    {#if $page.status === 400 && $page.form?.error}
        <div class="mb-4 p-4 rounded bg-red-100 text-red-700">
            {$page.form.error}
        </div>
    {/if}
    {#if $message}
        <div class="mb-4 p-4 rounded {$message.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}">
            {$message.text}
        </div>
    {/if}

    <form 
        method="POST" 
        action="?/create" 
        bind:this={formElement}
        use:enhance
        class="detail-card-grid"
    >
        <!-- Left Column: Basic Info -->
        <div class="detail-card-content">
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <h3 class="detail-card-label">Basic Information</h3>
                </div>

                <div class="space-y-4">
                    <div>
                        <label for="name" class="detail-card-label">Team Name</label>
                        <input 
                            type="text" 
                            id="name" 
                            name="name"
                            bind:value={$form.name}
                            class="form-input-sm"
                        />
                        {#if $errors.name}<span class="text-red-500 text-sm mt-1">{$errors.name}</span>{/if}
                    </div>

                    <div>
                        <label for="year" class="detail-card-label">Year (e.g., U13)</label>
                        <input 
                            type="text" 
                            id="year" 
                            name="year"
                            bind:value={$form.year}
                            class="form-input-sm"
                            placeholder="U13"
                        />
                        {#if $errors.year}<span class="text-red-500 text-sm mt-1">{$errors.year}</span>{/if}
                    </div>

                    <div>
                        <label for="gender" class="detail-card-label">Gender</label>
                        <select 
                            id="gender" 
                            name="gender"
                            bind:value={$form.gender}
                            class="form-input-sm"
                        >
                            <option value="boys">Boys</option>
                            <option value="girls">Girls</option>
                        </select>
                        {#if $errors.gender}<span class="text-red-500 text-sm mt-1">{$errors.gender}</span>{/if}
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Field Requirements -->
        <div class="detail-card-content">
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <h3 class="detail-card-label">Field Requirements</h3>
                </div>

                <div class="space-y-4">
                    <div>
                        <label for="weekly_trainings" class="detail-card-label">Weekly Trainings</label>
                        <input
                            type="number"
                            id="weekly_trainings"
                            name="weekly_trainings"
                            bind:value={$form.weekly_trainings}
                            min="1"
                            max="5"
                            class="form-input-sm"
                            required
                        />
                        {#if $errors.weekly_trainings}
                            <span class="text-red-500 text-sm mt-1">{$errors.weekly_trainings}</span>
                        {/if}
                    </div>

                    <div>
                        <label for="minimum_field_size" class="detail-card-label">Minimum Field Size</label>
                        <select 
                            id="minimum_field_size" 
                            name="minimum_field_size"
                            bind:value={$form.minimum_field_size}
                            class="form-input-sm"
                        >
                            <option value={125}>125</option>
                            <option value={250}>250</option>
                            <option value={500}>500</option>
                            <option value={1000}>1000</option>
                        </select>
                        {#if $errors.minimum_field_size}<span class="text-red-500 text-sm mt-1">{$errors.minimum_field_size}</span>{/if}
                    </div>

                    <div>
                        <label for="preferred_field_size" class="detail-card-label">Preferred Field Size</label>
                        <select 
                            id="preferred_field_size" 
                            name="preferred_field_size"
                            bind:value={$form.preferred_field_size}
                            class="form-input-sm"
                        >
                            <option value="">None</option>
                            <option value={125}>125</option>
                            <option value={250}>250</option>
                            <option value={500}>500</option>
                            <option value={1000}>1000</option>
                        </select>
                        {#if $errors.preferred_field_size}<span class="text-red-500 text-sm mt-1">{$errors.preferred_field_size}</span>{/if}
                    </div>

                    <div>
                        <label for="level" class="detail-card-label">Team Level (1-5)</label>
                        <input 
                            type="number" 
                            id="level" 
                            name="level"
                            bind:value={$form.level}
                            min="1"
                            max="5"
                            class="form-input-sm"
                        />
                        {#if $errors.level}<span class="text-red-500 text-sm mt-1">{$errors.level}</span>{/if}
                    </div>

                    <div class="pt-2">
                        <label class="inline-flex items-center">
                            <input 
                                type="checkbox" 
                                name="is_academy"
                                bind:checked={$form.is_academy}
                                class="rounded border-sage-300 text-mint-600 shadow-sm focus:border-mint-500 focus:ring-mint-500"
                            />
                            <span class="ml-2 text-sm text-sage-700">Academy Team</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-span-2 field-actions">
            <button 
                type="submit"
                class="btn-primary"
            >
                Create Team
            </button>
        </div>
    </form>
</div>
