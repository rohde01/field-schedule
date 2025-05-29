<script lang="ts">
    import { Card, Toggle, GradientButton, Spinner } from 'flowbite-svelte';
    import { WandMagicSparklesOutline} from 'flowbite-svelte-icons';
    import { get } from 'svelte/store';
    import { selectedSchedule, setScheduleEntries } from '$lib/stores/schedules';
    import { fields } from '$lib/stores/fields';
    import { selectedConstraints } from '$lib/stores/constraints';
    import { fieldSchema } from '$lib/schemas/field';
    import { constraintSchema } from '$lib/schemas/constraint';
    import { scheduleEntrySchema } from '$lib/schemas/schedule';

    let fairWeekdays = true;
    let fairStartTimes = true;
    let generating = false;
    const API_URL = 'http://localhost:8000';

    async function generateModel() {
        generating = true;
        const schedule = get(selectedSchedule);
        if (!schedule) return;
        const facilityId = schedule.facility_id;
        const allFields = get(fields);
        const facilityFields = allFields.filter(f => f.facility_id === facilityId);
        const parsedFields = fieldSchema.array().parse(facilityFields);
        const constraintsList = get(selectedConstraints);
        const parsedConstraints = constraintSchema.array().parse(constraintsList);
        const payload = { fields: parsedFields, constraints: parsedConstraints, weekday_objective: fairWeekdays, 
            start_time_objective: fairStartTimes
         };
        const response = await fetch(`${API_URL}/schedules/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            const data = await response.json();
            try {
                const entries = scheduleEntrySchema.array().parse(data);
                setScheduleEntries(schedule.schedule_id!, entries);
                console.log('Schedule entries updated:', entries);
            } catch (e) {
                console.error('Invalid schedule entries response:', e);
            }
        } else {
            const err = await response.json();
            console.error('Failed to generate schedule:', response.status, err);
        }
        generating = false;
    }
</script>
  
<Card size="xl" class="mb-4 h-[24rem] w-full p-4 2xl:col-span-2 flex flex-col">
    <h3 class="text-l font-medium text-gray-900 dark:text-white mb-4">
        Model settings
    </h3>
    <Toggle color=purple bind:checked={fairWeekdays} class="mb-6">Fair weekdays</Toggle>

    <Toggle color=purple bind:checked={fairStartTimes} class="mb-6">Fair start times</Toggle>

    <GradientButton outline color="purpleToBlue" class="mt-auto" on:click={generateModel} disabled={generating}>
        {#if generating}
            <Spinner class="me-3" size="4" color="white" />Generating
        {:else}
            <WandMagicSparklesOutline class="mr-2 h-5 w-5" />
            Generate
        {/if}
    </GradientButton>

</Card>