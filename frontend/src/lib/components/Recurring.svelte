<script lang="ts">
  import { Modal, Button, Radio } from 'flowbite-svelte';
  import { recurringEditStore, confirmRecurringEdit, cancelRecurringEdit } from '$lib/utils/entryEditUtils';
  import { derived } from 'svelte/store';

  let localOpen = $state(false);
  let modificationType: 'this' | 'future' = $state('this');

  const editFlow = recurringEditStore;
  const eventTitle = derived(editFlow, $s => $s.title);
  const changeDesc = derived(editFlow, $s => $s.changeDesc);

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
      You are changing the event "{$eventTitle}". Apply changes to only this occurrence or this and future occurrences?
    </p>
    <div class="space-y-3">
      <Radio bind:group={modificationType} value="this">Only this occurrence</Radio>
      <Radio bind:group={modificationType} value="future">This and future occurrences</Radio>
    </div>
    <p class="text-sm font-medium">Change: {$changeDesc}</p>
  </div>
  <svelte:fragment slot="footer">
    <Button on:click={handleConfirm} class="mr-2">Apply</Button>
    <Button color="alternative" on:click={handleCancel}>Cancel</Button>
  </svelte:fragment>
</Modal>