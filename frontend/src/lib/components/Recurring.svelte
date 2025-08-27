<script lang="ts">
  import { Modal, Button, Radio } from 'flowbite-svelte';
  import { recurringEditStore, confirmRecurringEdit, cancelRecurringEdit } from '$lib/utils/entryEditUtils';
  import { derived } from 'svelte/store';

  let localOpen = $state(false);
  let modificationType: 'this' | 'all' = $state('this');

  const editFlow = recurringEditStore;
  const eventTitle = derived(editFlow, $s => $s.eventTitle);
  const newTime = derived(editFlow, $s => $s.newTime);

  $effect(() => {
    const unsub = editFlow.subscribe($s => { localOpen = $s.open; if ($s.open) modificationType = 'this'; });
    return () => unsub();
  });

  function handleConfirm() { confirmRecurringEdit(modificationType); }
  function handleCancel() { cancelRecurringEdit(); }
</script>

<Modal bind:open={localOpen} title="Change Recurring Event" size="sm" autoclose={false} on:close={handleCancel}>
  <div class="space-y-4" class:hidden={!localOpen}>
    <p class="text-gray-700 dark:text-gray-300">
      You're changing a repeating event "{$eventTitle}". Apply changes to only this occurrence or all occurrences?
    </p>
    <div class="space-y-3">
      <Radio bind:group={modificationType} value="this">Only this occurrence</Radio>
      <Radio bind:group={modificationType} value="all">All occurrences</Radio>
    </div>
    <p class="text-sm font-medium">Change: {$newTime}</p>
  </div>
  <svelte:fragment slot="footer">
    <Button on:click={handleConfirm} class="mr-2">Apply Changes</Button>
    <Button color="alternative" on:click={handleCancel}>Cancel</Button>
  </svelte:fragment>
</Modal>