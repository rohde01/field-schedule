<script lang="ts">
    import '../../app.css';
    import { invalidate } from '$app/navigation';
    import { page } from '$app/stores';
    import type { LayoutData } from './$types';
    import { setFacilities } from '$stores/facilities';
    import { setFields } from '$stores/fields';
    import { setTeams } from '$stores/teams';
    import { setSchedules } from '$stores/schedules';
    import Sidebar from './Sidebar.svelte';
    import Navbar from './Navbar.svelte';
    import type { Snippet } from 'svelte';

    let { data, children }: { data: LayoutData; children: Snippet } = $props();
    let drawerHidden = $state(false);

    let { supabase } = $derived(data);

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

<header class="fixed top-0 z-40 mx-auto w-full flex-none border-b border-gray-200 bg-white dark:border-gray-600 dark:bg-gray-800">
    <Navbar/>
  </header>
  <div class="overflow-hidden lg:flex">
    <Sidebar bind:drawerHidden />
    <div class="relative h-full w-full overflow-y-auto pt-[70px] lg:ml-64">
      {@render children()}
    </div>
  </div>