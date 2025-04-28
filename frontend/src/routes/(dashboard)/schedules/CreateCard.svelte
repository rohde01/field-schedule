<script lang="ts">
    import { Heading, Button } from 'flowbite-svelte';
    import { Card } from 'flowbite-svelte';
    import type { PlaygroundProps } from '$lib/types/types';
    import { facilities } from '$lib/stores/facilities';
    import { schedules, selectedSchedule, IsCreating } from '$lib/stores/schedules';
    import { Label, Select, Textarea, Input, Helper } from 'flowbite-svelte';
    import { get } from 'svelte/store';
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createScheduleSchema } from '$lib/schemas/schedule';
    import { page } from '$app/stores';
  
    let { breadcrumb, title = 'Creating new schedule' }: PlaygroundProps = $props();

    // Initialize superForm
    const { form, errors, enhance, submitting, message } = superForm($page.data.createForm, {
      validators: zodClient(createScheduleSchema),
      resetForm: false,
      onResult: ({ result }) => {
        if (result.type === 'success') {
          IsCreating.set(false);
        }
      }
    });

    // Update form data from selectedSchedule whenever it changes
    $effect(() => {
      if ($selectedSchedule) {
        form.update((formData) => ({
          ...formData,
          name: $selectedSchedule.name || '',
          facility_id: $selectedSchedule.facility_id || null,
          description: $selectedSchedule.description || null,
          club_id: $selectedSchedule.club_id || $page.data.user?.club_id || 0
        }));
      }
    });

    // Update handlers for form fields
    function updateSelectedSchedule(fieldName: string, value: any) {
      if (!$selectedSchedule) return;
      
      const updatedSchedule = { 
        ...$selectedSchedule, 
        [fieldName]: value 
      };
      
      schedules.update(list => 
        list.map(s => s.schedule_id === updatedSchedule.schedule_id ? updatedSchedule : s)
      );
      
      selectedSchedule.set(updatedSchedule);
    }
  </script>
  
  <main>
    <div class="grid grid-cols-1 pt-2 xl:grid-cols-3 xl:gap-4 xl:px-0 dark:bg-gray-900">
      <div class="col-span-full mb-4 xl:mb-2">
        {#if breadcrumb}
          {@render breadcrumb()}
        {/if}
        <Heading tag="h1" class="text-xl font-semibold sm:text-2xl">{title}</Heading>
      </div>
      <div class="col-span-full xl:col-auto">
        <Card size="xl" class="mb-4 min-h-[20rem] w-full space-y-6 p-4 2xl:col-span-2">
          <form method="POST" action="?/createSchedule" use:enhance>
            <div class="space-y-4">
              <input type="hidden" name="club_id" bind:value={$form.club_id}>
              
              <Label class="space-y-2">
                <span>Name</span>
                <Input 
                  id="name" 
                  name="name" 
                  type="text" 
                  value={$selectedSchedule?.name || ''} 
                  on:input={(e) => {
                    const target = e.target as HTMLInputElement;
                    updateSelectedSchedule('name', target.value);
                  }}
                  required 
                />
                {#if $errors.name}
                  <Helper class="mt-2" color="red">{$errors.name}</Helper>
                {/if}
              </Label>

              <Label class="space-y-2">
                <span>Facility</span>
                <Select 
                  id="facility" 
                  name="facility_id" 
                  value={$selectedSchedule?.facility_id || ''} 
                  on:change={(e) => {
                    const target = e.target as HTMLSelectElement;
                    updateSelectedSchedule('facility_id', target.value ? parseInt(target.value) : null);
                  }}
                  required
                >
                  <option value="">Select facility</option>
                  {#each $facilities as f}
                    <option value={f.facility_id}>{f.name}</option>
                  {/each}
                </Select>
                {#if $errors.facility_id}
                  <Helper class="mt-2" color="red">{$errors.facility_id}</Helper>
                {/if}
              </Label>

              <Label class="space-y-2">
                <span>Description</span>
                <Textarea 
                  id="description" 
                  name="description" 
                  rows={4} 
                  placeholder="Description" 
                  value={$selectedSchedule?.description || ''}
                  on:input={(e) => {
                    const target = e.target as HTMLTextAreaElement;
                    updateSelectedSchedule('description', target.value);
                  }}
                ></Textarea>
                {#if $errors.description}
                  <Helper class="mt-2" color="red">{$errors.description}</Helper>
                {/if}
              </Label>

              <div class="flex justify-end pt-4">
                <Button type="submit" disabled={$submitting}>
                  {$submitting ? 'Saving...' : 'Save Schedule'}
                </Button>
              </div>
              
              {#if $message}
                <div class="mt-4 text-sm text-red-600">{$message}</div>
              {/if}
            </div>
          </form>
        </Card>
      </div>
      <div class="col-span-2">
        <Card class="mb-4 min-h-[20rem] max-w-none space-y-6 p-4">
          <div class="rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card header</h3></div>
          <div class="h-full rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card body</h3></div>
          <div class="rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card footer</h3></div>
        </Card>
      </div>
    </div>
  </main>
