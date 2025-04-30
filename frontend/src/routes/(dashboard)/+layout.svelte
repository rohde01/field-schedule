<script lang="ts">
    import '../../app.css';
    import type { LayoutData } from './$types';
    import { setFacilities } from '$lib/stores/facilities';
    import { setFields } from '$lib/stores/fields';
    import { setTeams } from '$lib/stores/teams';
    import { setSchedules } from '$lib/stores/schedules';
    import { setClubs } from '$lib/stores/clubs';
    import Sidebar from './Sidebar.svelte';
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

    $effect(() => {
        if (data.clubs) {
            setClubs(data.clubs);
        }
    });

</script>

<div class="overflow-hidden lg:flex">
  <Sidebar bind:drawerHidden />
  <div class="relative h-full w-full overflow-y-auto pt-[70px] lg:ml-64">
    {@render children()}
  </div>
</div>