<script lang="ts">
    import type { PageData } from './$types';
    import { setSchedules } from '$stores/schedules';
    import Calendar from '$lib/components/Calendar.svelte';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';

    let { data }: { data: PageData } = $props();

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }
    });
</script>

<Calendar/>
<SchedulesDropdown />

