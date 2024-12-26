<script lang="ts">
    import type { PageData } from './$types';
    import { setSchedules } from '$stores/schedules';
    import Calendar from '$lib/components/Calendar.svelte';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';
    import SchedulesSidebar from '$lib/components/SchedulesSidebar.svelte';
    import { teams, setTeams } from '$stores/teams';

    let { data }: { data: PageData } = $props();

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }

        if (data.teams) {
            setTeams(data.teams);
        }
    });

    
</script>

<SchedulesDropdown />
<SchedulesSidebar teams={$teams}/>

