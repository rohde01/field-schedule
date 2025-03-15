<script lang="ts">
    import type { PageData } from './$types';
    import { goto } from '$app/navigation';
    import DashboardSidebar from '$lib/components/DashboardSidebar.svelte';
    import Calendar from '$lib/components/Calendar.svelte';
    import { currentView } from '$stores/dashboardNav';
    import { activeSchedules, hasUnsavedChanges, deletedSchedules } from '$stores/activeSchedules';

    let { data }: { data: PageData } = $props();
    const { user } = data;

    $effect(() => {
        if (data.activeSchedules) {
            activeSchedules.set(data.activeSchedules);
        }
    });

    function getGreeting(): string {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good morning';
        if (hour < 17) return 'Good afternoon';
        return 'Good evening';
    }

    function navigateTo(path: string) {
        goto(path);
    }

    function handleKeyDown(event: KeyboardEvent, path: string) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            navigateTo(path);
        }
    }

    async function saveChanges() {
        let success = true;
        
        try {
            // Process deleted schedules
            for (const scheduleId of $deletedSchedules) {
                const formData = new FormData();
                formData.append('activeScheduleId', scheduleId.toString());
                
                const deleteRes = await fetch('?/deleteActiveSchedule', {
                    method: 'POST',
                    body: formData
                });
                
                if (!deleteRes.ok) success = false;
            }
            
            // Process existing and new schedules
            for (const schedule of $activeSchedules) {
                const isNew = schedule.active_schedule_id < 0 || 
                             schedule.active_schedule_id > 1000000000;
                
                const formData = new FormData();
                if (!isNew) {
                    formData.append('activeScheduleId', schedule.active_schedule_id.toString());
                }
                formData.append('schedule_id', schedule.schedule_id.toString());
                formData.append('start_date', new Date(schedule.start_date).toISOString().split('T')[0]);
                formData.append('end_date', new Date(schedule.end_date).toISOString().split('T')[0]);
                
                const endpoint = isNew ? '?/createActiveSchedule' : '?/updateActiveSchedule';
                const res = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
                
                if (!res.ok) success = false;
            }
            
            if (success) {
                window.location.reload();
            }
        } catch (error) {
            console.error('Error saving changes:', error);
        }
    }
</script>

<div class="page-container">
    <DashboardSidebar />
    
    <div class="main-content">
        <h1 class="text-3xl font-bold text-mint-600 mb-6">
            {getGreeting()}, <span class="text-sage-800">{user.first_name ?? 'User'}</span>!
        </h1>

        {#if $currentView === 'active'}
            <div class="calendar-view">
                <Calendar />
                {#if $hasUnsavedChanges}
                    <div class="flex justify-end mt-4">
                        <button type="button" class="btn-primary" onclick={saveChanges}>
                            Save Changes
                        </button>
                    </div>
                {/if}
            </div>
        {:else}
            <div class="dashboard-welcome">
                <div class="dashboard-welcome-text">
                    <p>
                        This is the Dashboard page. For now this is a quiet place, but in the future this will be the place to 
                        <span class="dashboard-welcome-highlight">manage details about your club</span> and make plans for when the schedules 
                        you create should go live.
                    </p>
                    <p>
                        You will be able to create a calendar with field-schedules for the year round, and have it 
                        <span class="dashboard-welcome-highlight">published and updated automatically</span> on a custom URL or your club's homepage. 
                        This will be an easy way for your club to always keep up to date with the current schedule, and what's coming up later in the year.
                    </p>
                    <p>
                        No more messy Google Sheets, or repetitive downloading of Excel files. Your fellow club members may even 
                        <span class="dashboard-welcome-highlight">subscribe to changes</span> you make throughout the year or submit comments 
                        to the schedules for you to review directly in the dashboard. Maybe something third? Or perhaps completely else?
                    </p>
                </div>
            </div>

            <div class="shortcut-container">
                <button 
                    type="button"
                    class="shortcut-box"
                    onclick={() => navigateTo('/schedules')}
                    onkeydown={(e) => handleKeyDown(e, '/schedules')}
                    role="link"
                    tabindex="0">
                    <span class="shortcut-icon">📅</span>
                    <h2 class="shortcut-title">Schedules</h2>
                    <p class="shortcut-description">View and manage your field schedules</p>
                </button>
                
                <button 
                    type="button"
                    class="shortcut-box"
                    onclick={() => navigateTo('/fields')}
                    onkeydown={(e) => handleKeyDown(e, '/fields')}
                    role="link"
                    tabindex="0">
                    <span class="shortcut-icon">🏟️</span>
                    <h2 class="shortcut-title">Fields</h2>
                    <p class="shortcut-description">Manage your sports fields</p>
                </button>
                
                <button 
                    type="button"
                    class="shortcut-box"
                    onclick={() => navigateTo('/teams')}
                    onkeydown={(e) => handleKeyDown(e, '/teams')}
                    role="link"
                    tabindex="0">
                    <span class="shortcut-icon">👥</span>
                    <h2 class="shortcut-title">Teams</h2>
                    <p class="shortcut-description">Organize and view team information</p>
                </button>
            </div>
        {/if}
    </div>
</div>
