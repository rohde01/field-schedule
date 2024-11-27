
<script>
    import { user } from '../../stores/auth';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    export let requiredRole = null;

    onMount(() => {
        if (!$user) {
            goto('/login');
            return;
        }

        if (requiredRole && $user.role !== requiredRole) {
            goto('/unauthorized');
        }
    });
</script>

{#if $user}
    <slot />
{/if}