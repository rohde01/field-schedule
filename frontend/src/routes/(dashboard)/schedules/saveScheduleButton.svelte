<!-- SaveScheduleButton.svelte -->
<script lang="ts">
    import { enhance } from '$app/forms';
    import { deletedEntryIds, unsavedChanges, selectedSchedule } from '../../../lib/stores/schedules';
    import { get } from 'svelte/store';
    import { Button, Spinner } from 'flowbite-svelte';
    
    let saving = false;
    let message = '';
    let result: any;
    
    // Using selectedSchedule store directly, no dropdownState needed
</script>

{#if $selectedSchedule}
    <form 
        method="POST" 
        action="?/insertScheduleEntries" 
        use:enhance={() => {
            saving = true;
            message = '';
            
            return async ({ result }) => {
                // first insert new entries
                if (result.type === 'success') {
                    const fd = new FormData();
                    fd.append('scheduleId', String(get(selectedSchedule)!.schedule_id));
                    fd.append('entries', JSON.stringify(get(selectedSchedule)!.schedule_entries));
                    const resUpdate = await fetch('?/updateScheduleEntries', { method: 'POST', body: fd });
                    const updateData = await resUpdate.json();
                    if (resUpdate.ok) {
                        // delete entries removed locally
                        const deleteIds = get(deletedEntryIds);
                        if (deleteIds.length) {
                            const fdDel = new FormData();
                            fdDel.append('deleteIds', JSON.stringify(deleteIds));
                            const resDel = await fetch('?/deleteScheduleEntries', { method: 'POST', body: fdDel });
                            const delData = await resDel.json();
                            if (!resDel.ok) {
                                message = delData?.message || 'Failed to delete entries';
                            }
                            deletedEntryIds.set([]);
                        }
                        message = 'Changes saved successfully!';
                        unsavedChanges.set(false);
                    } else {
                        message = updateData?.message || 'Failed to save changes';
                    }
                } else if (result.type === 'failure') {
                    message = result.data?.message as string || 'Failed to save changes';
                }
                saving = false;
                setTimeout(() => message = '', 3000);
            };
        }}
    >
        <input type="hidden" name="scheduleId" value={$selectedSchedule!.schedule_id} />
        <input type="hidden" name="entries" value={JSON.stringify($selectedSchedule!.schedule_entries)} />
        
        <Button type="submit" size="xs" disabled={saving}>
            {#if saving}
                <Spinner class="me-3" size="4" color="white" />Saving ...
            {:else}
                Save Changes
            {/if}
        </Button>
        
        {#if message}
            <div class={result?.type === 'success' ? 'alert alert-success' : 'alert alert-error'}>
                {message}
            </div>
        {/if}
    </form>
{/if}