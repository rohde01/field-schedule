<script lang="ts">
    import type { GenerateScheduleRequest } from '$lib/schemas/schedule';
    import type { Writable } from 'svelte/store';
    import type { SuperForm, ValidationErrors } from 'sveltekit-superforms';

    let { form, enhance, errors } = $props<{ 
        form: Writable<GenerateScheduleRequest>,
        enhance: Function,
        errors: Writable<ValidationErrors<GenerateScheduleRequest>>
    }>();

    let formElement: HTMLFormElement;

    $form.is_active = true;
</script>

<form 
    method="POST" 
    action="?/createSchedule" 
    bind:this={formElement}
    use:enhance
    class="mt-4"
>
    <div class="flex justify-end">
        <button 
            type="submit"
                    class="btn btn-primary"
        >
            Create Schedule
        </button>
    </div>
</form>
