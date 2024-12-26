<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import type { SuperValidated } from 'sveltekit-superforms';
    import type { z } from 'zod';
    import EditableField from './EditableField.svelte';
    import { generateScheduleRequestSchema } from '$lib/schemas/schedule';
    import { dropdownState } from '$stores/teamDropdownState';
    import { selectedTeamIds } from '$stores/scheduleFormState';
    import { page } from '$app/stores';


    type ScheduleFormData = SuperValidated<z.infer<typeof generateScheduleRequestSchema>>;

    let { form: formData } = $props<{ form: ScheduleFormData }>();
    let formElement: HTMLFormElement;

    const { form, errors, enhance, message } = superForm(formData, {
        taintedMessage: null,
        onUpdate: ({ form }) => {
            console.log('Form data being submitted:', form.data);
        },
        onResult: ({ result }) => {
            console.log('Form submission result:', result);
            if (result.type === 'success') {
                dropdownState.update(state => ({
                    ...state,
                    showCreateSchedule: false
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
            {form}
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

