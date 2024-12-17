<script lang="ts">
    import type { PageData } from './$types';
    import { setSchedules } from '$stores/schedules';

    let { data }: { data: PageData } = $props();

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }
    });
</script>