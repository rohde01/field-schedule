<script lang="ts">
    import { Button, CloseButton, Heading, Input, Label, Select, Textarea, Toggle, Helper } from 'flowbite-svelte';
    import { CloseOutline } from 'flowbite-svelte-icons';
    import type { SuperForm } from 'sveltekit-superforms';
  
    let { hidden = $bindable(true), title = 'Add new facility', form }: { 
        hidden: boolean; 
        title: string; 
        form: SuperForm<any, any>
    } = $props();
    
    const { form: formData, enhance, errors, message } = form;
</script>
  
<Heading tag="h5" class="mb-6 text-sm font-semibold uppercase">{title}</Heading>
<CloseButton onclick={() => (hidden = true)} class="absolute top-2.5 right-2.5 text-gray-400 hover:text-black dark:text-white" />
  
<form method="POST" action="?/create" use:enhance id="facility-form">
  <input type="hidden" name="club_id" bind:value={$formData.club_id} />
  <div class="space-y-4">
    <Label class="space-y-2">
      <span>Name</span>
      <Input name="name" bind:value={$formData.name} class="border font-normal outline-none" placeholder="Type facility name" required />
      {#if $errors.name}
        <Helper class="mt-2" color="red">{$errors.name}</Helper>
      {/if}
    </Label>

    <Label class="space-y-2">
      <span>Address</span>
      <Input name="address" bind:value={$formData.address} class="border font-normal outline-none" placeholder="Type facility address" />
      {#if $errors.address}
        <Helper class="mt-2" color="red">{$errors.address}</Helper>
      {/if}
    </Label>
  
    <Label class="space-y-2">
      <span>Description</span>
      <Textarea name="description" bind:value={$formData.description} rows={4} placeholder="Enter facility description here" class="border-gray-300 font-normal outline-none"></Textarea>
      {#if $errors.description}
        <Helper class="mt-2" color="red">{$errors.description}</Helper>
      {/if}
    </Label>

    <Label class="flex items-center space-x-2">
      <span>Primary Facility</span>
      <Toggle bind:checked={$formData.is_primary} name="is_primary" />
      {#if $errors.is_primary}
        <Helper class="mt-2" color="red">{$errors.is_primary}</Helper>
      {/if}
    </Label>
  
    {#if $message}
      <div class="mt-4 text-sm text-red-600">{$message}</div>
    {/if}
  
    <div class="bottom-0 left-0 flex w-full justify-center space-x-4 pb-4 md:absolute md:px-4">
      <Button type="submit" form="facility-form" class="w-full">Add facility</Button>
      <Button color="alternative" class="w-full" onclick={() => (hidden = true)}>
        <CloseOutline />
        Cancel
      </Button>
    </div>
  </div>
</form>
