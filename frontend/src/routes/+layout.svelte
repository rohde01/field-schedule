<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { beforeNavigate, afterNavigate } from '$app/navigation';
    import { auth } from '$stores/auth';
    import { goto } from '$app/navigation';
    import type { LayoutData } from './$types';
    import { page } from '$app/stores';
    
    export let data: LayoutData;
    const protectedRoutes = ['/dashboard'];

    $: if (data.user) {
        auth.setUser(data.user);
    }

    $: {
    if (data.user !== undefined) {
        const isProtectedRoute = protectedRoutes.some(route => 
            $page.url.pathname.startsWith(route)
        );

        if (isProtectedRoute && !data.user) {
            goto('/login');
        }
    }
}

    beforeNavigate(({ to, cancel }) => {
        if (!to) return;

        const isProtectedRoute = protectedRoutes.some(route => 
            to.url.pathname.startsWith(route)
        );

        if (isProtectedRoute && !$auth.isAuthenticated) {
            cancel();
            goto('/login');
        }
    });

    afterNavigate(({ from, to }) => {
        if (!to) return;

        const isProtectedRoute = protectedRoutes.some(route => 
            to.url.pathname.startsWith(route)
        );

        if (isProtectedRoute && !$auth.isAuthenticated) {
            goto('/login');
        }
    });

    async function handleLogout(e: MouseEvent) {
        e.preventDefault();
        try {
            await auth.logout();
            await goto('/', { invalidateAll: true });
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }
</script>

<nav>
    <div class="left">
        <a href="/">Home</a>
    {#if $auth.isAuthenticated}
        <a href="/dashboard">Dashboard</a>
    {/if}
    </div>
    <div class="right">
        {#if $auth.isAuthenticated}
            <button on:click={handleLogout}>Logout</button>
        {:else}
            <a href="/login">Login</a>
            <a href="/register">Register</a>
        {/if}
    </div>
</nav>

<slot />
