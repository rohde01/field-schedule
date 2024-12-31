<script lang="ts">
    import type { GenerateScheduleRequest } from '$lib/schemas/schedule';
    import type { Writable } from 'svelte/store';
    import type { SuperForm, SuperValidated } from 'sveltekit-superforms';
    import type { ZodValidation } from 'sveltekit-superforms/adapters';
    import type { z } from 'zod';

    let { form, enhance, errors } = $props<{ 
        form: Writable<GenerateScheduleRequest>,
        enhance: Function,
        errors: Writable<SuperValidated<GenerateScheduleRequest, ZodValidation<z.ZodObject<any>>>['errors']>
    }>();

    let formElement: HTMLFormElement;
    let showErrorModal = $state(false);

    $effect(() => {
        if ($errors?.team_ids?._errors) {
            showErrorModal = true;
        } else {
            showErrorModal = false;
        }
    });

    function closeErrorModal() {
        showErrorModal = false;
    }

    $form.is_active = true;
</script>

<form 
    method="POST" 
    action="?/createSchedule" 
    bind:this={formElement}
    use:enhance
    class="mt-4"
>
    <div class="mt-4">
        {#if $errors?.team_ids?._errors}
            <p class="text-red-500 text-sm mb-2">{$errors.team_ids._errors[0]}</p>
        {/if}
        <div class="flex justify-end">
            <button 
                type="submit"
                class="btn btn-primary"
            >
                Create Schedule
            </button>
        </div>
    </div>
</form>

{#if showErrorModal}
    <div class="modal-overlay">
        <div class="modal-container">
            <h3 class="modal-title">Schedule Creation Error</h3>
            <p class="modal-description">{$errors.team_ids._errors[0]}</p>
            <div class="modal-actions">
                <button 
                    class="btn btn-secondary"
                    onclick={closeErrorModal}
                >
                    Close
                </button>
            </div>
        </div>
    </div>
{/if}
