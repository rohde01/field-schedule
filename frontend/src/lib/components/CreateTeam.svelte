<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import type { SuperValidated } from 'sveltekit-superforms';
    import type { z } from 'zod';
    import { teamSchema } from '$lib/schemas/team';
    import { page } from '$app/stores';
    import { dropdownState } from '$stores/teamDropdownState';
    import { addTeam } from '$stores/teams';
    import EditableField from './EditableField.svelte';

    type TeamFormData = SuperValidated<z.infer<typeof teamSchema>>;

    let { form: formData } = $props<{ form: TeamFormData }>();
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

    const yearOptions = Array.from({ length: 21 }, (_, i) => ({
        value: `U${i + 4}`,
        label: `U${i + 4}`
    }));

    const genderOptions = [
        { value: 'boys', label: 'Boys' },
        { value: 'girls', label: 'Girls' }
    ];

    const levelOptions = Array.from({ length: 5 }, (_, i) => ({
        value: i + 1,
        label: `Level ${i + 1}`
    }));

    const fieldSizeOptions = [
        { value: 125, label: '125' },
        { value: 250, label: '250' },
        { value: 500, label: '500' },
        { value: 1000, label: '1000' }
    ];

    const weeklyTrainingOptions = Array.from({ length: 5 }, (_, i) => ({
        value: i + 1,
        label: `${i + 1}`
    }));
</script>

<div class="detail-card">
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
        class="space-y-6"
    >
        <EditableField
            bind:form={$form}
            errors={$errors}
            name="name"
            label="Team Name"
            type="text"
            required={true}
            placeholder="Enter team name"
            view_mode_style="title"
            hide_label_in_view={true}
        />

        <div class="detail-card-grid">
            <div class="detail-card-content">
                <div class="space-y-4">
                    <div class="space-y-4">
                        <EditableField
                            bind:form={$form}
                            errors={$errors}
                            name="year"
                            label="Year"
                            type="select"
                            options={yearOptions}
                            required={true}
                            placeholder="Select year group"
                            view_mode_style="normal"
                        />

                        <EditableField
                            bind:form={$form}
                            errors={$errors}
                            name="gender"
                            label="Gender"
                            type="select"
                            options={genderOptions}
                            required={true}
                            placeholder="Select gender"
                            view_mode_style="normal"
                        />

                        <EditableField
                            bind:form={$form}
                            errors={$errors}
                            name="level"
                            label="Level"
                            type="select"
                            options={levelOptions}
                            required={true}
                            placeholder="Select level"
                            view_mode_style="normal"
                        />

                        <EditableField
                            bind:form={$form}
                            errors={$errors}
                            name="is_academy"
                            label="Academy Team"
                            type="checkbox"
                            placeholder=""
                            view_mode_style="normal"
                        />
                    </div>
                </div>
            </div>

            <div class="detail-card-content">
                <div class="space-y-4">
                    <div class="space-y-4">
                        <EditableField
                            bind:form={$form}
                            errors={$errors}
                            name="weekly_trainings"
                            label="Weekly Trainings"
                            type="select"
                            options={weeklyTrainingOptions}
                            required={true}
                            placeholder="Select number of trainings"
                            view_mode_style="normal"
                        />

                        <EditableField
                            bind:form={$form}
                            errors={$errors}
                            name="minimum_field_size"
                            label="Minimum Field Size"
                            type="select"
                            options={fieldSizeOptions}
                            required={true}
                            placeholder="Select minimum field size"
                            view_mode_style="pill"
                        />

                        <EditableField
                            bind:form={$form}
                            errors={$errors}
                            name="preferred_field_size"
                            label="Preferred Field Size"
                            type="select"
                            options={fieldSizeOptions}
                            placeholder="Select preferred field size"
                            view_mode_style="pill"
                        />
                    </div>
                </div>
            </div>

            <div class="col-span-2 field-actions">
                <button 
                    type="submit"
                    class="btn btn-primary"
                >
                    Create Team
                </button>
            </div>
        </div>
    </form>
</div>
