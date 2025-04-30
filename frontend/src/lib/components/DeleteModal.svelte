<script lang="ts">
    import { Button, Modal } from 'flowbite-svelte';
    import { ExclamationCircleOutline } from 'flowbite-svelte-icons';
    import type { DeleteModalProps } from '$lib/types/types';
    import type { SuperForm } from 'sveltekit-superforms';
    import type { Snippet } from 'svelte';

    let { open = $bindable(true), title = 'Are you sure you want to delete this?', yes = "Yes, I'm sure", no = 'No, cancel', form, actionName = '', children }: DeleteModalProps & { form: SuperForm<any, any>, children: Snippet } = $props();

    const { enhance } = form;
</script>

<Modal bind:open size="sm">
    <ExclamationCircleOutline class="mx-auto mt-8 mb-4 h-10 w-10 text-red-600" />

    <h3 class="mb-6 text-center text-lg text-gray-500 dark:text-gray-300">{title}</h3>

    <form method="POST" action={actionName ? `?/${actionName}` : undefined} use:enhance>
        {@render children()}
        <div class="flex items-center justify-center">
            <Button type="submit" color="red" class="mr-2">{yes}</Button>
            <Button type="button" color="alternative" on:click={() => (open = false)}>{no}</Button>
        </div>
    </form>
</Modal>

