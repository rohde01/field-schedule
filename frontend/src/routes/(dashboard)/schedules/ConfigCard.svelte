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
    import ToastMessage from '$lib/components/Toast.svelte';
    import { PUBLIC_API_URL } from '$env/static/public';

    let fairWeekdays = true;
    let fairStartTimes = true;
    let generating = false;
    let toastMessage = '';
    let toastType = 'success'; // 'success', 'warning', 'error'

    async function pollJobStatus(jobId: string): Promise<boolean> {
        const schedule = get(selectedSchedule);
        if (!schedule) return false;
        const response = await fetch(`${PUBLIC_API_URL}/schedules/status/${jobId}`);
        if (!response.ok) {
            throw new Error('Failed to check job status');
        }
        
        const data = await response.json();
        // handle intermediate solutions
        if (data.status === 'running' && data.result) {
            const entries = scheduleEntrySchema.array().parse(data.result.entries);
            setScheduleEntries(schedule.schedule_id!, entries);
        }
        
        if (data.status === 'completed') {
            if (data.result) {
                const schedule = get(selectedSchedule);
                if (!schedule) {
                    toastMessage = 'Error: No schedule selected';
                    toastType = 'error';
                    return true;
                }
                const entries = scheduleEntrySchema.array().parse(data.result.entries);
                setScheduleEntries(schedule.schedule_id!, entries);
                toastMessage = data.result.message || 'Schedule generated successfully!';
                
                // Set toast color based on solution type
                if (data.result.message?.includes('OPTIMAL')) {
                    toastType = 'success';
                } else if (data.result.message?.includes('FEASIBLE')) {
                    toastType = 'warning';
                } else {
                    toastType = 'success';
                }
                
            }
            return true;
        } else if (data.status === 'failed') {
            toastMessage = `Error: ${data.error || 'Schedule generation failed'}`;
            toastType = 'error';
            return true;
        }
        
        return false; // Still running
    }

    async function generateModel() {
        generating = true;
        const schedule = get(selectedSchedule);
        if (!schedule) {
            generating = false;
            return;
        }
        
        try {
            const facilityId = schedule.facility_id;
            const allFields = get(fields);
            const facilityFields = allFields.filter(f => f.facility_id === facilityId);
            const parsedFields = fieldSchema.array().parse(facilityFields);
            const constraintsList = get(selectedConstraints);
            const parsedConstraints = constraintSchema.array().parse(constraintsList);
            const payload = { 
                fields: parsedFields, 
                constraints: parsedConstraints, 
                weekday_objective: fairWeekdays, 
                start_time_objective: fairStartTimes
            };
            
            // Start the job
            const response = await fetch(`${PUBLIC_API_URL}/schedules/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const err = await response.json();
                toastMessage = `Error: ${err.detail || 'Failed to start schedule generation'}`;
                toastType = 'error';
                generating = false;
                return;
            }
            
            const jobData = await response.json();
            const jobId = jobData.job_id;
            
            // Poll for results
            const pollInterval = setInterval(async () => {
                try {
                    const isComplete = await pollJobStatus(jobId);
                    if (isComplete) {
                        clearInterval(pollInterval);
                        generating = false;
                    }
                } catch (error) {
                    clearInterval(pollInterval);
                    toastMessage = 'Error: Failed to check job status';
                    toastType = 'error';
                    generating = false;
                }
            }, 500); // Poll every 0.5 seconds
            
        } catch (error) {
            toastMessage = 'Error: Failed to generate schedule';
            toastType = 'error';
            generating = false;
        }
    }
</script>
  
<Card size="xl" class="mb-4 h-[24rem] w-full p-4 2xl:col-span-2 flex flex-col">
    <h3 class="text-l font-medium text-gray-900 dark:text-white mb-4">
        Model settings
    </h3>
    <Toggle color=purple bind:checked={fairWeekdays} class="mb-6">Fair weekdays</Toggle>

    <Toggle color=purple bind:checked={fairStartTimes} class="mb-6">Age grouping</Toggle>

    <GradientButton outline color="purpleToBlue" class="mt-auto" on:click={generateModel} disabled={generating}>
        {#if generating}
            <Spinner class="me-3" size="4" color="white" />Generating
        {:else}
            <WandMagicSparklesOutline class="mr-2 h-5 w-5" />
            Generate
        {/if}
    </GradientButton>

</Card>

<!-- Toast message -->
<ToastMessage message={toastMessage} type={toastType} />