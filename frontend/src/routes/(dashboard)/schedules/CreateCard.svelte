<script lang="ts">
    import { Heading } from 'flowbite-svelte';
    import { Card } from 'flowbite-svelte';
    import type { PlaygroundProps } from '$lib/types/types';
    import { facilities } from '$lib/stores/facilities';
    import { schedules, selectedSchedule } from '$lib/stores/schedules';
    import { Label, Select, Textarea, Input } from 'flowbite-svelte';
    import { get } from 'svelte/store';
  
    let { breadcrumb, title = 'Create something awesome here' }: PlaygroundProps = $props();

    function updateField(field: string) {
      return (event: any) => {
        const raw = event.target.value;
        const value = field === 'facility_id' ? (raw ? parseInt(raw) : null) : raw;
        const current = get(selectedSchedule);
        if (!current) return;
        const updated = { ...current, [field]: value };
        schedules.update(list => list.map(s => s === current ? updated : s));
        selectedSchedule.set(updated);
      };
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
          <div class="space-y-4">
            <Label class="space-y-2">
              <span>Name</span>
              <Input id="name" name="name" type="text" value={$selectedSchedule?.name} on:input={updateField('name')} />
            </Label>

            <Label class="space-y-2">
              <span>Facility</span>
              <Select id="facility" name="facility_id" value={$selectedSchedule?.facility_id} on:change={updateField('facility_id')}>
                <option value="">Select facility</option>
                {#each $facilities as f}
                  <option value={f.facility_id} selected={f.facility_id === $selectedSchedule?.facility_id}>{f.name}</option>
                {/each}
              </Select>
            </Label>

            <Label class="space-y-2">
              <span>Description</span>
              <Textarea id="description" name="description" rows={4} placeholder="Description" on:input={updateField('description')}>{$selectedSchedule?.description}</Textarea>
            </Label>
          </div>
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
