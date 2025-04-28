<script lang="ts">
    import { Button } from 'flowbite-svelte';
    import { Card } from 'flowbite-svelte';
    import { facilities } from '$lib/stores/facilities';
    import { schedules, selectedSchedule, IsCreating } from '$lib/stores/schedules';
    import { Label, Select, Textarea, Input, Helper } from 'flowbite-svelte';
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createScheduleSchema, scheduleSchema } from '$lib/schemas/schedule';
    import { page } from '$app/stores';

    const { form, errors, enhance, submitting, message } = superForm($page.data.createForm, {
      validators: zodClient(createScheduleSchema),
      resetForm: false,
      dataType: "json",
      onResult: ({ result }) => {
        if (result.type === 'success') {
          if (result.data?.schedule) {
            try {
              const returnedSchedule = result.data.schedule;
              
              // Update the schedules store with the new schedule
              schedules.update(currentSchedules => {
                const filtered = currentSchedules.filter(s => 
                  s.schedule_id !== returnedSchedule.schedule_id && 
                  !(s.schedule_id === null && s.name === returnedSchedule.name)
                );
                return [...filtered, scheduleSchema.parse(returnedSchedule)];
              });
        
              selectedSchedule.set(returnedSchedule);
            } catch (error) {
              console.error("Error updating schedule store:", error);
            }
          }
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
          club_id: $selectedSchedule.club_id || $page.data.user?.club_id || 0,
          schedule_entries: $selectedSchedule.schedule_entries || []
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
  
  <Card size="xl" class="mb-4 min-h-[20rem] w-full space-y-6 p-4 2xl:col-span-2">
    <form id="create-schedule-form" method="POST" action="?/createSchedule" use:enhance>
      <div class="space-y-4">
        <input type="hidden" name="club_id" bind:value={$form.club_id}>
        <input type="hidden" name="schedule_entries" value={JSON.stringify($selectedSchedule?.schedule_entries || [])} />
        
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
        
        {#if $message}
          <div class="mt-4 text-sm text-red-600">{$message}</div>
        {/if}
      </div>
    </form>
  </Card>
