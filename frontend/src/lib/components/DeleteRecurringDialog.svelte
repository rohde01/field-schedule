<script lang="ts">
  import { Modal, Button, Radio } from 'flowbite-svelte';
  import { deleteRecurringEditStore, confirmRecurringDelete, cancelRecurringDelete } from '$lib/utils/deleteRecurringUtils';
  import { derived } from 'svelte/store';

  let localOpen = $state(false);
  let deleteScope: 'this' | 'future' = $state('this');

  const deleteFlow = deleteRecurringEditStore;
  const eventTitle = derived(deleteFlow, $s => $s.eventTitle);
  const isMasterEntry = derived(deleteFlow, $s => $s.isMasterEntry);

  $effect(() => {
    const unsub = deleteFlow.subscribe($s => { 
      localOpen = $s.open; 
      if ($s.open) deleteScope = 'this'; 
    });
    return () => unsub();
  });

  function handleConfirm() { 
    confirmRecurringDelete(deleteScope); 
  }
  
  function handleCancel() { 
    cancelRecurringDelete(); 
  }
</script>

<Modal bind:open={localOpen} title="Delete Recurring Event" size="sm" autoclose={false} on:close={handleCancel}>
  <div class="space-y-4" class:hidden={!localOpen}>
    {#if $isMasterEntry}
      <p class="text-gray-700 dark:text-gray-300">
        You're about to delete the recurring event "{$eventTitle}" and all of its occurrences.
      </p>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        This action cannot be undone.
      </p>
    {:else}
      <p class="text-gray-700 dark:text-gray-300">
        You're deleting a repeating event "{$eventTitle}". What would you like to delete?
      </p>
      <div class="space-y-3">
        <Radio bind:group={deleteScope} value="this">Only this occurrence</Radio>
        <Radio bind:group={deleteScope} value="future">This and all future occurrences</Radio>
      </div>
    {/if}
  </div>
  <svelte:fragment slot="footer">
    <Button color="red" on:click={handleConfirm} class="mr-2">
      {$isMasterEntry ? 'Delete All' : 'Delete'}
    </Button>
    <Button color="alternative" on:click={handleCancel}>Cancel</Button>
  </svelte:fragment>
</Modal>