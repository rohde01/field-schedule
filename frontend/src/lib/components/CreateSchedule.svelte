<script lang="ts">
    import type { GenerateScheduleRequest } from '$lib/schemas/schedule';
    import type { Writable } from 'svelte/store';

    let { form, enhance } = $props<{ 
        form: Writable<GenerateScheduleRequest>,
        enhance: Function
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
