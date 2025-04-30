<script lang="ts">
  import { Toast } from 'flowbite-svelte';
  import { CheckCircleSolid, CloseCircleSolid } from 'flowbite-svelte-icons';

  let { 
    message = $bindable(''),
    position = 'top-right'
  } = $props();

  // Determine if this is a success message
  let isSuccess = $derived(message.toLowerCase().includes('success'));
  
  // Compute position classes
  let positionClass = $derived(
    position === 'top-right' ? 'fixed top-20 right-4 z-50' :
    position === 'top-left' ? 'fixed top-20 left-4 z-50' :
    position === 'bottom-right' ? 'fixed bottom-4 right-4 z-50' :
    position === 'bottom-left' ? 'fixed bottom-4 left-4 z-50' :
    position === 'center' ? 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50' :
    'fixed top-20 right-4 z-50'
  );
</script>

{#if message}
  <Toast color={isSuccess ? 'green' : 'red'} class={positionClass}>
    <svelte:fragment slot="icon">
      {#if isSuccess}
        <CheckCircleSolid class="w-5 h-5" />
        <span class="sr-only">Check icon</span>
      {:else}
        <CloseCircleSolid class="w-5 h-5" />
        <span class="sr-only">Error icon</span>
      {/if}
    </svelte:fragment>
    {message}
  </Toast>
{/if}