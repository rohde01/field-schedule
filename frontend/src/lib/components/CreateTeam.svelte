<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import type { SuperValidated } from 'sveltekit-superforms';
    import type { TeamSchema } from '$lib/schemas/team';
    import { page } from '$app/stores';
    import { dropdownState } from '$stores/teamDropdownState';
    import { addTeam } from '$stores/teams';

    let { form: formData } = $props<{ form: SuperValidated<TeamSchema> }>();
    let formElement: HTMLFormElement;
    let isNameEditMode = $state(true);
    let isYearEditMode = $state(true);
    let isGenderEditMode = $state(true);
    let isLevelEditMode = $state(true);
    let isAcademyEditMode = $state(true);
    let isWeeklyTrainingsEditMode = $state(true);
    let isMinFieldSizeEditMode = $state(true);
    let isPrefFieldSizeEditMode = $state(true);
    let isFieldSizeEditMode = $state(true);

    function handleNameInput(event: KeyboardEvent) {
        if (event.key === 'Enter' && $form.name) {
            isNameEditMode = false;
            event.preventDefault();
        }
    }

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
    <div class="relative">
        {#if !isNameEditMode && $form.name}
            <div class="flex items-center space-x-2">
                <h2 class="detail-card-title my-0">{$form.name}</h2>
                <button
                    type="button"
                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                    onclick={() => isNameEditMode = true}
                    aria-label="Edit team name"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                </button>
            </div>
        {/if}
    </div>

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
                    <div class="{!isNameEditMode ? 'hidden' : ''}">
                        <label for="name" class="detail-card-label">Team Name</label>
                        <div class="relative">
                            <input 
                                type="text" 
                                id="name" 
                                name="name"
                                bind:value={$form.name}
                                class="form-input-sm"
                                onblur={() => $form.name && (isNameEditMode = false)}
                                onkeydown={handleNameInput}
                            />
                        </div>
                        {#if $errors.name}<span class="text-red-500 text-sm mt-1">{$errors.name}</span>{/if}
                    </div>

                    <div>
                        <label for="year" class="detail-card-label">Year (e.g., U13)</label>
                        <div class="{!isYearEditMode ? 'hidden' : ''}">
                            <div class="relative">
                                <input 
                                    type="text" 
                                    id="year" 
                                    name="year"
                                    bind:value={$form.year}
                                    placeholder="U13"
                                    class="form-input-sm"
                                    onblur={() => {
                                        if ($form.year) {
                                            isYearEditMode = false;
                                        }
                                    }}
                                />
                            </div>
                        </div>
                        {#if !isYearEditMode && $form.year}
                            <div class="flex items-center space-x-2">
                                <p class="detail-card-value">{$form.year}</p>
                                <button
                                    type="button"
                                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                                    onclick={() => isYearEditMode = true}
                                    aria-label="Edit year"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                            </div>
                        {/if}
                        {#if $errors.year}<span class="text-red-500 text-sm mt-1">{$errors.year}</span>{/if}
                    </div>

                    <div>
                        <label for="gender" class="detail-card-label">Gender</label>
                        <div class="{!isGenderEditMode ? 'hidden' : ''}">
                            <select 
                                id="gender" 
                                name="gender"
                                bind:value={$form.gender}
                                class="form-input-sm"
                                onblur={() => {
                                    if ($form.gender) {
                                        isGenderEditMode = false;
                                    }
                                }}
                            >
                                <option value="boys">Boys</option>
                                <option value="girls">Girls</option>
                            </select>
                        </div>
                        {#if !isGenderEditMode && $form.gender}
                            <div class="flex items-center space-x-2">
                                <p class="detail-card-value">{$form.gender}</p>
                                <button
                                    type="button"
                                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                                    onclick={() => isGenderEditMode = true}
                                    aria-label="Edit gender"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                            </div>
                        {/if}
                        {#if $errors.gender}<span class="text-red-500 text-sm mt-1">{$errors.gender}</span>{/if}
                    </div>

                    <div>
                        <label for="level" class="detail-card-label">Team Level (1-5)</label>
                        <div class="{!isLevelEditMode ? 'hidden' : ''}">
                            <input 
                                type="number" 
                                id="level" 
                                name="level"
                                bind:value={$form.level}
                                min="1"
                                max="5"
                                class="form-input-sm"
                                onblur={() => {
                                    if ($form.level) {
                                        isLevelEditMode = false;
                                    }
                                }}
                            />
                        </div>
                        {#if !isLevelEditMode && $form.level}
                            <div class="flex items-center space-x-2">
                                <p class="detail-card-value">{$form.level}</p>
                                <button
                                    type="button"
                                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                                    onclick={() => isLevelEditMode = true}
                                    aria-label="Edit level"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                            </div>
                        {/if}
                        {#if $errors.level}<span class="text-red-500 text-sm mt-1">{$errors.level}</span>{/if}
                    </div>

                    <div class="pt-2">
                        <div class="{!isAcademyEditMode ? 'hidden' : ''}">
                            <label class="inline-flex items-center">
                                <input 
                                    type="checkbox" 
                                    name="is_academy"
                                    bind:checked={$form.is_academy}
                                    class="rounded border-sage-300 text-mint-600 shadow-sm focus:border-mint-500 focus:ring-mint-500"
                                    onblur={() => {
                                        isAcademyEditMode = false;
                                    }}
                                />
                                <span class="ml-2 text-sm text-sage-700">Academy Team</span>
                            </label>
                        </div>
                        {#if !isAcademyEditMode}
                            <div class="flex items-center space-x-2">
                                <p class="detail-card-value">{$form.is_academy ? 'Yes' : 'No'}</p>
                                <button
                                    type="button"
                                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                                    onclick={() => isAcademyEditMode = true}
                                    aria-label="Edit academy status"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Training Requirements -->
        <div class="detail-card-content">
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <h3 class="detail-card-label">Training Requirements</h3>
                </div>

                <div class="space-y-4">
                    <div>
                        <label for="weekly_trainings" class="detail-card-label">Weekly Trainings</label>
                        <div class="{!isWeeklyTrainingsEditMode ? 'hidden' : ''}">
                            <input
                                type="number"
                                id="weekly_trainings"
                                name="weekly_trainings"
                                bind:value={$form.weekly_trainings}
                                min="1"
                                max="5"
                                class="form-input-sm"
                                required
                                onblur={() => {
                                    if ($form.weekly_trainings) {
                                        isWeeklyTrainingsEditMode = false;
                                    }
                                }}
                            />
                        </div>
                        {#if !isWeeklyTrainingsEditMode && $form.weekly_trainings}
                            <div class="flex items-center space-x-2">
                                <p class="detail-card-value">{$form.weekly_trainings}</p>
                                <button
                                    type="button"
                                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                                    onclick={() => isWeeklyTrainingsEditMode = true}
                                    aria-label="Edit weekly trainings"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                            </div>
                        {/if}
                        {#if $errors.weekly_trainings}
                            <span class="text-red-500 text-sm mt-1">{$errors.weekly_trainings}</span>
                        {/if}
                    </div>

                    <div>
                        <label for="minimum_field_size" class="detail-card-label">Required Field Size</label>
                        <div class="{!isMinFieldSizeEditMode ? 'hidden' : ''}">
                            <select 
                                id="minimum_field_size" 
                                name="minimum_field_size"
                                bind:value={$form.minimum_field_size}
                                class="form-input-sm"
                                onblur={() => {
                                    if ($form.minimum_field_size) {
                                        isMinFieldSizeEditMode = false;
                                    }
                                }}
                            >
                                <option value={125}>125</option>
                                <option value={250}>250</option>
                                <option value={500}>500</option>
                                <option value={1000}>1000</option>
                            </select>
                        </div>
                        {#if !isMinFieldSizeEditMode && $form.minimum_field_size}
                            <div class="flex items-center space-x-2">
                                <span class="field-tag">{$form.minimum_field_size}</span>
                                <button
                                    type="button"
                                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                                    onclick={() => isMinFieldSizeEditMode = true}
                                    aria-label="Edit field size"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                            </div>
                        {/if}
                        {#if $errors.minimum_field_size}
                            <span class="text-red-500 text-sm mt-1">{$errors.minimum_field_size}</span>
                        {/if}
                    </div>

                    <div>
                        <label for="preferred_field_size" class="detail-card-label">Preferred Field Size</label>
                        <div class="{!isPrefFieldSizeEditMode ? 'hidden' : ''}">
                            <select 
                                id="preferred_field_size" 
                                name="preferred_field_size"
                                bind:value={$form.preferred_field_size}
                                class="form-input-sm"
                                onblur={() => {
                                    if ($form.preferred_field_size) {
                                        isPrefFieldSizeEditMode = false;
                                    }
                                }}
                            >
                                <option value="">None</option>
                                <option value={125}>125</option>
                                <option value={250}>250</option>
                                <option value={500}>500</option>
                                <option value={1000}>1000</option>
                            </select>
                        </div>
                        {#if !isPrefFieldSizeEditMode && $form.preferred_field_size}
                            <div class="flex items-center space-x-2">
                                <span class="field-tag">{$form.preferred_field_size}</span>
                                <button
                                    type="button"
                                    class="text-gray-500 hover:text-gray-700 flex-shrink-0 flex items-center"
                                    onclick={() => isPrefFieldSizeEditMode = true}
                                    aria-label="Edit field size"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                            </div>
                        {/if}
                        {#if $errors.preferred_field_size}
                            <span class="text-red-500 text-sm mt-1">{$errors.preferred_field_size}</span>
                        {/if}
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
