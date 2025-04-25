<script lang="ts">
  import { Button, Input, Label, Modal, Helper } from 'flowbite-svelte';
  import type { SuperForm } from 'sveltekit-superforms';
  import type { CreateClub } from '$lib/schemas/club';
  
  let { open = $bindable(true), data = {}, form }: { 
    open: boolean; 
    data: Partial<CreateClub>; 
    form: SuperForm<any, any>
  } = $props();

  const { form: formData, enhance, errors, message } = form;
</script>

<Modal bind:open title="Create Your Club" size="md" autoclose={false} class="m-4">
  <div class="space-y-6 p-0">
    <p class="text-sm text-gray-500 dark:text-gray-400">
      Create a club to manage your teams, facilities, and schedules.
    </p>
    <form method="POST" action="?/createClub" use:enhance id="club-form">
      <div class="grid grid-cols-6 gap-6">
        <Label class="col-span-6 space-y-2">
          <span>Club Name</span>
          <Input name="name" id="name" class="border outline-none" placeholder="Club name" 
            bind:value={$formData.name} required />
          {#if $errors.name}
            <Helper class="mt-2" color="red">{$errors.name}</Helper>
          {/if}
        </Label>
      </div>
      {#if $message}
        <div class="mt-4 text-sm text-red-600">{$message}</div>
      {/if}
    </form>
  </div>

  <svelte:fragment slot="footer">
    <Button type="submit" form="club-form">Create Club</Button>
  </svelte:fragment>
</Modal>