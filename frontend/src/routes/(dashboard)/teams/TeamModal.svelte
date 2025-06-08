<script lang="ts">
  import { Button, Input, Checkbox, Label, Modal, Select, Helper, Spinner } from 'flowbite-svelte';
  import type { Team } from '$lib/schemas/team';
  import type { SuperForm } from 'sveltekit-superforms';
  import { onMount } from 'svelte';
  
  let { 
    open = $bindable(true), 
    data = {} as Team, 
    form,
    actionPath = '?/create'
  }: { 
    open: boolean; 
    data: Team; 
    form: SuperForm<any, any>;
    actionPath: string;
  } = $props();

  const { form: formData, enhance, errors, message, submitting } = form;
  let saving = $state(false);
  
  $effect(() => {
    saving = $submitting;
  });
  
  $effect(() => {
    if (open && data && Object.keys(data).length > 0) {
      formData.set(data);
    }
  });
</script>

<Modal bind:open title={Object.keys(data).length ? 'Edit team' : 'Add new team'} size="md" class="m-4">
  <!-- Modal body -->
  <div class="space-y-6 p-0">
    <form method="POST" action={actionPath} use:enhance id="team-form">
      {#if data.team_id}
        <input type="hidden" name="team_id" bind:value={$formData.team_id} />
      {/if}
      <div class="grid grid-cols-6 gap-6">
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Name</span>
          <Input name="name" id="name" class="border outline-none" placeholder="Team name" 
            bind:value={$formData.name} required />
          {#if $errors.name}
            <Helper class="mt-2" color="red">{$errors.name}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Year</span>
          <Input name="year" id="year" class="border outline-none" placeholder="e.g. U10" 
            bind:value={$formData.year} required />
          {#if $errors.year}
            <Helper class="mt-2" color="red">{$errors.year}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Gender</span>
          <Select name="gender" id="gender" bind:value={$formData.gender} required>
            <option value="boys">Boys</option>
            <option value="girls">Girls</option>
          </Select>
          {#if $errors.gender}
            <Helper class="mt-2" color="red">{$errors.gender}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Weekly Trainings</span>
          <Input name="weekly_trainings" id="weekly_trainings" type="number" min="1" max="7" 
            bind:value={$formData.weekly_trainings} class="border outline-none" required />
          {#if $errors.weekly_trainings}
            <Helper class="mt-2" color="red">{$errors.weekly_trainings}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Field Size</span>
          <Select name="minimum_field_size" id="minimum_field_size" bind:value={$formData.minimum_field_size} required>
            <option value={125}>3v3, Half 5v5, Quarter 8v8</option>
            <option value={250}>5v5, Half 8v8, Quarter 11v11</option>
            <option value={500}>8v8, Half 11v11</option>
            <option value={1000}>11v11</option>
          </Select>
          {#if $errors.minimum_field_size}
            <Helper class="mt-2" color="red">{$errors.minimum_field_size}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Level</span>
          <Input name="level" id="level" type="number" min="1" max="5" bind:value={$formData.level} class="border outline-none" required />
          {#if $errors.level}
            <Helper class="mt-2" color="red">{$errors.level}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3 flex items-center">
          <Checkbox name="is_active" bind:checked={$formData.is_active} /> <span class="ms-2">Active</span>
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3 flex items-center">
          <Checkbox name="is_academy" bind:checked={$formData.is_academy} /> <span class="ms-2">Academy</span>
        </Label>
      </div>
      {#if $message}
        <div class="mt-4 text-sm text-red-600">{$message}</div>
      {/if}
    </form>
  </div>

  <!-- Modal footer -->
  <svelte:fragment slot="footer">
    <Button type="submit" form="team-form" disabled={saving}>
      {#if saving}
        <Spinner class="me-3" size="4" color="white" />Saving...
      {:else}
        {Object.keys(data).length ? 'Save all' : 'Add team'}
      {/if}
    </Button>
  </svelte:fragment>
</Modal>

