<script lang="ts">
  import { Toast } from 'flowbite-svelte';
  import { CheckCircleSolid, CloseCircleSolid } from 'flowbite-svelte-icons';

  let { 
    message = $bindable(''),
    type = 'success', // 'success', 'warning', 'error'
    position = 'top-right'
  } = $props();

  // Determine color based on type
  let toastColor: 'green' | 'yellow' | 'red' = $derived(
    type === 'success' ? 'green' :
    type === 'warning' ? 'yellow' :
    'red'
  );
  
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
  <Toast color={toastColor} class={positionClass}>
    <svelte:fragment slot="icon">
      {#if type === 'success' || type === 'warning'}
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