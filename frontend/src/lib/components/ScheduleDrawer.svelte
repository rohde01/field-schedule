<script lang="ts">
    import { Button, CloseButton, Heading, Input, Label, Textarea, Toggle, Helper, Spinner } from 'flowbite-svelte';
    import { CloseOutline } from 'flowbite-svelte-icons';
    import type { SuperForm } from 'sveltekit-superforms';
    import ToastMessage from '$lib/components/Toast.svelte';
  
    let { hidden = $bindable(true), title = 'Update schedule', form }: { 
        hidden: boolean; 
        title: string; 
        form: SuperForm<any, any>
    } = $props();
    
    const { form: formData, enhance, errors, message, submitting } = form;
    let saving = $state(false);
    
    $effect(() => {
      saving = $submitting;
    });
    
</script>
  
<Heading tag="h5" class="mb-6 text-sm font-semibold uppercase">{title}</Heading>
<CloseButton onclick={() => (hidden = true)} class="absolute top-2.5 right-2.5 text-gray-400 hover:text-black dark:text-white" />
  
<form method="POST" action="?/updateSchedule" use:enhance id="schedule-form">
  <input type="hidden" name="schedule_id" bind:value={$formData.schedule_id} />
  <div class="space-y-4">
    <Label class="space-y-2">
      <span>Name</span>
      <Input name="name" bind:value={$formData.name} class="border font-normal outline-none" placeholder="Schedule name" required />
      {#if $errors.name}
        <Helper class="mt-2" color="red">{$errors.name}</Helper>
      {/if}
    </Label>

    <Label class="space-y-2">
      <span>Description</span>
      <Textarea name="description" bind:value={$formData.description} rows={4} placeholder="Enter description" class="border-gray-300 font-normal outline-none" />
      {#if $errors.description}
        <Helper class="mt-2" color="red">{$errors.description}</Helper>
      {/if}
    </Label>

    <Label class="space-y-2">
      <span>Active From</span>
      <Input type="date" name="active_from" bind:value={$formData.active_from} class="border font-normal outline-none" />
      {#if $errors.active_from}
        <Helper class="mt-2" color="red">{$errors.active_from}</Helper>
      {/if}
    </Label>
    <Label class="space-y-2">
      <span>Active Until</span>
      <Input type="date" name="active_until" bind:value={$formData.active_until} class="border font-normal outline-none" />
      {#if $errors.active_until}
        <Helper class="mt-2" color="red">{$errors.active_until}</Helper>
      {/if}
    </Label>

    {#if $message}
      <div class="mt-4 text-sm text-red-600">{$message}</div>
    {/if}

    <div class="bottom-0 left-0 flex w-full justify-center space-x-4 pb-4 md:absolute md:px-4">
      <Button type="submit" form="schedule-form" class="w-full" disabled={saving}>
        {#if saving}
          <Spinner class="me-3" size="4" color="white" />Saving...
        {:else}
          Update Schedule
        {/if}
      </Button>
      <Button color="alternative" class="w-full" onclick={() => (hidden = true)}>
        <CloseOutline /> Cancel
      </Button>
    </div>
  </div>
</form>
