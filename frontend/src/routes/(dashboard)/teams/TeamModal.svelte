<script lang="ts">
  import { Button, Input, Checkbox, Label, Modal, Select, Helper } from 'flowbite-svelte';
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

  const { form: formData, enhance, errors, message } = form;
  
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
        <Label class="col-span-6 space-y-2 sm:col-span-3 flex items-center">
          <Checkbox name="is_academy" bind:checked={$formData.is_academy} /> <span class="ms-2">Academy</span>
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Min Field Size</span>
          <Select name="minimum_field_size" id="minimum_field_size" bind:value={$formData.minimum_field_size} required>
            <option value={125}>125</option>
            <option value={250}>250</option>
            <option value={500}>500</option>
            <option value={1000}>1000</option>
          </Select>
          {#if $errors.minimum_field_size}
            <Helper class="mt-2" color="red">{$errors.minimum_field_size}</Helper>
          {/if}
        </Label>
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Preferred Field Size</span>
          <Select name="preferred_field_size" id="preferred_field_size" bind:value={$formData.preferred_field_size}>
            <option value={null}>None</option>
            <option value={125}>125</option>
            <option value={250}>250</option>
            <option value={500}>500</option>
            <option value={1000}>1000</option>
          </Select>
          {#if $errors.preferred_field_size}
            <Helper class="mt-2" color="red">{$errors.preferred_field_size}</Helper>
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
        <Label class="col-span-6 space-y-2 sm:col-span-3">
          <span>Weekly Trainings</span>
          <Input name="weekly_trainings" id="weekly_trainings" type="number" min="1" max="7" 
            bind:value={$formData.weekly_trainings} class="border outline-none" required />
          {#if $errors.weekly_trainings}
            <Helper class="mt-2" color="red">{$errors.weekly_trainings}</Helper>
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
    <Button type="submit" form="team-form">
      {Object.keys(data).length ? 'Save all' : 'Add team'}
    </Button>
  </svelte:fragment>
</Modal>

