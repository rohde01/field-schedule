<script lang="ts">
    import '../../app.css';
    import type { LayoutData } from './$types';
    import { setFacilities } from '$lib/stores/facilities';
    import { setFields } from '$lib/stores/fields';
    import { setTeams } from '$lib/stores/teams';
    import { setSchedules } from '$lib/stores/schedules';
    import Sidebar from './Sidebar.svelte';
    import Navbar from './Navbar.svelte';
    import type { Snippet } from 'svelte';

    let { data, children }: { data: LayoutData; children: Snippet } = $props();
    let drawerHidden = $state(false);

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