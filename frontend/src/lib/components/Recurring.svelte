<script lang="ts">
  import { Modal, Button, Radio } from 'flowbite-svelte';
  
  export let open = false;
  export let eventTitle = '';
  export let newTime = '';
  export let modificationType: 'this' | 'all' = 'this';
  export let onConfirm: (type: 'this' | 'all') => void;
  export let onCancel: () => void;
  
  function handleConfirm() {
    onConfirm(modificationType);
    open = false;
  }
  
  function handleCancel() {
    onCancel();
    open = false;
  }
</script>

<Modal bind:open title="Change Recurring Event" size="sm" autoclose={false}>
  <div class="space-y-4">
    <p class="text-gray-700 dark:text-gray-300">
      You're changing the time of a repeating event "{eventTitle}". 
      Do you want to move only this occurrence to {newTime}, or change the time for this and all future occurrences?
    </p>
    
    <div class="space-y-3">
      <Radio bind:group={modificationType} value="this">
        Only this occurrence
      </Radio>
      <Radio bind:group={modificationType} value="all">
        All occurrences
      </Radio>
    </div>
  </div>
  
  <svelte:fragment slot="footer">
    <Button on:click={handleConfirm} class="mr-2">
      Apply Changes
    </Button>
    <Button color="alternative" on:click={handleCancel}>
      Cancel
    </Button>
  </svelte:fragment>
</Modal>