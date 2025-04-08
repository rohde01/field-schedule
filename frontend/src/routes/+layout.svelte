<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { supabase } from '$lib/supabaseClient';
    import { invalidateAll } from '$app/navigation';
    import { page } from '$app/stores';
    import { setFacilities } from '$stores/facilities';
    import { setFields } from '$stores/fields';
    import { setTeams } from '$stores/teams';
    import { setConstraints } from '$stores/constraints';
    import { setSchedules } from '$stores/schedules';
    import { setEvents } from '$stores/events';

    let { data } = $props();

    $effect(() => {
        if (data.facilities) {
            setFacilities(data.facilities);
        }
    });

    $effect(() => {
        if (data.fields) {
            setFields(data.fields);
        }
    });

    $effect(() => {
        if (data.teams) {
            setTeams(data.teams);
        }
    });

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }
    });

    $effect(() => {
        if (data.constraints) {
            setConstraints(data.constraints);
        }
    });

    $effect(() => {
        if (data.events) {
            setEvents(data.events);
        }
    });

    const isLandingPage = $derived($page.url.pathname === '/');
    onMount(() => {
	const {
		data: { subscription }
	} = supabase.auth.onAuthStateChange(() => {
		console.log('Auth state changed, invalidating layout');
		invalidateAll();
	});

	return () => subscription.unsubscribe();
});
</script>

<div class="min-h-screen bg-sage-50"> 
    <div class="h-24">
        <nav class="fixed top-4 left-0 right-0 z-50">
            <div class="max-w-[90%] mx-auto">
                <div class="bg-white shadow-lg rounded-2xl">
                    <div class="flex justify-between h-14 px-6">
                        <div class="flex items-center space-x-4">
                            <a href="/" class="nav-link">Home</a>
                            {#if data.user}
                                <a href="/dashboard" class="nav-link">Dashboard</a>
                                <a href="/schedules" class="nav-link">Schedules</a>
                                <a href="/teams" class="nav-link">Teams</a>
                                <a href="/fields" class="nav-link">Fields</a>
                            {:else}
                                <a href="/dashboard" class="nav-link">Dashboard</a>
                            {/if}
                        </div>
                        <div class="flex items-center space-x-4">
                            {#if data.user}
                                <form action="/logout" method="POST">
                                    <button type="submit" class="btn-secondary">Logout</button>
                                </form>
                            {:else}
                                <a href="/login" class="nav-link">Login</a>
                                <a href="/register" class="btn-primary">Register</a>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    </div>
    <main class="{isLandingPage ? '' : 'max-w-[90%] mx-auto px-4'}">
        <slot />
    </main>
</div>