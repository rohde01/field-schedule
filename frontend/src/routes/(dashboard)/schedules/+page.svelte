<script lang="ts">
    import Schedule from './Schedule.svelte'
    import CreateCard from './CreateCard.svelte'
    import TeamCard from './ConstraintCard.svelte'
    import ConfigCard from './ConfigCard.svelte'
    import { Datepicker, P, Card, Drawer } from 'flowbite-svelte';
    import { Heading, Button } from 'flowbite-svelte';
    import { PenOutline } from 'flowbite-svelte-icons';
    import { selectedSchedule, IsCreating } from '$lib/stores/schedules';
    import ScheduleDrawer from '$lib/components/ScheduleDrawer.svelte';
    import { superForm } from 'sveltekit-superforms/client';
    import ToastMessage from '$lib/components/Toast.svelte';
    
    let { data } = $props();
    
    let hiddenDrawer = $state(true);
    
    const updateForm = superForm(data.updateForm, {
        onResult: ({ result }) => {
            if (result.type === 'success' && 'data' in result) {
            }
            if (result.type === 'success') {
                hiddenDrawer = true;
            }
            if (result.type === 'failure' && 'data' in result && result.data?.message) {
            }
        }
    });
    
    const { message: updateMessage } = updateForm;
    
    function editSchedule() {
        if ($selectedSchedule) {
            updateForm.form.set({
                schedule_id: $selectedSchedule.schedule_id ?? 0,
                name: $selectedSchedule.name ?? '',
                description: $selectedSchedule.description,
                active_from: $selectedSchedule.active_from,
                active_until: $selectedSchedule.active_until
            });
            hiddenDrawer = false;
        }
    }
</script>

    <div id="main-content" class="relative mx-auto h-full w-full overflow-y-auto bg-gray-50 p-4 dark:bg-gray-900"></div>
    <div id="main-content" class="relative mx-auto h-full w-full overflow-y-auto bg-gray-50 p-4 dark:bg-gray-900">
        {#if $IsCreating}
            <div class="flex gap-4">
                <div style="flex: 2">
                    <CreateCard />
                </div>
                <div style="flex: 7">
                    <TeamCard />
                </div>
                <div style="flex: 1">
                    <ConfigCard />
                </div>
            </div>
        {/if}
      {#if $selectedSchedule}
        <div class="flex items-center gap-2">
          <Heading tag="h1">{$selectedSchedule.name}</Heading>
          {#if !$IsCreating}
            <Button size="sm" outline class="p-2!" on:click={editSchedule}>
              <PenOutline class="w-6 h-6" />
            </Button>
          {/if}
        </div>
      {/if}
        <Schedule />
    </div>

<Drawer placement="right" bind:hidden={hiddenDrawer}>
  <ScheduleDrawer title="Update schedule" bind:hidden={hiddenDrawer} form={updateForm} />
</Drawer>

<ToastMessage message={$updateMessage} />