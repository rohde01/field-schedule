<script lang="ts">
  import { Button, Input, Label, Modal, Helper } from 'flowbite-svelte';
  import type { SuperForm } from 'sveltekit-superforms';
  
  let { open = $bindable(true), data = {}, form }: { 
    open: boolean; 
    data: any; 
    form: SuperForm<any, any>
  } = $props();

  const { form: formData, enhance, errors, message } = form;
</script>

<Modal bind:open title="Complete Your Profile" size="md" class="m-4">
  <!-- Modal body -->
  <div class="space-y-6 p-0">
    <form method="POST" action="?/updateUser" use:enhance id="name-form">
      <div class="grid grid-cols-6 gap-6">
        <Label class="col-span-6 space-y-2 sm:col-span-6">
          <span>First Name</span>
          <Input name="first_name" id="first_name" class="border outline-none" placeholder="First name" 
            bind:value={$formData.first_name} required />
          {#if $errors.first_name}
            <Helper class="mt-2" color="red">{$errors.first_name}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-6">
          <span>Last Name</span>
          <Input name="last_name" id="last_name" class="border outline-none" placeholder="Last name" 
            bind:value={$formData.last_name} required />
          {#if $errors.last_name}
            <Helper class="mt-2" color="red">{$errors.last_name}</Helper>
          {/if}
        </Label>
      </div>
      {#if $message}
        <div class="mt-4 text-sm text-red-600">{$message}</div>
      {/if}
    </form>
  </div>

  <!-- Modal footer -->
  <svelte:fragment slot="footer">
    <Button type="submit" form="name-form">
      Save Profile
    </Button>
  </svelte:fragment>
</Modal>