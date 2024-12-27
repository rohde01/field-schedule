<script lang="ts">
    import type { PageData } from './$types';
    import { setSchedules } from '$stores/schedules';
    import Calendar from '$lib/components/Calendar.svelte';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';
    import SchedulesSidebar from '$lib/components/SchedulesSidebar.svelte';
    import { teams, setTeams } from '$stores/teams';
    import SuperDebug from 'sveltekit-superforms';
    import { superForm } from 'sveltekit-superforms/client';

    let { data }: { data: PageData } = $props();
    const { form: rawForm } = data;
    const { form, enhance } = superForm(rawForm);

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }

        if (data.teams) {
            setTeams(data.teams);
        }
    });

    
</script>

<style>
    .container {
        display: flex;
        justify-content: space-between;
        width: 100%;
    }
    .main-content {
        flex: 3;
        width: 100%;
    }
    .super-debug {
        margin-left: 40px;
        width: 75%;
    }
</style>

<div class="container">
    <div class="main-content">
        <SchedulesDropdown />
        <SchedulesSidebar teams={$teams} {form} />
    </div>
    <div class="super-debug">
        <SuperDebug data={$form} />
    </div>
</div>
