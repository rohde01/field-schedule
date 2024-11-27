<script lang="ts">
    import '../app.css';
    import { user, logout } from '../stores/auth';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    // List of protected routes
    const protectedRoutes = ['/dashboard', '/profile'];

    onMount(() => {
        // Subscribe to route changes
        page.subscribe(($page) => {
            if (protectedRoutes.includes($page.url.pathname) && !$user) {
                goto('/login');
            }
        });
    });
</script>

{#if $user}
    <nav>
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/profile">Profile</a>
        <button on:click={() => logout()}>Logout</button>
    </nav>
{/if}

<slot />
