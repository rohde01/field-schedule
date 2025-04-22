<script lang="ts">
    import '../app.css';
    import { invalidate } from '$app/navigation';
    import { page } from '$app/stores';
    import type { PageData } from './$types';
    import { setFacilities } from '$stores/facilities';
    import { setFields } from '$stores/fields';
    import { setTeams } from '$stores/teams';
    import { setConstraints } from '$stores/constraints';
    import { setSchedules } from '$stores/schedules';

    let { data } = $props<{ data: PageData }>();
    let { session, supabase } = $derived(data);

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

    const isLandingPage = $derived($page.url.pathname === '/');

    // client-side logout function
    async function handleLogout() {
        const { error } = await supabase.auth.signOut();
        if (error) {
            return;
        }
        await invalidate('supabase:auth');
        
        // Create and submit the form programmatically
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/auth?/logout';
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    }
</script>

<div class="min-h-screen bg-sage-50"> 
    <div class="h-24">
        <nav class="fixed top-4 left-0 right-0 z-50">
            <div class="max-w-[90%] mx-auto">
                <div class="bg-white shadow-lg rounded-2xl">
                    <div class="flex justify-between h-14 px-6">
                        <div class="flex items-center space-x-4">
                            {#if data.user}
                                <a href="/schedules" class="nav-link">Schedules</a>
                                <a href="/teams" class="nav-link">Teams</a>
                                <a href="/fields" class="nav-link">Fields</a>
                            {:else}
                                <a href="/" class="nav-link">Home</a>
                            {/if}
                        </div>
                        <div class="flex items-center space-x-4">
                            {#if data.user}
                                <button 
                                    type="button" 
                                    class="btn-secondary" 
                                    onclick={handleLogout}
                                >
                                    Logout
                                </button>
                            {:else}
                                <a href="/auth" class="nav-link">Login</a>
                                <a href="/auth" class="btn-primary">Register</a>
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
